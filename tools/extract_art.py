"""Copy the drawings the home page's widget board uses out of the app's source.

The illustrations (猫, 沙漏, 台灯, 咖啡) and the radio are SVG kept as strings in the app
(IllustrationWidgets.swift, PlayerWidgets.swift). This reads them as they are and writes
tools/widget-art.json, so the page shows the app's own drawings. Usage:

    python3 tools/extract_art.py <MemoryClockApp/UI/HomeBoard/Widgets>
"""
import json
import pathlib
import re
import sys

WANTED = {
    "IllustrationWidgets.swift": [
        "catS", "catCSS", "deskS", "deskCSS", "coffeeS", "coffeeCSS",
        "hourglassCSS", "hourglassBackPart", "hourglassDotsPart", "hourglassFrontPart", "hourglassTagPart",
    ],
    "PlayerWidgets.swift": ["radioMedium", "radioCSS", "radioBand"],
}


def strings(source):
    found = {}
    for m in re.finditer(r'static let (\w+) = #"""\n(.*?)\n"""#', source, re.S):
        found[m.group(1)] = m.group(2)
    return found


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    folder = pathlib.Path(sys.argv[1])
    out = {}
    for name, keys in WANTED.items():
        found = strings((folder / name).read_text(encoding="utf-8"))
        for key in keys:
            out[key] = found[key]
    target = pathlib.Path(__file__).resolve().parent / "widget-art.json"
    target.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", target.name, sorted(out))


if __name__ == "__main__":
    main()
