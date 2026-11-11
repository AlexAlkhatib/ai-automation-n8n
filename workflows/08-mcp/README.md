# 08 · MCP Lab

> **Avancé** · 1 h · 1 workflow(s) · 7 nœuds

Le laboratoire MCP d'n8n : un serveur MCP expose une action Gmail, un agent la consomme via un client MCP. Le workflow montre comment standardiser vos intégrations et les partager entre agents.

## Ce que vous apprenez

- Comprendre serveur MCP, client MCP et outils exposés
- Publier un outil n8n derrière un endpoint MCP
- Connecter un agent à un serveur MCP distant
- Comparer MCP et appels HTTP classiques

## Workflows

| Fichier | Rôle | Déclencheur | Sortie |
| --- | --- | --- | --- |
| [`mcp-lab.json`](mcp-lab.json) | main | Chat | E-mail via outil MCP |

### 08 — MCP Lab

**Parcours principal**

```text
When chat message received → AI Agent
MCP Server Trigger
```

| Ressource | Nœuds |
| --- | --- |
| Modèle de langage | OpenAI Chat Model |
| Mémoire | Simple Memory |
| Outil de l'agent | MCP Client, Send a message in Gmail |

## Credentials n8n requis

| Type | Libellé | Utilisé pour |
| --- | --- | --- |
| `openAiApi` | OpenAI API | Agent |
| `gmailOAuth2` | Gmail OAuth2 | Outil exposé |

Créez-les dans **n8n → Credentials → Create credential**, puis sélectionnez-les dans les nœuds concernés.

## Importer ce module

```bash
n8n import:workflow --input workflows/08-mcp/mcp-lab.json
```

Ou, depuis l'interface : **Workflows → Import from File**, fichier par fichier.

## Points d'attention

- Remplacez YOUR-N8N-DOMAIN par l'URL publique de votre instance dans le client MCP.
- Copiez l'URL exacte affichée par le nœud MCP Server Trigger : le préfixe dépend de votre installation.
- MCP est utile quand plusieurs agents doivent partager le même catalogue d'outils.

---

Documentation complète : [docs/WORKFLOWS.md](../../docs/WORKFLOWS.md) · [Guide PDF](../../docs/AI-Workflow-Automation-n8n-Guide.pdf)
