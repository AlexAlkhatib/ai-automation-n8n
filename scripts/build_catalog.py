#!/usr/bin/env python3
"""Génère le catalogue Markdown et les README de modules depuis catalog.json.

Sorties :

* ``docs/WORKFLOWS.md`` — catalogue complet ;
* ``workflows/README.md`` — index de la bibliothèque ;
* ``workflows/<module>/README.md`` — fiche pédagogique de chaque module.

Usage :
    python3 scripts/build_catalog.py            # écrit les fichiers
    python3 scripts/build_catalog.py --check    # échoue si un fichier diverge
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS_DIR = ROOT / "workflows"
CATALOG = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))

AI_ROLE_BY_TYPE = [
    ("lmchat", "Modèle de langage"),
    ("memory", "Mémoire"),
    ("embedding", "Embeddings"),
    ("vectorstore", "Base vectorielle"),
    ("documentdefaultdataloader", "Chargement documentaire"),
    ("textsplitter", "Découpage de texte"),
    ("tool", "Outil de l'agent"),
]


def load_workflow(module: dict[str, Any], workflow: dict[str, Any]) -> dict[str, Any]:
    path = WORKFLOWS_DIR / module["slug"] / workflow["file"]
    return json.loads(path.read_text(encoding="utf-8"))


def is_trigger(node: dict[str, Any]) -> bool:
    node_type = node.get("type", "").lower()
    return "trigger" in node_type


def main_paths(workflow: dict[str, Any], limit: int = 4) -> list[str]:
    """Construit les chemins principaux déclencheur → … → sortie."""
    connections = workflow.get("connections", {})
    nodes = {node["name"]: node for node in workflow.get("nodes", [])}
    paths: list[str] = []

    def visit(name: str, trail: list[str]) -> None:
        if len(paths) >= limit or len(trail) > 10:
            return
        outputs = connections.get(name, {}).get("main", [])
        targets = [connection["node"] for branch in outputs for connection in branch]
        if not targets:
            paths.append(" → ".join(trail))
            return
        for target in targets:
            if target in trail:
                continue
            visit(target, trail + [target])

    for node in workflow.get("nodes", []):
        if is_trigger(node):
            visit(node["name"], [node["name"]])
        if len(paths) >= limit:
            break

    if not paths:
        paths.append(" → ".join(node["name"] for node in workflow.get("nodes", [])[:4]))
    return [path for path in dict.fromkeys(paths)]


def ai_resources(workflow: dict[str, Any]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for node in workflow.get("nodes", []):
        node_type = node.get("type", "").lower()
        for fragment, label in AI_ROLE_BY_TYPE:
            if fragment in node_type:
                grouped[label].append(node["name"])
                break
    return dict(grouped)


def module_stats(module: dict[str, Any]) -> tuple[int, int]:
    node_count = 0
    for workflow in module["workflows"]:
        node_count += len(load_workflow(module, workflow).get("nodes", []))
    return len(module["workflows"]), node_count


def module_readme(module: dict[str, Any]) -> str:
    workflow_count, node_count = module_stats(module)
    lines = [
        f"# {module['id']} · {module['title']}",
        "",
        f"> **{module['level']}** · {module['duration']} · {workflow_count} workflow(s) · "
        f"{node_count} nœuds",
        "",
        module["summary"],
        "",
        "## Ce que vous apprenez",
        "",
    ]
    lines += [f"- {outcome}" for outcome in module.get("outcomes", [])]

    lines += [
        "",
        "## Workflows",
        "",
        "| Fichier | Rôle | Déclencheur | Sortie |",
        "| --- | --- | --- | --- |",
    ]
    for workflow in module["workflows"]:
        lines.append(
            f"| [`{workflow['file']}`]({workflow['file']}) | {workflow['role']} | "
            f"{workflow['trigger']} | {workflow['output']} |"
        )

    for workflow in module["workflows"]:
        data = load_workflow(module, workflow)
        lines += ["", f"### {workflow['name']}", "", "**Parcours principal**", "", "```text"]
        lines += main_paths(data)
        lines += ["```", ""]

        resources = ai_resources(data)
        if resources:
            lines += ["| Ressource | Nœuds |", "| --- | --- |"]
            for label, node_names in resources.items():
                lines.append(f"| {label} | {', '.join(node_names)} |")
            lines.append("")

    if module.get("credentials"):
        lines += ["## Credentials n8n requis", "", "| Type | Libellé | Utilisé pour |", "| --- | --- | --- |"]
        for credential in module["credentials"]:
            lines.append(
                f"| `{credential['type']}` | {credential['label']} | {credential['usedFor']} |"
            )
        lines += [
            "",
            "Créez-les dans **n8n → Credentials → Create credential**, puis sélectionnez-les "
            "dans les nœuds concernés.",
            "",
        ]

    if module.get("env"):
        lines += ["## Variables d'environnement", ""]
        for item in module["env"]:
            lines.append(f"- `{item['name']}` — {item['description']}")
        lines.append("")

    lines += [
        "## Importer ce module",
        "",
        "```bash",
        "n8n import:workflow --input "
        + " ".join(f"workflows/{module['slug']}/{w['file']}" for w in module["workflows"]),
        "```",
        "",
        "Ou, depuis l'interface : **Workflows → Import from File**, fichier par fichier.",
        "",
    ]

    if module["id"] == "05" or module["id"] == "09":
        lines += [
            "> Les nœuds *Execute Workflow* / *toolWorkflow* ne conservent pas les identifiants "
            "d'instance : après import, lancez `python3 scripts/link_subworkflows.py` pour les "
            "relier automatiquement.",
            "",
        ]

    if module.get("notes"):
        lines += ["## Points d'attention", ""]
        lines += [f"- {note}" for note in module["notes"]]
        lines.append("")

    lines += [
        "---",
        "",
        f"Documentation complète : [docs/WORKFLOWS.md](../../docs/WORKFLOWS.md) · "
        f"[Guide PDF](../../docs/AI-Workflow-Automation-n8n-Guide.pdf)",
        "",
    ]
    return "\n".join(lines)


def library_index() -> str:
    lines = [
        "# Bibliothèque de workflows",
        "",
        "Chaque dossier contient un module autonome : workflows exportés, fiche pédagogique et "
        "prérequis. Importez les fichiers JSON dans n8n via **Workflows → Import from File**.",
        "",
        "| # | Module | Niveau | Durée | Workflows | Nœuds | Fiche |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for module in CATALOG["modules"]:
        workflow_count, node_count = module_stats(module)
        lines.append(
            f"| {module['id']} | {module['title']} | {module['level']} | {module['duration']} | "
            f"{workflow_count} | {node_count} | [README]({module['slug']}/README.md) |"
        )
    lines += [
        "",
        "## Parcours conseillé",
        "",
        "1. **01 → 02** : bases d'un agent, planification, enchaînement d'agents.",
        "2. **03 → 04** : APIs asynchrones, polling et livraison de médias.",
        "3. **05** : orchestration et réutilisation par sous-workflows.",
        "4. **06 → 08** : outils métier, RAG, MCP.",
        "5. **09** : architecture multi-agents complète.",
        "6. **10** : robustesse et supervision en production.",
        "",
        "Voir [docs/WORKFLOWS.md](../docs/WORKFLOWS.md) pour les détails et les prérequis.",
        "",
    ]
    return "\n".join(lines)


def full_catalog() -> str:
    total_workflows = sum(len(module["workflows"]) for module in CATALOG["modules"])
    total_nodes = sum(module_stats(module)[1] for module in CATALOG["modules"])

    lines = [
        "# Catalogue des workflows",
        "",
        "> Généré automatiquement depuis [`catalog.json`](../catalog.json) — "
        "ne pas éditer à la main. Lancez `python3 scripts/build_catalog.py`.",
        "",
        f"**{len(CATALOG['modules'])} modules · {total_workflows} workflows · "
        f"{total_nodes} nœuds · version {CATALOG['version']}**",
        "",
        "| # | Module | Niveau | Durée | Workflows | Nœuds | Intégrations |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for module in CATALOG["modules"]:
        workflow_count, node_count = module_stats(module)
        lines.append(
            f"| [{module['id']}]({module['slug']}/README.md) | {module['title']} | "
            f"{module['level']} | {module['duration']} | {workflow_count} | {node_count} | "
            f"{', '.join(module.get('stack', [])[:3])} |"
        )

    lines += ["", "---", ""]

    for module in CATALOG["modules"]:
        workflow_count, node_count = module_stats(module)
        lines += [
            f"## {module['id']} · {module['title']}",
            "",
            f"*{module['tagline']}*",
            "",
            f"**Niveau** {module['level']} · **Durée** {module['duration']} · "
            f"**{workflow_count} workflow(s)** · **{node_count} nœuds**",
            "",
            module["summary"],
            "",
            f"Fiche détaillée : [workflows/{module['slug']}/README.md]"
            f"(../workflows/{module['slug']}/README.md)",
            "",
            "| Workflow | Fichier | Rôle | Déclencheur | Sortie |",
            "| --- | --- | --- | --- | --- |",
        ]
        for workflow in module["workflows"]:
            lines.append(
                f"| {workflow['name']} | [`{workflow['file']}`]"
                f"(../workflows/{module['slug']}/{workflow['file']}) | {workflow['role']} | "
                f"{workflow['trigger']} | {workflow['output']} |"
            )
        lines.append("")

        if module.get("notes"):
            lines += ["**Points d'attention**", ""]
            lines += [f"- {note}" for note in module["notes"]]
            lines.append("")

    lines += ["---", "", "## Matrice des credentials", "",
              "| Module | Credentials requis |", "| --- | --- |"]
    for module in CATALOG["modules"]:
        credentials = ", ".join(c["type"] for c in module.get("credentials", []))
        lines.append(f"| {module['id']} · {module['title']} | {credentials or '—'} |")

    lines += [
        "",
        "## Variables d'environnement",
        "",
        "| Variable | Modules | Rôle |",
        "| --- | --- | --- |",
    ]
    for module in CATALOG["modules"]:
        for item in module.get("env", []):
            lines.append(f"| `{item['name']}` | {module['id']} | {item['description']} |")

    lines += [
        "",
        "## Importer toute la bibliothèque",
        "",
        "```bash",
        "# instance locale (SQLite dans .n8n/)",
        "npx n8n import:workflow --separate --input=workflows",
        "",
        "# relier les sous-workflows",
        "N8N_URL=http://localhost:5678 N8N_API_KEY=... python3 scripts/link_subworkflows.py",
        "```",
        "",
        "Ou avec Docker : `docker compose up -d`, puis import via l'interface.",
        "",
    ]
    return "\n".join(lines)


def write(path: Path, content: str, check: bool) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            print(f"✗ à régénérer : {path.relative_to(ROOT)}")
            return False
        return True
    path.write_text(content, encoding="utf-8")
    print(f"✓ {path.relative_to(ROOT)}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="Vérifie que les fichiers générés sont à jour")
    args = parser.parse_args()

    ok = True
    ok &= write(WORKFLOWS_DIR / "README.md", library_index(), args.check)
    for module in CATALOG["modules"]:
        ok &= write(WORKFLOWS_DIR / module["slug"] / "README.md", module_readme(module), args.check)
    ok &= write(ROOT / "docs/WORKFLOWS.md", full_catalog(), args.check)

    if args.check and not ok:
        print("\nCatalogue obsolète : lancez `python3 scripts/build_catalog.py`.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
