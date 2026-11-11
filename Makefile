SHELL := /bin/bash
PYTHON ?= python3
N8N_PORT ?= 5678

.PHONY: help install start docker-up docker-down import link validate catalog docs diagrams test zip clean

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Installe n8n et les dépendances Python de documentation
	npm install
	$(PYTHON) -m pip install -r requirements-docs.txt

start: ## Démarre n8n en local (http://localhost:5678)
	npm start

docker-up: ## Démarre n8n via Docker Compose
	docker compose up -d

docker-down: ## Arrête la stack Docker
	docker compose down

import: ## Importe les workflows dans l'instance locale
	bash scripts/import_workflows.sh

link: ## Relie les sous-workflows (nécessite N8N_API_KEY et N8N_URL)
	$(PYTHON) scripts/link_subworkflows.py

validate: ## Valide tous les workflows JSON
	$(PYTHON) scripts/validate_workflows.py

catalog: ## Régénère le catalogue et les README de modules
	$(PYTHON) scripts/build_catalog.py

diagrams: ## Régénère les schémas PNG
	$(PYTHON) scripts/make_diagrams.py

docs: diagrams catalog ## Régénère README, catalogue, PDF et PowerPoint
	$(PYTHON) scripts/generate_docs.py

test: validate ## Suite de vérification utilisée par la CI
	$(PYTHON) scripts/build_catalog.py --check

zip: ## Crée l'archive distribuable
	$(PYTHON) scripts/package.py

clean: ## Supprime les artefacts locaux (pas les workflows)
	rm -rf .venv __pycache__ scripts/__pycache__ dist
