"""Draw the news-image entry for Monday 23 November 2026.

Renders a one-page newspaper front page (1024x1024 PNG) that sums up the
world's news of 23 November 2026: a masthead, the date, one lead story and
eight more stories across regions and fields. Run it, then look at the
picture it writes:

    python3 draw_news.py            # writes entry.png beside this file
    python3 draw_news.py out.png    # writes to the given path instead

Every story below was first reported on 23 November 2026 (checked against
that day's wire headlines). Text is wrapped by measured width so nothing
overflows: the layout measures every wrapped line first, then sizes each
card from what it actually holds, and shrinks the story fonts a step if
the page would run past 1024 pixels.
"""

import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (251, 248, 241)
INK = (22, 35, 61)
RED = (179, 39, 30)
MUTED = (90, 100, 114)
CARD = (255, 255, 255)
RULE = (22, 35, 61)
TEAL = (14, 124, 107)
GOLD = (154, 107, 0)
PURPLE = (106, 62, 150)

FONTS = "/usr/share/fonts/truetype/dejavu"
SERIF_BOLD = f"{FONTS}/DejaVuSerif-Bold.ttf"
SANS = f"{FONTS}/DejaVuSans.ttf"
SANS_BOLD = f"{FONTS}/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width, max_lines=None):
    """Split text into lines that fit max_width, measured with the font."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(".") + "\u2026"
    return lines


def text_h(draw, text, fnt):
    """Pixel height of one line of text in this font."""
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[3] - box[1]


def draw_centered(draw, y, text, fnt, fill, spacing=0):
    """Draw text centered on the page, with optional extra letter spacing."""
    if spacing:
        widths = [draw.textlength(ch, font=fnt) for ch in text]
        total = sum(widths) + spacing * (len(text) - 1)
        x = (W - total) / 2
        for ch, w in zip(text, widths):
            draw.text((x, y), ch, font=fnt, fill=fill)
            x += w + spacing
    else:
        width = draw.textlength(text, font=fnt)
        draw.text(((W - width) / 2, y), text, font=fnt, fill=fill)
    return text_h(draw, text, fnt)


# (tag, tag colour, headline, summary)
STORIES = [
    (
        "CLIMATE",
        TEAL,
        "COP31 climate talks collapse",
        "UN climate summit ends without a deal.",
    ),
    (
        "MARKETS",
        GOLD,
        "Bitcoin rebounds to $61,000",
        "Recovers after a plunge to a two-year low.",
    ),
    (
        "MEXICO",
        PURPLE,
        "Cartel boss \u201cEl Chapo Isidro\u201d caught",
        "Arrested in Sinaloa, Mexico says.",
    ),
    (
        "UNITED STATES",
        INK,
        "FBI probes hack of police database",
        "National police database breached.",
    ),
    (
        "INDONESIA",
        TEAL,
        "Dozens missing after factory fire",
        "Search under way after a factory blaze.",
    ),
    (
        "MIDDLE EAST",
        RED,
        "Iran warns of retaliation",
        "Tehran threatens a response to the blockade.",
    ),
    (
        "EUROPE",
        INK,
        "Belgium flights grounded by strike",
        "Austerity protest halts air traffic.",
    ),
    (
        "SPORT & CULTURE",
        GOLD,
        "Skubal signs record $450M Mets deal",
        "Biggest deal ever for a pitcher.",
    ),
]

LEAD_TAG = "UKRAINE \u00b7 WAR"
LEAD_HEADLINE = "Naval drones sink Russian warship off Libya"
LEAD_SUMMARY = (
    "Kyiv says its sea drones struck two Russian ships; "
    "Moscow hit the Kyiv region, killing at least 11 in Dymer."
)


def layout(draw, head_size, body_size):
    """Measure the whole page at the given story font sizes.

    Returns (lead_lines, story_lines, total_height) where story_lines is a
    list of (headline_lines, summary_lines) per story.
    """
    margin = 36
    content_w = W - 2 * margin
    f_lead = font(SANS_BOLD, 36)
    f_sum = font(SANS, 22)
    f_head = font(SANS_BOLD, head_size)
    f_body = font(SANS, body_size)

    lead_head = wrap(draw, LEAD_HEADLINE, f_lead, content_w - 42, 2)
    lead_sum = wrap(draw, LEAD_SUMMARY, f_sum, content_w - 42, 2)
    lead_h = 16 + 28 + len(lead_head) * 44 + 4 + len(lead_sum) * 28 + 16

    cell_w = (content_w - 20) // 2
    inner = cell_w - 32
    story_lines = []
    max_cell = 0
    for _tag, _colour, headline, summary in STORIES:
        hl = wrap(draw, headline, f_head, inner, 2)
        sl = wrap(draw, summary, f_body, inner, 2)
        story_lines.append((hl, sl))
        cell = 16 + 26 + len(hl) * (head_size + 5) + 2 + len(sl) * (body_size + 6) + 12
        max_cell = max(max_cell, cell)

    # Masthead block: rule + masthead + date + rule.
    mast_h = 26 + 6 + 46 + text_h(draw, "THE WORLD IN ONE DAY", font(SERIF_BOLD, 52))
    mast_h += 10 + text_h(draw, "MONDAY", font(SANS_BOLD, 30)) + 12 + 2 + 18
    total = mast_h + lead_h + 18 + 4 * max_cell + 3 * 14 + 16 + 2 + 12 + 19 + 8
    return lead_head, lead_sum, lead_h, story_lines, max_cell, total


def main(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    margin = 36
    content_w = W - 2 * margin

    # Shrink the story fonts a step at a time until the page fits.
    for head_size, body_size in [(26, 20), (25, 19), (24, 19), (23, 18)]:
        lead_head, lead_sum, lead_h, story_lines, cell_h, total = layout(
            d, head_size, body_size
        )
        if total <= H:
            break

    # Top red rule.
    d.rectangle([margin, 26, W - margin, 32], fill=RED)

    # Masthead.
    y = 46
    f_mast = font(SERIF_BOLD, 52)
    y += draw_centered(d, y, "THE WORLD IN ONE DAY", f_mast, INK)
    y += 10

    # Date line, letter-spaced.
    f_date = font(SANS_BOLD, 30)
    y += draw_centered(d, y, "MONDAY  \u00b7  23 NOVEMBER 2026", f_date, RED, spacing=2)
    y += 12
    d.line([margin, y, W - margin, y], fill=RULE, width=2)
    y += 18

    # Lead story card.
    card_top = y
    d.rectangle([margin, card_top, W - margin, card_top + lead_h], fill=CARD)
    d.rectangle([margin, card_top, margin + 8, card_top + lead_h], fill=RED)
    lx = margin + 26
    lw = content_w - 26 - 16
    f_tag = font(SANS_BOLD, 20)
    f_lead = font(SANS_BOLD, 36)
    f_sum = font(SANS, 22)
    ly = card_top + 16
    d.text((lx, ly), LEAD_TAG, font=f_tag, fill=RED)
    ly += 28
    for line in lead_head:
        d.text((lx, ly), line, font=f_lead, fill=INK)
        ly += 44
    ly += 4
    for line in lead_sum:
        d.text((lx, ly), line, font=f_sum, fill=MUTED)
        ly += 28
    y = card_top + lead_h + 18

    # Story grid: 2 columns x 4 rows.
    gap_x, gap_y = 20, 14
    cell_w = (content_w - gap_x) // 2
    f_stag = font(SANS_BOLD, 18)
    f_head = font(SANS_BOLD, head_size)
    f_body = font(SANS, body_size)
    for i, ((tag, colour, _h, _s), (hl, sl)) in enumerate(zip(STORIES, story_lines)):
        col, row = i % 2, i // 2
        x0 = margin + col * (cell_w + gap_x)
        y0 = y + row * (cell_h + gap_y)
        d.rectangle([x0, y0, x0 + cell_w, y0 + cell_h], fill=CARD)
        d.rectangle([x0, y0, x0 + cell_w, y0 + 5], fill=colour)
        tx = x0 + 16
        ty = y0 + 16
        d.text((tx, ty), tag, font=f_stag, fill=colour)
        ty += 26
        for line in hl:
            d.text((tx, ty), line, font=f_head, fill=INK)
            ty += head_size + 5
        ty += 2
        for line in sl:
            d.text((tx, ty), line, font=f_body, fill=MUTED)
            ty += body_size + 6

    # Footer.
    fy = y + 4 * cell_h + 3 * gap_y + 16
    d.line([margin, fy, W - margin, fy], fill=RULE, width=2)
    f_foot = font(SANS, 19)
    draw_centered(
        d,
        fy + 12,
        "9 stories from around the world  \u00b7  All events first reported 23 November 2026",
        f_foot,
        MUTED,
    )

    img.save(out_path, format="PNG", optimize=True)
    print(f"wrote {out_path} ({img.size[0]}x{img.size[1]}) "
          f"head={head_size} body={body_size} total={total}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
