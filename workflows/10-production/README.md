# 10 · Ops & Error Handling

> **Avancé** · 30 min · 1 workflow(s) · 4 nœuds

Un workflow d'erreur global : déclenché par n'importe quel échec, il normalise le contexte (workflow, nœud, message, lien d'exécution) et alerte l'équipe dans Slack. À définir une fois dans les paramètres n8n pour tous les workflows.

## Ce que vous apprenez

- Activer un Error Workflow global
- Normaliser les informations d'échec
- Alerter avec un lien direct vers l'exécution
- Réduire le temps de diagnostic en production

## Workflows

| Fichier | Rôle | Déclencheur | Sortie |
| --- | --- | --- | --- |
| [`error-handler.json`](error-handler.json) | ops | Error Trigger | Alerte Slack |

### 10 — Production Error Handler

**Parcours principal**

```text
Error Trigger → Normalize Error → Alert Slack
```

## Credentials n8n requis

| Type | Libellé | Utilisé pour |
| --- | --- | --- |
| `slackApi` | Slack API | Canal d'alerte |

Créez-les dans **n8n → Credentials → Create credential**, puis sélectionnez-les dans les nœuds concernés.

## Importer ce module

```bash
n8n import:workflow --input workflows/10-production/error-handler.json
```

Ou, depuis l'interface : **Workflows → Import from File**, fichier par fichier.

## Points d'attention

- Définissez ce workflow dans Settings → Error Workflow de chaque workflow critique.
- Sélectionnez le canal Slack après import.
- Ajoutez un fallback e-mail si Slack est indisponible.

---

Documentation complète : [docs/WORKFLOWS.md](../../docs/WORKFLOWS.md) · [Guide PDF](../../docs/AI-Workflow-Automation-n8n-Guide.pdf)
