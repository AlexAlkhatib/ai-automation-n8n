# 07 · RAG avec Pinecone

> **Avancé** · 1 h 30 · 2 workflow(s) · 13 nœuds

Deux workflows complémentaires : l'ingestion transforme les documents Google Drive en vecteurs Pinecone, et l'agent support répond aux clients en s'appuyant sur ces SOP. Le dossier contient un jeu de données d'exemple (AirNova) pour tester immédiatement.

## Ce que vous apprenez

- Découper un document en chunks pertinents
- Créer des embeddings et les indexer dans Pinecone
- Exposer l'index comme outil de retrieval à un agent
- Mettre à jour une base de connaissances sans redéploiement

## Workflows

| Fichier | Rôle | Déclencheur | Sortie |
| --- | --- | --- | --- |
| [`knowledge-ingestion.json`](knowledge-ingestion.json) | ingestion | Google Drive (nouveau fichier) | Vecteurs Pinecone |
| [`rag-support-agent.json`](rag-support-agent.json) | agent | Chat | Réponse sourcée |

### 07 — Knowledge Ingestion (Drive → Pinecone)

**Parcours principal**

```text
Google Drive Trigger → Loop Files → Download from Drive → Insert into Pinecone
```

| Ressource | Nœuds |
| --- | --- |
| Base vectorielle | Insert into Pinecone |
| Embeddings | Embeddings OpenAI |
| Chargement documentaire | Load Binary Document |
| Découpage de texte | Split Text (500/50) |


### 07 — RAG Support Agent (Pinecone)

**Parcours principal**

```text
When chat message received → AI Agent
```

| Ressource | Nœuds |
| --- | --- |
| Modèle de langage | OpenAI Chat Model |
| Mémoire | Simple Memory |
| Base vectorielle | Pinecone Vector Store |
| Embeddings | Embeddings OpenAI |

## Credentials n8n requis

| Type | Libellé | Utilisé pour |
| --- | --- | --- |
| `pineconeApi` | Pinecone API | Index vectoriel |
| `openAiApi` | OpenAI API | LLM et embeddings |
| `googleDriveOAuth2Api` | Google Drive OAuth2 | Source documentaire |

Créez-les dans **n8n → Credentials → Create credential**, puis sélectionnez-les dans les nœuds concernés.

## Importer ce module

```bash
n8n import:workflow --input workflows/07-rag-pinecone/knowledge-ingestion.json workflows/07-rag-pinecone/rag-support-agent.json
```

Ou, depuis l'interface : **Workflows → Import from File**, fichier par fichier.

## Points d'attention

- Créez l'index Pinecone avant l'ingestion, puis sélectionnez-le dans les deux workflows.
- Le chunking 500/50 est un bon compromis ; ajustez selon la longueur des documents.
- Le fichier data/airnova-sop.txt permet de tester sans brancher Google Drive.

---

Documentation complète : [docs/WORKFLOWS.md](../../docs/WORKFLOWS.md) · [Guide PDF](../../docs/AI-Workflow-Automation-n8n-Guide.pdf)
