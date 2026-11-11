# 09 · Marketing Team

> **Expert** · 2 h · 5 workflow(s) · 40 nœuds

Un agent maître coordonne quatre sous-workflows spécialisés : image, vidéo, blogpost et déclinaisons sociales. Il choisit l'outil adapté à la demande, délègue, puis restitue le contenu — le cas d'usage multi-agent le plus complet du dépôt.

## Ce que vous apprenez

- Concevoir un orchestrateur multi-agents
- Transformer un workflow en outil d'agent
- Specialiser des sous-agents par format de contenu
- Structurer une sortie éditoriale multi-canal

## Workflows

| Fichier | Rôle | Déclencheur | Sortie |
| --- | --- | --- | --- |
| [`marketing-team-orchestrator.json`](marketing-team-orchestrator.json) | main | Chat | Image, vidéo, blogpost ou captions |
| [`text-to-image-subworkflow.json`](text-to-image-subworkflow.json) | subworkflow | Execute Workflow Trigger | Visuel généré |
| [`text-to-video-subworkflow.json`](text-to-video-subworkflow.json) | subworkflow | Execute Workflow Trigger | Vidéo générée |
| [`caption-copywriter-subworkflow.json`](caption-copywriter-subworkflow.json) | subworkflow | Execute Workflow Trigger | Captions LinkedIn / X / Instagram |
| [`blogpost-copywriter-subworkflow.json`](blogpost-copywriter-subworkflow.json) | subworkflow | Execute Workflow Trigger | Article Google Docs |

### 09 — Marketing Team Orchestrator

**Parcours principal**

```text
When chat message received → Marketing Team Master Agent
```

| Ressource | Nœuds |
| --- | --- |
| Mémoire | Simple Memory |
| Outil de l'agent | Think, Create_Image, Create_Video, Caption_Writer_Agent, Blogpost_Copywriter, Research With Perplexity |
| Modèle de langage | OpenAI Chat Model |


### 09 — Subworkflow: Text-to-Image

**Parcours principal**

```text
Image Prompt Agent → Wavespeed Get → Wavespeed Post → Wait 15 Seconds
```


### 09 — Subworkflow: Text-to-Video

**Parcours principal**

```text
Video Prompt Agent → Wavespeed Post → Wait 15 Secs → Wavespeed Get
```


### 09 — Subworkflow: Social Captions

**Parcours principal**

```text
When Executed by Another Workflow → Caption Copywriter Agent
```

| Ressource | Nœuds |
| --- | --- |
| Modèle de langage | Anthropic Chat Model |
| Mémoire | Simple Memory |


### 09 — Subworkflow: Blogpost Copywriter

**Parcours principal**

```text
When Executed by Another Workflow → Blogpost AI Agent → Create a document → Update a document
```

| Ressource | Nœuds |
| --- | --- |
| Modèle de langage | Anthropic Chat Model |
| Base vectorielle | Pinecone Vector Store |
| Embeddings | Embeddings OpenAI |

## Credentials n8n requis

| Type | Libellé | Utilisé pour |
| --- | --- | --- |
| `openAiApi` | OpenAI API | Orchestrateur et prompts image |
| `anthropicApi` | Anthropic API | Rédaction longue |
| `perplexityApi` | Perplexity API | Recherche |
| `pineconeApi` | Pinecone API | Style éditorial |
| `googleDocsOAuth2Api` | Google Docs OAuth2 | Publication |
| `httpHeaderAuth` | HTTP Header Auth | Clé API Wavespeed |

Créez-les dans **n8n → Credentials → Create credential**, puis sélectionnez-les dans les nœuds concernés.

## Importer ce module

```bash
n8n import:workflow --input workflows/09-marketing-team/marketing-team-orchestrator.json workflows/09-marketing-team/text-to-image-subworkflow.json workflows/09-marketing-team/text-to-video-subworkflow.json workflows/09-marketing-team/caption-copywriter-subworkflow.json workflows/09-marketing-team/blogpost-copywriter-subworkflow.json
```

Ou, depuis l'interface : **Workflows → Import from File**, fichier par fichier.

> Les nœuds *Execute Workflow* / *toolWorkflow* ne conservent pas les identifiants d'instance : après import, lancez `python3 scripts/link_subworkflows.py` pour les relier automatiquement.

## Points d'attention

- Après import, reliez les quatre outils workflow via scripts/link_subworkflows.py.
- L'orchestrateur n'a pas de sortie dédiée : branchez le canal de votre choix (Slack, Gmail, Drive).
- Les sous-workflows restent utilisables seuls : c'est tout l'intérêt du découpage.

---

Documentation complète : [docs/WORKFLOWS.md](../../docs/WORKFLOWS.md) · [Guide PDF](../../docs/AI-Workflow-Automation-n8n-Guide.pdf)
