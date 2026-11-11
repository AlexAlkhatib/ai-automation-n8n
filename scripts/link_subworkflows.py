#!/usr/bin/env python3
"""Relie les sous-workflows après import.

n8n réattribue les identifiants à l'import : les nœuds *Execute Workflow* et
*toolWorkflow* du dépôt sont donc volontairement livrés sans identifiant. Ce
script retrouve les workflows cibles par leur nom, puis met à jour les nœuds via
l'API publique n8n.

Prérequis :
    * une instance n8n accessible (locale ou Docker) ;
    * une clé API : n8n → Settings → n8n API → Create an API key.

Usage :
    N8N_URL=http://localhost:5678 N8N_API_KEY=xxx python3 scripts/link_subworkflows.py
    ... --dry-run     # affiche les modifications sans les appliquer
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib import error, request

ROOT = Path(__file__).resolve().parents[1]

# Nom du nœud → nom du workflow cible tel qu'il apparaît dans n8n.
TARGETS_BY_NODE = {
    "Run Video Subworkflow": "05 — Image-to-Video Subworkflow (Seedance)",
    "Create_Image": "09 — Subworkflow: Text-to-Image",
    "Create_Video": "09 — Subworkflow: Text-to-Video",
    "Caption_Writer_Agent": "09 — Subworkflow: Social Captions",
    "Blogpost_Copywriter": "09 — Subworkflow: Blogpost Copywriter",
}


def api(method: str, url: str, api_key: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = request.Request(url, data=data, method=method)
    req.add_header("X-N8N-API-KEY", api_key)
    req.add_header("Accept", "application/json")
    if data:
        req.add_header("Content-Type", "application/json")
    with request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def list_workflows(base_url: str, api_key: str) -> list[dict]:
    workflows: list[dict] = []
    cursor: str | None = None
    while True:
        url = f"{base_url}/api/v1/workflows?limit=250"
        if cursor:
            url += f"&cursor={cursor}"
        page = api("GET", url, api_key)
        workflows.extend(page.get("data", []))
        cursor = page.get("nextCursor")
        if not cursor:
            break
    return workflows


def connect_nodes(nodes: list[dict], by_name: dict[str, str], dry_run: bool) -> list[str]:
    changes: list[str] = []
    for node in nodes:
        target_name = TARGETS_BY_NODE.get(node.get("name", ""))
        if not target_name:
            continue
        target_id = by_name.get(target_name)
        if not target_id:
            changes.append(f"  ⚠ workflow cible introuvable : {target_name}")
            continue
        parameters = node.setdefault("parameters", {})
        workflow_id = parameters.get("workflowId")
        current = workflow_id.get("value") if isinstance(workflow_id, dict) else workflow_id
        if current == target_id:
            changes.append(f"  = {node['name']} déjà relié")
            continue
        if isinstance(workflow_id, dict):
            workflow_id["value"] = target_id
            workflow_id.pop("cachedResultName", None)
        else:
            parameters["workflowId"] = {"__rl": True, "value": target_id, "mode": "list"}
        changes.append(f"  → {node['name']} relié à {target_name} ({target_id})")
        if not dry_run:
            pass
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Simulation uniquement")
    parser.add_argument("--url", default=os.environ.get("N8N_URL", "http://localhost:5678"))
    args = parser.parse_args()

    api_key = os.environ.get("N8N_API_KEY", "")
    base_url = args.url.rstrip("/")
    if not api_key:
        print("✗ N8N_API_KEY manquante (n8n → Settings → n8n API).", file=sys.stderr)
        return 2

    try:
        workflows = list_workflows(base_url, api_key)
    except error.HTTPError as exc:
        print(f"✗ API n8n : HTTP {exc.code} — vérifiez l'URL et la clé.", file=sys.stderr)
        return 1
    except error.URLError as exc:
        print(f"✗ Instance injoignable : {base_url} ({exc.reason})", file=sys.stderr)
        return 1

    by_name = {workflow["name"]: workflow["id"] for workflow in workflows}
    missing = sorted(
        name for name in TARGETS_BY_NODE.values() if name not in by_name
    )
    for name in missing:
        print(f"⚠ workflow cible absent de l'instance : {name}")

    updated = 0
    for summary in workflows:
        full = api("GET", f"{base_url}/api/v1/workflows/{summary['id']}", api_key)
        changes = connect_nodes(full.get("nodes", []), by_name, args.dry_run)
        if not changes:
            continue
        print(f"\n{full['name']}")
        print("\n".join(changes))
        if any("→" in change for change in changes):
            updated += 1
        if args.dry_run:
            continue
        payload = {
            "name": full["name"],
            "nodes": full["nodes"],
            "connections": full["connections"],
            "settings": full.get("settings", {}),
            "staticData": full.get("staticData"),
        }
        try:
            api("PUT", f"{base_url}/api/v1/workflows/{full['id']}", api_key, payload)
        except error.HTTPError as exc:
            print(f"  ✗ mise à jour refusée (HTTP {exc.code})", file=sys.stderr)
            return 1

    suffix = " (simulation)" if args.dry_run else ""
    print(f"\n✓ {updated} workflow(s) mis à jour{suffix}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
