# 02 · Daily AI News Digest

> **Intermédiaire** · 45 min · 1 workflow(s) · 6 nœuds

Chaque matin à 9 h, un agent de recherche interroge Perplexity sur les 24 dernières heures, un second agent reformate les résultats pour l'e-mail, puis Gmail envoie la synthèse. Le workflow illustre la séparation recherche / mise en forme.

## Ce que vous apprenez

- Planifier un workflow avec un Schedule Trigger
- Enchaîner deux agents aux responsabilités distinctes
- Exploiter une API de recherche avec fraîcheur des résultats
- Livrer un digest propre par e-mail

## Workflows

| Fichier | Rôle | Déclencheur | Sortie |
| --- | --- | --- | --- |
| [`daily-ai-news-digest.json`](daily-ai-news-digest.json) | main | Schedule (9 h) | E-mail Gmail |

### 02 — Daily AI News Digest (Perplexity + GPT)

**Parcours principal**

```text
Schedule Trigger → Research Agent → Formatter AI Agent → Send a message
```

| Ressource | Nœuds |
| --- | --- |
| Modèle de langage | OpenAI Chat Model |
| Mémoire | Simple Memory |

## Credentials n8n requis

| Type | Libellé | Utilisé pour |
| --- | --- | --- |
| `perplexityApi` | Perplexity API | Recherche web récente |
| `openAiApi` | OpenAI API | Reformatage du digest |
| `gmailOAuth2` | Gmail OAuth2 | Envoi du digest |

Créez-les dans **n8n → Credentials → Create credential**, puis sélectionnez-les dans les nœuds concernés.

## Importer ce module

```bash
n8n import:workflow --input workflows/02-research-agent/daily-ai-news-digest.json
```

Ou, depuis l'interface : **Workflows → Import from File**, fichier par fichier.

## Points d'attention

- Le Schedule Trigger utilise le fuseau horaire de l'instance (GENERIC_TIMEZONE).
- La mémoire du formateur est indexée sur l'identifiant de la réponse Perplexity.
- Adaptez le prompt système pour cibler un autre secteur que l'IA.

---

Documentation complète : [docs/WORKFLOWS.md](../../docs/WORKFLOWS.md) · [Guide PDF](../../docs/AI-Workflow-Automation-n8n-Guide.pdf)
