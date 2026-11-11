#!/usr/bin/env python3
"""Génère les schémas PNG utilisés par le README, le PDF et le PowerPoint.

Sortie : docs/assets/*.png
Dépendance : Pillow.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets"
CATALOG = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))

NAVY = (13, 18, 40)
INK = (27, 33, 58)
VIOLET = (108, 92, 231)
VIOLET_SOFT = (235, 232, 253)
CYAN = (0, 178, 204)
PINK = (233, 74, 131)
GREEN = (32, 168, 125)
AMBER = (232, 150, 24)
LIGHT = (246, 247, 252)
WHITE = (255, 255, 255)
MUTED = (104, 112, 145)
BORDER = (223, 226, 240)

FONT_DIR = ROOT / "scripts" / "fonts"
FONT_REGULAR = FONT_DIR / "DejaVuSans.ttf"
FONT_BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"
FONT_MONO = FONT_DIR / "DejaVuSansMono.ttf"

SCALE = 2


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_MONO if mono else (FONT_BOLD if bold else FONT_REGULAR)
    if path.is_file():
        return ImageFont.truetype(str(path), size * SCALE)
    return ImageFont.load_default(size * SCALE)


def canvas(width: int, height: int, background=LIGHT) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (width * SCALE, height * SCALE), background)
    return image, ImageDraw.Draw(image)


def save(image: Image.Image, width: int, height: int, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    image = image.resize((width, height), Image.LANCZOS)
    image.save(OUT / name, optimize=True)
    print(f"✓ docs/assets/{name}")


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=fnt) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def text_block(draw, x, y, text, fnt, color, max_width, line_height=1.35,
               align="left") -> int:
    lines = wrap(draw, text, fnt, max_width)
    for index, line in enumerate(lines):
        if align == "center":
            draw.text((x, y + index * fnt.size * line_height), line, font=fnt,
                      fill=color, anchor="ma")
        else:
            draw.text((x, y + index * fnt.size * line_height), line, font=fnt, fill=color)
    return len(lines)


def card(draw, box, radius=24, fill=WHITE, outline=BORDER, width=2) -> None:
    draw.rounded_rectangle(
        [box[0] * SCALE, box[1] * SCALE, box[2] * SCALE, box[3] * SCALE],
        radius=radius * SCALE,
        fill=fill,
        outline=outline,
        width=width * SCALE,
    )


def pill(draw, box, text, fill, color=WHITE, size=26, bold=True, radius=None) -> None:
    radius = radius if radius is not None else (box[3] - box[1]) / 2
    draw.rounded_rectangle(
        [box[0] * SCALE, box[1] * SCALE, box[2] * SCALE, box[3] * SCALE],
        radius=radius * SCALE,
        fill=fill,
    )
    draw.text(
        ((box[0] + box[2]) / 2 * SCALE, (box[1] + box[3]) / 2 * SCALE),
        text,
        font=font(size, bold),
        fill=color,
        anchor="mm",
    )


def arrow(draw, start, end, color=VIOLET, width=4, head=14) -> None:
    x1, y1 = start[0] * SCALE, start[1] * SCALE
    x2, y2 = end[0] * SCALE, end[1] * SCALE
    draw.line([x1, y1, x2, y2], fill=color, width=width * SCALE)
    dx, dy = x2 - x1, y2 - y1
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    h = head * SCALE
    base = (x2 - ux * h, y2 - uy * h)
    draw.polygon(
        [(x2, y2), (base[0] + px * h * 0.55, base[1] + py * h * 0.55),
         (base[0] - px * h * 0.55, base[1] - py * h * 0.55)],
        fill=color,
    )


def header(draw, title: str, subtitle: str, width: int) -> None:
    draw.rectangle([110 * SCALE, 96 * SCALE, 122 * SCALE, 196 * SCALE], fill=VIOLET)
    draw.text((150 * SCALE, 90 * SCALE), title, font=font(54, True), fill=NAVY)
    draw.text((152 * SCALE, 166 * SCALE), subtitle, font=font(28), fill=MUTED)
    draw.line([110 * SCALE, 232 * SCALE, (width - 110) * SCALE, 232 * SCALE],
              fill=BORDER, width=2 * SCALE)


def architecture() -> None:
    width, height = 3200, 1320
    image, draw = canvas(width, height)
    header(draw, "Architecture de la bibliothèque",
           "Un déclencheur, un agent orchestré par n8n, des outils et des sorties mesurables.", width)

    columns = [(480, "DÉCLENCHEURS"), (1600, "ORCHESTRATION N8N"), (2720, "SORTIES")]
    for center_x, label in columns:
        draw.text((center_x * SCALE, 285 * SCALE), label, font=font(24, True), fill=MUTED,
                  anchor="ma")

    triggers = [
        ("Chat n8n", "Conversation de test"),
        ("Schedule", "Cron / 9 h chaque matin"),
        ("Webhook", "Appel HTTP externe"),
        ("Événements", "Slack · Drive · Telegram"),
    ]
    for index, (title, subtitle) in enumerate(triggers):
        y = 340 + index * 170
        card(draw, (200, y, 760, y + 130), radius=20)
        draw.rectangle([200 * SCALE, y * SCALE, 208 * SCALE, (y + 130) * SCALE], fill=CYAN)
        draw.text((240 * SCALE, (y + 32) * SCALE), title, font=font(30, True), fill=INK)
        draw.text((240 * SCALE, (y + 78) * SCALE), subtitle, font=font(22), fill=MUTED)

    card(draw, (880, 330, 2320, 1050), radius=28, fill=WHITE, outline=VIOLET, width=3)
    draw.text((1600 * SCALE, 375 * SCALE), "Agent IA", font=font(36, True), fill=VIOLET,
              anchor="ma")
    draw.text((1600 * SCALE, 428 * SCALE), "Reasoning loop · prompt système · garde-fous",
              font=font(22), fill=MUTED, anchor="ma")

    pill(draw, (1310, 520, 1890, 630), "Agent IA", VIOLET, size=32)
    pill(draw, (950, 540, 1240, 610), "Mémoire", VIOLET_SOFT, color=INK, size=24)
    pill(draw, (1960, 540, 2250, 610), "LLM", VIOLET_SOFT, color=INK, size=24)
    arrow(draw, (1240, 575), (1305, 575), color=VIOLET, width=3, head=10)
    arrow(draw, (1895, 575), (1955, 575), color=VIOLET, width=3, head=10)

    tools = [
        (950, "Outils HTTP"),
        (1370, "Google · Slack"),
        (1790, "Sous-workflows"),
    ]
    for x, label in tools:
        pill(draw, (x, 740, x + 380, 810), label, WHITE, color=INK, size=24, radius=20)
        draw.rounded_rectangle([x * SCALE, 740 * SCALE, (x + 380) * SCALE, 810 * SCALE],
                               radius=20 * SCALE, outline=BORDER, width=2 * SCALE)
        draw.line([(x + 190) * SCALE, 640 * SCALE, (x + 190) * SCALE, 735 * SCALE],
                  fill=BORDER, width=3 * SCALE)

    draw.text((1600 * SCALE, 880 * SCALE),
              "Mémoire courte · retries · journalisation · Error Workflow",
              font=font(22), fill=MUTED, anchor="ma")
    pill(draw, (1180, 930, 2020, 990), "n8n = plan de contrôle, pas de boîte noire", NAVY, size=22)

    outputs = [
        ("Gmail", "Digest, résultat, alerte"),
        ("Slack", "Réponse contextuelle"),
        ("Telegram", "Photo, vidéo, question"),
        ("Drive / Docs", "Article, PDF, livrable"),
        ("Pinecone", "Connaissances indexées"),
    ]
    for index, (title, subtitle) in enumerate(outputs):
        y = 330 + index * 140
        card(draw, (2560, y, 3040, y + 108), radius=18)
        draw.rectangle([2560 * SCALE, y * SCALE, 2568 * SCALE, (y + 108) * SCALE], fill=GREEN)
        draw.text((2600 * SCALE, (y + 24) * SCALE), title, font=font(28, True), fill=INK)
        draw.text((2600 * SCALE, (y + 64) * SCALE), subtitle, font=font(20), fill=MUTED)

    arrow(draw, (770, 600), (870, 600), color=CYAN, width=5, head=16)
    arrow(draw, (2330, 600), (2540, 480), color=GREEN, width=5, head=16)
    arrow(draw, (2330, 620), (2540, 640), color=GREEN, width=5, head=16)

    card(draw, (110, 1100, 3090, 1245), radius=24, fill=NAVY, outline=NAVY)
    draw.text((150 * SCALE, 1138 * SCALE),
              "Fournisseurs & données : OpenAI · Anthropic · Perplexity · Wavespeed · Pinecone · Google Workspace",
              font=font(26), fill=(226, 229, 245))
    draw.text((150 * SCALE, 1185 * SCALE),
              "Chaque intégration est un credential n8n — aucun secret dans les fichiers du dépôt.",
              font=font(20), fill=(160, 168, 200))

    save(image, width, height, "architecture.png")


def modules_map() -> None:
    width, height = 3200, 1620
    image, draw = canvas(width, height)
    header(draw, "Parcours en 10 modules",
           "Du premier agent au système multi-agents de production.", width)

    accent = [CYAN, VIOLET, PINK, GREEN, AMBER]
    columns, card_w, card_h = 5, 560, 540
    gap = 40
    left = 140
    for index, module in enumerate(CATALOG["modules"]):
        row, col = divmod(index, columns)
        x = left + col * (card_w + gap)
        y = 300 + row * (card_h + 40)
        card(draw, (x, y, x + card_w, y + card_h), radius=24)
        draw.rounded_rectangle([x * SCALE, y * SCALE, (x + card_w) * SCALE, (y + 12) * SCALE],
                               radius=6 * SCALE, fill=accent[index % len(accent)])
        draw.text(((x + 36) * SCALE, (y + 42) * SCALE), module["id"], font=font(46, True),
                  fill=(205, 210, 230))
        lines = wrap(draw, module["title"], font(32, True), (card_w - 72) * SCALE)
        for line_index, line in enumerate(lines[:2]):
            draw.text(((x + 36) * SCALE, (y + 100 + line_index * 44) * SCALE), line,
                      font=font(32, True), fill=INK)
        pill(draw, (x + 36, y + 200, x + 36 + 220, y + 248), module["level"], VIOLET_SOFT,
             color=VIOLET, size=20)
        text_block(draw, (x + 36) * SCALE, (y + 275) * SCALE, module["tagline"], font(22),
                   MUTED, (card_w - 72) * SCALE, line_height=1.4)
        workflow_count = len(module["workflows"])
        draw.text(((x + 36) * SCALE, (y + card_h - 60) * SCALE),
                  f"{workflow_count} workflow(s) · {module['duration']}",
                  font=font(20, True), fill=VIOLET)

    draw.text((1600 * SCALE, 1510 * SCALE),
              "Chaque module est autonome : importez-le, configurez ses credentials, exécutez.",
              font=font(24), fill=MUTED, anchor="ma")
    save(image, width, height, "modules-map.png")


def rag_pipeline() -> None:
    width, height = 3200, 1240
    image, draw = canvas(width, height)
    header(draw, "Pipeline RAG",
           "Ingestion incrémentale des documents et réponse ancrée dans la base vectorielle.", width)

    def lane(y, label, subtitle, color):
        card(draw, (110, y, 3090, y + 380), radius=24, fill=WHITE)
        draw.rounded_rectangle([110 * SCALE, y * SCALE, (110 + 14) * SCALE, (y + 380) * SCALE],
                               radius=7 * SCALE, fill=color)
        draw.text((170 * SCALE, (y + 34) * SCALE), label, font=font(28, True), fill=color)
        draw.text((170 * SCALE, (y + 78) * SCALE), subtitle, font=font(20), fill=MUTED)

    lane(280, "1 · INGESTION", "À chaque nouveau document déposé dans Google Drive", CYAN)
    lane(720, "2 · REQUÊTE", "À chaque question d'un client dans le chat", VIOLET)

    def box(x, y, w, h, title, lines, fill=WHITE, outline=BORDER, accent=None):
        card(draw, (x, y, x + w, y + h), radius=20, fill=fill, outline=outline)
        if accent:
            draw.rectangle([x * SCALE, (y + h - 8) * SCALE, (x + w) * SCALE, (y + h) * SCALE],
                           fill=accent)
        draw.text(((x + 30) * SCALE, (y + 32) * SCALE), title, font=font(26, True), fill=INK)
        for index, line in enumerate(lines):
            draw.text(((x + 30) * SCALE, (y + 80 + index * 36) * SCALE), line,
                      font=font(20), fill=MUTED)

    ingestion = [
        (200, "Google Drive", ["Nouveau fichier", "PDF / TXT / DOCX"]),
        (780, "Chunking", ["500 caractères", "overlap 50"]),
        (1360, "Embeddings", ["OpenAI", "text-embedding-3"]),
        (1940, "Pinecone", ["index airnova-sop", "upsert vectoriel"]),
    ]
    for index, (x, title, lines) in enumerate(ingestion):
        box(x, 400, 500, 190, title, lines, accent=CYAN)
        if index < len(ingestion) - 1:
            arrow(draw, (x + 505, 495), (x + 575, 495), color=CYAN, width=4, head=12)

    query = [
        (200, "Chat client", ["question libre", "session mémoire"]),
        (780, "Agent support", ["system prompt", "garde-fous"]),
        (1360, "Retrieval", ["top-k vectoriel", "SOP AirNova"]),
        (1940, "Réponse", ["ancrée + sourcée", "chat n8n"]),
    ]
    for index, (x, title, lines) in enumerate(query):
        box(x, 840, 500, 190, title, lines, accent=VIOLET)
        if index < len(query) - 1:
            arrow(draw, (x + 505, 935), (x + 575, 935), color=VIOLET, width=4, head=12)

    pill(draw, (2600, 400, 2990, 470), "INSERT", CYAN, size=22)
    pill(draw, (2600, 520, 2990, 590), "RETRIEVE", VIOLET, size=22)
    draw.text((2600 * SCALE, 650 * SCALE), "pipeline continu", font=font(18), fill=MUTED)

    draw.text((1600 * SCALE, 1150 * SCALE),
              "Le même index sert à l'ingestion et à la réponse : la base reste la source de vérité.",
              font=font(22), fill=MUTED, anchor="ma")
    save(image, width, height, "rag-pipeline.png")


def async_pipeline() -> None:
    width, height = 3000, 900
    image, draw = canvas(width, height)
    header(draw, "Patron asynchrone (image / vidéo)",
           "Créer, attendre, vérifier, relancer : le socle des modules 03, 04 et 09.", width)

    steps = [
        (140, "Chat", "demande"),
        (600, "Prompt Agent", "GPT-4.1"),
        (1060, "POST API", "création"),
        (1520, "Wait 15 s", "attente"),
        (1980, "GET statut", "polling"),
    ]
    for index, (x, title, subtitle) in enumerate(steps):
        card(draw, (x, 300, x + 380, 430), radius=20)
        draw.text(((x + 30) * SCALE, 335 * SCALE), title, font=font(27, True), fill=INK)
        draw.text(((x + 30) * SCALE, 382 * SCALE), subtitle, font=font(20), fill=MUTED)
        if index < len(steps) - 1:
            arrow(draw, (x + 385, 365), (x + 450, 365), color=VIOLET, width=4, head=12)

    card(draw, (2400, 300, 2840, 430), radius=20, fill=VIOLET_SOFT, outline=VIOLET)
    draw.text((2430 * SCALE, 330 * SCALE), "Statut ?", font=font(27, True), fill=VIOLET)
    draw.text((2430 * SCALE, 378 * SCALE), "completed / processing", font=font(20), fill=INK)
    arrow(draw, (2365, 365), (2395, 365), color=VIOLET, width=4, head=12)

    arrow(draw, (2610, 440), (2610, 555), color=GREEN, width=4, head=12)
    pill(draw, (2380, 570, 2840, 640), "Livraison (Gmail / Telegram)", GREEN, size=22)
    draw.line([2610 * SCALE, 435 * SCALE, 2610 * SCALE, 470 * SCALE], fill=GREEN, width=4 * SCALE)

    arrow(draw, (2410, 300), (1706, 300), color=AMBER, width=3, head=10)
    draw.line([2410 * SCALE, 300 * SCALE, 2410 * SCALE, 230 * SCALE], fill=AMBER, width=3 * SCALE)
    draw.line([2410 * SCALE, 230 * SCALE, 1710 * SCALE, 230 * SCALE], fill=AMBER, width=3 * SCALE)
    draw.line([1710 * SCALE, 230 * SCALE, 1710 * SCALE, 295 * SCALE], fill=AMBER, width=3 * SCALE)
    draw.text((2030 * SCALE, 198 * SCALE), "status ≠ completed → retry", font=font(20, True),
              fill=AMBER, anchor="ma")

    draw.text((1500 * SCALE, 700 * SCALE),
              "Point de vigilance : plafonnez le nombre de tentatives et ajoutez une branche d'échec.",
              font=font(21), fill=MUTED, anchor="ma")
    save(image, width, height, "async-pipeline.png")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    architecture()
    modules_map()
    rag_pipeline()
    async_pipeline()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
