# 06 · Slack AI Teammate

> **Intermédiaire** · 45 min · 1 workflow(s) · 6 nœuds

Un agent écoute les messages Slack, adopte une personnalité définie et consulte une base de connaissances Google Docs avant de répondre dans le canal d'origine. La mémoire est indexée par canal.

## Ce que vous apprenez

- Déclencher un agent depuis un événement Slack
- Concevoir une personnalité et des garde-fous
- Brancher Google Docs comme outil de connaissance
- Répondre dans le bon canal avec le bon ton

## Workflows

| Fichier | Rôle | Déclencheur | Sortie |
| --- | --- | --- | --- |
| [`slack-ai-teammate.json`](slack-ai-teammate.json) | main | Slack (événement) | Réponse Slack |

### 06 — Slack AI Teammate

**Parcours principal**

```text
Slack Trigger → GPT 5 Slack Agent → Send a message
```

| Ressource | Nœuds |
| --- | --- |
| Modèle de langage | OpenAI Chat Model |
| Mémoire | Simple Memory |
| Outil de l'agent | Project Knowledge Base |

## Credentials n8n requis

| Type | Libellé | Utilisé pour |
| --- | --- | --- |
| `slackApi` | Slack API | Trigger et réponse |
| `openAiApi` | OpenAI API | Agent conversationnel |
| `googleDocsOAuth2Api` | Google Docs OAuth2 | Base de connaissances |

Créez-les dans **n8n → Credentials → Create credential**, puis sélectionnez-les dans les nœuds concernés.

## Importer ce module

```bash
n8n import:workflow --input workflows/06-slack-agent/slack-ai-teammate.json
```

Ou, depuis l'interface : **Workflows → Import from File**, fichier par fichier.

## Points d'attention

- Le filtre userIds est un placeholder : renseignez les identifiants Slack à écouter.
- Le paramètre sendAsUser utilise un nom d'affichage ; vérifiez les droits du bot.
- La mémoire par canal évite de mélanger les contextes entre équipes.

---

Documentation complète : [docs/WORKFLOWS.md](../../docs/WORKFLOWS.md) · [Guide PDF](../../docs/AI-Workflow-Automation-n8n-Guide.pdf)
