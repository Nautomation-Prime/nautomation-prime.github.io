#!/usr/bin/env python3
"""Generate the Open Graph preview cards in docs/assets/social/.

Every card is 1200x630, which is what overrides/main.html declares in its
og:image:width and og:image:height tags.

- default.jpg is the brand banner (docs/assets/main_logo.jpg) cropped to
  size, used for any page that does not set its own image.
- Each entry in PAGE_CARDS produces a page-specific card. Point a page at it
  with `image: assets/social/<filename>` in that page's front matter.

This is a local authoring tool, not part of the site build. It needs two
packages that are deliberately not in requirements.txt:

    pip install pillow font-roboto

then, from the repository root:

    python scripts/make_social_cards.py
"""
from __future__ import annotations

from pathlib import Path

import font_roboto
from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs" / "assets" / "social"
LOGO = REPO / "docs" / "assets" / "main_logo.jpg"
FONTS = Path(font_roboto.__file__).parent / "files"

PAGE_CARDS = [
    {
        "filename": "trusted-automation-execution.png",
        "eyebrow": "REFERENCE ARCHITECTURE",
        "title_lines": ["Trusted Automation", "Execution"],
        "subtitle": "Your automation has valid credentials. But should you trust the automation itself?",
    },
]

W, H = 1200, 630
NAVY = (11, 42, 72)  # sampled from the wordmark
STEEL = (44, 74, 99)
ORANGE = (242, 152, 46)  # sampled from the logo underline
ORANGE_TEXT = (184, 98, 12)  # darker orange, legible as small text on the light ground
BG_TOP, BG_BOTTOM = (240, 246, 250), (222, 234, 243)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / f"Roboto-{name}.ttf"), size)


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=fnt) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def default_card(logo: Image.Image) -> None:
    scaled = logo.resize((W, round(logo.height * W / logo.width)), Image.LANCZOS)
    top = (scaled.height - H) // 2
    card = scaled.crop((0, top, W, top + H))
    card.save(OUT / "default.jpg", quality=88, optimize=True, progressive=True)


def page_card(logo: Image.Image, filename: str, eyebrow: str, title_lines: list[str], subtitle: str) -> None:
    card = Image.new("RGB", (W, H))
    grad = ImageDraw.Draw(card)
    for y in range(H):
        t = y / (H - 1)
        grad.line([(0, y), (W, y)], fill=tuple(round(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOTTOM)))

    # Emblem badge: the "N" mark cropped from the banner, as a rounded tile with a soft shadow.
    badge_size, bx, by = 300, 80, 150
    emblem = logo.crop((160, 340, 940, 1120)).resize((badge_size, badge_size), Image.LANCZOS)
    mask = Image.new("L", (badge_size, badge_size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, badge_size - 1, badge_size - 1), radius=40, fill=255)
    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).rounded_rectangle(
        (bx + 6, by + 12, bx + badge_size + 6, by + badge_size + 12), radius=40, fill=90
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    card = Image.composite(Image.new("RGB", (W, H), (150, 175, 195)), card, shadow)
    card.paste(emblem, (bx, by), mask)

    draw = ImageDraw.Draw(card)
    x, col_w = 440, 690

    eb = font("Medium", 22)
    cx = x
    for ch in eyebrow:
        draw.text((cx, 120), ch, font=eb, fill=ORANGE_TEXT)
        cx += draw.textlength(ch, font=eb) + 2.2

    tf = font("Bold", 64)
    y = 158
    for line in title_lines:
        draw.text((x, y), line, font=tf, fill=NAVY)
        y += 74

    y += 16
    draw.rounded_rectangle((x, y, x + 120, y + 7), radius=3, fill=ORANGE)
    y += 34

    sf = font("Regular", 30)
    for line in wrap(draw, subtitle, sf, col_w):
        draw.text((x, y), line, font=sf, fill=STEEL)
        y += 42

    draw.line([(80, 540), (W - 80, 540)], fill=(196, 214, 228), width=2)
    ff = font("Medium", 24)
    draw.text((80, 560), "Nautomation Prime Academy", font=ff, fill=NAVY)
    url = "nautomationprime.io"
    uf = font("Regular", 24)
    draw.text((W - 80 - draw.textlength(url, font=uf), 560), url, font=uf, fill=STEEL)

    card.save(OUT / filename, optimize=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    logo = Image.open(LOGO).convert("RGB")
    default_card(logo)
    for spec in PAGE_CARDS:
        page_card(logo, **spec)
    for path in sorted(OUT.iterdir()):
        with Image.open(path) as im:
            print(f"{path.name}: {im.size[0]}x{im.size[1]}, {path.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
