#!/usr/bin/env python3
"""Migre les exports n8n d'origine vers l'arborescence `workflows/`.

Transformations appliquées (idempotentes sur une source brute) :

* renommage des dossiers et fichiers (typos, casse, noms génériques) ;
* suppression des métadonnées d'instance : ``id``, ``versionId``, ``meta``,
  ``pinData`` (données de test contenant des informations personnelles) ;
* suppression des blocs ``credentials`` (noms de comptes internes à l'instance) ;
* neutralisation des identifiants de ressources personnelles (Google Drive,
  Sheets, Docs, Pinecone, Telegram) pour forcer une reconfiguration locale ;
* harmonisation des noms de nœuds et réécriture des connexions ;
* titres de workflows explicites, préfixés par le numéro de module.

Usage :
    python3 scripts/sanitize_workflows.py --source _extract/ai-automation-n8n-main
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]

# source relative -> (destination relative, nouveau nom de workflow, renommages de nœuds)
WORKFLOWS: dict[str, tuple[str, str, dict[str, str]]] = {
    "01. building-first-ai-agent/building-your-first-ai-email-agent-on-n8n.json": (
        "workflows/01-email-agent/email-agent.json",
        "01 — Email AI Agent (Starter)",
        {},
    ),
    "02. multi-agent-research-with-perplexity/multi-agent-research-with-perplexity-or-openai.json": (
        "workflows/02-research-agent/daily-ai-news-digest.json",
        "02 — Daily AI News Digest (Perplexity + GPT)",
        {},
    ),
    "03. text-to-image/test-to-image.json": (
        "workflows/03-text-to-image/text-to-image.json",
        "03 — Text-to-Image Studio (Wavespeed)",
        {
            "Wait 15 Seconds": "Poll Wait (15s)",
            "If": "Completed?",
            "Wait Another 15 Secs": "Retry Wait (15s)",
            "Send a message": "Email Image",
        },
    ),
    "04. text-to-video/text-to-video.json": (
        "workflows/04-text-to-video/text-to-video.json",
        "04 — Text-to-Video Studio (Veo 3)",
        {
            "Wait 15 Secs": "Poll Wait (15s)",
            "If": "Completed?",
            "Wait another 15 Secs": "Retry Wait (15s)",
            "Send a message": "Email Video",
        },
    ),
    "05. calling-subworkflows/main-workflow-demo.json": (
        "workflows/05-subworkflows/image-to-video-orchestrator.json",
        "05 — Image-to-Video Orchestrator",
        {
            "Google Drive Trigger": "New Image in Drive",
            "Telegram": "Notify Telegram (photo)",
            "Image Log": "Log to Google Sheets",
            "Execute Workflow": "Run Video Subworkflow",
        },
    ),
    "05. calling-subworkflows/sub-workflow-demo.json": (
        "workflows/05-subworkflows/image-to-video-subworkflow.json",
        "05 — Image-to-Video Subworkflow (Seedance)",
        {
            "When Executed by Another Workflow": "When Called by Orchestrator",
            "Telegram": "Ask Video Idea (Telegram)",
            "Google Sheet Log": "Sheets Log (AI tool)",
            "Seedance Post": "Create Video (Seedance)",
            "Wait 15 secs": "Poll Wait (15s)",
            "Seedance Get": "Check Video Status",
            "If": "Completed?",
            "Wait Another 15 Secs": "Retry Wait (15s)",
            "Telegram Send A Video": "Send Video on Telegram",
        },
    ),
    "06. fun-slack-impersonator/fun-slack-impersonator.json": (
        "workflows/06-slack-agent/slack-ai-teammate.json",
        "06 — Slack AI Teammate",
        {},
    ),
    "07. rag-agent-pinecone-vector-db/RAG-AI-Agent-Vector-DB.json": (
        "workflows/07-rag-pinecone/rag-support-agent.json",
        "07 — RAG Support Agent (Pinecone)",
        {},
    ),
    "07. rag-agent-pinecone-vector-db/pinecone-upsert.json": (
        "workflows/07-rag-pinecone/knowledge-ingestion.json",
        "07 — Knowledge Ingestion (Drive → Pinecone)",
        {
            "Loop Over Items": "Loop Files",
            "Download file": "Download from Drive",
            "Pinecone Vector Store": "Insert into Pinecone",
            "Default Data Loader - Binary": "Load Binary Document",
            "Recursive Character Text Splitter": "Split Text (500/50)",
        },
    ),
    "08. mcp/mcp-in-n8n.json": (
        "workflows/08-mcp/mcp-lab.json",
        "08 — MCP Lab",
        {},
    ),
    "09. replace-your-marketing-team/Replace-Your-Marketing-Team.json": (
        "workflows/09-marketing-team/marketing-team-orchestrator.json",
        "09 — Marketing Team Orchestrator",
        {},
    ),
    "09. replace-your-marketing-team/Text-to-image-Subworflow.json": (
        "workflows/09-marketing-team/text-to-image-subworkflow.json",
        "09 — Subworkflow: Text-to-Image",
        {},
    ),
    "09. replace-your-marketing-team/Text-to-video-SubWorkflow.json": (
        "workflows/09-marketing-team/text-to-video-subworkflow.json",
        "09 — Subworkflow: Text-to-Video",
        {},
    ),
    "09. replace-your-marketing-team/Caption-Copywriter-subworkflow.json": (
        "workflows/09-marketing-team/caption-copywriter-subworkflow.json",
        "09 — Subworkflow: Social Captions",
        {},
    ),
    "09. replace-your-marketing-team/Blogpost-Copywriter-subworkflow.json": (
        "workflows/09-marketing-team/blogpost-copywriter-subworkflow.json",
        "09 — Subworkflow: Blogpost Copywriter",
        {},
    ),
}

# Clés dont la valeur littérale pointe vers une ressource interne à l'auteur.
CLEARABLE_RESOURCES = {
    "folderToWatch",
    "documentId",
    "sheetName",
    "folderId",
    "workflowId",
    "pineconeIndex",
    "documentURL",
    "fileId",
}

# Remplacements explicites, par fichier de destination.
def patch_mcp(workflow: dict[str, Any]) -> None:
    """MCP : URL de test personnelle -> placeholder documenté."""
    for node in workflow["nodes"]:
        node_type = node.get("type", "")
        if node_type.endswith("mcpTrigger"):
            node["parameters"]["path"] = "mcp-lab"
        elif node_type.endswith("mcpClientTool"):
            node["parameters"]["endpointUrl"] = "https://YOUR-N8N-DOMAIN/mcp-test/mcp-lab"


def patch_error_handler(workflow: dict[str, Any]) -> None:
    """Aucun correctif spécifique pour le moment."""


PATCHES: dict[str, Callable[[dict[str, Any]], None]] = {
    "workflows/08-mcp/mcp-lab.json": patch_mcp,
}


def scrub_parameters(value: Any, key: str | None = None) -> Any:
    """Parcourt et neutralise les identifiants de ressources / données perso."""
    if isinstance(value, dict):
        if value.get("__rl") is True and key in CLEARABLE_RESOURCES:
            if isinstance(value.get("value"), str) and not value["value"].startswith("="):
                value["value"] = ""
            value.pop("cachedResultName", None)
            value.pop("cachedResultUrl", None)
        for child_key, child in list(value.items()):
            value[child_key] = scrub_parameters(child, child_key)
        return value

    if isinstance(value, list):
        return [scrub_parameters(item, key) for item in value]

    if isinstance(value, str):
        if key == "chatId":
            return "={{ $env.TELEGRAM_CHAT_ID }}"
        if key == "sendTo" and not value.startswith("="):
            return "youremail@example.com"
    return value


def rename_connections(connections: dict[str, Any], mapping: dict[str, str]) -> dict[str, Any]:
    renamed: dict[str, Any] = {}
    for source, outputs in connections.items():
        new_source = mapping.get(source, source)
        renamed[new_source] = {}
        for output_type, branches in outputs.items():
            renamed[new_source][output_type] = [
                [{**connection, "node": mapping.get(connection["node"], connection["node"])}
                 for connection in branch]
                for branch in branches
            ]
    return renamed


def transform(workflow: dict[str, Any], name: str, renames: dict[str, str]) -> dict[str, Any]:
    for node in workflow.get("nodes", []):
        node.pop("credentials", None)
        if node.get("name") in renames:
            node["name"] = renames[node["name"]]
        node["parameters"] = scrub_parameters(node.get("parameters", {}))

    workflow["name"] = name
    workflow["active"] = False
    workflow["connections"] = rename_connections(workflow.get("connections", {}), renames)
    workflow.setdefault("settings", {"executionOrder": "v1"})

    for metadata_key in ("id", "versionId", "meta", "pinData"):
        workflow.pop(metadata_key, None)

    return workflow


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path,
                        help="Dossier racine de l'export GitHub d'origine")
    args = parser.parse_args()

    source_root: Path = args.source
    if not source_root.is_dir():
        parser.error(f"Source introuvable : {source_root}")

    copied = 0
    for relative, (destination, name, renames) in WORKFLOWS.items():
        source_file = source_root / relative
        if not source_file.is_file():
            print(f"⚠ fichier absent : {source_file}")
            continue

        workflow = json.loads(source_file.read_text(encoding="utf-8"))
        workflow = transform(workflow, name, renames)
        if destination in PATCHES:
            PATCHES[destination](workflow)

        target = ROOT / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(workflow, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        copied += 1
        print(f"✓ {relative}  →  {destination}")

    # Ressource annexe du module RAG.
    sop_source = source_root / "07. rag-agent-pinecone-vector-db/airnove-sop.txt"
    if sop_source.is_file():
        sop_target = ROOT / "workflows/07-rag-pinecone/data/airnova-sop.txt"
        sop_target.parent.mkdir(parents=True, exist_ok=True)
        sop_target.write_text(sop_source.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"✓ SOP  →  {sop_target.relative_to(ROOT)}")

    print(f"\n{copied} workflow(s) migré(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
