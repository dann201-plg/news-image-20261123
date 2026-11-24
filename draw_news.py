"""Draw the news-image entry for Monday 23 November 2026 (v4).

Renders a one-page newspaper front page (1024x1024 PNG) that sums up the
world's news of 23 November 2026: a masthead with the date and a story-count
badge, one lead story, four featured stories, and a dense "Also today" band
of 45 more one-line stories in three columns -- 50 stories in total across
7 regions and 15 fields -- plus a DATE CHECK footer that names two big
stories deliberately left out because they were first reported before
Monday.

    python3 draw_news.py            # writes entry.png beside this file
    python3 draw_news.py out.png    # writes to the given path instead

Every story below was first reported on 23 November 2026 (checked against
that day's wire headlines: Reuters, WSJ, CNN, BBC, Al Jazeera, CoinDesk,
Dow Jones and the day's news roundups). Two stories were checked and
EXCLUDED on purpose: COP31 ended without a deal on Sunday 22 November
(UN News, Le Monde, WRI), and Miley Cyrus married on Saturday 21 November,
first reported that day by Entertainment Tonight and confirmed by her on
Sunday 22 November. Text is wrapped by measured width so nothing
overflows: the layout measures every wrapped line first, then sizes each
card from what it actually holds, and shrinks the story fonts a step if
the page would run past 1024 pixels or a band line would spill its column.
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


# Featured stories: (tag, tag colour, headline, summary)
FEATURED = [
    (
        "TECH",
        PURPLE,
        "Nvidia brings back Jensen Huang",
        "Shares jump a third on the news.",
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
        "INDONESIA",
        TEAL,
        "Dozens missing after factory fire",
        "Search under way after a factory blaze.",
    ),
]

# Also today: one line each, (tag, tag colour, text). Three columns.
ALSO = [
    ("MIDEAST", RED, "Iran threatens retaliation."),
    ("EUROPE", INK, "Belgium flights halted."),
    ("BRITAIN", INK, "12,000 flee concert scare."),
    ("ASIA", TEAL, "India pledges \u20ac1.4bn to Nepal."),
    ("USA", INK, "Democrats set 12 debates."),
    ("SPORT", GOLD, "Skubal signs record $450M deal."),
    ("EUROPE", INK, "Poland calls NATO meeting."),
    ("USA", INK, "States sue SpaceX over Grok."),
    ("COLOMBIA", PURPLE, "Starlink in prison probe."),
    ("GERMANY", INK, "Merz warns of Russia threat."),
    ("USA", INK, "Trump limits Congress data access."),
    ("SUDAN", RED, "Humanitarian crisis grows."),
    ("CHINA", TEAL, "2030 goals for care, childcare."),
    ("BRITAIN", INK, "New force to stop small boats."),
    ("CULTURE", GOLD, "Princess of Wales film out."),
    ("TECH", PURPLE, "$72bn Ether faces quantum risk."),
    ("USA", INK, "FBI probes police database hack."),
    ("EUROPE", INK, "EU unveils Russia sanctions."),
    ("FINLAND", INK, "Russian cargo ship hit."),
    ("USA", INK, "Trump backs cap on card rates."),
    ("MARKETS", GOLD, "Nasdaq futures jump 3%."),
    ("CANADA", TEAL, "No sign of Hegseth memo."),
    ("USA", INK, "The Rock crashes GameDay set."),
    ("USA", INK, "Storm to soak East Coast."),
    ("UK", INK, "Burnham defends EU reset deal."),
    ("UK", INK, "PIP review proposes fast-track."),
    ("SPORT", GOLD, "UK to host 2035 Women's Cup."),
    ("HEALTH", TEAL, "AI screening trial for 700,000."),
    ("NIGERIA", RED, "Villa hit by power, water cuts."),
    ("SPORT", GOLD, "Prespakis wins AFLW best."),
    ("CHINA", TEAL, "Beijing frets over stock markets."),
    ("UK", INK, "Asylum removals \u201cintimidating\u201d."),
    ("TECH", PURPLE, "Claude Code adds Code Mode."),
    ("BANGLADESH", TEAL, "Workers seek pay rise."),
    ("USA", INK, "ICE arrests at Seattle airport."),
    ("INDIA", TEAL, "Modi visit to reset Canada ties."),
    ("ALBANIA", INK, "Denies drones launched here."),
    ("GAZA", RED, "Oxfam: Gaza a \u201ctoxic wasteland\u201d."),
    ("TECH", PURPLE, "HPE lifts outlook on AI demand."),
    ("TECH", PURPLE, "CrowdStrike to buy Zscaler."),
    ("EUROPE", INK, "EU probes Coca-Cola bottler."),
    ("TECH", PURPLE, "Anthropic's $900bn alarms."),
    ("MARKETS", GOLD, "Micron jumps 19%."),
    ("COLOMBIA", PURPLE, "Drone attack injures three."),
    ("CULTURE", GOLD, "Disney bets on streaming."),
]

LEAD_TAG = "UKRAINE \u00b7 WAR"
LEAD_HEADLINE = "Naval drones sink Russian warship off Libya"
LEAD_SUMMARY = (
    "Kyiv says its sea drones struck two Russian ships; "
    "Moscow hit the Kyiv region, killing at least 11 in Dymer."
)
BADGE = "50 STORIES  \u00b7  7 REGIONS  \u00b7  15 FIELDS"
FOOT_1 = "50 stories from around the world  \u00b7  All events first reported 23 November 2026"
FOOT_2 = (
    "Date-checked: COP31 ended Sunday 22 Nov; "
    "Miley Cyrus married Saturday 21 Nov \u2014 not Monday news."
)
BAND_COLS = 3


def layout(draw, head_size, body_size, band_size):
    """Measure the whole page at the given story font sizes.

    Returns (lead_head, lead_sum, lead_h, feat_lines, cell_h, band_h,
    band_max_w, total).
    """
    margin = 36
    content_w = W - 2 * margin
    f_lead = font(SANS_BOLD, 30)
    f_sum = font(SANS, 19)
    f_head = font(SANS_BOLD, head_size)
    f_body = font(SANS, body_size)
    f_band = font(SANS, band_size)
    f_band_b = font(SANS_BOLD, band_size)

    lead_head = wrap(draw, LEAD_HEADLINE, f_lead, content_w - 42, 2)
    lead_sum = wrap(draw, LEAD_SUMMARY, f_sum, content_w - 42, 2)
    lead_h = 12 + 24 + len(lead_head) * 38 + 3 + len(lead_sum) * 25 + 12

    cell_w = (content_w - 20) // 2
    inner = cell_w - 32
    feat_lines = []
    max_cell = 0
    for _tag, _colour, headline, summary in FEATURED:
        hl = wrap(draw, headline, f_head, inner, 2)
        sl = wrap(draw, summary, f_body, inner, 2)
        feat_lines.append((hl, sl))
        cell = 12 + 23 + len(hl) * (head_size + 5) + 2 + len(sl) * (body_size + 6) + 9
        max_cell = max(max_cell, cell)

    band_col_w = (content_w - 2 * 16) // BAND_COLS
    band_max_w = 0
    for tag, _colour, text in ALSO:
        w = draw.textlength(tag + "  \u2014  ", font=f_band_b) + draw.textlength(text, font=f_band)
        band_max_w = max(band_max_w, w)
    band_rows = (len(ALSO) + BAND_COLS - 1) // BAND_COLS
    band_h = 24 + band_rows * (band_size + 5) + 7

    mast_h = (
        20 + 5 + 34
        + text_h(draw, "THE WORLD IN ONE DAY", font(SERIF_BOLD, 44))
        + 6 + text_h(draw, "MONDAY", font(SANS_BOLD, 24))
        + 6 + text_h(draw, BADGE, font(SANS_BOLD, 15))
        + 8 + 2 + 10
    )
    rows = (len(FEATURED) + 1) // 2
    foot_h = 2 + 10 + (18 + 5) + (16 + 4) + 7
    total = (
        mast_h + lead_h + 9 + rows * max_cell + (rows - 1) * 12
        + 9 + band_h + 9 + foot_h
    )
    return lead_head, lead_sum, lead_h, feat_lines, max_cell, band_h, band_max_w, total


def main(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    margin = 36
    content_w = W - 2 * margin
    band_col_w = (content_w - 2 * 16) // BAND_COLS

    # Pick the band size and the story fonts independently: the band is
    # limited by column width, the featured stories by page height.
    band_size = 12
    for candidate in (15, 14, 13, 12):
        _lh, _ls, _lead_h, _fl, _ch, _bh, band_max_w, _t = layout(
            d, 20, 17, candidate
        )
        if band_max_w <= band_col_w:
            band_size = candidate
            break
    head_size, body_size = 20, 17
    for h_cand, b_cand in [(24, 19), (23, 18), (22, 18), (21, 17), (20, 17)]:
        (lead_head, lead_sum, lead_h, feat_lines, cell_h, band_h,
         band_max_w, total) = layout(d, h_cand, b_cand, band_size)
        if total <= H:
            head_size, body_size = h_cand, b_cand
            break
    else:
        (lead_head, lead_sum, lead_h, feat_lines, cell_h, band_h,
         band_max_w, total) = layout(d, head_size, body_size, band_size)

    # Top red rule.
    d.rectangle([margin, 20, W - margin, 26], fill=RED)

    # Masthead.
    y = 34
    f_mast = font(SERIF_BOLD, 44)
    y += draw_centered(d, y, "THE WORLD IN ONE DAY", f_mast, INK)
    y += 6

    # Date line, letter-spaced.
    f_date = font(SANS_BOLD, 24)
    y += draw_centered(d, y, "MONDAY  \u00b7  23 NOVEMBER 2026", f_date, RED, spacing=2)
    y += 6

    # Badge line.
    f_badge = font(SANS_BOLD, 15)
    y += draw_centered(d, y, BADGE, f_badge, INK, spacing=1)
    y += 8
    d.line([margin, y, W - margin, y], fill=RULE, width=2)
    y += 10

    # Lead story card.
    card_top = y
    d.rectangle([margin, card_top, W - margin, card_top + lead_h], fill=CARD)
    d.rectangle([margin, card_top, margin + 8, card_top + lead_h], fill=RED)
    lx = margin + 26
    f_tag = font(SANS_BOLD, 18)
    f_lead = font(SANS_BOLD, 30)
    f_sum = font(SANS, 19)
    ly = card_top + 12
    d.text((lx, ly), LEAD_TAG, font=f_tag, fill=RED)
    ly += 24
    for line in lead_head:
        d.text((lx, ly), line, font=f_lead, fill=INK)
        ly += 38
    ly += 3
    for line in lead_sum:
        d.text((lx, ly), line, font=f_sum, fill=MUTED)
        ly += 25
    y = card_top + lead_h + 9

    # Featured grid: 2 columns x 2 rows.
    gap_x, gap_y = 20, 12
    cell_w = (content_w - gap_x) // 2
    f_stag = font(SANS_BOLD, 17)
    f_head = font(SANS_BOLD, head_size)
    f_body = font(SANS, body_size)
    for i, ((tag, colour, _h, _s), (hl, sl)) in enumerate(zip(FEATURED, feat_lines)):
        col, row = i % 2, i // 2
        x0 = margin + col * (cell_w + gap_x)
        y0 = y + row * (cell_h + gap_y)
        d.rectangle([x0, y0, x0 + cell_w, y0 + cell_h], fill=CARD)
        d.rectangle([x0, y0, x0 + cell_w, y0 + 5], fill=colour)
        tx = x0 + 16
        ty = y0 + 12
        d.text((tx, ty), tag, font=f_stag, fill=colour)
        ty += 23
        for line in hl:
            d.text((tx, ty), line, font=f_head, fill=INK)
            ty += head_size + 5
        ty += 2
        for line in sl:
            d.text((tx, ty), line, font=f_body, fill=MUTED)
            ty += body_size + 6
    rows = (len(FEATURED) + 1) // 2
    y = y + rows * cell_h + (rows - 1) * gap_y + 9

    # Also today band: three columns.
    f_band_h = font(SANS_BOLD, 18)
    d.text((margin, y), "ALSO TODAY", font=f_band_h, fill=RED)
    d.line([margin, y + 22, W - margin, y + 22], fill=RULE, width=1)
    y += 24
    gap_b = 16
    f_band = font(SANS, band_size)
    f_band_b = font(SANS_BOLD, band_size)
    band_rows = (len(ALSO) + BAND_COLS - 1) // BAND_COLS
    for i, (tag, colour, text) in enumerate(ALSO):
        col, row = i % BAND_COLS, i // BAND_COLS
        x0 = margin + col * (band_col_w + gap_b)
        y0 = y + row * (band_size + 5)
        d.text((x0, y0), tag + "  \u2014  ", font=f_band_b, fill=colour)
        tw = d.textlength(tag + "  \u2014  ", font=f_band_b)
        d.text((x0 + tw, y0), text, font=f_band, fill=INK)
    y = y + band_rows * (band_size + 5) + 7

    # Footer.
    fy = y + 9
    d.line([margin, fy, W - margin, fy], fill=RULE, width=2)
    f_foot = font(SANS, 18)
    f_foot2 = font(SANS, 16)
    draw_centered(d, fy + 10, FOOT_1, f_foot, MUTED)
    draw_centered(d, fy + 10 + 23, FOOT_2, f_foot2, RED)

    img.save(out_path, format="PNG", optimize=True)
    print(f"wrote {out_path} ({img.size[0]}x{img.size[1]}) "
          f"head={head_size} body={body_size} band={band_size} "
          f"band_max_w={band_max_w:.0f}/{band_col_w} total={total}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "entry.png")
