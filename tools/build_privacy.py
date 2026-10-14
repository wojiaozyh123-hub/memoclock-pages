"""Build privacy.html / privacy-en.html from the policy Markdown.

The Markdown is the one source: the app shows the same text (AppLegal.swift), so the web page
is generated from it rather than edited by hand. Usage:

    python3 tools/build_privacy.py <privacy-zh.md> <privacy-en.md>

Only the Markdown this policy uses is understood: "# " title, "## " headings, "- " list items
and plain paragraphs. Nothing in the wording is changed; a list item's lead-in before the first
colon is set in bold, and the email address becomes a mail link.
"""
import html
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
EMAIL = "3528872473@qq.com"

PAGES = {
    "zh": {
        "out": "privacy.html",
        "lang": "zh-Hans",
        "title": "隐私政策 · Memo Clock-记忆时钟",
        "description": "Memo Clock-记忆时钟 2.0 保存哪些数据、存在哪里、怎么删除。",
        "nav": [("support.html", "支持", None), ("privacy.html", "隐私政策", "page"), ("privacy-en.html", "English", "en")],
        "home": "index.html",
        "colon": "：",
        "max_label": 12,
    },
    "en": {
        "out": "privacy-en.html",
        "lang": "en",
        "title": "Privacy Policy · Memo Clock",
        "description": "What Memo Clock 2.0 stores, where it is kept, and how to delete it.",
        "nav": [("support-en.html", "Support", None), ("privacy-en.html", "Privacy", "page"), ("privacy.html", "中文", "zh-Hans")],
        "home": "index-en.html",
        "colon": ": ",
        "max_label": 40,
    },
}


def inline(text):
    out = html.escape(text, quote=False)
    return out.replace(EMAIL, f'<a href="mailto:{EMAIL}">{EMAIL}</a>')


def list_item(text, page):
    colon = page["colon"]
    head, sep, rest = text.partition(colon)
    if sep and 0 < len(head) <= page["max_label"]:
        return f"<li><strong>{inline(head)}</strong>{inline(sep + rest)}</li>"
    return f"<li>{inline(text)}</li>"


def body(markdown, page):
    lines = markdown.strip().splitlines()
    parts = []
    in_list = False
    after_title = False
    for raw in lines:
        line = raw.rstrip()
        if line.startswith("- "):
            if not in_list:
                parts.append("<ul>")
                in_list = True
            parts.append("  " + list_item(line[2:], page))
            continue
        if in_list:
            parts.append("</ul>")
            in_list = False
        if not line:
            continue
        if line.startswith("## "):
            parts.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("# "):
            parts.append(f"<h1>{inline(line[2:])}</h1>")
            after_title = True
            continue
        elif after_title:
            parts.append(f'<p class="updated">{inline(line)}</p>')
        else:
            parts.append(f"<p>{inline(line)}</p>")
        after_title = False
    if in_list:
        parts.append("</ul>")
    return "\n".join("      " + p for p in parts)


def nav(page):
    links = []
    for href, label, kind in page["nav"]:
        if kind == "page":
            links.append(f'<a href="{href}" aria-current="page">{label}</a>')
        elif kind:
            links.append(f'<a href="{href}" lang="{kind}" hreflang="{kind}">{label}</a>')
        else:
            links.append(f'<a href="{href}">{label}</a>')
    return "\n".join("      " + l for l in links)


def render(markdown, page):
    return f"""<!doctype html>
<html lang="{page['lang']}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{page['title']}</title>
  <meta name="description" content="{page['description']}">
  <link rel="icon" href="assets/icon-64.png">
  <link rel="apple-touch-icon" href="assets/icon-256.png">
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <header class="top">
    <a class="brand" href="{page['home']}"><img src="assets/icon-64.png" alt="">Memo Clock</a>
    <nav>
{nav(page)}
    </nav>
  </header>

  <main>
    <article class="policy sheet">
{body(markdown, page)}
    </article>
  </main>
</body>
</html>
"""


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    for key, path in (("zh", sys.argv[1]), ("en", sys.argv[2])):
        page = PAGES[key]
        markdown = pathlib.Path(path).read_text(encoding="utf-8")
        (ROOT / page["out"]).write_text(render(markdown, page), encoding="utf-8")
        print("wrote", page["out"])


if __name__ == "__main__":
    main()
