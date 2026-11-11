# 01 · Email AI Agent

> **Débutant** · 30 min · 1 workflow(s) · 6 nœuds

Un agent n8n minimal mais complet : une discussion en langage naturel, un modèle OpenAI, une mémoire de conversation et un outil Gmail. L'agent choisit lui-même le sujet et le corps du message, puis envoie l'e-mail.

## Ce que vous apprenez

- Comprendre le triptyque Trigger → Agent → Outil
- Brancher un modèle de langage et une mémoire courte
- Exposer une action externe (Gmail) comme outil de l'agent
- Tester un workflow dans le chat n8n

## Workflows

| Fichier | Rôle | Déclencheur | Sortie |
| --- | --- | --- | --- |
| [`email-agent.json`](email-agent.json) | main | Chat | E-mail Gmail |

### 01 — Email AI Agent (Starter)

**Parcours principal**

```text
When chat message received → AI Agent → No Operation, do nothing
```

| Ressource | Nœuds |
| --- | --- |
| Modèle de langage | OpenAI Chat Model |
| Outil de l'agent | Gmail |
| Mémoire | Simple Memory |

## Credentials n8n requis

| Type | Libellé | Utilisé pour |
| --- | --- | --- |
| `openAiApi` | OpenAI API | Modèle de langage |
| `gmailOAuth2` | Gmail OAuth2 | Outil d'envoi d'e-mail |

Créez-les dans **n8n → Credentials → Create credential**, puis sélectionnez-les dans les nœuds concernés.

## Importer ce module

```bash
n8n import:workflow --input workflows/01-email-agent/email-agent.json
```

Ou, depuis l'interface : **Workflows → Import from File**, fichier par fichier.

## Points d'attention

- Le nœud Gmail est branché en ai_tool : c'est l'agent qui décide quand l'appeler.
- Remplacez youremail@example.com par votre adresse de test avant la première exécution.
- La mémoire est une fenêtre glissante : elle ne persiste pas après redémarrage de n8n.

---

Documentation complète : [docs/WORKFLOWS.md](../../docs/WORKFLOWS.md) · [Guide PDF](../../docs/AI-Workflow-Automation-n8n-Guide.pdf)
