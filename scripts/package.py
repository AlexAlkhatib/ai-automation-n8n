#!/usr/bin/env python3
"""Crée l'archive distribuable du projet (sans secrets ni dépendances).

Usage : python3 scripts/package.py [--output dist/ai-workflow-automation-n8n.zip]
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXCLUDED_DIRS = {
    ".git", "node_modules", ".n8n", ".venv", "dist", "tmp_preview",
    "__pycache__", "_extract", ".idea", ".vscode", "n8n_data",
}
EXCLUDED_SUFFIXES = {".zip", ".log", ".sqlite", ".pyc", ".pid"}
EXCLUDED_FILES = {".env", ".DS_Store", "npm-install.log", "n8n.log", "n8n.pid", ".git"}


def included(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if any(part in EXCLUDED_DIRS for part in relative.parts[:-1]):
        return False
    if relative.name in EXCLUDED_FILES or relative.suffix in EXCLUDED_SUFFIXES:
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="dist/ai-workflow-automation-n8n-v2.zip")
    args = parser.parse_args()

    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(path for path in ROOT.rglob("*") if path.is_file() and included(path))
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT))

    size_mb = output.stat().st_size / (1024 * 1024)
    print(f"✓ {output.relative_to(ROOT)} — {len(files)} fichiers, {size_mb:.1f} Mo")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
