#!/usr/bin/env bash
# Importe tous les workflows du dépôt dans une instance n8n locale.
#
# Usage :
#   bash scripts/import_workflows.sh                 # via npx n8n (sqlite locale)
#   N8N_BIN="docker exec -i n8n-automation n8n" bash scripts/import_workflows.sh
#
# Les sous-workflows (05 et 09) doivent ensuite être reliés :
#   python3 scripts/link_subworkflows.py

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
N8N_BIN="${N8N_BIN:-npx n8n}"
export N8N_USER_FOLDER="${N8N_USER_FOLDER:-$ROOT/.n8n}"

if ! command -v npx >/dev/null 2>&1 && [[ "$N8N_BIN" == "npx n8n" ]]; then
  echo "✗ Node.js/npx est requis. Voir README.md (Prérequis)." >&2
  exit 1
fi

echo "Instance : $N8N_BIN"
echo "Données : $N8N_USER_FOLDER"
echo

count=0
while IFS= read -r file; do
  echo "→ $file"
  $N8N_BIN import:workflow --input="$file" >/dev/null
  count=$((count + 1))
done < <(find "$ROOT/workflows" -name '*.json' -type f | sort)

echo
echo "✓ $count workflow(s) importé(s)."
echo "  Démarrez n8n puis ouvrez http://localhost:5678"
echo "  Reliez les sous-workflows : python3 scripts/link_subworkflows.py"
