"""Build index.html and index-en.html.

Everything on the page is drawn the way the app (3.0) draws it:
- the desk objects after UI/Desk/DeskObjects.swift (CSS over the paper, leather and linen
  textures in assets/tex): the decks as word cards on a metal ring, the 记录本 in its ink and
  oatmeal cloth (the cover of r27), the word books with their index tabs;
- the 今天 widgets after the app's widget code (HomeWidgetChrome.swift and the Widgets folder),
  with the app's own illustration and radio SVG copied out by tools/extract_art.py into
  tools/widget-art.json;
- the words on them as the app's catalogue (Localizable.xcstrings) has them.

It also writes tools/hand-chars.txt, the characters set in the handwriting face, for the font
subset. Usage:

    python3 tools/build_home.py
"""
import colorsys
import json
import math
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
ART = json.loads((ROOT / "tools" / "widget-art.json").read_text(encoding="utf-8"))

STORE = "https://apps.apple.com/app/id6780967507"

HAND = set()  # every string set in the handwriting face, for the font subset


def hand(text):
    HAND.update(text)
    return text


# ---------- Desk objects (after DeskObjects.swift) ----------

NAVY = ("#2A3860", ("#141C33", "#24305A", "#43538A"), ("#6E2820", "#9C3B2F"))
BRICK = ("#8B3A2F", ("#4A1A14", "#6E2A21", "#A6564A"), ("#B5A27C", "#DCCBA6"))

# WordBookCover: the books that come with the app have their own cloth.
WORDBOOK_COVERS = {"ielts": ("#8A5A4F", False), "academic2": ("#50646B", False)}


def obj(w, h, inner, name, meta, extra_class=""):
    return f"""          <figure class="obj{extra_class}" style="--w: {w}px; --h: {h}px;">
            <div class="art" aria-hidden="true">
{inner}            </div>
            <figcaption class="cap"><b>{name}</b><i>{meta}</i></figcaption>
          </figure>
"""


def hardcover_art(color, band, ribbon):
    return f"""              <span class="pages-r"></span><span class="pages-b"></span>
              <span class="ribbon" style="left: 54px; background: linear-gradient(90deg, {ribbon[0]}, {ribbon[1]} 50%, {ribbon[0]});"></span>
              <span class="cover leather" style="background-color: {color};"><span class="spine"></span><span class="hinge"></span><span class="band" style="background: linear-gradient(90deg, {band[0]}, {band[1]} 35%, {band[2]} 52%, {band[1]} 70%, {band[0]});"></span><span class="rim"></span></span>
"""


def ledger_art():
    # LedgerObject (r27): ink cloth from the spine over the left column's share of a page, then
    # the oatmeal cloth, a red rule where they meet; cream page edges and one ribbon.
    return """              <span class="pages-r"></span><span class="pages-b"></span>
              <span class="ribbon" style="left: 90px; background: linear-gradient(90deg, #5E2421, #7D2E2A 50%, #5E2421);"></span>
              <span class="cover ledger"><span class="spine" style="background: linear-gradient(90deg, rgba(0,0,0,.28), rgba(0,0,0,.03) 50%, rgba(0,0,0,0));"></span><span class="hinge" style="background: linear-gradient(90deg, rgba(0,0,0,.32), rgba(0,0,0,.04) 40%, rgba(255,255,255,.12) 68%, rgba(255,255,255,0));"></span><span class="ledger-shade"></span><span class="ledger-rule"></span><span class="ledger-rim"></span></span>
"""


def wordbook_art(cover):
    color, light = WORDBOOK_COVERS[cover]
    tabs = "".join(f'<span class="tab" style="top: {16 + i * 28}px;"></span>' for i in range(6))
    sheen = (f"linear-gradient(140deg, rgba(255,255,255,{0.30 if light else 0.18}), rgba(255,255,255,0) 40%, "
             f"rgba(0,0,0,0) 60%, rgba(0,0,0,{0.12 if light else 0.18}))")
    spine = f"linear-gradient(90deg, rgba(0,0,0,{0.12 if light else 0.24}), rgba(0,0,0,.06) 50%, rgba(0,0,0,0))"
    hinge = (f"linear-gradient(90deg, rgba(0,0,0,{0.16 if light else 0.24}), rgba(0,0,0,.05) 40%, "
             f"rgba(255,255,255,{0.4 if light else 0.18}) 68%, rgba(255,255,255,0))")
    rim = (f"inset 0 1px 0 rgba(255,255,255,{0.5 if light else 0.2}), inset 0 -1px 0 rgba(0,0,0,{0.14 if light else 0.22}), "
           f"inset -1px 0 0 rgba(0,0,0,{0.10 if light else 0.14})")
    return f"""              {tabs}
              <span class="pages-r"></span><span class="pages-b"></span>
              <span class="ribbon" style="left: 108px; background: linear-gradient(90deg, #6E2820, #9C3B2F 50%, #6E2820);"></span>
              <span class="cover" style="background-color: {color}; background-image: {sheen}, url('assets/tex/linen.png'); background-size: 100% 100%, 96px 96px;"><span class="spine" style="background: {spine};"></span><span class="hinge" style="background: {hinge};"></span><span class="rim" style="box-shadow: {rim};"></span></span>
"""


def pdf_art():
    bars = ('<span class="bar" style="width: 30%; margin: 0;"></span>'
            '<span class="bar" style="width: 72%; height: 4px; margin: 12px auto 0; background: #B9BBC0;"></span>'
            '<span class="bar" style="width: 52%; height: 4px; margin: 5px auto 0; background: #B9BBC0;"></span>'
            '<span class="bar" style="width: 26%; margin-top: 14px; background: #A9ABB0;"></span>'
            '<span class="bar" style="width: 100%;"></span><span class="bar" style="width: 94%;"></span><span class="bar" style="width: 62%;"></span>'
            '<span class="bar" style="width: 100%; margin-top: 10px;"></span><span class="bar" style="width: 88%;"></span><span class="bar" style="width: 70%;"></span>'
            '<span class="bar" style="width: 100%; margin-top: 10px;"></span><span class="bar" style="width: 84%;"></span>')
    clip = ('<svg class="clip" width="44" height="40" viewBox="0 0 44 40"><path d="M12 22 C10 10, 14 3, 22 3 C30 3, 34 10, 32 22" fill="none" stroke="#B9BDC4" stroke-width="1.8"></path>'
            '<path d="M15 22 C14 13, 17 8, 22 8 C27 8, 30 13, 29 22" fill="none" stroke="#D9DCE0" stroke-width="1.2"></path>'
            '<path d="M6 22 H38 L35 36 H9 Z" fill="#1C1D20"></path><path d="M8 23 H36 L35.4 26 H8.6 Z" fill="#4A4C52"></path>'
            '<path d="M9 36 H35" stroke="#000" stroke-opacity="0.4" stroke-width="1"></path></svg>')
    return f"""              <span class="pdfsheet texpaper" style="left: 8px; top: 8px; transform: rotate(-3deg);"></span>
              <span class="pdfsheet texpaper" style="left: 4px; top: 3px; transform: rotate(1.8deg);"></span>
              <span class="pdfsheet texpaper" style="left: 0; top: 0; padding: 26px 16px 0;">{bars}</span>
              {clip}
"""


# DeckObject: word cards on a metal ring. One card is 128 × 172 at (12, 24) in a 150 × 200
# frame, the ring through its hole at (18, 16).

def deck_look(name):
    """DeckObject.Look: the top card's two strokes and how far its cards fan, from its name."""
    word, line, spread = 64, 44, 1.0
    if name:
        h = 5381
        for byte in name.encode("utf-8"):
            h = (h * 33 + byte) & 0xFFFFFFFFFFFFFFFF
        word = min(84, max(44, 22 + len(name) * 7))
        line = min(word - 14, 26 + (h % 4) * 8)
        spread = 0.75 + ((h // 4) % 6) * 0.1
    return word, line, spread


def deck_fan(count):
    every = [(8, "#E7E2D6"), (5, "#EFEBE1"), (2.5, "#E9E4D8"), (-3, "#F1EEE6")]
    if count < 2:
        return []
    if count < 5:
        return [every[1]]
    if count < 10:
        return [every[1], every[3]]
    if count < 20:
        return [every[0], every[1], every[3]]
    return every


def deck_thickness(count):
    return 0 if count < 2 else 1 if count < 5 else 2 if count < 10 else 3 if count < 20 else 4


RING_IDS = [0]


def deck_art(name, count):
    word, line, spread = deck_look(name)
    out = []
    for degrees, tone in deck_fan(count):
        out.append(f'<span class="rcard texpaper" style="background-color: {tone}; transform: rotate({degrees * spread:.2f}deg);"></span>')
    edges = ["#E9E3D6", "#E1DACB", "#D9D1C0", "#D1C8B6"]
    for layer in reversed(range(deck_thickness(count))):
        out.append(f'<span class="rcard texpaper" style="background-color: {edges[layer]}; '
                   f'left: {12 + (layer + 1) * 0.6:.1f}px; top: {24 + (layer + 1) * 1.6:.1f}px;"></span>')
    out.append(f'<span class="rcard texpaper top"><span class="rhole"></span>'
               f'<span class="rmark" style="left: {(128 - word) / 2:.1f}px; top: 84px; width: {word}px; height: 3px; opacity: .62;"></span>'
               f'<span class="rmark" style="left: {(128 - line) / 2:.1f}px; top: 98px; width: {line}px; height: 2.5px; opacity: .34;"></span></span>')
    # The ring: in past the card's left edge, round outside its top-left corner, into the hole.
    RING_IDS[0] += 1
    gid = f"ring{RING_IDS[0]}"
    cx, cy = 6.0, 4.0
    r = math.hypot(12, 12)
    start = (0.0, cy + math.sqrt(r * r - cx * cx))
    d = f"M{start[0]:.2f} {start[1]:.2f}A{r:.2f} {r:.2f} 0 1 1 18 16"
    out.append(f'<svg class="ring" width="128" height="172" viewBox="0 0 128 172">'
               f'<defs><linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="128" y2="172">'
               f'<stop offset="0" stop-color="#EDEFF2"/><stop offset=".5" stop-color="#BFC4CA"/><stop offset="1" stop-color="#8D9299"/></linearGradient></defs>'
               f'<g fill="none" stroke-linecap="round"><path d="{d}" stroke="#878C93" stroke-width="3.4"/>'
               f'<path d="{d}" stroke="url(#{gid})" stroke-width="2.5"/>'
               f'<path d="{d}" stroke="rgba(255,255,255,.7)" stroke-width=".7" transform="translate(-.4 -.6)"/></g></svg>')
    return "".join(f"              {piece}\n" for piece in out)


def desk_item(item):
    kind, args = item[0], item[1:]
    if kind == "deck":
        count, name, meta = args
        return obj(150, 200, deck_art(name, count), name, meta, " deck")
    if kind == "ledger":
        name, meta = args
        return obj(150, 200, ledger_art(), name, meta)
    if kind == "wordbook":
        cover, name, meta = args
        return obj(150, 200, wordbook_art(cover), name, meta, " wordbook")
    if kind == "hardcover":
        (color, band, ribbon), name, meta = args
        return obj(150, 200, hardcover_art(color, band, ribbon), name, meta)
    if kind == "pdf":
        name, meta = args
        return obj(160, 220, pdf_art(), name, meta)
    raise ValueError(kind)


def desk_html(rows):
    return "".join('        <div class="desk-row">\n' + "".join(desk_item(i) for i in row) + "        </div>\n" for row in rows)


# ---------- Widget icons (the SF Symbols the widgets use, drawn small) ----------

ICONS = {
    "clock": '<circle cx="8" cy="8" r="6.3"/><path d="M8 4.6V8l2.4 1.6"/>',
    "flame": '<path d="M8.4 1.6c.4 2.6 3.9 4 3.9 7.8A4.3 4.3 0 0 1 8 13.9 4.3 4.3 0 0 1 3.7 9.6c0-2.2 1.2-3.6 2.4-4.6.1 1.6.7 2.6 1.6 2.9-.3-2.2-.2-4.3.7-6.3Z"/><path d="M8 13.9c-1.3 0-2-.9-2-2 0-1 .7-1.7 1.3-2.1.2.8.6 1.2 1.1 1.4.3-.5.5-1 .5-1.6.7.6 1.1 1.3 1.1 2.2 0 1.2-.8 2.1-2 2.1Z"/>',
    "timer": '<circle cx="8" cy="9" r="5.6"/><path d="M8 9 10.2 6.8M6.4 1.6h3.2M8 1.6v1.8"/>',
    "calendar": '<rect x="2" y="3" width="12" height="11" rx="2"/><path d="M2 6.6h12M5.2 1.6v2.6M10.8 1.6v2.6"/>',
    "number": '<path d="M6.2 2 4.8 14M11.2 2 9.8 14M2.6 5.6h11M2.2 10.4h11"/>',
    "book": '<path d="M3.2 2.4h8.2a1.4 1.4 0 0 1 1.4 1.4v10H4.6a1.4 1.4 0 0 1-1.4-1.4Z"/><path d="M3.2 12.4a1.4 1.4 0 0 1 1.4-1.4h8.2M6 2.4v8.6"/>',
    "list": '<circle cx="3.2" cy="4.4" r=".6" fill="currentColor"/><circle cx="3.2" cy="8" r=".6" fill="currentColor"/><circle cx="3.2" cy="11.6" r=".6" fill="currentColor"/><path d="M6 4.4h7.6M6 8h7.6M6 11.6h7.6"/>',
    "arrow-right": '<path d="M3 8h10M9 4l4 4-4 4"/>',
    "swap": '<path d="M2.6 5.4h10.4M10 2.4l3 3-3 3M13.4 10.6H3M6 7.6l-3 3 3 3"/>',
    "table": '<rect x="2" y="2.6" width="12" height="10.8" rx="1.8"/><path d="M2 6.2h12M2 9.8h12M6 2.6v10.8M10 2.6v10.8"/>',
    "chevron": '<path d="m4 6 4 4 4-4"/>',
}


def icon(name, size=13, width=1.5):
    return (f'<svg class="i" width="{size}" height="{size}" viewBox="0 0 16 16" fill="none" stroke="currentColor" '
            f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def header(title, icon_name, trailing=""):
    tail = f'<span class="w-note">{trailing}</span>' if trailing else ""
    return f'<div class="w-head">{icon(icon_name)}<span class="w-title">{title}</span>{tail}</div>'


def value(v, unit="", size=56, unit_size=13):
    u = f'<span class="w-unit" style="font-size: {unit_size}px">{unit}</span>' if unit else ""
    return f'<div class="w-value"><span class="w-num" style="--s: {size}px">{v}</span>{u}</div>'


def widget(size, inner, material="paper", extra="", label=""):
    cls = {"s": "", "m": " m", "l": " l"}[size]
    aria = f' role="img" aria-label="{label}"' if label else ""
    return f'        <div class="w{cls} mat-{material}{extra}"{aria}>{inner}</div>\n'


FILL = '<div class="w-fill"></div>'


def mist(hex_color):
    """AgendaColor.mist: a calendar's colour, quieted and warmed to sit on the paper."""
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    r, g, b = colorsys.hsv_to_rgb(h, min(s * 0.78, 0.62), min(max(v * 0.88, 0.45), 0.78))
    warm = (0.55, 0.51, 0.46)
    mixed = [c * 0.9 + w * 0.1 for c, w in zip((r, g, b), warm)]
    return "#" + "".join(f"{round(c * 255):02X}" for c in mixed)


# InkTone: a course's colour is its tone's text; the timetable's own (灰青) washes the class on now.
COURSE = {"berry": "#973044", "inkBlue": "#2E4B6E", "moss": "#4A6435"}
SLATE_WASH = "#DDEDEC"


# ---------- Widgets ----------

def w_today_review(t):
    # TodayReviewWidget, medium with work left: what is left today and how long it takes, the bar
    # and what is done; beside it 开始复习, 背几张 and the words due today.
    progress = 24 / 62
    left = (f'<div class="w-col">{header(t["today"], "clock")}{FILL}'
            f'{value("38", t["cards"], 40, 13)}<span class="w-cap13 lift">{t["minutes12"]}</span>'
            f'<div class="w-fill min6"></div><div class="w-bar"><i style="width: {progress * 100:.0f}%"></i></div>'
            f'<span class="w-cap12 gap">{t["reviewed"]}</span></div>')
    right = (f'<div class="w-side">{FILL}<span class="w-btn thick">{t["start"]}{icon("arrow-right", 12, 2)}</span>'
             f'<span class="w-plain">{t["few"]}{icon("chevron", 10, 2.2)}</span>'
             f'<span class="w-words">{icon("book", 12, 1.5)}{t["wordsWord"]}<b>20</b></span></div>')
    return widget("m", f'<div class="w-row">{left}<span class="w-vrule"></span>{right}</div>', extra=" corner-grid")


def streak_flame():
    return ('<svg class="w-flame" viewBox="0 0 48 58" aria-hidden="true">'
            '<path d="M25 3C27 12 39 18 39 33C39 44.5 32.5 53 24 53C15.5 53 9 45.5 9 36C9 28.5 13 23.5 17 20C17.5 25.5 20 29 22.5 30C21 21.5 22 11 25 3Z" fill="#FFE15A" stroke="#111317" stroke-width="2.1" stroke-linejoin="round"/>'
            '<path d="M24.5 31C26 36 31 38.5 31 43.5C31 48 28 50.5 24 50.5C20 50.5 17 47.8 17 44C17 41 19 39 20.5 37.5C21 40 22.5 41.5 23.5 42C23 38.5 23.4 34.5 24.5 31Z" fill="#FFFFFF" stroke="#111317" stroke-width="1.7" stroke-linejoin="round"/>'
            '<path d="M38 8 41 5M42 15.5 45.5 14.5" stroke="#111317" stroke-width="2" stroke-linecap="round"/></svg>')


def w_streak(t):
    dots = "".join("<i></i>" for _ in range(6)) + '<i class="today"></i>'
    inner = (f'{header(t["streak"], "flame")}{FILL}'
             f'<div class="w-row w-bottom">{value("12", t["days"], 56)}{FILL}{streak_flame()}</div>'
             f'<div class="w-fill min6"></div><div class="w-dots">{dots}</div>')
    return widget("s", inner)


def tick_ring(fraction, count=60, length=6, width=2):
    filled = round(fraction * count)
    lines = []
    for i in range(count):
        a = i / count * 2 * math.pi - math.pi / 2
        r1, r2 = 49, 49 - length
        color = "#111317" if i < filled else "#EDEDE8"
        lines.append(f'<path d="M{50 + math.cos(a) * r2:.2f} {50 + math.sin(a) * r2:.2f}L{50 + math.cos(a) * r1:.2f} {50 + math.sin(a) * r1:.2f}" stroke="{color}"/>')
    return (f'<svg class="w-ring" viewBox="0 0 100 100" aria-hidden="true"><g stroke-width="{width}" stroke-linecap="round">'
            + "".join(lines) + "</g></svg>")


def w_focus(t):
    inner = (f'{header(t["focus"], "timer")}<div class="w-dial">{tick_ring(42 / 60)}'
             f'<div class="w-dial-c"><span class="w-num" style="--s: 30px">42</span><span class="w-cap11">{t["of60"]}</span></div></div>')
    return widget("s", inner)


def w_forecast(t):
    # Seven days back, today, fourteen ahead: done in grey, today in ink with what is left
    # dashed above it, the days ahead dashed (ForecastChart in StatsWidgets.swift).
    past = [44, 58, 37, 61, 49, 55, 40]
    today_done, today_left = 24, 38
    ahead = [23, 31, 18, 27, 12, 22, 9, 15, 26, 11, 19, 8, 14, 10]
    top = max(past + [today_done + today_left] + ahead)
    n = 22
    W, H = 300.0, 100.0
    gap = 3.0
    bw = (W - gap * (n - 1)) / n
    ch = H - 18.0
    rects = []
    for i in range(n):
        x = i * (bw + gap)
        if i < 7:
            h = past[i] / top * ch
            rects.append(f'<rect x="{x:.2f}" y="{H - h:.2f}" width="{bw:.2f}" height="{h:.2f}" rx="1.5" fill="#C9CBC4"/>')
        elif i == 7:
            hd, hl = today_done / top * ch, today_left / top * ch
            rects.append(f'<rect x="{x:.2f}" y="{H - hd:.2f}" width="{bw:.2f}" height="{hd:.2f}" rx="1.5" fill="#111317"/>')
            rects.append(f'<rect x="{x + .5:.2f}" y="{H - hd - hl + .5:.2f}" width="{bw - 1:.2f}" height="{hl - 1:.2f}" rx="1.5" fill="none" stroke="#111317" stroke-width="1" stroke-dasharray="2 2" vector-effect="non-scaling-stroke"/>')
        else:
            h = ahead[i - 8] / top * ch
            rects.append(f'<rect x="{x + .5:.2f}" y="{H - h + .5:.2f}" width="{bw - 1:.2f}" height="{h - 1:.2f}" rx="1.5" fill="none" stroke="#9A9EA5" stroke-width="1" stroke-dasharray="2 2" vector-effect="non-scaling-stroke"/>')
    band_x = 8 * (bw + gap) - gap / 2
    band_w = 7 * (bw + gap)
    band = f'<rect x="{band_x:.2f}" y="0" width="{band_w:.2f}" height="{H:.0f}" rx="6" fill="#F8F8F4"/>'
    svg = (f'<svg class="w-chart-svg" viewBox="0 0 {W:.0f} {H:.0f}" preserveAspectRatio="none" aria-hidden="true">'
           + band + "".join(rects) + "</svg>")
    slot = 100 / n
    today_center = 7.5 * slot
    left_top = (H - (today_done + today_left) / top * ch) / H * 100
    labels = (f'<span class="w-chart-band" style="left: {band_x / W * 100:.2f}%; width: {band_w / W * 100:.2f}%">{t["week7"]}</span>'
              f'<span class="w-chart-left" style="left: {today_center:.2f}%; top: {left_top:.2f}%">{t["left38"]}</span>')
    axis = (f'<span style="left: {0.5 * slot:.2f}%">11/18</span>'
            f'<span class="b" style="left: {today_center:.2f}%">{t["todayAxis"]}</span>'
            f'<span style="left: {14.5 * slot:.2f}%">12/2</span>'
            f'<span style="left: {21.5 * slot:.2f}%">12/9</span>')
    cells = (f'<div class="w-cells"><div><span class="w-cap12">{t["tomorrow"]}</span>{value("23", t["cards"], 26, 12)}</div>'
             f'<span class="w-vrule"></span><div><span class="w-cap12">{t["in7"]}</span>{value("96", t["cards"], 26, 12)}</div>'
             f'<span class="w-vrule"></span><div><span class="w-cap12">{t["overdue"]}</span>{value("0", t["cards"], 26, 12)}</div></div>')
    inner = (f'{header(t["forecast"], "calendar", "11/18 – 12/9")}{cells}'
             f'<div class="w-chart"><div class="w-chart-plot">{svg}{labels}</div><div class="w-axis">{axis}</div></div>'
             f'<span class="w-btn ghost">{icon("swap", 14, 1.6)}{t["rebalance"]}</span>')
    return widget("l", inner, extra=" forecast")


def w_metrics(t):
    cells = [("62", t["times"], t["reviewToday"]), ("87", "%", t["correct"]), ("42", t["min"], t["focus"]), ("118", "/ 340", t["longterm"])]
    grid = "".join(f'<div>{value(v, u, 24, 11)}<span class="w-cap11">{label}</span></div>' for v, u, label in cells)
    inner = f'{header(t["metrics"], "number")}<div class="w-fill min8"></div><div class="w-grid2">{grid}</div>'
    return widget("s", inner)


def day_ring(fraction, today):
    if fraction >= 1:
        fill = "#FFE15A" if today else "#111317"
        ring = '<circle cx="8" cy="8" r="6.75" fill="none" stroke="#111317" stroke-width="1.5"/>' if today else ""
        return f'<svg viewBox="0 0 16 16"><circle cx="8" cy="8" r="7.5" fill="{fill}"/>{ring}</svg>'
    r = 6.4
    c = 2 * math.pi * r
    bg = '<circle cx="8" cy="8" r="7.5" fill="#FFF4B8"/>' if today else ""
    return (f'<svg viewBox="0 0 16 16">{bg}<circle cx="8" cy="8" r="{r}" fill="none" stroke="#EDEDE8" stroke-width="2.2"/>'
            f'<circle cx="8" cy="8" r="{r}" fill="none" stroke="#111317" stroke-width="2.2" stroke-linecap="round" '
            f'stroke-dasharray="{c * fraction:.2f} {c:.2f}" transform="rotate(-90 8 8)"/></svg>')


def w_week(t):
    counts = [48, 52, 18, 60, 45, 58, 62]
    rings = "".join(f"<i>{day_ring(min(1, c / 30), i == 6)}</i>" for i, c in enumerate(counts))
    inner = (f'{header(t["week"], "calendar")}{FILL}{value("343", t["reviews"], 56)}'
             f'{FILL}<div class="w-rings">{rings}</div>')
    return widget("s", inner)


def agenda_row(time, title, color, cls="", place=""):
    tail = f'<span class="ag-place">{place}</span>' if place else ""
    return (f'<div class="ag-row{cls}"><span class="ag-time">{time}</span><i class="ag-bar" style="background: {color}"></i>'
            f'<span class="ag-title">{title}</span>{tail}</div>')


def w_schedule(t):
    # ScheduleWidget, medium: today's events beside today's to-dos (each with its circle).
    events = "".join(agenda_row(time, title, mist(color)) for time, title, color in t["events"])
    tasks = "".join(
        f'<div class="tk-row"><i class="tk-tick" style="box-shadow: inset 0 0 0 1.4px {mist(color)}"></i>'
        f'<span class="tk-title">{title}</span>{f"<span class=tk-time>{due}</span>" if due else ""}</div>'
        for title, due, color in t["tasks"])
    inner = (f'{header(t["schedule"], "calendar", t["dateNote"])}'
             f'<div class="w-split"><div>{events}</div><span class="w-vrule"></span><div>{tasks}</div></div>')
    return widget("m", inner)


def w_timetable(t):
    # TimetableWidget, medium: today's classes, the one on now on the timetable's own wash, those
    # over faded; each in its course's colour, its room at the end.
    rows = "".join(agenda_row(time, name, COURSE[tone], {"over": " over", "on": " on"}.get(state, ""), place)
                   for time, name, place, tone, state in t["classes"])
    inner = f'{header(t["classesTitle"], "table", t["weekNote"])}<div class="ag-list">{rows}</div>'
    return widget("m", inner, extra=" timetable")


def w_write_cell(t):
    # WriteCellBoardWidget, medium: the last cell of the logbook's last page, and under it the new
    # one waiting, its keys to say it or take a photo of it; the empty stretch ruled.
    mic = ('<svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="#fff" stroke-width="1.7" stroke-linecap="round">'
           '<rect x="5.6" y="1.6" width="4.8" height="8.2" rx="2.4"/><path d="M3.2 7.6a4.8 4.8 0 0 0 9.6 0M8 12.4v2.2"/></svg>')
    inner = (f'<div class="wc"><div class="wc-row"><span class="wc-note">{hand(t["cellNote"])}</span>'
             f'<span class="wc-body">{hand(t["cellBody"])}</span></div>'
             f'<div class="wc-new"><span class="wc-note"></span><span class="wc-keys"><i class="wc-key">{mic}</i>'
             f'<i class="wc-key shutter"></i></span></div></div>')
    return widget("m", inner, extra=" write-cell", label=t["writeLabel"])


def subst(svg, values):
    return re.sub(r"\{\{([^}]*)\}\}", lambda m: values.get(m.group(1).strip(), ""), svg)


def scene(svg, css, values=None, hidden=()):
    svg = subst(svg, values or {})
    # textLength is a "keep within" width in the app's renderer; in a browser it would stretch
    # the words, so it is dropped (the labels are short).
    svg = re.sub(r'\stextLength="[^"]*"', "", svg)
    for cls in hidden:
        css += f".{cls}{{display:none}}"
    for m in re.finditer(r"<text[^>]*>([^<]*)</text>", svg):
        hand(m.group(1))
    svg = svg.replace("<svg ", '<svg class="w-scene" preserveAspectRatio="xMidYMid slice" ', 1)
    return f"<style>{css}</style>{svg}"


def illustration(inner, label, extra=""):
    return widget("s", f'<div class="w-bleed">{inner}</div>', "wall", extra, label=label)


def w_cat(t):
    svg = ART["catS"]
    for sample, name in zip(["高等数学", "大学物理", "线性代数"], t["books"]):
        svg = svg.replace(f">{sample}<", f">{name}<")
    return illustration(scene(svg, ART["catCSS"], {"due": "38", "label": t["dueLabel"], "minutes": ""}), t["catLabel"])


def hourglass(step, transform):
    fraction = step / 48
    running = 0 < step < 48
    s = f'<g transform="{transform}" stroke="#111317" stroke-linecap="round" stroke-linejoin="round">' + ART["hourglassBackPart"]
    if step < 48:
        level = 82.6 - 48.6 * math.sqrt(1 - fraction)
        dip = 5.0 if running else 0
        s += '<g clip-path="url(#hgTop)"><g clip-path="url(#hgTopSand)"><path d="M30 20H138V90H30Z" fill="#FFE15A" stroke="none"/>' + ART["hourglassDotsPart"] + "</g></g>"
        s += f'<defs><clipPath id="hgTopSand"><path d="M30 {level:.1f}L78 {level:.1f}L84 {level + dip:.1f}L90 {level:.1f}L138 {level:.1f}V92H30Z"/></clipPath></defs>'
    peak = 142.0
    if step > 0:
        level = 142 - 50 * (1 - math.sqrt(1 - fraction))
        peak = level - 1
        s += '<g clip-path="url(#hgBottom)"><g clip-path="url(#hgBottomSand)"><path d="M30 84H138V150H30Z" fill="#FFE15A" stroke="none"/>' + ART["hourglassDotsPart"] + "</g></g>"
        s += f'<defs><clipPath id="hgBottomSand"><path d="M30 146L30 {level + 5:.1f}Q84 {level - 7:.1f} 138 {level + 5:.1f}L138 146Z"/></clipPath></defs>'
    if running:
        s += f'<path class="hg-fall hg-s1" d="M84 84V{peak:.1f}" stroke="#E0B400" stroke-width="1.8" stroke-dasharray=".1 3.4"/>'
        s += f'<path class="hg-fall hg-s2" opacity="0" d="M84.4 84V{peak:.1f}" stroke="#E0B400" stroke-width="1.4" stroke-dasharray=".1 2.4"/>'
        s += f'<g transform="translate(84 {peak:.1f})"><path class="hg-b1" d="M0 0h.1" stroke="#E0B400" stroke-width="1.8"/><path class="hg-b2" d="M0 0h.1" stroke="#E0B400" stroke-width="1.6"/></g>'
    return s + ART["hourglassFrontPart"] + "</g>"


def w_hourglass(t):
    clips = ('<defs><clipPath id="hgTop"><path d="M60 26C59 44 64 61 79 76.6L84 82.6L89 76.6C104 61 109 44 108 26Z"/></clipPath>'
             '<clipPath id="hgBottom"><path d="M84 87.4L79 93.4C64 109 59 126 60 142H108C109 126 104 109 89 93.4Z"/></clipPath></defs>')
    tag = ART["hourglassTagPart"].replace("/ {{ goal }} 分钟", t["ofGoal"])
    svg = ('<svg viewBox="0 0 168 168" fill="none" data-lines="uniform"><g stroke="#111317" stroke-linecap="round">'
           '<path d="M-24-24H192V155H-24Z" fill="#FAF6EC" stroke="none"/><path d="M-24 155H192V192H-24Z" fill="#F0E1C2" stroke="none"/>'
           '<path d="M-6 155.2C50 154.6 120 155.6 174 155" stroke-width="2.4"/></g>'
           + clips + hourglass(round(42 / 60 * 48), "translate(26 0)")
           + '<g stroke="#111317" stroke-linecap="round" stroke-linejoin="round">' + tag + "</g></svg>")
    return illustration(scene(svg, ART["hourglassCSS"], {"min": "42", "goal": "60"}), t["hourglassLabel"])


def w_lamp(t):
    return illustration(scene(ART["deskS"], ART["deskCSS"], {"dk1": t["lamp1"], "dk2": t["lamp2"], "dkLine": ""}, hidden=["dk-off"]), t["lampLabel"])


def w_coffee(t):
    return illustration(scene(ART["coffeeS"], ART["coffeeCSS"], {}), t["coffeeLabel"], " opt w-optional-4")


def w_radio(t):
    channels = t["channels"]
    index = 2  # 雨声
    keys = ["snow", "pink", "rain", "wave", "fire", "cafe", "lib", "tick"]
    values = {
        "m.win": "#FFE15A", "m.ptr": str(4 + index * 7), "m.tip": "#C8361F",
        "m.blink": "rzBlink 1.8s ease-in-out infinite", "m.bob": "rzBob 2.4s ease-in-out infinite",
        "m.cone": "rzCone 2s ease-in-out infinite", "m.arcs": "inline",
        "m.knobA": str(-105 + index * 30), "m.knobB": str(-120 + 2 * 60),
    }
    for k, key in enumerate(keys):
        values[f"m.v.{key}"] = "inline" if k == index else "none"
    art = subst(ART["radioMedium"], values).replace('width="144" height="96" ', 'class="w-radio-art" ', 1)
    band = ART["radioBand"].replace('width="322" height="14" ', "", 1).replace(
        'style="position: absolute; left: 0; top: 0"', 'class="w-band-svg" preserveAspectRatio="none"', 1)
    names = "".join(f'<span{" class=on" if i == index else ""}>{name}</span>' for i, name in enumerate(channels))
    tuning = (f'<div class="w-tuning">{band}<i class="w-needle" style="left: calc({(index + 0.5) / 8 * 100:.3f}% - 1px)"></i>'
              f'<div class="w-channels">{names}</div></div>')
    pause = ('<span class="w-play" aria-hidden="true"><svg viewBox="0 0 16 16" width="15" height="15"><rect x="4" y="3" width="2.6" height="10" rx=".8" fill="#fff"/>'
             '<rect x="9.4" y="3" width="2.6" height="10" rx=".8" fill="#fff"/></svg></span>')
    top = (f'<div class="w-radio-top">{art}<div class="w-radio-text"><b>{channels[index]}</b>'
           f'<span class="w-cap12">{t["playing"]}</span></div>{pause}</div>')
    return widget("m", f"<style>{ART['radioCSS']}</style>" + top + tuning, extra=" radio")


def w_countdown(t):
    inner = (f'{header(t["exam"], "calendar")}{FILL}'
             f'<div class="w-figure base"><span class="w-cap13">{t["left"]}</span><span class="w-num" style="--s: 56px">23</span><span class="w-cap13">{t["dayUnit"]}</span></div>')
    return widget("s", inner, "hl")


def w_pomodoro(t):
    r = 46
    c = 2 * math.pi * r
    fraction = (18 * 60 + 42) / (25 * 60)
    dial = (f'<svg class="w-ring" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="{r}" fill="none" stroke="rgba(255,255,255,.18)" stroke-width="6"/>'
            f'<circle cx="50" cy="50" r="{r}" fill="none" stroke="#FF8C7D" stroke-width="6" stroke-linecap="round" stroke-dasharray="{c * fraction:.2f} {c:.2f}" transform="rotate(-90 50 50)"/></svg>')
    inner = (f'{header(t["pomodoro"], "timer")}<div class="w-dial">{dial}'
             f'<div class="w-dial-c"><span class="w-num" style="--s: 24px">18:42</span><span class="w-cap11">{t["focusing"]}</span></div></div>')
    return widget("s", inner, "ink")


def w_clock(t):
    r = 48.5
    marks = []
    for k in range(12):
        a = k * math.pi / 6
        inner = r * (0.8 if k % 3 == 0 else 0.88)
        marks.append(f"M{50 + inner * math.sin(a):.2f} {50 - inner * math.cos(a):.2f}L{50 + r * 0.94 * math.sin(a):.2f} {50 - r * 0.94 * math.cos(a):.2f}")
    svg = (f'<svg class="w-clock" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="{r}" fill="none" stroke="#111317" stroke-width="1.6"/>'
           f'<path d="{" ".join(marks)}" stroke="#111317" stroke-width="2.2" stroke-linecap="round"/>'
           f'<g stroke="#C8361F" stroke-linecap="round"><path class="h" d="M50 50V{50 - r * 0.5:.2f}" stroke-width="3.9" transform="rotate(305 50 50)"/>'
           f'<path class="mi" d="M50 50V{50 - r * 0.74:.2f}" stroke-width="2.7" transform="rotate(60 50 50)"/>'
           f'<path class="se" d="M50 50V{50 - r * 0.82:.2f}" stroke-width="1" transform="rotate(0 50 50)"/></g>'
           '<circle cx="50" cy="50" r="2.5" fill="#111317"/></svg>')
    return widget("s", f'<div class="w-clock-wrap">{svg}</div>', extra=" opt", label=t["clockLabel"])


def w_semester(t):
    total, current = 14, 12
    r = 41
    segs = []
    for week in range(1, total + 1):
        gap = 0.012
        a0 = ((week - 1) / total + gap) * 2 * math.pi - math.pi / 2
        a1 = (week / total - gap) * 2 * math.pi - math.pi / 2
        color = "#111317" if week < current else ("#C8361F" if week == current else "#EDEDE8")
        segs.append(f'<path d="M{50 + r * math.cos(a0):.2f} {50 + r * math.sin(a0):.2f}A{r} {r} 0 0 1 {50 + r * math.cos(a1):.2f} {50 + r * math.sin(a1):.2f}" stroke="{color}"/>')
    svg = f'<svg class="w-ring" viewBox="0 0 100 100" aria-hidden="true"><g fill="none" stroke-width="9">{"".join(segs)}</g></svg>'
    pre = f'<span class="w-cap11">{t["weekPre"]}</span>' if t["weekPre"] else ""
    post = f'<span class="w-cap11">{t["weekPost"]}</span>' if t["weekPost"] else ""
    inner = (f'{header(t["semester"], "book")}<div class="w-dial">{svg}<div class="w-dial-c">'
             f'<div class="w-figure base tight">{pre}<span class="w-num" style="--s: 28px">{current}</span>{post}</div>'
             f'<span class="w-cap11">/ {total}</span></div></div>')
    return widget("s", inner, extra=" opt")


def w_checklist(t):
    rows = "".join(f'<div class="w-todo"><i></i><span>{item}</span></div>' for item in t["todos"])
    inner = (f'{header(t["checklist"], "list")}<div class="w-figure base tight"><span class="w-num" style="--s: 56px">2</span><span class="w-num faint" style="--s: 20px">/5</span></div>'
             f'{FILL}{rows}')
    return widget("s", inner, "grid", " opt w-optional-4")


def desk_entry(art, name, meta, cls=""):
    inner = (f'<div class="w-entry"><div class="w-entry-obj{cls}" style="--w: 150px; --h: 200px;"><div class="art" aria-hidden="true">{art}</div></div>'
             f'<span class="w-entry-cap"><b>{name}</b><i>{meta}</i></span></div>')
    return widget("s", inner, "bare")


def w_desk_deck(t):
    return desk_entry(deck_art(t["pinDeck"], 86), t["pinDeck"], t["pinDeckMeta"], " deck")


def w_desk_ledger(t):
    return desk_entry(ledger_art(), t["pinLedger"], t["pinLedgerMeta"])


def w_desk_wordbook(t):
    return desk_entry(wordbook_art("ielts"), t["pinWords"], t["pinWordsMeta"])


def board_html(t):
    # 30 cells on six columns; 28 on four (w-optional-4 gone), 26 on two (.opt gone): no holes.
    return "".join([
        w_today_review(t), w_streak(t), w_focus(t), w_forecast(t),
        w_schedule(t), w_radio(t), w_metrics(t), w_week(t),
        w_cat(t), w_countdown(t), w_timetable(t), w_pomodoro(t), w_clock(t),
        w_write_cell(t), w_hourglass(t), w_desk_deck(t), w_desk_ledger(t),
        w_lamp(t), w_desk_wordbook(t), w_semester(t), w_checklist(t), w_coffee(t),
    ])


# ---------- Words ----------

# The sample day: Wednesday 25 November, ten to twelve, week 12 of a fourteen-week term.
BLUE, GREEN, ORANGE = "#1BADF8", "#63DA38", "#FF9500"

ZH_BOARD = {
    "today": "今天复习", "cards": "张", "minutes12": "约 12 分钟", "reviewed": "已复习 24 张",
    "start": "开始复习", "few": "背几张", "wordsWord": "单词",
    "streak": "连续打卡", "days": "天", "focus": "今天专注", "of60": "/ 60 分钟",
    "forecast": "前后两周", "tomorrow": "明天", "in7": "七天内", "overdue": "积压", "week7": "七天内",
    "left38": "还剩 38", "todayAxis": "今天", "rebalance": "重新安排",
    "metrics": "今天的数字", "times": "次", "reviewToday": "今天复习", "correct": "答对", "min": "分钟", "longterm": "长期记住",
    "week": "近 7 天", "reviews": "次复习",
    "schedule": "日程", "dateNote": "11月25日 周三",
    "events": [("13:00", "TA 答疑", BLUE), ("16:00", "小组讨论", GREEN), ("18:30", "和 Lin 吃饭", ORANGE)],
    "tasks": [("交实验报告", "23:59", BLUE), ("读第 9 章", "", BLUE), ("约 advisor", "", BLUE)],
    "classesTitle": "今天的课", "weekNote": "第 12 周 · 周三",
    "classes": [("09:30", "PSYCH 101", "MC 1085", "berry", "over"), ("11:30", "ECON 102", "AL 116", "inkBlue", "on"),
                ("14:30", "CHEM 2410 实验", "C2 278", "moss", "")],
    "cellNote": "巴甫洛夫", "cellBody": "铃声 + 食物，之后只响铃 → 流口水", "writeLabel": "记一格：在记录本的新一格里写",
    "books": ["PSYCH", "ECON", "CHEM"], "dueLabel": "张到期", "catLabel": "睡猫：38 张到期",
    "ofGoal": "/ 60 分钟", "hourglassLabel": "沙漏：今天专注 42 / 60 分钟",
    "lamp1": "今天专注", "lamp2": "42 分钟", "lampLabel": "台灯书桌：今天专注 42 分钟",
    "coffeeLabel": "咖啡",
    "channels": ["白噪音", "粉噪音", "雨声", "海浪", "篝火", "咖啡馆", "图书馆", "钟摆"], "playing": "播放中",
    "exam": "ECON 102 期末", "left": "还有", "dayUnit": "天",
    "pomodoro": "番茄钟", "focusing": "专注中",
    "clockLabel": "时钟",
    "semester": "学期进度", "weekPre": "第", "weekPost": "周",
    "checklist": "清单", "todos": ["问 TA 第 3 题", "ECON 提纲"],
    "pinDeck": "PSYCH 101", "pinDeckMeta": "86 张 · 今天 12",
    "pinLedger": "PSYCH 101 课堂记录", "pinLedgerMeta": "14 页",
    "pinWords": "雅思词汇", "pinWordsMeta": "1471 词 · 今天 20",
}

EN_BOARD = {
    "today": "Today’s Reviews", "cards": "cards", "minutes12": "~12 min", "reviewed": "24 cards reviewed",
    "start": "Start Review", "few": "Learn a Few", "wordsWord": "Words",
    "streak": "Streak", "days": "days", "focus": "Focus Today", "of60": "/ 60 min",
    "forecast": "Two Weeks", "tomorrow": "Tomorrow", "in7": "Next 7 days", "overdue": "Overdue", "week7": "Next 7 days",
    "left38": "38 left", "todayAxis": "Today", "rebalance": "Reschedule",
    "metrics": "Today’s Numbers", "times": "", "reviewToday": "Reviews", "correct": "Correct", "min": "min", "longterm": "Long-term",
    "week": "Last 7 Days", "reviews": "reviews",
    "schedule": "Schedule", "dateNote": "Wed, Nov 25",
    "events": [("13:00", "Office hours", BLUE), ("16:00", "Study group", GREEN), ("18:30", "Lin’s party", ORANGE)],
    "tasks": [("Lab report", "23:59", BLUE), ("Read ch. 9", "", BLUE), ("Email advisor", "", BLUE)],
    "classesTitle": "Today’s Classes", "weekNote": "Week 12 · Wed",
    "classes": [("09:30", "PSYCH 101", "MC 1085", "berry", "over"), ("11:30", "ECON 102", "AL 116", "inkBlue", "on"),
                ("14:30", "CHEM 2410 Lab", "C2 278", "moss", "")],
    "cellNote": "Pavlov", "cellBody": "bell + food, then the bell alone → drooling", "writeLabel": "Write a Cell: a new cell of the logbook",
    "books": ["PSYCH", "ECON", "CHEM"], "dueLabel": "due", "catLabel": "Sleepy cat: 38 cards due",
    "ofGoal": "/ 60 min", "hourglassLabel": "Hourglass: 42 of 60 minutes of focus today",
    "lamp1": "Focus", "lamp2": "42 min", "lampLabel": "Desk lamp: 42 minutes of focus today",
    "coffeeLabel": "Coffee",
    "channels": ["White", "Pink", "Rain", "Ocean", "Fire", "Café", "Library", "Clock"], "playing": "Playing",
    "exam": "ECON 102 final", "left": "in", "dayUnit": "days",
    "pomodoro": "Pomodoro", "focusing": "Focusing",
    "clockLabel": "Clock",
    "semester": "Term Progress", "weekPre": "Week", "weekPost": "",
    "checklist": "Checklist", "todos": ["Ask TA re Q3", "ECON outline"],
    "pinDeck": "PSYCH 101", "pinDeckMeta": "86 · 12 due",
    "pinLedger": "PSYCH 101 lectures", "pinLedgerMeta": "14 pages",
    "pinWords": "IELTS Words", "pinWordsMeta": "1471 words · 20 today",
}

PAGES = {
    "zh": {
        "out": "index.html",
        "lang": "zh-Hans",
        "title": "Memo Clock 记忆时钟：笔记与复习",
        "description": "Memo Clock 记忆时钟：课堂笔记、记录本、单词本和抽认卡放在一起，快忘的时候叫你回来复习。iPad 和 iPhone，一次买断，没有订阅，不用注册。",
        "nav": '<a href="support.html">支持</a>\n      <a href="privacy.html">隐私政策</a>\n      <a href="index-en.html" lang="en" hreflang="en">English</a>',
        "name": "Memo Clock 记忆时钟：笔记与复习",
        "line": "记一次，快忘的时候它自己回来。",
        "store": "在 App Store 下载",
        "card": {
            "title": "经典条件反射",
            "ask": "Classical conditioning 是什么？举个例子。",
            "answer": "一个中性刺激反复和本来就能引起反应的刺激一起出现，之后它自己也能引起这个反应。",
            "legend": [("NS", "中性刺激：铃声"), ("US", "无条件刺激：食物"), ("CR", "条件反应：听到铃声流口水")],
            "why": "例：巴甫洛夫的狗，铃声和食物一起出现很多次以后，只响铃它也流口水。",
        },
        "grades": [("忘记", "还要记得 2 次"), ("模糊", "还要记得 1 次"), ("记得", "5 天后")],
        "desk_title": "卡组、记录本、单词本、笔记和 PDF，摆在一张书桌上",
        "desk": [
            [("deck", 86, "PSYCH 101", "86 张 · 今天 12"), ("deck", 52, "ECON 102", "52 张 · 今天 8"),
             ("deck", 31, "有机化学反应", "31 张"), ("ledger", "PSYCH 101 课堂记录", "14 页")],
            [("wordbook", "ielts", "雅思词汇", "1471 词 · 今天 20"), ("wordbook", "academic2", "学术英语 · 进阶", "834 条"),
             ("hardcover", NAVY, "ECON 102 笔记", "12 页"), ("pdf", "CHEM 2410 期中复习", "PDF · 23 页")],
        ],
        "board_title": "今天页：小组件大中小混排，想看什么放什么",
        "board": ZH_BOARD,
        "features": [
            ("记", "记录本一格记一条，右栏写内容，左栏写提示。按住页尾那一格说一句就记下；拍下课件和板书，选中要的字放进格子。iPad 上用 Apple Pencil 记笔记，PDF、Word、PPT 打开就能读、能写。"),
            ("变成复习", "按住一格选「背这一格」，它就是一张卡：正面右栏，翻过来左栏；也能整本一起背。笔记和 PDF 上圈一块，就加进复习。"),
            ("到点复习", "每天先定好今天这一批，最多你设的张数。忘记、模糊、记得三档，每个键下写着这张什么时候再来；提醒时间自己定，断了打卡可以补签。"),
            ("背单词", "自带雅思、四级、六级和学术英语（三个难度）词书，有释义和例句；粘贴自己的词表就是一本。"),
            ("公式", "公式键里有分式、根号、积分、矩阵和化学式。iOS 18 起能手写公式，自动排好。"),
            ("书桌和今天页", "卡组、记录本、笔记本、单词本摆在一张书桌上。今天页用小组件自己搭：日程连着系统日历和提醒事项，还有课程表、番茄钟、白噪音。"),
            ("数据是你的", "iPad 和 iPhone 通过你自己的 iCloud 同步，每周自动备份成一个文件。Anki 牌组连进度一起导入。没有账号，没有服务器，没有广告。"),
            ("一次买断", "买一次，全部功能都能用。没有订阅，没有内购。"),
        ],
        "foot": '<a href="support.html">支持</a>\n    <a href="privacy.html">隐私政策</a>\n    <a href="mailto:3528872473@qq.com">3528872473@qq.com</a>',
    },
    "en": {
        "out": "index-en.html",
        "lang": "en",
        "title": "Memo Clock: Notes & Flashcards",
        "description": "Memo Clock keeps your class notes, a logbook, word books and flashcards in one place, and brings each thing back right before you forget it. iPad and iPhone. Pay once: no subscription, no account.",
        "nav": '<a href="support-en.html">Support</a>\n      <a href="privacy-en.html">Privacy</a>\n      <a href="index.html" lang="zh-Hans" hreflang="zh-Hans">中文</a>',
        "name": "Memo Clock: Notes &amp; Flashcards",
        "line": "Write it down once and it comes back right before you forget.",
        "store": "Download on the App Store",
        "card": {
            "title": "Classical conditioning",
            "ask": "What is classical conditioning? Give an example.",
            "answer": "A neutral stimulus, paired again and again with one that already triggers a response, comes to trigger that response on its own.",
            "legend": [("NS", "neutral stimulus: the bell"), ("US", "unconditioned stimulus: food"), ("CR", "conditioned response: drooling at the bell")],
            "why": "Pavlov’s dogs: after the bell rang with food many times, the bell alone made them drool.",
        },
        "grades": [("Forgot", "Got it 2 more times"), ("Fuzzy", "Got it 1 more time"), ("Got it", "in 5 days")],
        "desk_title": "Decks, logbooks, word books, notebooks and PDFs, all on one desk",
        "desk": [
            [("deck", 86, "PSYCH 101", "86 · 12 due"), ("deck", 52, "ECON 102", "52 · 8 due"),
             ("deck", 31, "Organic reactions", "31 cards"), ("ledger", "PSYCH 101 lectures", "14 pages")],
            [("wordbook", "ielts", "IELTS Words", "1471 words · 20 today"), ("wordbook", "academic2", "Academic English · Intermediate", "834 entries"),
             ("hardcover", NAVY, "ECON 102 notes", "12 pages"), ("pdf", "CHEM 2410 midterm review", "PDF · 23 pages")],
        ],
        "board_title": "Today: widgets small, medium and large, laid out your way",
        "board": EN_BOARD,
        "features": [
            ("Write it down", "A logbook with one note per cell: the content on the right, a cue on the left. Hold the last cell of a page and say it; snap a slide or the whiteboard and drop the text in. On iPad, take notes with Apple Pencil, and open PDF, Word and PowerPoint files to read and write on."),
            ("Turn it into review", "Hold a cell and choose Learn this cell: it becomes a card, the right column in front and the left on the back. Or learn every cell in the book. Circle any part of a notebook page or a PDF to review it."),
            ("Review on time", "Each day starts with today’s batch, up to the number you choose. Grade Forgot, Fuzzy or Got it, and every button tells you when the card comes back. Pick your reminder time, and keep your streak with make-ups."),
            ("Words for English", "IELTS, CET-4, CET-6 and Academic English in three levels come with the app, with meanings and examples. Paste your own word list to make a book."),
            ("Formulas", "Formula keys for fractions, roots, integrals, matrices and chemistry. On iOS 18, write a formula by hand and it is typeset for you."),
            ("Your desk and your day", "Decks, logbooks, notebooks and word books on one desk. Build your Today page from widgets: Schedule with your Calendar and Reminders, your class timetable, a Pomodoro timer, white noise."),
            ("Your data stays yours", "Syncs your iPad and iPhone through your own iCloud, and backs everything up to a file every week. Imports Anki decks with their progress. No account, no server, no ads."),
            ("Pay once", "Buy it once and every feature is yours. No subscription, no in-app purchases."),
        ],
        "foot": '<a href="support-en.html">Support</a>\n    <a href="privacy-en.html">Privacy</a>\n    <a href="mailto:3528872473@qq.com">3528872473@qq.com</a>',
    },
}


def card_html(card):
    legend = "".join(
        f'            <span class="sym">{sym}</span><span class="mean">{hand(mean)}</span>\n'
        for sym, mean in card["legend"]
    )
    return f"""        <div class="pile">
          <div class="cardback sheet">
            <p class="title">{hand(card['title'])}</p>
            <p class="ask">{hand(card['ask'])}</p>
            <p class="answer">{hand(card['answer'])}</p>
            <div class="legend">
{legend}            </div>
            <p class="why">{hand(card['why'])}</p>
          </div>
        </div>
"""


def grades_html(grades):
    cells = []
    for i, (word, when) in enumerate(grades):
        cls = ' class="forgot"' if i == 0 else ""
        cells.append(f"          <div{cls}><b>{word}</b><span>{when}</span></div>")
    return '        <div class="grades sheet" aria-hidden="true">\n' + "\n".join(cells) + "\n        </div>\n"


def features_html(features):
    return "".join(f'      <div class="row"><dt>{t}</dt><dd>{d}</dd></div>\n' for t, d in features)


CLOCK_SCRIPT = """  <script>
    (function () {
      var clock = document.querySelector('.w-clock');
      if (!clock) return;
      function set() {
        var d = new Date(), s = d.getSeconds(), m = d.getMinutes() + s / 60, h = (d.getHours() % 12) + m / 60;
        clock.querySelector('.h').setAttribute('transform', 'rotate(' + (h * 30) + ' 50 50)');
        clock.querySelector('.mi').setAttribute('transform', 'rotate(' + (m * 6) + ' 50 50)');
        clock.querySelector('.se').setAttribute('transform', 'rotate(' + (s * 6) + ' 50 50)');
      }
      set();
      setInterval(set, 1000);
    })();
  </script>
"""


def render(p):
    return f"""<!doctype html>
<html lang="{p['lang']}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{p['title']}</title>
  <meta name="description" content="{p['description']}">
  <link rel="icon" href="assets/icon-64.png">
  <link rel="apple-touch-icon" href="assets/icon-256.png">
  <link rel="stylesheet" href="styles.css">
</head>
<body class="home">
  <header class="top">
    <a class="brand" href="{p['out']}"><img src="assets/icon-64.png" alt="">Memo Clock</a>
    <nav>
      {p['nav']}
    </nav>
  </header>

  <main>
    <section class="hero">
      <div class="hero-copy">
        <img class="hero-icon" src="assets/icon-256.png" alt="">
        <h1>{p['name']}</h1>
        <p class="line">{p['line']}</p>
        <a class="store" href="{STORE}">{p['store']}</a>
      </div>
      <div class="study">
{card_html(p['card'])}{grades_html(p['grades'])}      </div>
    </section>

    <section class="desk-section">
      <h2 class="section-title">{p['desk_title']}</h2>
      <div class="desk">
{desk_html(p['desk'])}      </div>
    </section>

    <section class="board-section">
      <h2 class="section-title">{p['board_title']}</h2>
      <div class="board">
{board_html(p['board'])}      </div>
    </section>

    <section class="does">
      <dl>
{features_html(p['features'])}      </dl>
    </section>
  </main>

  <footer class="foot">
    {p['foot']}
  </footer>
{CLOCK_SCRIPT}</body>
</html>
"""


def main():
    for p in PAGES.values():
        RING_IDS[0] = 0
        (ROOT / p["out"]).write_text(render(p), encoding="utf-8")
        print("wrote", p["out"])
    chars = "".join(sorted(HAND | set(chr(i) for i in range(32, 127)) | set("，。；：？！、“”‘’（）—–…·→")))
    (ROOT / "tools" / "hand-chars.txt").write_text(chars, encoding="utf-8")
    print("hand chars:", len(chars))


if __name__ == "__main__":
    main()
