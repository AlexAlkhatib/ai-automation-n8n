#!/usr/bin/env python3
"""Contrôle qualité des workflows n8n du dépôt.

Vérifie, sans instance n8n :

* la validité JSON et la structure minimale d'un export n8n ;
* l'unicité des noms de nœuds et l'intégrité des connexions ;
* l'absence de secrets, d'identifiants d'instance et de données personnelles ;
* la cohérence entre ``catalog.json`` et les fichiers présents ;
* l'existence des variables d'environnement référencées (``$env.*``).

Code de sortie : 0 si tout est valide, 1 sinon.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS_DIR = ROOT / "workflows"
CATALOG_PATH = ROOT / "catalog.json"
ENV_EXAMPLE = ROOT / ".env.example"

FORBIDDEN_ROOTS = {"credentials", "pinData", "id", "versionId", "meta"}
FORBIDDEN_ANYWHERE = {"cachedResultUrl", "cachedResultName", "apiKey", "password", "secret"}
ALLOWED_EMAILS = {"youremail@example.com"}

SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("clé OpenAI", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")),
    ("clé Google", re.compile(r"\bAIza[0-9A-Za-z_-]{20,}")),
    ("token Slack", re.compile(r"\bxox[baprs]-[0-9A-Za-z-]{10,}")),
    ("token GitHub", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}")),
    ("clé API n8n", re.compile(r"\bn8n_api_[A-Za-z0-9]{20,}")),
    ("clé privée", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.")),
]

errors: list[str] = []
warnings: list[str] = []


def error(message: str) -> None:
    errors.append(message)


def warn(message: str) -> None:
    warnings.append(message)


def walk_keys(value: Any, forbidden: set[str], path: str, file_label: str) -> None:
    """Signale les clés interdites à n'importe quel niveau d'un export."""
    if isinstance(value, dict):
        for key, child in value.items():
            if key in forbidden:
                error(f"{file_label} : clé interdite « {key} » à {path}")
            walk_keys(child, forbidden, f"{path}.{key}", file_label)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk_keys(child, forbidden, f"{path}[{index}]", file_label)


def check_connections(workflow: dict[str, Any], file_label: str) -> int:
    nodes = {node.get("name"): node for node in workflow.get("nodes", [])}
    connections = workflow.get("connections", {})
    if not isinstance(connections, dict):
        error(f"{file_label} : « connections » doit être un objet")
        return 0

    count = 0
    for source, outputs in connections.items():
        if source not in nodes:
            error(f"{file_label} : connexion depuis un nœud inconnu « {source} »")
            continue
        if not isinstance(outputs, dict):
            error(f"{file_label} : sorties invalides pour « {source} »")
            continue
        for output_type, branches in outputs.items():
            for branch in branches:
                for connection in branch:
                    count += 1
                    target = connection.get("node")
                    if target not in nodes:
                        error(
                            f"{file_label} : « {source} » pointe vers un nœud inconnu « {target} »"
                        )
                    if connection.get("type") != output_type:
                        warn(
                            f"{file_label} : type incohérent entre « {source} » et « {target} »"
                        )
    return count


def check_workflow(path: Path, catalog_names: dict[str, str]) -> dict[str, Any]:
    file_label = str(path.relative_to(ROOT))
    try:
        workflow = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        error(f"{file_label} : JSON invalide ({exc})")
        return {}

    for required in ("name", "nodes", "connections"):
        if required not in workflow:
            error(f"{file_label} : clé obligatoire manquante « {required} »")

    for key in FORBIDDEN_ROOTS:
        if key in workflow:
            error(f"{file_label} : clé de métadonnées interdite « {key} »")
    walk_keys(
        workflow,
        {"credentials", "cachedResultUrl"},
        "$",
        file_label,
    )

    nodes = workflow.get("nodes", [])
    if not isinstance(nodes, list) or not nodes:
        error(f"{file_label} : aucun nœud")
        return workflow

    names = [node.get("name") for node in nodes]
    duplicates = {name for name in names if names.count(name) > 1}
    if duplicates:
        error(f"{file_label} : noms de nœuds dupliqués {sorted(duplicates)}")

    for node in nodes:
        if not node.get("type"):
            error(f"{file_label} : nœud sans type « {node.get('name')} »")
        if not node.get("typeVersion"):
            warn(f"{file_label} : nœud sans typeVersion « {node.get('name')} »")
        if "position" not in node:
            warn(f"{file_label} : nœud sans position « {node.get('name')} »")

    connections = check_connections(workflow, file_label)

    text = path.read_text(encoding="utf-8")
    for label, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            error(f"{file_label} : secret potentiel ({label}) : {match.group(0)[:12]}…")

    for email in set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", text)):
        if email not in ALLOWED_EMAILS:
            warn(f"{file_label} : adresse e-mail codée en dur « {email} »")

    name = workflow.get("name", "")
    if name not in catalog_names:
        error(f"{file_label} : workflow absent de catalog.json (nom « {name} »)")
    elif catalog_names[name] != path.name:
        error(f"{file_label} : catalog.json attend le fichier {catalog_names[name]}")

    if workflow.get("active") is not False:
        warn(f"{file_label} : le workflow devrait être inactif à l'import")

    workflow["_stats"] = {"nodes": len(nodes), "connections": connections}
    return workflow


def check_catalog() -> tuple[dict[str, dict[str, Any]], set[str]]:
    if not CATALOG_PATH.is_file():
        error("catalog.json introuvable")
        return {}, set()

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    names: dict[str, str] = {}
    slugs: set[str] = set()
    files: set[str] = set()

    for module in catalog.get("modules", []):
        slug = module.get("slug", "")
        if slug in slugs:
            error(f"catalog.json : slug dupliqué « {slug} »")
        slugs.add(slug)

        if not re.fullmatch(r"\d{2}-[a-z0-9-]+", slug):
            error(f"catalog.json : slug invalide « {slug} » (attendu 01-mon-module)")

        for key in ("title", "summary", "level", "duration"):
            if not module.get(key):
                warn(f"catalog.json : module {slug} sans « {key} »")

        for workflow in module.get("workflows", []):
            relative = WORKFLOWS_DIR / slug / workflow["file"]
            files.add(str(relative.relative_to(ROOT)))
            if not relative.is_file():
                error(f"catalog.json : fichier manquant {relative.relative_to(ROOT)}")
            if workflow["name"] in names:
                error(f"catalog.json : nom de workflow dupliqué « {workflow['name']} »")
            names[workflow["name"]] = workflow["file"]

        for credential in module.get("credentials", []):
            if not credential.get("type"):
                error(f"catalog.json : credential sans type dans {slug}")
    return catalog, files


def check_env(workflows: dict[str, dict[str, Any]]) -> None:
    used: set[str] = set()
    for workflow in workflows.values():
        for node in workflow.get("nodes", []):
            used.update(re.findall(r"\$env\.([A-Z0-9_]+)", json.dumps(node)))

    declared: set[str] = set()
    if ENV_EXAMPLE.is_file():
        for line in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^([A-Z0-9_]+)=", line.strip())
            if match:
                declared.add(match.group(1))

    for name in sorted(used - declared):
        error(f"Variable d'environnement utilisée mais absente de .env.example : {name}")


def main() -> int:
    if not WORKFLOWS_DIR.is_dir():
        print("✗ dossier workflows/ introuvable", file=sys.stderr)
        return 1

    catalog, catalog_files = check_catalog()
    names = {
        workflow["name"]: workflow["file"]
        for module in catalog.get("modules", [])
        for workflow in module.get("workflows", [])
    }

    paths = sorted(WORKFLOWS_DIR.rglob("*.json"))
    found_files = {str(path.relative_to(ROOT)) for path in paths}
    for missing in sorted(found_files - catalog_files):
        error(f"{missing} : fichier non référencé dans catalog.json")

    workflows: dict[str, dict[str, Any]] = {}
    total_nodes = total_connections = 0
    for path in paths:
        workflow = check_workflow(path, names)
        if workflow:
            workflows[str(path.relative_to(ROOT))] = workflow
            stats = workflow.get("_stats", {})
            total_nodes += stats.get("nodes", 0)
            total_connections += stats.get("connections", 0)

    check_env(workflows)

    for unexpected in ROOT.rglob(".DS_Store"):
        error(f"fichier système à supprimer : {unexpected.relative_to(ROOT)}")

    print("─" * 64)
    print("Validation des workflows n8n")
    print("─" * 64)
    print(f"  Workflows      : {len(workflows)}")
    print(f"  Modules        : {len(catalog.get('modules', []))}")
    print(f"  Nœuds          : {total_nodes}")
    print(f"  Connexions     : {total_connections}")

    for message in warnings:
        print(f"  ⚠ {message}")
    for message in errors:
        print(f"  ✗ {message}")

    if errors:
        print(f"\n✗ {len(errors)} erreur(s), {len(warnings)} avertissement(s)")
        return 1

    print(f"\n✓ Tout est valide ({len(warnings)} avertissement(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
