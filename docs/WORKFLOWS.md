# Catalogue des workflows

> Généré automatiquement depuis [`catalog.json`](../catalog.json) — ne pas éditer à la main. Lancez `python3 scripts/build_catalog.py`.

**10 modules · 16 workflows · 112 nœuds · version 2.0.0**

| # | Module | Niveau | Durée | Workflows | Nœuds | Intégrations |
| --- | --- | --- | --- | --- | --- | --- |
| [01](01-email-agent/README.md) | Email AI Agent | Débutant | 30 min | 1 | 6 | OpenAI GPT-4.1 mini, Gmail, n8n Chat Trigger |
| [02](02-research-agent/README.md) | Daily AI News Digest | Intermédiaire | 45 min | 1 | 6 | Perplexity sonar-pro, OpenAI GPT-4.1 mini, Gmail |
| [03](03-text-to-image/README.md) | Text-to-Image Studio | Intermédiaire | 45 min | 1 | 8 | OpenAI GPT-4.1, Wavespeed Seedream v3, Gmail |
| [04](04-text-to-video/README.md) | Text-to-Video Studio | Intermédiaire | 45 min | 1 | 8 | OpenAI GPT-4.1, Wavespeed Veo 3, Gmail |
| [05](05-subworkflows/README.md) | Orchestration & Subworkflows | Avancé | 1 h | 2 | 14 | Google Drive, Google Sheets, Telegram |
| [06](06-slack-agent/README.md) | Slack AI Teammate | Intermédiaire | 45 min | 1 | 6 | Slack, OpenAI GPT-5, Google Docs |
| [07](07-rag-pinecone/README.md) | RAG avec Pinecone | Avancé | 1 h 30 | 2 | 13 | Pinecone, OpenAI embeddings, OpenAI GPT-4.1 mini |
| [08](08-mcp/README.md) | MCP Lab | Avancé | 1 h | 1 | 7 | MCP Server Trigger, MCP Client Tool, OpenAI GPT-4.1 mini |
| [09](09-marketing-team/README.md) | Marketing Team | Expert | 2 h | 5 | 40 | OpenAI GPT-5, Anthropic Claude Sonnet 4, Perplexity |
| [10](10-production/README.md) | Ops & Error Handling | Avancé | 30 min | 1 | 4 | Error Trigger, Code, Slack |

---

## 01 · Email AI Agent

*Votre premier agent conversationnel qui envoie de vrais e-mails*

**Niveau** Débutant · **Durée** 30 min · **1 workflow(s)** · **6 nœuds**

Un agent n8n minimal mais complet : une discussion en langage naturel, un modèle OpenAI, une mémoire de conversation et un outil Gmail. L'agent choisit lui-même le sujet et le corps du message, puis envoie l'e-mail.

Fiche détaillée : [workflows/01-email-agent/README.md](../workflows/01-email-agent/README.md)

| Workflow | Fichier | Rôle | Déclencheur | Sortie |
| --- | --- | --- | --- | --- |
| 01 — Email AI Agent (Starter) | [`email-agent.json`](../workflows/01-email-agent/email-agent.json) | main | Chat | E-mail Gmail |

**Points d'attention**

- Le nœud Gmail est branché en ai_tool : c'est l'agent qui décide quand l'appeler.
- Remplacez youremail@example.com par votre adresse de test avant la première exécution.
- La mémoire est une fenêtre glissante : elle ne persiste pas après redémarrage de n8n.

## 02 · Daily AI News Digest

*Une veille IA quotidienne générée, formatée et envoyée automatiquement*

**Niveau** Intermédiaire · **Durée** 45 min · **1 workflow(s)** · **6 nœuds**

Chaque matin à 9 h, un agent de recherche interroge Perplexity sur les 24 dernières heures, un second agent reformate les résultats pour l'e-mail, puis Gmail envoie la synthèse. Le workflow illustre la séparation recherche / mise en forme.

Fiche détaillée : [workflows/02-research-agent/README.md](../workflows/02-research-agent/README.md)

| Workflow | Fichier | Rôle | Déclencheur | Sortie |
| --- | --- | --- | --- | --- |
| 02 — Daily AI News Digest (Perplexity + GPT) | [`daily-ai-news-digest.json`](../workflows/02-research-agent/daily-ai-news-digest.json) | main | Schedule (9 h) | E-mail Gmail |

**Points d'attention**

- Le Schedule Trigger utilise le fuseau horaire de l'instance (GENERIC_TIMEZONE).
- La mémoire du formateur est indexée sur l'identifiant de la réponse Perplexity.
- Adaptez le prompt système pour cibler un autre secteur que l'IA.

## 03 · Text-to-Image Studio

*Du texte au visuel, avec polling asynchrone et retry*

**Niveau** Intermédiaire · **Durée** 45 min · **1 workflow(s)** · **8 nœuds**

Un agent transforme la demande en prompt optimisé, Wavespeed génère l'image, puis le workflow interroge l'API toutes les 15 secondes jusqu'à obtenir un statut « completed » et envoie le résultat par e-mail.

Fiche détaillée : [workflows/03-text-to-image/README.md](../workflows/03-text-to-image/README.md)

| Workflow | Fichier | Rôle | Déclencheur | Sortie |
| --- | --- | --- | --- | --- |
| 03 — Text-to-Image Studio (Wavespeed) | [`text-to-image.json`](../workflows/03-text-to-image/text-to-image.json) | main | Chat | E-mail avec URL de l'image |

**Points d'attention**

- La boucle de retry n'a pas de compteur maximal : ajoutez un compteur + sortie d'erreur avant la production.
- La taille demandée est 1024×1322 ; vérifiez qu'elle est supportée par le modèle choisi.
- Conservez la clé Wavespeed dans un credential httpHeaderAuth, jamais dans le nœud.

## 04 · Text-to-Video Studio

*Génération vidéo Veo 3 pilotée par un agent prompt engineer*

**Niveau** Intermédiaire · **Durée** 45 min · **1 workflow(s)** · **8 nœuds**

Même architecture que le studio image, appliquée à la vidéo : un agent produit un prompt cinématographique, Wavespeed lance la génération Veo 3, le workflow attend la fin du rendu et envoie le lien vidéo.

Fiche détaillée : [workflows/04-text-to-video/README.md](../workflows/04-text-to-video/README.md)

| Workflow | Fichier | Rôle | Déclencheur | Sortie |
| --- | --- | --- | --- | --- |
| 04 — Text-to-Video Studio (Veo 3) | [`text-to-video.json`](../workflows/04-text-to-video/text-to-video.json) | main | Chat | E-mail avec URL de la vidéo |

**Points d'attention**

- Les rendus vidéo peuvent dépasser plusieurs minutes : le polling de 15 s est un point de départ.
- Le prompt système interdit les caractères spéciaux pour éviter les erreurs d'API.
- Surveillez le coût par génération : chaque essai est facturé par le fournisseur.

## 05 · Orchestration & Subworkflows

*Un workflow maître qui délègue à un workflow métier réutilisable*

**Niveau** Avancé · **Durée** 1 h · **2 workflow(s)** · **14 nœuds**

Le workflow principal surveille un dossier Google Drive, notifie Telegram, journalise l'image dans Google Sheets et appelle un sous-workflow qui génère une vidéo à partir de l'image. C'est le patron d'architecture à réutiliser pour tout pipeline métier.

Fiche détaillée : [workflows/05-subworkflows/README.md](../workflows/05-subworkflows/README.md)

| Workflow | Fichier | Rôle | Déclencheur | Sortie |
| --- | --- | --- | --- | --- |
| 05 — Image-to-Video Orchestrator | [`image-to-video-orchestrator.json`](../workflows/05-subworkflows/image-to-video-orchestrator.json) | main | Google Drive (nouveau fichier) | Sheet + Telegram + appel de sous-workflow |
| 05 — Image-to-Video Subworkflow (Seedance) | [`image-to-video-subworkflow.json`](../workflows/05-subworkflows/image-to-video-subworkflow.json) | subworkflow | Execute Workflow Trigger | Vidéo Telegram |

**Points d'attention**

- Après import, reliez le nœud Execute Workflow au sous-workflow (script link_subworkflows.py).
- Le sous-workflow attend deux entrées : Image URL et Date.
- Le chat Telegram est lu depuis l'environnement : renseignez TELEGRAM_CHAT_ID dans .env.

## 06 · Slack AI Teammate

*Un coéquipier IA qui répond dans Slack avec la voix de votre marque*

**Niveau** Intermédiaire · **Durée** 45 min · **1 workflow(s)** · **6 nœuds**

Un agent écoute les messages Slack, adopte une personnalité définie et consulte une base de connaissances Google Docs avant de répondre dans le canal d'origine. La mémoire est indexée par canal.

Fiche détaillée : [workflows/06-slack-agent/README.md](../workflows/06-slack-agent/README.md)

| Workflow | Fichier | Rôle | Déclencheur | Sortie |
| --- | --- | --- | --- | --- |
| 06 — Slack AI Teammate | [`slack-ai-teammate.json`](../workflows/06-slack-agent/slack-ai-teammate.json) | main | Slack (événement) | Réponse Slack |

**Points d'attention**

- Le filtre userIds est un placeholder : renseignez les identifiants Slack à écouter.
- Le paramètre sendAsUser utilise un nom d'affichage ; vérifiez les droits du bot.
- La mémoire par canal évite de mélanger les contextes entre équipes.

## 07 · RAG avec Pinecone

*Une base de connaissances vivante et un agent support qui la consulte*

**Niveau** Avancé · **Durée** 1 h 30 · **2 workflow(s)** · **13 nœuds**

Deux workflows complémentaires : l'ingestion transforme les documents Google Drive en vecteurs Pinecone, et l'agent support répond aux clients en s'appuyant sur ces SOP. Le dossier contient un jeu de données d'exemple (AirNova) pour tester immédiatement.

Fiche détaillée : [workflows/07-rag-pinecone/README.md](../workflows/07-rag-pinecone/README.md)

| Workflow | Fichier | Rôle | Déclencheur | Sortie |
| --- | --- | --- | --- | --- |
| 07 — Knowledge Ingestion (Drive → Pinecone) | [`knowledge-ingestion.json`](../workflows/07-rag-pinecone/knowledge-ingestion.json) | ingestion | Google Drive (nouveau fichier) | Vecteurs Pinecone |
| 07 — RAG Support Agent (Pinecone) | [`rag-support-agent.json`](../workflows/07-rag-pinecone/rag-support-agent.json) | agent | Chat | Réponse sourcée |

**Points d'attention**

- Créez l'index Pinecone avant l'ingestion, puis sélectionnez-le dans les deux workflows.
- Le chunking 500/50 est un bon compromis ; ajustez selon la longueur des documents.
- Le fichier data/airnova-sop.txt permet de tester sans brancher Google Drive.

## 08 · MCP Lab

*Exposer et consommer des outils via le Model Context Protocol*

**Niveau** Avancé · **Durée** 1 h · **1 workflow(s)** · **7 nœuds**

Le laboratoire MCP d'n8n : un serveur MCP expose une action Gmail, un agent la consomme via un client MCP. Le workflow montre comment standardiser vos intégrations et les partager entre agents.

Fiche détaillée : [workflows/08-mcp/README.md](../workflows/08-mcp/README.md)

| Workflow | Fichier | Rôle | Déclencheur | Sortie |
| --- | --- | --- | --- | --- |
| 08 — MCP Lab | [`mcp-lab.json`](../workflows/08-mcp/mcp-lab.json) | main | Chat | E-mail via outil MCP |

**Points d'attention**

- Remplacez YOUR-N8N-DOMAIN par l'URL publique de votre instance dans le client MCP.
- Copiez l'URL exacte affichée par le nœud MCP Server Trigger : le préfixe dépend de votre installation.
- MCP est utile quand plusieurs agents doivent partager le même catalogue d'outils.

## 09 · Marketing Team

*Une équipe marketing complète pilotée par un agent orchestrateur*

**Niveau** Expert · **Durée** 2 h · **5 workflow(s)** · **40 nœuds**

Un agent maître coordonne quatre sous-workflows spécialisés : image, vidéo, blogpost et déclinaisons sociales. Il choisit l'outil adapté à la demande, délègue, puis restitue le contenu — le cas d'usage multi-agent le plus complet du dépôt.

Fiche détaillée : [workflows/09-marketing-team/README.md](../workflows/09-marketing-team/README.md)

| Workflow | Fichier | Rôle | Déclencheur | Sortie |
| --- | --- | --- | --- | --- |
| 09 — Marketing Team Orchestrator | [`marketing-team-orchestrator.json`](../workflows/09-marketing-team/marketing-team-orchestrator.json) | main | Chat | Image, vidéo, blogpost ou captions |
| 09 — Subworkflow: Text-to-Image | [`text-to-image-subworkflow.json`](../workflows/09-marketing-team/text-to-image-subworkflow.json) | subworkflow | Execute Workflow Trigger | Visuel généré |
| 09 — Subworkflow: Text-to-Video | [`text-to-video-subworkflow.json`](../workflows/09-marketing-team/text-to-video-subworkflow.json) | subworkflow | Execute Workflow Trigger | Vidéo générée |
| 09 — Subworkflow: Social Captions | [`caption-copywriter-subworkflow.json`](../workflows/09-marketing-team/caption-copywriter-subworkflow.json) | subworkflow | Execute Workflow Trigger | Captions LinkedIn / X / Instagram |
| 09 — Subworkflow: Blogpost Copywriter | [`blogpost-copywriter-subworkflow.json`](../workflows/09-marketing-team/blogpost-copywriter-subworkflow.json) | subworkflow | Execute Workflow Trigger | Article Google Docs |

**Points d'attention**

- Après import, reliez les quatre outils workflow via scripts/link_subworkflows.py.
- L'orchestrateur n'a pas de sortie dédiée : branchez le canal de votre choix (Slack, Gmail, Drive).
- Les sous-workflows restent utilisables seuls : c'est tout l'intérêt du découpage.

## 10 · Ops & Error Handling

*Un filet de sécurité commun à tous vos workflows*

**Niveau** Avancé · **Durée** 30 min · **1 workflow(s)** · **4 nœuds**

Un workflow d'erreur global : déclenché par n'importe quel échec, il normalise le contexte (workflow, nœud, message, lien d'exécution) et alerte l'équipe dans Slack. À définir une fois dans les paramètres n8n pour tous les workflows.

Fiche détaillée : [workflows/10-production/README.md](../workflows/10-production/README.md)

| Workflow | Fichier | Rôle | Déclencheur | Sortie |
| --- | --- | --- | --- | --- |
| 10 — Production Error Handler | [`error-handler.json`](../workflows/10-production/error-handler.json) | ops | Error Trigger | Alerte Slack |

**Points d'attention**

- Définissez ce workflow dans Settings → Error Workflow de chaque workflow critique.
- Sélectionnez le canal Slack après import.
- Ajoutez un fallback e-mail si Slack est indisponible.

---

## Matrice des credentials

| Module | Credentials requis |
| --- | --- |
| 01 · Email AI Agent | openAiApi, gmailOAuth2 |
| 02 · Daily AI News Digest | perplexityApi, openAiApi, gmailOAuth2 |
| 03 · Text-to-Image Studio | openAiApi, httpHeaderAuth, gmailOAuth2 |
| 04 · Text-to-Video Studio | openAiApi, httpHeaderAuth, gmailOAuth2 |
| 05 · Orchestration & Subworkflows | googleDriveOAuth2Api, googleSheetsOAuth2Api, telegramApi, openAiApi, httpHeaderAuth |
| 06 · Slack AI Teammate | slackApi, openAiApi, googleDocsOAuth2Api |
| 07 · RAG avec Pinecone | pineconeApi, openAiApi, googleDriveOAuth2Api |
| 08 · MCP Lab | openAiApi, gmailOAuth2 |
| 09 · Marketing Team | openAiApi, anthropicApi, perplexityApi, pineconeApi, googleDocsOAuth2Api, httpHeaderAuth |
| 10 · Ops & Error Handling | slackApi |

## Variables d'environnement

| Variable | Modules | Rôle |
| --- | --- | --- |
| `TELEGRAM_CHAT_ID` | 05 | Identifiant du chat Telegram cible, injecté via {{ $env.TELEGRAM_CHAT_ID }}. |

## Importer toute la bibliothèque

```bash
# instance locale (SQLite dans .n8n/)
npx n8n import:workflow --separate --input=workflows

# relier les sous-workflows
N8N_URL=http://localhost:5678 N8N_API_KEY=... python3 scripts/link_subworkflows.py
```

Ou avec Docker : `docker compose up -d`, puis import via l'interface.
