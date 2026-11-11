# 04 · Text-to-Video Studio

> **Intermédiaire** · 45 min · 1 workflow(s) · 8 nœuds

Même architecture que le studio image, appliquée à la vidéo : un agent produit un prompt cinématographique, Wavespeed lance la génération Veo 3, le workflow attend la fin du rendu et envoie le lien vidéo.

## Ce que vous apprenez

- Gérer un rendu long avec polling et attente
- Nettoyer les prompts générés par LLM
- Comprendre le cycle create → poll → deliver
- Préparer un pipeline vidéo réutilisable

## Workflows

| Fichier | Rôle | Déclencheur | Sortie |
| --- | --- | --- | --- |
| [`text-to-video.json`](text-to-video.json) | main | Chat | E-mail avec URL de la vidéo |

### 04 — Text-to-Video Studio (Veo 3)

**Parcours principal**

```text
When chat message received → Video Prompt Agent → Wavespeed Post → Poll Wait (15s) → Wavespeed Get → Completed? → Email Video
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
n8n import:workflow --input workflows/04-text-to-video/text-to-video.json
```

Ou, depuis l'interface : **Workflows → Import from File**, fichier par fichier.

## Points d'attention

- Les rendus vidéo peuvent dépasser plusieurs minutes : le polling de 15 s est un point de départ.
- Le prompt système interdit les caractères spéciaux pour éviter les erreurs d'API.
- Surveillez le coût par génération : chaque essai est facturé par le fournisseur.

---

Documentation complète : [docs/WORKFLOWS.md](../../docs/WORKFLOWS.md) · [Guide PDF](../../docs/AI-Workflow-Automation-n8n-Guide.pdf)
