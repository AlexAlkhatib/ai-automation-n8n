# Polices embarquées

Les fichiers `DejaVuSans*.ttf` sont distribués avec le projet pour que la génération
du PDF et des schémas soit **reproductible**, y compris sur une machine sans police
DejaVu installée.

- Source : projet [DejaVu Fonts](https://dejavu-fonts.github.io/).
- Licence : Bitstream Vera Fonts License / DejaVu Fonts License (libre, redistribution
  autorisée, y compris dans un document PDF qui embarque des sous-ensembles).
- Fichiers : `DejaVuSans.ttf`, `DejaVuSans-Bold.ttf`, `DejaVuSansMono.ttf`,
  `DejaVuSansMono-Bold.ttf`.

Ils sont utilisés uniquement par `scripts/make_diagrams.py` et
`scripts/generate_docs.py`. Le PowerPoint utilise Arial, disponible sur les
systèmes Windows, macOS et la plupart des installations Linux.
