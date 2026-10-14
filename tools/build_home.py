"""Build index.html and index-en.html.

Everything on the page is drawn the way the app draws it:
- the desk objects after the design's objects.py (CSS over the paper, leather, linen and kraft
  textures in assets/tex);
- the 今天 widgets after the app's widget code (HomeWidgetChrome.swift and the Widgets folder),
  with the app's own illustration and radio SVG copied out by tools/extract_art.py into
  tools/widget-art.json;
- formulas as KaTeX output made once with the KaTeX the app ships (tools/home-formulas.json).

It also writes tools/hand-chars.txt, the characters set in the handwriting face, for the font
subset. Usage:

    python3 tools/build_home.py
"""
import json
import math
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEX = json.loads((ROOT / "tools" / "home-formulas.json").read_text(encoding="utf-8"))
ART = json.loads((ROOT / "tools" / "widget-art.json").read_text(encoding="utf-8"))

HAND = set()  # every string set in the handwriting face, for the font subset


def hand(text):
    HAND.update(text)
    return text


# ---------- Desk objects (after objects.py) ----------

NAVY = ("#2A3860", ("#141C33", "#24305A", "#43538A"), ("#6E2820", "#9C3B2F"))
BRICK = ("#8B3A2F", ("#4A1A14", "#6E2A21", "#A6564A"), ("#B5A27C", "#DCCBA6"))


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


def cloth_art(color, ribbon, dark=False):
    hl = "0.12" if dark else "0.4"
    return f"""              <span class="pages-r"></span><span class="pages-b"></span>
              <span class="ribbon" style="left: 54px; background: linear-gradient(90deg, {ribbon[0]}, {ribbon[1]} 50%, {ribbon[0]});"></span>
              <span class="cover linen" style="background-color: {color};"><span class="spine" style="background: linear-gradient(90deg, rgba(0,0,0,{0.28 if dark else 0.12}), rgba(0,0,0,0.03) 70%, rgba(0,0,0,0));"></span><span class="hinge" style="background: linear-gradient(90deg, rgba(0,0,0,{0.32 if dark else 0.16}), rgba(0,0,0,0.04) 40%, rgba(255,255,255,{hl}) 68%, rgba(255,255,255,0));"></span><span class="rim" style="box-shadow: inset 0 1px 0 rgba(255,255,255,{0.18 if dark else 0.5}), inset 0 -1px 0 rgba(0,0,0,{0.3 if dark else 0.14}), inset -1px 0 0 rgba(0,0,0,{0.2 if dark else 0.10});"></span></span>
"""


def exercise_art(color):
    spine = ('<span style="left: 0; top: 0; bottom: 0; width: 11px; background: linear-gradient(90deg, rgba(60,35,10,0.22), rgba(60,35,10,0.04));"></span>'
             '<span style="left: 11px; top: 0; bottom: 0; width: 1px; background: rgba(60,35,10,0.22);"></span>'
             '<span class="staple" style="top: 44px;"></span><span class="staple" style="top: 132px;"></span>')
    return f"""              <span class="pages-b" style="left: 6px; height: 4px; bottom: -4px;"></span>
              <span class="cover kraft thin" style="background-color: {color};">{spine}<span class="rim" style="box-shadow: inset 0 1px 0 rgba(255,255,255,0.22), inset 0 -1px 0 rgba(60,35,10,0.25);"></span></span>
"""


def spiral_art(color="#C9A97C"):
    coils = "".join(f'<span class="coil" style="top: {9 + i * 10.6:.1f}px;"></span>' for i in range(18))
    holes = "".join(f'<span class="hole" style="top: {9.5 + i * 10.6:.1f}px;"></span>' for i in range(18))
    return f"""              <span class="pages-r" style="top: 3px; bottom: 3px;"></span>
              <span class="cover kraft thin" style="background-color: {color};">{holes}<span class="rim" style="box-shadow: inset 0 1px 0 rgba(255,255,255,0.22), inset 0 -1px 0 rgba(60,35,10,0.25);"></span></span>
              <span style="left: 0; top: 0; bottom: 0; width: 16px;">{coils}</span>
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


def deck_art(edges):
    tones = ["#E6E2D8", "#F2EFE7", "#E9E6DC", "#F4F2EA", "#EAE7DE", "#F5F3EC", "#ECE9E0"]
    es = "".join(f'              <span class="edge" style="left: {1.5 * i + 0.5}px; top: {1.5 * i + 0.5}px; background: {tones[(7 - i) % 7]};"></span>\n'
                 for i in range(edges, 0, -1))
    h = 124 + int(1.5 * edges) + 4
    return h, f"""{es}              <span class="flash texpaper" style="left: 0; top: 0; background-color: #FBFAF5; box-shadow: 0 0 0 0.5px rgba(0,0,0,0.10);"><span class="flash rules" style="left: 0; top: 0;"></span></span>
              <span class="beltband kraftbelt" style="left: 140px; height: {h}px;"></span>
"""


def memo_art(rot=-1.5):
    return f"""              <span class="memo texpaper" style="left: 0; top: 0; transform: rotate({rot}deg);"><span class="memo-lines"></span><span class="ink" style="left: 18px; top: 46px; width: 64px;"></span><span class="ink" style="left: 18px; top: 64px; width: 104px; opacity: 0.6;"></span><span class="ink" style="left: 18px; top: 82px; width: 86px; opacity: 0.6;"></span><span class="memo-curl"></span></span>
              <span class="tape texpaper" style="left: 42px; top: -9px; transform: rotate(-5deg);"></span>
"""


def desk_item(item):
    kind, args = item[0], item[1:]
    if kind == "deck":
        edges, name, meta = args
        h, art = deck_art(edges)
        return obj(210, h, art, name, meta, " deck")
    if kind == "hardcover":
        (color, band, ribbon), name, meta = args
        return obj(150, 200, hardcover_art(color, band, ribbon), name, meta)
    if kind == "cloth":
        color, ribbon, name, meta = args
        return obj(150, 200, cloth_art(color, ribbon), name, meta)
    if kind == "exercise":
        color, name, meta = args
        return obj(150, 200, exercise_art(color), name, meta)
    if kind == "spiral":
        name, meta = args
        return obj(150, 200, spiral_art(), name, meta)
    if kind == "pdf":
        name, meta = args
        return obj(160, 220, pdf_art(), name, meta)
    if kind == "memo":
        name, meta, rot = args
        return obj(150, 150, memo_art(rot), name, meta, " note")
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
    "alarm": '<circle cx="8" cy="8.8" r="5.4"/><path d="M8 6v2.8l1.8 1.2M2.4 3.8 4.4 2M13.6 3.8 11.6 2M4.4 13.4 3.4 14.6M11.6 13.4l1 1.2"/>',
    "excl": '<circle cx="8" cy="8" r="6.3"/><path d="M8 4.6v4.2"/><circle cx="8" cy="11.3" r=".5" fill="currentColor"/>',
    "check": '<circle cx="8" cy="8" r="6.3"/><path d="m5.4 8.2 1.8 1.8 3.4-3.6"/>',
    "book": '<path d="M3.2 2.4h8.2a1.4 1.4 0 0 1 1.4 1.4v10H4.6a1.4 1.4 0 0 1-1.4-1.4Z"/><path d="M3.2 12.4a1.4 1.4 0 0 1 1.4-1.4h8.2M6 2.4v8.6"/>',
    "list": '<circle cx="3.2" cy="4.4" r=".6" fill="currentColor"/><circle cx="3.2" cy="8" r=".6" fill="currentColor"/><circle cx="3.2" cy="11.6" r=".6" fill="currentColor"/><path d="M6 4.4h7.6M6 8h7.6M6 11.6h7.6"/>',
    "arrow-right": '<path d="M3 8h10M9 4l4 4-4 4"/>',
    "retry": '<path d="M13 8a5 5 0 1 1-1.6-3.7"/><path d="M11.8 1.8v2.8H9"/>',
    "swap": '<path d="M2.6 5.4h10.4M10 2.4l3 3-3 3M13.4 10.6H3M6 7.6l-3 3 3 3"/>',
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


# ---------- Widgets ----------

def w_today_review(t):
    progress = 24 / 62
    left = (f'<div class="w-col">{header(t["today"], "clock")}{FILL}'
            f'<div class="w-figure"><span class="w-num" style="--s: 48px">38</span><span class="w-stack"><span>{t["cards"]}</span><span>{t["minutes12"]}</span></span></div>'
            f'{FILL}<div class="w-bar"><i style="width: {progress * 100:.0f}%"></i></div>'
            f'<span class="w-cap12 gap">{t["reviewed"]}</span></div>')
    right = (f'<div class="w-side"><div class="w-resume"><span class="w-cap12">{t["resume"]}</span><b>{t["deck1"]}</b><span class="w-mono12">{t["twelve"]}</span></div>'
             f'{FILL}<span class="w-btn">{t["continue"]}{icon("arrow-right", 12, 2)}</span></div>')
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
    axis = (f'<span style="left: {0.5 * slot:.2f}%">10/7</span>'
            f'<span class="b" style="left: {today_center:.2f}%">{t["todayAxis"]}</span>'
            f'<span style="left: {14.5 * slot:.2f}%">10/21</span>'
            f'<span style="left: {21.5 * slot:.2f}%">10/28</span>')
    cells = (f'<div class="w-cells"><div><span class="w-cap12">{t["tomorrow"]}</span>{value("23", t["cards"], 26, 12)}</div>'
             f'<span class="w-vrule"></span><div><span class="w-cap12">{t["in7"]}</span>{value("96", t["cards"], 26, 12)}</div>'
             f'<span class="w-vrule"></span><div><span class="w-cap12">{t["overdue"]}</span>{value("0", t["cards"], 26, 12)}</div></div>')
    inner = (f'{header(t["forecast"], "calendar", "10/7 – 10/28")}{cells}'
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


def upcoming_row(when, title, deck, formula):
    return (f'<div class="w-up"><span class="w-when">{when}</span><span class="w-up-t"><b>{title}</b><span class="w-cap11">{deck}</span></span>'
            f'<span class="w-up-f">{TEX[formula]}</span></div>')


def w_upcoming(t):
    rows = (upcoming_row(t["when1"], t["up1"], t["deck1"], "tangent_short") + '<span class="w-hrule"></span>'
            + upcoming_row(t["when2"], t["up2"], t["deck1"], "lhopital"))
    return widget("m", f'{header(t["upcoming"], "alarm", t["now"])}<div class="w-ups">{rows}</div>', "grid")


def w_forgotten(t):
    slips = ""
    for i, (title, formula) in enumerate(t["slips"]):
        rot, dx, dy = (-4, -4, -18) if i == 0 else (5, 8, 22)
        slips = (f'<div class="w-slip" style="transform: translate(calc(-50% + {dx}px), calc(-50% + {dy}px)) rotate({rot}deg)">'
                 f'<span class="w-cap11 lead">{title}</span><span class="w-slip-f">{TEX[formula]}</span></div>') + slips
    left = (f'<div class="w-col narrow">{header(t["forgot"], "excl", t["three"])}{FILL}'
            f'<div class="w-figure base"><span class="w-cap13 w-strong">{t["forgotWord"]}</span><span class="w-num red" style="--s: 48px">3</span><span class="w-cap13 w-strong">{t["cardUnit"]}</span></div>'
            f'{FILL}<span class="w-btn red">{icon("retry", 14, 1.8)}{t["retest"]}</span></div>')
    return widget("m", f'<div class="w-row">{left}<div class="w-slips">{slips}</div></div>', "red")


def w_accuracy(t):
    rates = [0.82, 0.9, 0.78, 0.88, 0.93, 0.85, 0.87]
    low = 0.6
    W, H = 100.0, 28.0
    px, py = 4, 5
    pw, ph = W - 2 * px, H - 2 * py
    pts = [(px + i / 6 * pw, py + (1 - (r - low) / (1 - low)) * ph) for i, r in enumerate(rates)]
    band_top = py + ph * (1 - 0.95) / (1 - low)
    band_bottom = py + ph * (1 - 0.85) / (1 - low)
    path = "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts)
    svg = (f'<svg class="w-rate-svg" viewBox="0 0 {W:.0f} {H:.0f}" preserveAspectRatio="none" aria-hidden="true">'
           f'<rect x="0" y="{band_top:.2f}" width="{W:.0f}" height="{band_bottom - band_top:.2f}" fill="#FFF4B8"/>'
           f'<path d="{path}" fill="none" stroke="#111317" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke"/></svg>')
    lx, ly = pts[-1]
    dot = f'<i class="w-rate-dot" style="left: {lx:.2f}%; top: {ly / H * 100:.2f}%"></i>'
    inner = (f'{header(t["accuracy"], "check", t["todayNote"])}{FILL}{value("87", "%", 56, 20)}'
             f'<div class="w-fill min6"></div><div class="w-rate">{svg}{dot}</div>')
    return widget("s", inner)


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
    total, current = 18, 7
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
             f'<div class="w-figure base tight">{pre}<span class="w-num" style="--s: 28px">7</span>{post}</div>'
             f'<span class="w-cap11">/ 18</span></div></div>')
    return widget("s", inner, extra=" opt")


def w_checklist(t):
    rows = "".join(f'<div class="w-todo"><i></i><span>{item}</span></div>' for item in t["todos"])
    inner = (f'{header(t["checklist"], "list")}<div class="w-figure base tight"><span class="w-num" style="--s: 56px">2</span><span class="w-num faint" style="--s: 20px">/5</span></div>'
             f'{FILL}{rows}')
    return widget("s", inner, "grid", " opt w-optional-4")


def w_note(t):
    lines = "".join(f'<span class="w-pin-line">{hand(line)}</span>' for line in t["noteLines"])
    inner = (f'<div class="w-pin"><div class="w-pin-paper texpaper"><span class="w-pin-title">{hand(t["noteTitle"])}</span>{lines}</div>'
             f'<span class="w-pin-tape texpaper"></span></div>')
    return widget("m", inner, "bare", label=t["noteLabel"])


def w_desk_deck(t):
    h, art = deck_art(7)
    inner = (f'<div class="w-entry"><div class="w-entry-obj deck" style="--w: 210px; --h: {h}px;"><div class="art" aria-hidden="true">{art}</div></div>'
             f'<span class="w-entry-cap"><b>{t["pinDeck"]}</b><i>{t["pinDeckMeta"]}</i></span></div>')
    return widget("s", inner, "bare")


def w_desk_notebook(t):
    color, band, ribbon = BRICK
    inner = (f'<div class="w-entry"><div class="w-entry-obj book" style="--w: 150px; --h: 200px;"><div class="art" aria-hidden="true">{hardcover_art(color, band, ribbon)}</div></div>'
             f'<span class="w-entry-cap"><b>{t["pinBook"]}</b><i>{t["pinBookMeta"]}</i></span></div>')
    return widget("s", inner, "bare")


def board_html(t):
    return "".join([
        w_today_review(t), w_streak(t), w_focus(t), w_forecast(t),
        w_radio(t), w_metrics(t), w_week(t),
        w_cat(t), w_countdown(t), w_upcoming(t), w_pomodoro(t), w_clock(t),
        w_forgotten(t), w_accuracy(t), w_hourglass(t), w_note(t),
        w_desk_deck(t), w_desk_notebook(t), w_lamp(t), w_semester(t), w_checklist(t), w_coffee(t),
    ])


# ---------- Words ----------

ZH_BOARD = {
    "today": "今天复习", "cards": "张", "minutes12": "约 12 分钟", "reviewed": "已复习 24 · 还剩 38",
    "resume": "上次没复习完", "deck1": "高等数学", "twelve": "12 张", "continue": "继续这组",
    "streak": "连续打卡", "days": "天", "focus": "今天专注", "of60": "/ 60 分钟",
    "forecast": "前后两周", "tomorrow": "明天", "in7": "七天内", "overdue": "积压", "week7": "七天内",
    "left38": "还剩 38", "todayAxis": "今天", "rebalance": "重新安排",
    "metrics": "今天的数字", "times": "次", "reviewToday": "今天复习", "correct": "答对", "min": "分钟", "longterm": "长期记住",
    "week": "近 7 天", "reviews": "次复习",
    "books": ["高等数学", "大学物理", "线性代数"], "dueLabel": "张到期", "catLabel": "睡猫：38 张到期",
    "ofGoal": "/ 60 分钟", "hourglassLabel": "沙漏：今天专注 42 / 60 分钟",
    "lamp1": "今天专注", "lamp2": "42 分钟", "lampLabel": "台灯书桌：今天专注 42 分钟",
    "coffeeLabel": "咖啡",
    "channels": ["白噪音", "粉噪音", "雨声", "海浪", "篝火", "咖啡馆", "图书馆", "钟摆"], "playing": "播放中",
    "exam": "期末考试", "left": "还有", "dayUnit": "天",
    "upcoming": "快到期", "now": "现在 14:05", "when1": "下午 4:20", "up1": "曲面切平面公式", "when2": "明天 09:30", "up2": "洛必达法则",
    "forgot": "今天忘了的", "three": "3 张", "forgotWord": "忘了", "cardUnit": "张", "retest": "再测一遍",
    "slips": [("分部积分", "parts"), ("拉格朗日乘数法", "lagrange")],
    "accuracy": "答对率", "todayNote": "今天",
    "pomodoro": "番茄钟", "focusing": "专注中",
    "clockLabel": "时钟",
    "semester": "学期进度", "weekPre": "第", "weekPost": "周",
    "checklist": "清单", "todos": ["整理错题本", "预习第 9 章"],
    "noteTitle": "期中考试", "noteLines": ["11 月 3 日 上午 9:00", "带计算器和学生证", "第 8–10 章再过一遍"], "noteLabel": "钉在今天页的备忘录：期中考试",
    "pinDeck": "大学物理", "pinDeckMeta": "52 张 · 今天 8", "pinBook": "考前冲刺", "pinBookMeta": "9 页",
}

EN_BOARD = {
    "today": "Today’s reviews", "cards": "cards", "minutes12": "about 12 min", "reviewed": "24 done · 38 to go",
    "resume": "Left unfinished", "deck1": "Calculus", "twelve": "12 cards", "continue": "Continue",
    "streak": "Streak", "days": "days", "focus": "Focus today", "of60": "/ 60 min",
    "forecast": "Two weeks", "tomorrow": "Tomorrow", "in7": "Next 7 days", "overdue": "Overdue", "week7": "Next 7 days",
    "left38": "38 left", "todayAxis": "Today", "rebalance": "Rebalance",
    "metrics": "Today in numbers", "times": "", "reviewToday": "reviews", "correct": "correct", "min": "min", "longterm": "long-term",
    "week": "Last 7 days", "reviews": "reviews",
    "books": ["Calculus", "Physics", "Lin. alg."], "dueLabel": "due", "catLabel": "Sleepy cat: 38 cards due",
    "ofGoal": "/ 60 min", "hourglassLabel": "Hourglass: 42 of 60 minutes of focus today",
    "lamp1": "Focus", "lamp2": "42 min", "lampLabel": "Desk lamp: 42 minutes of focus today",
    "coffeeLabel": "Coffee",
    "channels": ["White", "Pink", "Rain", "Waves", "Fire", "Café", "Library", "Clock"], "playing": "Playing",
    "exam": "Final exam", "left": "in", "dayUnit": "days",
    "upcoming": "Due soon", "now": "Now 14:05", "when1": "4:20 pm", "up1": "Tangent plane", "when2": "Tmrw 09:30", "up2": "L’Hôpital’s rule",
    "forgot": "Forgot today", "three": "3", "forgotWord": "Forgot", "cardUnit": "cards", "retest": "Test again",
    "slips": [("Integration by parts", "parts"), ("Lagrange multipliers", "lagrange")],
    "accuracy": "Accuracy", "todayNote": "Today",
    "pomodoro": "Pomodoro", "focusing": "Focusing",
    "clockLabel": "Clock",
    "semester": "Semester", "weekPre": "Wk", "weekPost": "",
    "checklist": "To do", "todos": ["Sort my mistakes", "Read ch. 9"],
    "noteTitle": "Midterm", "noteLines": ["Nov 3, 9:00 am", "Calculator and ID", "Go over ch. 8–10"], "noteLabel": "Note pinned to Today: Midterm",
    "pinDeck": "Physics", "pinDeckMeta": "52 cards · 8 today", "pinBook": "Exam sprint", "pinBookMeta": "9 pages",
}

PAGES = {
    "zh": {
        "out": "index.html",
        "lang": "zh-Hans",
        "title": "Memo Clock-记忆时钟",
        "description": "Memo Clock-记忆时钟：把公式、概念和例题记成卡片，到该复习的时候翻出来。打字、手写、拍照都能记，iCloud 同步，买断无内购。",
        "nav": '<a href="support.html">支持</a>\n      <a href="privacy.html">隐私政策</a>\n      <a href="index-en.html" lang="en" hreflang="en">English</a>',
        "name": "Memo Clock-记忆时钟",
        "line": "把公式、概念和例题记成卡片，到该复习的时候翻出来。",
        "card": {
            "title": "曲面切平面公式",
            "ask": "写出曲面切平面公式，并说明法线方向怎么找？",
            "legend": [("surface", "曲面"), ("point", "切点"), ("partials", "偏导数")],
            "why": "适用于显式曲面 {surface} 的切平面；法向量可取 {normal}。",
        },
        "grades": [("忘了", "本轮再来"), ("模糊", "明天"), ("记得", "2 天后"), ("熟练", "8 天后")],
        "desk_title": "卡片、手写笔记、PDF 和备忘录，摆在一张书桌上",
        "desk": [
            [("deck", 7, "高等数学", "86 张 · 今天 12"), ("deck", 5, "大学物理", "52 张 · 今天 8"), ("deck", 3, "线性代数", "31 张")],
            [("hardcover", NAVY, "多元微分课堂笔记", "12 页"), ("cloth", "#E4DFD2", ("#1B2645", "#2A3860"), "读书笔记", "20 页"),
             ("exercise", "#D2B48C", "错题本", "5 页"), ("spiral", "听课速记", "26 页"), ("pdf", "2024 真题", "23 页")],
            [("memo", "期中考试", "10月12日", -1.5), ("memo", "问老师", "10月13日", 1.2), ("memo", "实验报告要点", "10月14日", -0.6)],
        ],
        "board_title": "今天页：小组件大中小混排，想看什么放什么",
        "board": ZH_BOARD,
        "features": [
            ("记一条", "打字带公式，Apple Pencil 手写，拍照后框出要遮住的地方。"),
            ("复习", "翻开答案，按忘了、模糊、记得、熟练评分，记忆算法排好下次时间；也能默写、自测。"),
            ("今天", "几十个小组件自由摆放：今天复习、番茄钟、白噪音、倒数日、课程表。"),
            ("书桌", "抽认卡、手写笔记、PDF 和备忘录，一键排齐，或者随手摆。"),
            ("搜索", "手写和照片里的字在本机识别，一样搜得到。"),
            ("导入", "Anki 牌组连同复习进度一起导入；PDF 导入后直接在上面写。"),
            ("同步", "iCloud 同步 iPad 和 iPhone，桌面小组件随时看今天还剩几张。"),
            ("买断", "买一次全部能用，没有内购、订阅和广告。"),
        ],
        "foot": '<a href="support.html">支持</a>\n    <a href="privacy.html">隐私政策</a>\n    <a href="mailto:3528872473@qq.com">3528872473@qq.com</a>',
    },
    "en": {
        "out": "index-en.html",
        "lang": "en",
        "title": "Memo Clock",
        "description": "Memo Clock turns formulas, concepts and worked problems into cards and shows each one again when it is due. Type, write or photograph; iCloud sync; one price, no in-app purchases.",
        "nav": '<a href="support-en.html">Support</a>\n      <a href="privacy-en.html">Privacy</a>\n      <a href="index.html" lang="zh-Hans" hreflang="zh-Hans">中文</a>',
        "name": "Memo Clock",
        "line": "Turn formulas, concepts and worked problems into cards, and see each one again right when it is due.",
        "card": {
            "title": "Tangent plane",
            "ask": "Write the tangent plane to a surface. How do you find the normal?",
            "legend": [("surface", "surface"), ("point", "point of tangency"), ("partials", "partial derivatives")],
            "why": "For an explicit surface {surface}; a normal vector is {normal}.",
        },
        "grades": [("Forgot", "this round"), ("Vague", "tomorrow"), ("Remember", "in 2 days"), ("Mastered", "in 8 days")],
        "desk_title": "Cards, handwritten notebooks, PDFs and notes, all on one desk",
        "desk": [
            [("deck", 7, "Calculus", "86 cards · 12 today"), ("deck", 5, "Physics", "52 cards · 8 today"), ("deck", 3, "Linear algebra", "31 cards")],
            [("hardcover", NAVY, "Multivariable notes", "12 pages"), ("cloth", "#E4DFD2", ("#1B2645", "#2A3860"), "Reading notes", "20 pages"),
             ("exercise", "#D2B48C", "Mistakes", "5 pages"), ("spiral", "Lecture notes", "26 pages"), ("pdf", "2024 past paper", "23 pages")],
            [("memo", "Midterm", "Oct 12", -1.5), ("memo", "Ask the teacher", "Oct 13", 1.2), ("memo", "Lab report", "Oct 14", -0.6)],
        ],
        "board_title": "Today: widgets small, medium and large, laid out your way",
        "board": EN_BOARD,
        "features": [
            ("Capture", "Type with formulas, write with Apple Pencil, or take a photo and box what to hide."),
            ("Review", "Turn the card, grade it Forgot, Vague, Remember or Mastered, and a memory model schedules the next time. Write-from-memory and self-tests too."),
            ("Today", "Dozens of widgets to arrange: today’s reviews, a pomodoro timer, ambient sounds, countdowns, a timetable."),
            ("Desk", "Cards, handwritten notebooks, PDFs and notes, lined up in one tap or laid out freely."),
            ("Search", "Text in handwriting and photos is recognized on your device, so search finds it."),
            ("Import", "Bring in Anki decks with their review history; write straight onto imported PDFs."),
            ("Sync", "iCloud keeps iPad and iPhone in step; Home Screen widgets show how many cards are left today."),
            ("One price", "Buy once and get everything: no in-app purchases, subscriptions or ads."),
        ],
        "foot": '<a href="support-en.html">Support</a>\n    <a href="privacy-en.html">Privacy</a>\n    <a href="mailto:3528872473@qq.com">3528872473@qq.com</a>',
    },
}


def card_html(card):
    legend = "".join(
        f'            <span class="sym">{TEX[key]}</span><span class="mean">{hand(mean)}</span>\n'
        for key, mean in card["legend"]
    )
    hand(card["why"].replace("{surface}", "").replace("{normal}", ""))
    why = card["why"].format(**TEX)
    return f"""        <div class="pile">
          <div class="cardback sheet">
            <p class="title">{hand(card['title'])}</p>
            <p class="ask">{hand(card['ask'])}</p>
            <div class="answer"><div class="wide">{TEX['main']}</div><div class="narrow">{TEX['main_narrow']}</div></div>
            <div class="legend">
{legend}            </div>
            <p class="why">{why}</p>
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
  <link rel="stylesheet" href="assets/katex/katex.min.css">
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
        (ROOT / p["out"]).write_text(render(p), encoding="utf-8")
        print("wrote", p["out"])
    chars = "".join(sorted(HAND | set(chr(i) for i in range(32, 127)) | set("，。；：？！、“”‘’（）—–…·")))
    (ROOT / "tools" / "hand-chars.txt").write_text(chars, encoding="utf-8")
    print("hand chars:", len(chars))


if __name__ == "__main__":
    main()
