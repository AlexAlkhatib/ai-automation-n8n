# 03 · Text-to-Image Studio

> **Intermédiaire** · 45 min · 1 workflow(s) · 8 nœuds

Un agent transforme la demande en prompt optimisé, Wavespeed génère l'image, puis le workflow interroge l'API toutes les 15 secondes jusqu'à obtenir un statut « completed » et envoie le résultat par e-mail.

## Ce que vous apprenez

- Appeler une API asynchrone avec n8n HTTP Request
- Implémenter une boucle de polling avec un nœud Wait
- Gérer un statut via un nœud If et une branche de retry
- Industrialiser un prompt d'ingénierie réutilisable

## Workflows

| Fichier | Rôle | Déclencheur | Sortie |
| --- | --- | --- | --- |
| [`text-to-image.json`](text-to-image.json) | main | Chat | E-mail avec URL de l'image |

### 03 — Text-to-Image Studio (Wavespeed)

**Parcours principal**

```text
When chat message received → Image Prompt Agent → Wavespeed Post → Poll Wait (15s) → Wavespeed Get → Completed? → Email Image
```

## Credentials n8n requis

| Type | Libellé | Utilisé pour |
| --- | --- | --- |
| `openAiApi` | OpenAI API | Génération du prompt |
| `httpHeaderAuth` | HTTP Header Auth | Clé API Wavespeed |
| `gmailOAuth2` | Gmail OAuth2 | Livraison du résultat |

Créez-les dans **n8n → Credentials → Create credential**, puis sélectionnez-les dans les nœuds concernés.

## Importer ce module

```bash
n8n import:workflow --input workflows/03-text-to-image/text-to-image.json
```

Ou, depuis l'interface : **Workflows → Import from File**, fichier par fichier.

## Points d'attention

- La boucle de retry n'a pas de compteur maximal : ajoutez un compteur + sortie d'erreur avant la production.
- La taille demandée est 1024×1322 ; vérifiez qu'elle est supportée par le modèle choisi.
- Conservez la clé Wavespeed dans un credential httpHeaderAuth, jamais dans le nœud.

---

Documentation complète : [docs/WORKFLOWS.md](../../docs/WORKFLOWS.md) · [Guide PDF](../../docs/AI-Workflow-Automation-n8n-Guide.pdf)
