#!/usr/bin/env python3
"""
Modern annotation generator v3 for NxtJob Resume Builder product guide.
Fixed: coordinates, element sizes, score panel placement, card action alignment.

All source screenshots are 2880x1308.
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCREENSHOTS_DIR = "/Users/rhutik/Documents/GitHub/docs/tasks/screenshots"
OUTPUT_DIR = os.path.join(SCREENSHOTS_DIR, "annotated")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------
INDIGO = (99, 102, 241)          # #6366F1
DARK_INDIGO = (30, 27, 75)      # #1E1B4B
WHITE = (255, 255, 255)
LEGEND_BG = (255, 255, 255, 230)
LEGEND_BORDER = (229, 231, 235)  # #E5E7EB
GRAY_700 = (55, 65, 81)         # #374151
LABEL_BG = (255, 255, 255, 240)

LINE_DOT_RADIUS = 14            # was 8
LINE_WIDTH = 5                   # was 3
DASH_LEN = 16                   # was 12
DASH_GAP = 10                   # was 8

# ---------------------------------------------------------------------------
# Font loading
# ---------------------------------------------------------------------------

def _load_font(size: int, bold: bool = False):
    candidates = []
    if bold:
        candidates = [
            ("/System/Library/Fonts/HelveticaNeue.ttc", 1),
            ("/System/Library/Fonts/Helvetica.ttc", 1),
            ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 0),
        ]
    else:
        candidates = [
            ("/System/Library/Fonts/HelveticaNeue.ttc", 0),
            ("/System/Library/Fonts/Helvetica.ttc", 0),
            ("/System/Library/Fonts/Supplemental/Arial.ttf", 0),
        ]
    for path, index in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size, index=index)
            except Exception:
                continue
    try:
        return ImageFont.truetype("Arial", size)
    except Exception:
        return ImageFont.load_default()


# Significantly larger fonts for 2880px images
FONT_BADGE = _load_font(42, bold=True)          # was 28
FONT_LEGEND_TITLE = _load_font(34, bold=True)   # was 24
FONT_LEGEND_ITEM = _load_font(30, bold=False)   # was 22
FONT_LABEL = _load_font(34, bold=True)          # was 24


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def _text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_pill_badge(d, overlay, x, y, number, font=None):
    """Draw a numbered pill badge centered at (x, y). Returns bounding rect."""
    if font is None:
        font = FONT_BADGE
    text = str(number)
    tw, th = _text_size(d, text, font)
    pad_x, pad_y = 28, 14
    w = max(tw + pad_x * 2, 76)
    h = th + pad_y * 2 + 6

    left = x - w // 2
    top = y - h // 2

    # Drop shadow
    d.rounded_rectangle(
        [left + 5, top + 5, left + w + 5, top + h + 5],
        radius=h // 2, fill=(30, 27, 75, 80))

    # White outer border
    d.rounded_rectangle(
        [left - 4, top - 4, left + w + 4, top + h + 4],
        radius=(h + 8) // 2, fill=(255, 255, 255, 255))

    # Main indigo pill
    d.rounded_rectangle(
        [left, top, left + w, top + h],
        radius=h // 2, fill=INDIGO + (255,))

    # Inner highlight (top third)
    d.rounded_rectangle(
        [left + 3, top + 3, left + w - 3, top + h // 3],
        radius=h // 2, fill=(129, 132, 255, 60))

    # Number text centered
    tx = left + (w - tw) // 2
    ty = top + (h - th) // 2 - 1
    d.text((tx, ty), text, fill=(255, 255, 255, 255), font=font)

    return (left, top, left + w, top + h)


def draw_connecting_line(d, badge_cx, badge_cy, target_x, target_y,
                         badge_rect=None, dashed=True):
    """Draw a line from badge edge to target with endpoint dot."""
    if badge_rect:
        bx1, by1, bx2, by2 = badge_rect
        bcx = (bx1 + bx2) / 2
        bcy = (by1 + by2) / 2
        bw = (bx2 - bx1) / 2
        bh = (by2 - by1) / 2
    else:
        bcx, bcy = badge_cx, badge_cy
        bw, bh = 38, 30

    dx = target_x - bcx
    dy = target_y - bcy
    dist = math.sqrt(dx * dx + dy * dy)
    if dist < 1:
        return

    # Start from badge edge
    start_x = bcx + dx / dist * (bw + 8)
    start_y = bcy + dy / dist * (bh + 8)

    color = INDIGO + (220,)

    if dashed:
        _draw_dashed_line(d, start_x, start_y, target_x, target_y,
                          color, LINE_WIDTH, DASH_LEN, DASH_GAP)
    else:
        d.line([(int(start_x), int(start_y)), (int(target_x), int(target_y))],
               fill=color, width=LINE_WIDTH)

    # Endpoint dot
    r = LINE_DOT_RADIUS
    d.ellipse(
        [int(target_x - r), int(target_y - r),
         int(target_x + r), int(target_y + r)],
        fill=INDIGO + (240,), outline=(255, 255, 255, 255), width=3)


def _draw_dashed_line(draw, x1, y1, x2, y2, fill, width,
                      dash_len=16, gap_len=10):
    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt(dx * dx + dy * dy)
    if dist < 1:
        return
    ux, uy = dx / dist, dy / dist
    pos = 0
    drawing = True
    while pos < dist:
        seg = dash_len if drawing else gap_len
        end_pos = min(pos + seg, dist)
        if drawing:
            sx = int(x1 + ux * pos)
            sy = int(y1 + uy * pos)
            ex = int(x1 + ux * end_pos)
            ey = int(y1 + uy * end_pos)
            draw.line([(sx, sy), (ex, ey)], fill=fill, width=width)
        pos = end_pos
        drawing = not drawing


def draw_legend(d, overlay, x, y, items, title="Key"):
    """Draw a legend box at (x, y) top-left."""
    pad = 26
    line_height = 44
    title_h = 50

    max_w = _text_size(d, title, FONT_LEGEND_TITLE)[0]
    for item in items:
        iw = _text_size(d, item, FONT_LEGEND_ITEM)[0]
        max_w = max(max_w, iw)

    box_w = max_w + pad * 2 + 16
    box_h = title_h + len(items) * line_height + pad * 2

    # Background
    d.rounded_rectangle(
        [x, y, x + box_w, y + box_h],
        radius=14, fill=LEGEND_BG,
        outline=LEGEND_BORDER + (255,), width=2)

    # Top accent stripe
    d.rounded_rectangle(
        [x, y, x + box_w, y + 6],
        radius=3, fill=INDIGO + (200,))

    # Title
    d.text((x + pad, y + pad), title,
           fill=DARK_INDIGO + (255,), font=FONT_LEGEND_TITLE)

    # Separator
    sep_y = y + pad + title_h - 6
    d.line([(x + pad, sep_y), (x + box_w - pad, sep_y)],
           fill=LEGEND_BORDER + (180,), width=1)

    # Items
    for i, item in enumerate(items):
        iy = y + pad + title_h + i * line_height
        d.text((x + pad, iy), item,
               fill=GRAY_700 + (255,), font=FONT_LEGEND_ITEM)

    return box_w, box_h


def draw_label_with_arrow(d, overlay, label_x, label_y,
                           target_x, target_y, text, font=None,
                           anchor="right"):
    """Draw a label box with arrow pointing to target."""
    if font is None:
        font = FONT_LABEL
    tw, th = _text_size(d, text, font)
    pad_x, pad_y = 24, 16
    box_w = tw + pad_x * 2
    box_h = th + pad_y * 2

    if anchor == "right":
        bx1 = label_x - box_w
        by1 = label_y - box_h // 2
    elif anchor == "left":
        bx1 = label_x
        by1 = label_y - box_h // 2
    else:  # center
        bx1 = label_x - box_w // 2
        by1 = label_y - box_h // 2

    bx2 = bx1 + box_w
    by2 = by1 + box_h

    # Shadow
    d.rounded_rectangle(
        [bx1 + 4, by1 + 4, bx2 + 4, by2 + 4],
        radius=12, fill=(30, 27, 75, 50))

    # Box
    d.rounded_rectangle(
        [bx1, by1, bx2, by2],
        radius=12, fill=LABEL_BG,
        outline=INDIGO + (255,), width=3)

    # Text
    d.text((bx1 + pad_x, by1 + pad_y - 1), text,
           fill=DARK_INDIGO + (255,), font=font)

    # Arrow from box edge to target
    if anchor == "right":
        arrow_start_x = bx2
        arrow_start_y = (by1 + by2) // 2
    elif anchor == "left":
        arrow_start_x = bx1
        arrow_start_y = (by1 + by2) // 2
    else:
        arrow_start_x = (bx1 + bx2) // 2
        arrow_start_y = by2

    d.line([(arrow_start_x, arrow_start_y), (target_x, target_y)],
           fill=INDIGO + (220,), width=LINE_WIDTH)

    _draw_arrowhead(d, arrow_start_x, arrow_start_y,
                    target_x, target_y, INDIGO + (220,), size=18)

    # Endpoint dot
    r = 8
    d.ellipse(
        [target_x - r, target_y - r, target_x + r, target_y + r],
        fill=INDIGO + (240,), outline=(255, 255, 255, 255), width=2)


def _draw_arrowhead(draw, x1, y1, x2, y2, fill, size=18):
    dx = x2 - x1
    dy = y2 - y1
    dist = math.sqrt(dx * dx + dy * dy)
    if dist < 1:
        return
    ux, uy = dx / dist, dy / dist
    px, py = -uy, ux
    left_x = x2 - ux * size + px * size * 0.4
    left_y = y2 - uy * size + py * size * 0.4
    right_x = x2 - ux * size - px * size * 0.4
    right_y = y2 - uy * size - py * size * 0.4
    draw.polygon(
        [(int(x2), int(y2)), (int(left_x), int(left_y)),
         (int(right_x), int(right_y))],
        fill=fill)


def create_overlay(base_img):
    return Image.new("RGBA", base_img.size, (0, 0, 0, 0))


def composite(base_img, overlay):
    return Image.alpha_composite(base_img.convert("RGBA"), overlay).convert("RGB")


# ===========================================================================
# 1. Dashboard Overview (01-dashboard-overview.png, 2880x1308)
#
# Layout:
#   - Sidebar icons: x=0-75
#   - Banner: y=35-440
#   - "Resumes (614)": x~160, y~495
#   - Search bar: x~1700-2200, y~495
#   - View toggles: x~2290, y~495
#   - "+ Create New": x~2550-2730, y~495
#   - Cards row: y~560-1250
#   - Primary badge on 1st card: x~320, y~990
#   - Score on 1st card: x~190, y~1085
# ===========================================================================

def annotate_dashboard():
    print("  [1/4] Dashboard overview...")
    img = Image.open(os.path.join(SCREENSHOTS_DIR, "01-dashboard-overview.png"))
    overlay = create_overlay(img)
    d = ImageDraw.Draw(overlay)

    # (number, badge_x, badge_y, target_x, target_y)
    annotations = [
        # 1: Left sidebar (mid-height)
        (1, 170, 650,  45, 650),
        # 2: "Resumes (614)" heading
        (2, 320, 430,  210, 498),
        # 3: Search bar
        (3, 1950, 430,  1900, 498),
        # 4: Grid / List view toggle
        (4, 2340, 430,  2300, 498),
        # 5: "+ Create New" button
        (5, 2680, 430,  2640, 498),
        # 6: Primary Resume badge on first card
        (6, 600, 990,  370, 998),
        # 7: Resume Score + ATS Score
        (7, 590, 1120,  260, 1090),
    ]

    for num, bx, by, tx, ty in annotations:
        rect = draw_pill_badge(d, overlay, bx, by, num)
        draw_connecting_line(d, bx, by, tx, ty, badge_rect=rect, dashed=True)

    legend_items = [
        "1 - Sidebar Navigation",
        "2 - Resume Count",
        "3 - Search Bar",
        "4 - View Toggle (Grid/List)",
        "5 - Create New Resume",
        "6 - Primary Resume Badge",
        "7 - Resume Score & ATS Score",
    ]
    draw_legend(d, overlay, 2250, 580, legend_items)

    result = composite(img, overlay)
    out = os.path.join(OUTPUT_DIR, "annotated-dashboard-overview.png")
    result.save(out, quality=95)
    print(f"    Saved: {out}")


# ===========================================================================
# 2. Card Action Menu (03-card-action-menu.png, 2880x1308)
#
# Layout: Dashboard with first card's 3-dot dropdown open.
# Dropdown menu items are on the first card (top-left):
#   - Menu appears at roughly x=300-580
#   - Mark Primary: y~170
#   - Preview: y~228
#   - Edit: y~286
#   - Download: y~344
#   - Rename: y~402
#   - Duplicate: y~460
# ===========================================================================

def annotate_card_actions():
    print("  [2/4] Card action menu...")
    img = Image.open(os.path.join(SCREENSHOTS_DIR, "03-card-action-menu.png"))
    overlay = create_overlay(img)
    d = ImageDraw.Draw(overlay)

    # Menu items: (label_text, menu_item_center_x, menu_item_center_y)
    # Dropdown is at x~350-560, items spaced ~58px apart starting y~170
    menu_items = [
        ("Mark Primary", 440, 170),
        ("Preview",      440, 228),
        ("Edit",         440, 286),
        ("Download",     440, 344),
        ("Rename",       440, 402),
        ("Duplicate",    440, 460),
    ]

    # Place labels to the right of the menu with arrows pointing left
    label_base_x = 900

    for label, item_cx, item_cy in menu_items:
        draw_label_with_arrow(
            d, overlay,
            label_x=label_base_x, label_y=item_cy,
            target_x=item_cx + 100, target_y=item_cy,
            text=label, font=FONT_LABEL, anchor="left")

    # Legend in bottom-right
    legend_items = [
        "Right-click or tap the",
        "3-dot menu on any card",
        "to access these actions",
    ]
    draw_legend(d, overlay, 2250, 1000, legend_items, title="Context Menu")

    result = composite(img, overlay)
    out = os.path.join(OUTPUT_DIR, "annotated-card-actions.png")
    result.save(out, quality=95)
    print(f"    Saved: {out}")


# ===========================================================================
# 3. Resume Builder (05-resume-builder-overview.png, 2880x1308)
#
# Layout:
#   - Top toolbar: y=0-65
#     - "My Resumes" link: x~70
#     - Resume name + Primary: x~180-360
#     - Templates/Sections/Style/Download: x~700-1100
#     - Score summary: x~2150-2500
#   - Left editor: x=75-1650, y=65+
#   - Right score panel: x=1700-2880, y=65+
# ===========================================================================

def annotate_builder():
    print("  [3/4] Builder overview...")
    img = Image.open(os.path.join(SCREENSHOTS_DIR, "05-resume-builder-overview.png"))
    overlay = create_overlay(img)
    d = ImageDraw.Draw(overlay)

    # Spread badges out clearly with staggered positions
    annotations = [
        # 1: Resume name + Primary badge (top-left toolbar area)
        (1, 250, 140,  260, 52),
        # 2: Toolbar buttons - Templates, Sections, Style, Download
        (2, 950, 140,  920, 52),
        # 3: Content editor area (center-left of resume)
        (3, 160, 550,  450, 400),
        # 4: Score panel (right side)
        (4, 2600, 160,  2400, 120),
    ]

    for num, bx, by, tx, ty in annotations:
        rect = draw_pill_badge(d, overlay, bx, by, num)
        draw_connecting_line(d, bx, by, tx, ty, badge_rect=rect, dashed=True)

    legend_items = [
        "1 - Resume Name & Primary Badge",
        "2 - Templates, Sections, Style, Download",
        "3 - Live Resume Editor",
        "4 - Score & Optimization Panel",
    ]
    draw_legend(d, overlay, 2300, 800, legend_items)

    result = composite(img, overlay)
    out = os.path.join(OUTPUT_DIR, "annotated-builder.png")
    result.save(out, quality=95)
    print(f"    Saved: {out}")


# ===========================================================================
# 4. Score Panel (06-score-panel.png, 2880x1308)
#
# Layout: Same as builder but focus on the right score panel.
# Score panel: x=2050-2880
#   - Tab bar ("Resume Score : 63%" | "ATS Score : 71%"): y~50-85
#   - Score circle (63%): centered ~x=2430, y=230
#   - "Average Resume Text" label: y~370
#   - "Let's Optimize" heading: y~460
#   - Category list: y=490-1100+
#
# FIX: Badges must be NEAR the score panel (right side), NOT on the left.
# ===========================================================================

def annotate_score_panel():
    print("  [4/4] Score panel...")
    img = Image.open(os.path.join(SCREENSHOTS_DIR, "06-score-panel.png"))
    overlay = create_overlay(img)
    d = ImageDraw.Draw(overlay)

    # Badges positioned just LEFT of the score panel, pointing INTO it
    annotations = [
        # 1: Score tab bar (Resume Score / ATS Score tabs)
        (1, 1920, 100,  2250, 72),
        # 2: Score circle + status summary
        (2, 1920, 290,  2350, 250),
        # 3: "Let's Optimize" category list
        (3, 1920, 530,  2200, 490),
    ]

    for num, bx, by, tx, ty in annotations:
        rect = draw_pill_badge(d, overlay, bx, by, num)
        draw_connecting_line(d, bx, by, tx, ty, badge_rect=rect, dashed=True)

    legend_items = [
        "1 - Score Tabs (Resume / ATS)",
        "2 - Score Circle & Status",
        "3 - Optimization Categories",
    ]
    # Legend in the lower-right area, near the score panel
    draw_legend(d, overlay, 2150, 1050, legend_items)

    result = composite(img, overlay)
    out = os.path.join(OUTPUT_DIR, "annotated-score-panel.png")
    result.save(out, quality=95)
    print(f"    Saved: {out}")


# ===========================================================================
# Main
# ===========================================================================

def main():
    print("NxtJob Resume Builder - Annotation Generator v3")
    print("=" * 50)
    print()

    annotate_dashboard()
    annotate_card_actions()
    annotate_builder()
    annotate_score_panel()

    print()
    print("All annotated images generated!")
    print(f"Output: {OUTPUT_DIR}")
    for f in sorted(os.listdir(OUTPUT_DIR)):
        fp = os.path.join(OUTPUT_DIR, f)
        sz = os.path.getsize(fp)
        im = Image.open(fp)
        print(f"  {f}: {im.size[0]}x{im.size[1]}, {sz // 1024}KB")


if __name__ == "__main__":
    main()
