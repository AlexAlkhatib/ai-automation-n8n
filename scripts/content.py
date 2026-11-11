#!/usr/bin/env python3
"""Contenu éditorial partagé par le guide Markdown, le PDF et le PowerPoint.

Une seule source de vérité pour les textes, les tableaux et les chiffres.
Les tableaux de modules sont dérivés de ``catalog.json`` afin de rester
synchronisés avec le dépôt.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
MODULES = CATALOG["modules"]

WORKFLOW_COUNT = sum(len(module["workflows"]) for module in MODULES)
NODE_COUNT = 0
for module in MODULES:
    for workflow in module["workflows"]:
        path = ROOT / "workflows" / module["slug"] / workflow["file"]
        NODE_COUNT += len(json.loads(path.read_text(encoding="utf-8"))["nodes"])

META = {
    "title": "AI Workflow Automation avec n8n",
    "subtitle": "Guide technique et pédagogique — agents IA, RAG, MCP et automatisations prêtes pour la production",
    "eyebrow": "GUIDE TECHNIQUE · VERSION 2.0",
    "version": CATALOG["version"],
    "date": "10 novembre 2026",
    "author": "Alex Alkhatib",
    "repo": "AI Workflow Automation (n8n)",
    "license": "MIT",
    "stats": [
        {"value": "10", "label": "modules", "note": "du débutant à l'expert"},
        {"value": str(WORKFLOW_COUNT), "label": "workflows", "note": "prêts à importer"},
        {"value": str(NODE_COUNT), "label": "nœuds", "note": "orchestration documentée"},
        {"value": "0", "label": "secret", "note": "dans le dépôt"},
    ],
}

MODULE_ROWS = [
    [module["id"], module["title"], module["level"], module["duration"],
     str(len(module["workflows"])), str(sum(
         len(json.loads((ROOT / "workflows" / module["slug"] / w["file"]).read_text(encoding="utf-8"))["nodes"])
         for w in module["workflows"]
     ))]
    for module in MODULES
]

WORKFLOW_ROWS = [
    [module["id"], workflow["file"], workflow["role"], workflow["trigger"], workflow["output"]]
    for module in MODULES
    for workflow in module["workflows"]
]

CREDENTIAL_ROWS = [
    [f"{module['id']} · {module['title']}", ", ".join(c["type"] for c in module["credentials"]) or "—"]
    for module in MODULES
]

ENV_ROWS = [
    [f"`{item['name']}`", module["id"], item["description"]]
    for module in MODULES
    for item in module.get("env", [])
]

CHAPTERS = [
    {
        "number": "01",
        "title": "Résumé exécutif",
        "kicker": "VUE D'ENSEMBLE",
        "blocks": [
            {"type": "lead", "text": "Ce dépôt rassemble **%d workflows n8n prêts à importer**, "
             "organisés en **%d modules progressifs** : agents conversationnels, génération "
             "d'images et de vidéos, orchestration de sous-workflows, RAG avec Pinecone, MCP et "
             "équipe marketing multi-agents." % (WORKFLOW_COUNT, len(MODULES))},
            {"type": "paragraph", "text": "La version 2 est une refonte complète : arborescence "
             "normalisée, exports nettoyés des identifiants d'instance et des données de test, "
             "documentation générée, contrôle qualité automatisé et script de reconnexion des "
             "sous-workflows. L'objectif est simple : qu'un lecteur puisse cloner le dépôt, "
             "importer un module et comprendre ce qu'il exécute en moins de trente minutes."},
            {"type": "stats", "items": META["stats"]},
            {"type": "bullets", "title": "Ce que la v2 apporte", "items": [
                "**Structure lisible** : un dossier par module, un README par module, un catalogue généré.",
                "**Sécurité** : aucun secret, aucune adresse personnelle, aucun identifiant de ressource privée.",
                "**Qualité** : validateur JSON et connexions, CI GitHub Actions, catalogue vérifié.",
                "**Documentation** : README, guide PDF, présentation PowerPoint et schémas d'architecture.",
                "**Exploitabilité** : Docker Compose, import en ligne de commande, workflow d'erreur global.",
            ]},
            {"type": "callout", "tone": "info", "title": "La promesse",
             "text": "Chaque module est autonome. Vous pouvez commencer par l'agent e-mail, puis "
             "ajouter le RAG et l'orchestration sans réécrire ce qui fonctionne."},
        ],
    },
    {
        "number": "02",
        "title": "Contexte et objectifs",
        "kicker": "POURQUOI CE DÉPÔT",
        "blocks": [
            {"type": "paragraph", "text": "L'automatisation par workflow répond à un problème "
             "concret : les tâches répétitives consomment du temps, les intégrations se "
             "multiplient et les équipes passent plus de temps à recâbler des scripts qu'à "
             "concevoir des processus. n8n apporte un plan de contrôle visuel, auto-hébergeable, "
             "capable d'appeler des API, des modèles de langage et des bases vectorielles."},
            {"type": "bullets", "title": "À qui s'adresse la bibliothèque", "items": [
                "**Développeurs et architectes** qui veulent un exemple complet d'orchestration IA.",
                "**Équipes data et ops** qui industrialisent des traitements documentaires.",
                "**Consultants et formateurs** qui cherchent un support de cours progressif.",
                "**Curieux techniques** à l'aise avec les API, les webhooks et les credentials.",
            ]},
            {"type": "table", "title": "Compétences visées",
             "headers": ["Compétence", "Modules"],
             "rows": [
                 ["Concevoir un agent avec outils et mémoire", "01, 02, 06"],
                 ["Piloter une API asynchrone et du polling", "03, 04, 09"],
                 ["Découper un processus en sous-workflows", "05, 09"],
                 ["Construire une base de connaissances vectorielle", "07"],
                 ["Exposer et consommer des outils MCP", "08"],
                 ["Superviser, sécuriser et diagnostiquer", "10"],
             ]},
            {"type": "callout", "tone": "warn", "title": "Prérequis",
             "text": "Une instance n8n (Docker ou npm), des comptes chez les fournisseurs "
             "utilisés et un minimum de familiarité avec les API HTTP. Aucun secret n'est "
             "fourni : chaque module liste les credentials à créer."},
        ],
    },
    {
        "number": "03",
        "title": "Architecture de la bibliothèque",
        "kicker": "COMMENT C'EST CONSTRUIT",
        "blocks": [
            {"type": "paragraph", "text": "n8n joue le rôle de plan de contrôle : il déclenche, "
             "séquence, réessaie et journalise. Le raisonnement est délégué aux modèles, les "
             "actions aux outils, et la connaissance aux bases vectorielles. Cette séparation "
             "permet de remplacer un fournisseur sans réécrire le processus métier."},
            {"type": "image", "path": "docs/assets/architecture.png",
             "caption": "Figure 1 — Déclencheurs, orchestration, outils et sorties."},
            {"type": "table", "title": "Les sept briques à connaître",
             "headers": ["Brique", "Rôle", "Exemple dans le dépôt"],
             "rows": [
                 ["Trigger", "Démarre le workflow", "Chat, Schedule 9 h, Drive, Slack"],
                 ["Agent", "Boucle raisonnement / action", "Email AI Agent, RAG Support Agent"],
                 ["Outil", "Action exposée au modèle", "Gmail, Google Docs, recherche Perplexity"],
                 ["Mémoire", "Contexte de conversation", "Simple Memory par canal ou session"],
                 ["Sous-workflow", "Workflow appelé comme fonction", "Modules 05 et 09"],
                 ["Credential", "Secret géré par n8n", "OAuth2 Google, clés API, header auth"],
                 ["Error Workflow", "Filet de sécurité global", "Module 10"],
             ]},
            {"type": "callout", "tone": "info", "title": "Règle d'architecture",
             "text": "Un workflow = une responsabilité. Dès qu'un enchaînement devient long ou "
             "réutilisable, extrayez-le en sous-workflow et exposez-le comme outil."},
        ],
    },
    {
        "number": "04",
        "title": "Parcours pédagogique",
        "kicker": "DIX MODULES",
        "blocks": [
            {"type": "paragraph", "text": "La progression suit une logique d'usage : d'abord un "
             "agent minimal, puis la planification et la recherche, ensuite les médias "
             "asynchrones, l'orchestration, la connaissance, et enfin les systèmes multi-agents "
             "et la supervision. Suivez l'ordre des numéros : chaque module réutilise les "
             "briques introduites par les précédents."},
            {"type": "image", "path": "docs/assets/modules-map.png",
             "caption": "Figure 2 — Les dix modules et leurs niveaux."},
            {"type": "table", "title": "Vue synthétique",
             "headers": ["#", "Module", "Niveau", "Durée", "Workflows", "Nœuds"],
             "rows": MODULE_ROWS, "small": True,
             "widths": [0.05, 0.31, 0.18, 0.15, 0.16, 0.15]},
        ],
    },
    {
        "number": "05",
        "title": "Fondations : un agent, des outils",
        "kicker": "MODULES 01, 02 ET 06",
        "blocks": [
            {"type": "paragraph", "text": "Un agent n8n n'est pas un chatbot magique : c'est un "
             "modèle de langage entouré d'un prompt système, d'une mémoire et d'outils. Le "
             "déclencheur fournit l'intention, l'agent décide de l'action, l'outil exécute, la "
             "mémoire conserve le contexte."},
            {"type": "bullets", "title": "Le patron commun", "items": [
                "**Trigger** : chat, événement Slack ou planification.",
                "**Modèle** : GPT-4.1 mini pour la vitesse, GPT-5 ou Claude pour la rédaction longue.",
                "**Mémoire** : fenêtre glissante, indexée par canal ou session.",
                "**Outils** : Gmail, Google Docs, recherche Perplexity, base vectorielle.",
                "**Sortie** : réponse, e-mail ou livrable.",
            ]},
            {"type": "table", "title": "Trois variantes utiles",
             "headers": ["Module", "Idée", "Point pédagogique"],
             "rows": [
                 ["01 · Email AI Agent", "L'agent rédige et envoie un e-mail",
                  "Un outil peut être une action métier complète"],
                 ["02 · Daily AI News Digest", "Perplexity cherche, GPT met en forme, Gmail envoie",
                  "Séparer recherche et présentation améliore la qualité"],
                 ["06 · Slack AI Teammate", "Un agent répond dans un canal avec une personnalité",
                  "La mémoire par canal évite les mélanges de contexte"],
             ]},
            {"type": "callout", "tone": "success", "title": "Bonne pratique",
             "text": "Décrivez explicitement le rôle, les contraintes et le format de sortie dans "
             "le prompt système. Les prompts fournis sont volontairement stricts : c'est ce qui "
             "rend la sortie exploitable par une machine."},
        ],
    },
    {
        "number": "06",
        "title": "Médias génératifs : le patron asynchrone",
        "kicker": "MODULES 03 ET 04",
        "blocks": [
            {"type": "paragraph", "text": "Les modèles d'image et de vidéo ne répondent pas en "
             "quelques centaines de millisecondes. Le workflow adopte donc un cycle en quatre "
             "temps : créer la prédiction, attendre, interroger le statut, livrer ou réessayer."},
            {"type": "image", "path": "docs/assets/async-pipeline.png",
             "caption": "Figure 3 — Créer, attendre, vérifier, livrer."},
            {"type": "numbered", "items": [
                "Un agent transforme la demande en prompt technique, sans métadonnées parasites.",
                "Le nœud HTTP POST envoie la prédiction à Wavespeed (Seedream pour l'image, Veo 3 pour la vidéo).",
                "Le nœud Wait suspend l'exécution quinze secondes, sans consommer de ressources.",
                "Le nœud HTTP GET lit le statut ; la branche positive livre le média, la branche négative relance l'attente.",
            ]},
            {"type": "callout", "tone": "danger", "title": "Limite connue",
             "text": "La boucle de retry n'a pas de compteur maximal. En production, ajoutez un "
             "compteur, une condition d'arrêt et une sortie d'erreur avant de laisser tourner "
             "le workflow sans surveillance."},
            {"type": "table", "title": "Choisir le bon modèle",
             "headers": ["Besoin", "Modèle du dépôt", "Remarque"],
             "rows": [
                 ["Visuel rapide", "Seedream v3 (1024×1322)", "Idéal pour des tests de prompts"],
                 ["Vidéo courte", "Veo 3 / Veo 3 Fast", "Rendu plus long, coût plus élevé"],
                 ["Image vers vidéo", "Seedance v1 lite", "Utilisé par le module 05"],
             ]},
        ],
    },
    {
        "number": "07",
        "title": "Orchestration et sous-workflows",
        "kicker": "MODULE 05",
        "blocks": [
            {"type": "paragraph", "text": "Le module 05 est le patron d'architecture à retenir : "
             "un workflow principal détecte un fichier, notifie, journalise, puis délègue la "
             "génération vidéo à un workflow séparé. Le sous-workflow reçoit des entrées typées "
             "et renvoie un résultat exploitable."},
            {"type": "code", "language": "text", "text":
                "Google Drive (nouveau fichier)\n"
                "   → Telegram (photo + lien)\n"
                "   → Google Sheets (journalisation)\n"
                "   → Execute Workflow (Image URL, Date)\n"
                "        → Agent prompt vidéo (Seedance)\n"
                "        → Wait 15 s → GET statut → Completed ?\n"
                "        → Telegram (vidéo)\n"
                "        → retour au workflow principal"},
            {"type": "bullets", "title": "Pourquoi découper", "items": [
                "**Réutilisation** : le même sous-workflow sert à plusieurs points d'entrée.",
                "**Lisibilité** : chaque workflow tient sur un écran.",
                "**Testabilité** : on exécute le sous-workflow seul avec des entrées contrôlées.",
                "**Évolution** : on change un fournisseur sans toucher à l'orchestrateur.",
            ]},
            {"type": "callout", "tone": "warn", "title": "Après import",
             "text": "n8n réattribue les identifiants des workflows. Les nœuds Execute Workflow "
             "sont donc livrés sans cible : lancez scripts/link_subworkflows.py avec une clé API "
             "pour les relier automatiquement par nom."},
            {"type": "table", "title": "Contrat d'interface du sous-workflow",
             "headers": ["Entrée", "Type", "Usage"],
             "rows": [
                 ["Image URL", "string", "Image source envoyée au modèle vidéo"],
                 ["Date", "string ISO", "Horodatage journalisé avec le résultat"],
             ]},
        ],
    },
    {
        "number": "08",
        "title": "RAG, MCP et connaissance",
        "kicker": "MODULES 07 ET 08",
        "blocks": [
            {"type": "paragraph", "text": "Un agent sans connaissance répond avec des généralités. "
             "Le module 07 construit une base vectorielle à partir de documents métier, puis "
             "expose cette base comme outil de retrieval. Le module 08 va plus loin : il "
             "standardise les outils via le Model Context Protocol."},
            {"type": "image", "path": "docs/assets/rag-pipeline.png",
             "caption": "Figure 4 — Ingestion documentaire et réponse ancrée."},
            {"type": "table", "title": "Les étapes du pipeline",
             "headers": ["Étape", "Décision", "Réglage du dépôt"],
             "rows": [
                 ["Découpage", "Taille des chunks", "500 caractères, overlap 50"],
                 ["Embeddings", "Modèle vectoriel", "OpenAI text-embedding-3"],
                 ["Indexation", "Base et index", "Pinecone, index airnova-sop"],
                 ["Retrieval", "Mode d'exposition", "retrieve-as-tool, top-k par défaut"],
                 ["Génération", "Modèle de réponse", "GPT-4.1 mini, prompt support"],
             ]},
            {"type": "bullets", "title": "MCP en pratique", "items": [
                "Le **MCP Server Trigger** publie un outil n8n derrière un endpoint standard.",
                "Le **MCP Client Tool** permet à un agent de consommer ce serveur, local ou distant.",
                "Le même catalogue d'outils peut servir à plusieurs agents et à d'autres clients MCP.",
                "L'URL dépend de votre hébergement : copiez-la depuis le nœud, ne la devinez pas.",
            ]},
            {"type": "callout", "tone": "info", "title": "Qualité documentaire",
             "text": "Un RAG ne vaut que par ses sources. Versionnez les documents, surveillez les "
             "documents obsolètes et testez régulièrement des questions dont vous connaissez la "
             "réponse attendue."},
        ],
    },
    {
        "number": "09",
        "title": "Système multi-agents marketing",
        "kicker": "MODULE 09",
        "blocks": [
            {"type": "paragraph", "text": "Le module 09 assemble un orchestrateur et quatre "
             "sous-agents spécialisés. L'orchestrateur comprend la demande, choisit l'outil "
             "adapté, transmet uniquement l'idée utile, puis restitue le livrable. C'est un "
             "exemple complet de division du travail entre modèles."},
            {"type": "table", "title": "Rôles de l'équipe",
             "headers": ["Agent", "Spécialité", "Sortie"],
             "rows": [
                 ["Marketing Team Master", "Comprend la demande et délègue", "Contenu final"],
                 ["Create_Image", "Prompt visuel et génération", "Image"],
                 ["Create_Video", "Prompt vidéo et génération", "Vidéo"],
                 ["Caption_Writer_Agent", "Déclinaisons LinkedIn / X / Instagram", "Captions"],
                 ["Blogpost_Copywriter", "Article long structuré", "Google Doc"],
             ]},
            {"type": "bullets", "title": "Règles de conception", "items": [
                "**Une entrée par outil** : ne transmettez que l'idée, pas tout le contexte.",
                "**Descriptions explicites** : le modèle choisit l'outil sur la description.",
                "**Modèles adaptés** : GPT-5 pour l'orchestration, Claude pour la rédaction longue.",
                "**Sortie contrôlée** : les sous-agents produisent un format stable, pas du bavardage.",
                "**Coût** : chaque appel d'outil consomme des tokens ; mesurez avant d'élargir.",
            ]},
            {"type": "callout", "tone": "warn", "title": "Point d'attention",
             "text": "L'orchestrateur n'a pas de sortie branchée par défaut : choisissez le canal "
             "de livraison (Slack, Gmail, Drive) et testez d'abord chaque sous-agent isolément."},
        ],
    },
    {
        "number": "10",
        "title": "Sécurité, coûts et production",
        "kicker": "CE QUI FAIT LA DIFFÉRENCE",
        "blocks": [
            {"type": "paragraph", "text": "Un workflow de démonstration devient un incident de "
             "production dès qu'il manipule des données réelles. Les contrôles ci-dessous sont "
             "appliqués dans le dépôt ou documentés pour l'exploitation."},
            {"type": "table", "title": "Contrôles de sécurité",
             "headers": ["Risque", "Contrôle", "Où"],
             "rows": [
                 ["Secret dans un export", "Credentials n8n, .env ignoré, validateur dédié", "Dépôt + CI"],
                 ["Données personnelles", "pinData supprimé, identifiants neutralisés", "Workflows"],
                 ["Webhook public", "Authentification, allowlist, rate limit", "Instance n8n"],
                 ["Injection de prompt", "Garde-fous, validation de sortie, outils restreints", "Agents"],
                 ["Fuite de contexte", "Minimisation des données envoyées aux modèles", "Prompts"],
                 ["Perte de chiffrement", "Sauvegarde de N8N_ENCRYPTION_KEY", "Infrastructure"],
                 ["Erreur silencieuse", "Error Workflow global + alerte Slack", "Module 10"],
                 ["Coûts incontrôlés", "Quotas fournisseurs et alertes budgétaires", "Comptes"],
             ]},
            {"type": "table", "title": "Ordres de grandeur des coûts",
             "headers": ["Fournisseur", "Usage", "Coût relatif", "Optimisation"],
             "rows": [
                 ["OpenAI", "Agents, prompts, embeddings", "€€", "Modèles mini, cache, batch"],
                 ["Anthropic", "Rédaction longue", "€€", "Sonnet plutôt qu'Opus"],
                 ["Perplexity", "Recherche web", "€€", "Une requête par jour"],
                 ["Wavespeed", "Image et vidéo", "€€€", "Valider les prompts avant génération"],
                 ["Pinecone", "Base vectorielle", "€", "Un index, nettoyage régulier"],
                 ["n8n", "Orchestration", "€", "Auto-hébergement Docker"],
             ]},
            {"type": "callout", "tone": "danger", "title": "À retenir",
             "text": "Consultez les grilles tarifaires à jour : les coûts évoluent vite. En "
             "revanche, la règle ne change pas — aucun secret dans un fichier de workflow, "
             "aucune clé dans un dépôt Git."},
        ],
    },
    {
        "number": "11",
        "title": "Mise en route",
        "kicker": "DE ZÉRO À PREMIER WORKFLOW",
        "blocks": [
            {"type": "paragraph", "text": "Deux chemins équivalents : Docker Compose pour une "
             "instance isolée, ou npm pour développer avec les outils locaux. Dans les deux cas, "
             "commencez par le module 01, puis ajoutez les briques une par une."},
            {"type": "code", "language": "bash", "text":
                "# 1. Configuration\n"
                "cp .env.example .env\n"
                "docker compose up -d          # http://localhost:5678\n"
                "\n"
                "# 2. Import (interface ou CLI)\n"
                "bash scripts/import_workflows.sh\n"
                "\n"
                "# 3. Credentials : OpenAI, Gmail, etc. puis sélection dans les nœuds\n"
                "# 4. Relier les sous-workflows (clé API n8n requise)\n"
                "N8N_URL=http://localhost:5678 N8N_API_KEY=... \\\n"
                "  python3 scripts/link_subworkflows.py\n"
                "\n"
                "# 5. Vérifier le dépôt\n"
                "python3 scripts/validate_workflows.py"},
            {"type": "numbered", "items": [
                "Créez les credentials dans n8n → Credentials, jamais dans le fichier JSON.",
                "Ouvrez le workflow importé, sélectionnez les credentials sur chaque nœud.",
                "Renseignez TELEGRAM_CHAT_ID dans .env pour le module 05.",
                "Testez en mode manuel, puis activez le workflow.",
            ]},
            {"type": "table", "title": "Commandes utiles",
             "headers": ["Commande", "Effet"],
             "rows": [
                 ["make start", "Démarre n8n en local"],
                 ["make import", "Importe les 16 workflows"],
                 ["make validate", "Valide JSON, connexions et secrets"],
                 ["make catalog", "Régénère catalogue et README de modules"],
                 ["make docs", "Régénère schémas, PDF et PowerPoint"],
                 ["make zip", "Produit l'archive distribuable"],
             ]},
        ],
    },
    {
        "number": "12",
        "title": "Qualité, limites et feuille de route",
        "kicker": "TRANSPARENCE",
        "blocks": [
            {"type": "table", "title": "Contrôles automatisés",
             "headers": ["Contrôle", "Outil", "Déclencheur"],
             "rows": [
                 ["JSON, nœuds, connexions, secrets", "scripts/validate_workflows.py", "Commit et CI"],
                 ["Catalogue et README à jour", "scripts/build_catalog.py --check", "CI"],
                 ["PDF et PowerPoint générés", "make docs", "CI"],
                 ["Import dans n8n", "CLI n8n", "Avant release"],
             ]},
            {"type": "table", "title": "Limites assumées",
             "headers": ["Limite", "Impact", "Contournement"],
             "rows": [
                 ["Polling sans plafond (03, 04, 09)", "Boucle possible en cas d'échec persistant",
                  "Compteur + condition d'arrêt"],
                 ["Sous-workflows non reliés à l'import", "Nœuds sans cible", "link_subworkflows.py"],
                 ["Credentials non fournis", "Workflows non exécutables tels quels", "Annexe B"],
                 ["Pas d'appels payants en CI", "Pas de test de bout en bout", "Tests manuels + pinned data"],
                 ["MCP dépend du domaine", "URL à adapter", "Copier l'URL du nœud"],
                 ["Instance unique par défaut", "Pas de montée en charge horizontale", "Queue mode + Postgres/Redis"],
             ]},
            {"type": "bullets", "title": "Feuille de route", "items": [
                "Plafonner les retries et ajouter une branche d'échec explicite.",
                "Ajouter des jeux de données épinglés pour tester sans appels externes.",
                "Industrialiser l'observabilité : logs structurés, métriques, alertes.",
                "Versionner les workflows dans Git via l'API n8n.",
                "Documenter un déploiement queue mode pour la charge.",
                "Proposer une version anglaise du guide.",
            ]},
            {"type": "callout", "tone": "success", "title": "Contribution",
             "text": "Un module = un dossier, un README, des credentials documentés et un export "
             "sans secret. Le validateur et la CI vérifient automatiquement ces règles."},
        ],
    },
    {
        "number": "A",
        "title": "Annexe A — Catalogue des workflows",
        "kicker": "RÉFÉRENCE",
        "blocks": [
            {"type": "table", "title": "Workflows livrés",
             "headers": ["#", "Fichier", "Rôle", "Déclencheur", "Sortie"],
             "rows": WORKFLOW_ROWS, "small": True,
             "widths": [0.05, 0.28, 0.14, 0.24, 0.29]},
        ],
    },
    {
        "number": "B",
        "title": "Annexe B — Credentials et variables",
        "kicker": "CONFIGURATION",
        "blocks": [
            {"type": "table", "title": "Credentials par module",
             "headers": ["Module", "Types de credentials n8n"],
             "rows": CREDENTIAL_ROWS},
            {"type": "table", "title": "Variables d'environnement",
             "headers": ["Variable", "Module", "Rôle"],
             "rows": ENV_ROWS},
            {"type": "callout", "tone": "info", "title": "Bon réflexe",
             "text": "Créez un credential par environnement (test, production) et nommez-le "
             "explicitement. Les exports ne contiennent que le nom du credential, jamais sa valeur."},
        ],
    },
    {
        "number": "C",
        "title": "Annexe C — Licence et crédits",
        "kicker": "INFORMATIONS LÉGALES",
        "blocks": [
            {"type": "paragraph", "text": "Le dépôt est distribué sous licence MIT. Vous pouvez "
             "l'utiliser, le modifier et le redistribuer, y compris commercialement, à condition "
             "de conserver la notice de copyright."},
            {"type": "paragraph", "text": "Les workflows s'appuient sur n8n (fair-code, licence "
             "Sustainable Use), sur les API d'OpenAI, Anthropic, Perplexity, Wavespeed et "
             "Pinecone, ainsi que sur Google Workspace, Slack et Telegram. Chaque fournisseur "
             "applique ses propres conditions d'utilisation et sa politique de confidentialité."},
            {"type": "paragraph", "text": "Auteur : Alex Alkhatib — ingénieur en intelligence "
             "artificielle, automatisation, agents IA et architectures intelligentes."},
            {"type": "callout", "tone": "info", "title": "Sources",
             "text": "Documentation n8n : docs.n8n.io · Documentation Pinecone : docs.pinecone.io "
             "· Spécification MCP : modelcontextprotocol.io"},
        ],
    },
]

SLIDES = [
    {"kind": "cover", "eyebrow": META["eyebrow"], "title": META["title"],
     "subtitle": META["subtitle"], "meta": f"{META['author']} · {META['date']}"},
    {"kind": "section", "number": "01", "title": "Le constat",
     "subtitle": "Automatiser ne suffit pas : il faut des workflows fiables, documentés et réutilisables."},
    {"kind": "bullets", "kicker": "POURQUOI N8N", "title": "Un plan de contrôle, pas une boîte noire",
     "bullets": [
         "Open-source et auto-hébergeable : vos données restent chez vous.",
         "Des centaines d'intégrations et un nœud HTTP pour le reste.",
         "Agents, outils, mémoire et bases vectorielles natifs.",
         "Exécution visuelle, journalisée et reproductible.",
         "Du prototype à la production sans changer d'outil.",
     ], "note": "n8n orchestre, les modèles raisonnent, les APIs exécutent."},
    {"kind": "section", "number": "02", "title": "La bibliothèque",
     "subtitle": "10 modules, 16 workflows, une progression du premier agent au système multi-agents."},
    {"kind": "image", "kicker": "ARCHITECTURE", "title": "Déclencheurs → orchestration → sorties",
     "image": "docs/assets/architecture.png", "caption": "Chaque intégration est un credential géré par n8n."},
    {"kind": "stats", "kicker": "EN CHIFFRES", "title": "Ce que contient le dépôt",
     "stats": META["stats"]},
    {"kind": "bullets", "kicker": "PATRONS", "title": "Trois patrons réutilisables",
     "bullets": [
         "Agent + outils : un modèle, un prompt, des actions métier (01, 02, 06).",
         "Asynchrone : créer, attendre, vérifier, livrer (03, 04, 09).",
         "Orchestration : un workflow maître délègue à des sous-workflows (05, 09).",
         "RAG et MCP ajoutent la couche connaissance et le partage d'outils (07, 08).",
     ], "note": "Un workflow = une responsabilité."},
    {"kind": "image", "kicker": "MÉDIAS GÉNÉRATIFS", "title": "Le patron asynchrone",
     "image": "docs/assets/async-pipeline.png",
     "caption": "Créer → attendre → vérifier → livrer, avec une branche de retry."},
    {"kind": "image", "kicker": "CONNAISSANCE", "title": "Pipeline RAG de bout en bout",
     "image": "docs/assets/rag-pipeline.png",
     "caption": "Ingestion continue et réponse ancrée dans la base vectorielle."},
    {"kind": "bullets", "kicker": "MULTI-AGENTS", "title": "Une équipe marketing qui se coordonne",
     "bullets": [
         "L'orchestrateur comprend la demande et choisit l'outil.",
         "Create_Image et Create_Video gèrent les médias.",
         "Caption_Writer_Agent décline par plateforme.",
         "Blogpost_Copywriter rédige et publie dans Google Docs.",
         "Chaque sous-agent reste utilisable seul.",
     ], "note": "La qualité vient des descriptions d'outils et des prompts système."},
    {"kind": "bullets", "kicker": "SÉCURITÉ", "title": "Zéro secret dans le dépôt",
     "bullets": [
         "Credentials n8n uniquement, .env ignoré par Git.",
         "pinData et identifiants de ressources supprimés des exports.",
         "Validateur dédié aux motifs de clés et de tokens.",
         "Error Workflow global et alertes Slack.",
         "Sauvegarde de N8N_ENCRYPTION_KEY et accès n8n restreint.",
     ], "note": "La sécurité est un contrôle continu, pas une case cochée."},
    {"kind": "table", "kicker": "QUALITÉ", "title": "Des garde-fous automatisés",
     "headers": ["Contrôle", "Outil", "Quand"],
     "rows": [
         ["JSON, nœuds, connexions, secrets", "validate_workflows.py", "Commit + CI"],
         ["Catalogue et README", "build_catalog.py --check", "CI"],
         ["PDF et PowerPoint", "make docs", "CI"],
         ["Import des 16 workflows", "CLI n8n", "Avant release"],
     ]},
    {"kind": "code", "kicker": "DÉMARRAGE", "title": "Trois commandes, puis vos credentials",
     "code": "cp .env.example .env\ndocker compose up -d      # http://localhost:5678\nbash scripts/import_workflows.sh\n\n# Relier les sous-workflows\npython3 scripts/link_subworkflows.py",
     "note": "Docker ou npm — la documentation détaille les deux chemins."},
    {"kind": "table", "kicker": "AVANT / APRÈS", "title": "Ce que change la version 2",
     "headers": ["Axe", "Avant", "Après"],
     "rows": [
         ["Structure", "Dossiers hétérogènes", "workflows/NN-slug + README"],
         ["Sécurité", "Données de test et comptes internes", "Exports nettoyés et vérifiés"],
         ["Documentation", "README seul", "README + guide PDF + deck"],
         ["Qualité", "Aucun contrôle", "Validateur, catalogue, CI"],
         ["Sous-workflows", "Liens cassés après import", "Script de reconnexion"],
     ]},
    {"kind": "bullets", "kicker": "HONNÊTETÉ", "title": "Limites assumées",
     "bullets": [
         "Polling sans plafond sur les modules médias.",
         "Credentials et comptes fournisseurs à fournir.",
         "Pas d'appels payants dans la CI.",
         "URL MCP dépendante de l'hébergement.",
         "Instance unique par défaut, pas de queue mode.",
     ], "note": "Chaque limite a un contournement documenté."},
    {"kind": "bullets", "kicker": "SUITE", "title": "Feuille de route",
     "bullets": [
         "Plafonner les retries et expliciter les échecs.",
         "Tests avec données épinglées, sans appel externe.",
         "Observabilité : logs structurés, métriques, alertes.",
         "Versionnement Git des workflows via l'API n8n.",
         "Déploiement queue mode pour la charge.",
     ]},
    {"kind": "end", "title": "Prêt à automatiser ?",
     "subtitle": "Importez le module 01, branchez vos credentials, exécutez.",
     "meta": f"{META['repo']} · v{META['version']} · Licence {META['license']}"},
]
