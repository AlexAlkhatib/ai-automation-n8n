# 05 · Orchestration & Subworkflows

> **Avancé** · 1 h · 2 workflow(s) · 14 nœuds

Le workflow principal surveille un dossier Google Drive, notifie Telegram, journalise l'image dans Google Sheets et appelle un sous-workflow qui génère une vidéo à partir de l'image. C'est le patron d'architecture à réutiliser pour tout pipeline métier.

## Ce que vous apprenez

- Découper un processus en workflows réutilisables
- Passer des données typées entre workflows
- Journaliser les exécutions dans Google Sheets
- Notifier et demander une action via Telegram

## Workflows

| Fichier | Rôle | Déclencheur | Sortie |
| --- | --- | --- | --- |
| [`image-to-video-orchestrator.json`](image-to-video-orchestrator.json) | main | Google Drive (nouveau fichier) | Sheet + Telegram + appel de sous-workflow |
| [`image-to-video-subworkflow.json`](image-to-video-subworkflow.json) | subworkflow | Execute Workflow Trigger | Vidéo Telegram |

### 05 — Image-to-Video Orchestrator

**Parcours principal**

```text
New Image in Drive → Notify Telegram (photo) → Log to Google Sheets → Run Video Subworkflow
```


### 05 — Image-to-Video Subworkflow (Seedance)

**Parcours principal**

```text
When Called by Orchestrator → Ask Video Idea (Telegram) → Video Prompt Agent → Create Video (Seedance) → Poll Wait (15s) → Check Video Status → Completed? → Send Video on Telegram
```

| Ressource | Nœuds |
| --- | --- |
| Outil de l'agent | Sheets Log (AI tool) |

## Credentials n8n requis

| Type | Libellé | Utilisé pour |
| --- | --- | --- |
| `googleDriveOAuth2Api` | Google Drive OAuth2 | Déclencheur fichier |
| `googleSheetsOAuth2Api` | Google Sheets OAuth2 | Journalisation |
| `telegramApi` | Telegram | Notification et question |
| `openAiApi` | OpenAI API | Prompt vidéo |
| `httpHeaderAuth` | HTTP Header Auth | Clé API Wavespeed |

Créez-les dans **n8n → Credentials → Create credential**, puis sélectionnez-les dans les nœuds concernés.

## Variables d'environnement

- `TELEGRAM_CHAT_ID` — Identifiant du chat Telegram cible, injecté via {{ $env.TELEGRAM_CHAT_ID }}.

## Importer ce module

```bash
n8n import:workflow --input workflows/05-subworkflows/image-to-video-orchestrator.json workflows/05-subworkflows/image-to-video-subworkflow.json
```

Ou, depuis l'interface : **Workflows → Import from File**, fichier par fichier.

> Les nœuds *Execute Workflow* / *toolWorkflow* ne conservent pas les identifiants d'instance : après import, lancez `python3 scripts/link_subworkflows.py` pour les relier automatiquement.

## Points d'attention

- Après import, reliez le nœud Execute Workflow au sous-workflow (script link_subworkflows.py).
- Le sous-workflow attend deux entrées : Image URL et Date.
- Le chat Telegram est lu depuis l'environnement : renseignez TELEGRAM_CHAT_ID dans .env.

---

Documentation complète : [docs/WORKFLOWS.md](../../docs/WORKFLOWS.md) · [Guide PDF](../../docs/AI-Workflow-Automation-n8n-Guide.pdf)
