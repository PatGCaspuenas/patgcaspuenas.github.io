#!/usr/bin/env python3
"""Render index.html from the plain-Python content files in content/.

    python3 build.py            rewrite index.html in place
    python3 build.py --check    report whether index.html is up to date

Only the regions between the `<!-- content:NAME START -->` and
`<!-- content:NAME END -->` markers are touched; everything else in
index.html stays exactly as you wrote it.

Nothing outside the standard library is needed.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
CONTENT = ROOT / "content"

# Friendly names for the Font Awesome glyphs used on project link buttons.
ICONS = {
    "paper": "fa-regular fa-file-lines",
    "code": "fa-brands fa-github",
    "slides": "fa-solid fa-display",
    "poster": "fa-solid fa-image",
    "video": "fa-brands fa-youtube",
    "data": "fa-solid fa-database",
    "web": "fa-solid fa-link",
    "doi": "fa-brands fa-orcid",
}

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Browsers cannot draw a PDF inside <img>, so a PDF figure is converted to a
# file they can draw. Vector conversion (PDF -> SVG) is tried first: it stays
# sharp at any size and on any screen. Rasterising to PNG is the fallback.
#
# Each converter is (name, suffix, probe, argv-builder). `out` is the target
# file, `stem` the same path without the extension (pdftoppm appends its own).
# A PDF that is really a wrapper around a bitmap (a figure exported from a
# plotting tool as an image) is flattened to PNG at the bitmap's own
# resolution: converting it to SVG would wrap it in an SVG filter, which
# browsers rasterise at their own resolution and which makes soft-mask edges
# show up as faint outlines. A genuinely vector PDF becomes SVG and stays
# sharp at any size.
PDF_DPI = 300          # floor for flattening
PDF_DPI_MAX = 600      # ceiling, to keep files sane

CONVERTERS = [
    ("pdftocairo", ".svg", lambda: shutil.which("pdftocairo"),
     lambda src, out, stem, dpi: [shutil.which("pdftocairo"), "-svg",
                                  str(src), str(out)]),
    ("inkscape", ".svg", lambda: _inkscape(),
     lambda src, out, stem, dpi: [_inkscape(), str(src), "--export-type=svg",
                                  "--export-plain-svg", "-o", str(out)]),
    ("pdftoppm", ".png", lambda: shutil.which("pdftoppm"),
     lambda src, out, stem, dpi: [shutil.which("pdftoppm"), "-png", "-r", str(dpi),
                                  "-singlefile", str(src), str(stem)]),
    ("inkscape", ".png", lambda: _inkscape(),
     lambda src, out, stem, dpi: [_inkscape(), str(src), "--export-type=png",
                                  f"--export-dpi={dpi}",
                                  "--export-background=#ffffff",
                                  "--export-background-opacity=1", "-o", str(out)]),
    ("magick", ".png", lambda: shutil.which("magick"),
     lambda src, out, stem, dpi: [shutil.which("magick"), "-density", str(dpi),
                                  "-background", "white", "-flatten",
                                  f"{src}[0]", str(out)]),
    ("sips", ".png", lambda: shutil.which("sips"),
     lambda src, out, stem, dpi: [shutil.which("sips"), "-s", "format", "png",
                                  str(src), "--out", str(out)]),
]


def embedded_bitmap_dpi(src: Path) -> int | None:
    """Resolution of the bitmaps inside a PDF, or None if it is pure vector.

    Needs `pdfimages` (poppler); without it we assume vector, which is the
    safe guess for a figure exported from a plotting library.
    """
    tool = shutil.which("pdfimages")
    if not tool:
        return None
    try:
        listing = subprocess.run([tool, "-list", str(src)],
                                 check=True, capture_output=True, text=True).stdout
    except subprocess.CalledProcessError:
        return None

    ppi = []
    for line in listing.splitlines()[2:]:
        parts = line.split()
        # columns: page num type width height color comp bpc enc interp obj x-ppi y-ppi ...
        if len(parts) >= 14 and parts[2] in ("image", "smask"):
            try:
                ppi += [int(parts[12]), int(parts[13])]
            except ValueError:
                continue
    ppi = [v for v in ppi if v > 0]
    return max(ppi) if ppi else None


def whiten(path: Path) -> Path:
    """Paint a white page behind a generated SVG.

    PDF figures usually have a transparent background. On the white project
    card that is invisible, but it bites the moment the figure is opened on
    its own or put on a tinted panel - so the background is made explicit.
    Safe to call repeatedly: the rectangle is tagged and only added once.
    """
    if path.suffix.lower() != ".svg":
        return path
    svg = path.read_text(encoding="utf-8", errors="surrogateescape")
    if 'id="page-background"' in svg:
        return path
    opening = re.search(r"<svg\b[^>]*?>", svg)
    if not opening:
        return path
    rect = ('<rect id="page-background" x="0" y="0" '
            'width="100%" height="100%" fill="#ffffff"/>')
    path.write_text(svg[:opening.end()] + "\n" + rect + svg[opening.end():],
                    encoding="utf-8", errors="surrogateescape")
    return path


def _inkscape() -> str | None:
    found = shutil.which("inkscape")
    if found:
        return found
    app = Path("/Applications/Inkscape.app/Contents/MacOS/inkscape")
    return str(app) if app.exists() else None


def rasterise(rel: str) -> str:
    """Return a browser-displayable path for an image, converting PDF if needed.

    The converted file is written next to the PDF and reused until the PDF
    changes, so it is a normal file you commit alongside the rest of the site.
    """
    src = ROOT / rel
    if src.suffix.lower() != ".pdf":
        return rel
    if not src.exists():
        print(f"  ! figure not found: {rel}")
        return rel

    # Some "PDF" exports are really SVG. Browsers draw SVG natively, so just
    # give the file the extension it deserves.
    head = src.open("rb").read(1024)
    if not head.startswith(b"%PDF"):
        if b"<svg" in head or head.lstrip().startswith(b"<?xml"):
            out = src.with_suffix(".svg")
            if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
                shutil.copyfile(src, out)
                print(f"  copied {rel} -> {out.relative_to(ROOT)} (it is SVG, not PDF)")
            return str(whiten(out).relative_to(ROOT))
        print(f"  ! {rel} is neither a PDF nor an SVG")
        return rel

    # A PDF built around a bitmap is flattened; a vector one becomes SVG.
    bitmap_dpi = embedded_bitmap_dpi(src)
    if bitmap_dpi:
        want, dpi = ".png", min(max(bitmap_dpi, PDF_DPI), PDF_DPI_MAX)
    else:
        want, dpi = ".svg", PDF_DPI

    out = src.with_suffix(want)
    if out.exists() and out.stat().st_mtime >= src.stat().st_mtime:
        return str(whiten(out).relative_to(ROOT))

    for name, suffix, probe, argv in CONVERTERS:
        if suffix != want or not probe():
            continue
        try:
            subprocess.run(argv(src, out, src.with_suffix(""), dpi),
                           check=True, capture_output=True)
        except subprocess.CalledProcessError:
            continue
        if not out.exists() or out.stat().st_size == 0:
            continue
        whiten(out)
        how = "vector" if want == ".svg" else f"flattened at {dpi} dpi"
        print(f"  converted {rel} -> {out.relative_to(ROOT)} ({name}, {how})")

        stale = src.with_suffix(".png" if want == ".svg" else ".svg")
        if stale.exists():
            print(f"    note: {stale.relative_to(ROOT)} is no longer used "
                  f"and can be deleted")
        return str(out.relative_to(ROOT))

    print(f"  ! could not convert {rel} - install poppler (brew install "
          f"poppler) or export the figure as SVG or PNG yourself")
    return rel


# ------------------------------------------------------------------ helpers
def load(module: str) -> dict:
    """Import content/<module>.py without needing it to be a package."""
    import importlib.util

    path = CONTENT / f"{module}.py"
    if not path.exists():
        raise SystemExit(f"missing content file: {path.relative_to(ROOT)}")
    spec = importlib.util.spec_from_file_location(f"content_{module}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return vars(mod)


def text(raw: str) -> str:
    """Escape a content string, then apply the small inline markup."""
    out = html.escape(" ".join(str(raw).split()), quote=False)
    out = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                 lambda m: '<a href="%s" target="_blank" rel="noopener">%s</a>'
                           % (html.escape(m.group(2), quote=True), m.group(1)),
                 out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", out)
    return out


def url(raw: str) -> str:
    """Escape a path/URL, percent-encoding spaces in local paths."""
    raw = str(raw).strip()
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:|^[#/]", raw):
        raw = quote(raw, safe="/.-_~()")
    return html.escape(raw, quote=True)


def length(raw) -> str:
    """Turn 420, "420" or "60%" into a CSS length."""
    raw = str(raw).strip()
    return raw if re.search(r"[a-z%)]$", raw, re.I) else raw + "px"


def slug(raw: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", str(raw).lower()).strip("-")
    return out or "topic"


def indent(lines: list[str], pad: str) -> str:
    return "\n".join(pad + ln if ln else "" for ln in lines)


# ------------------------------------------------------------------ renderers
def blocks(body, pad: str = "", bullet_class: str = "bullets") -> list[str]:
    """Render a body of text.

    A string becomes one paragraph. A list may mix strings (paragraphs) and
    nested lists (bullet lists), so a summary can read:

        ["Intro paragraph.", ["First point", "Second point"], "Closing."]
    """
    if isinstance(body, str):
        body = [body]

    lines = []
    for item in body:
        if isinstance(item, (list, tuple)):
            lines.append('%s<ul class="%s">' % (pad, bullet_class))
            for point in item:
                lines.append("%s  <li>%s</li>" % (pad, text(point)))
            lines.append("%s</ul>" % pad)
        else:
            lines += ["%s<p>" % pad, "%s  %s" % (pad, text(item)), "%s</p>" % pad]
    return lines


def render_about(data: dict) -> str:
    return indent(blocks(data["ABOUT"], bullet_class="about-bullets"), "      ")


def render_news(data: dict) -> str:
    items = []
    for item in data["NEWS"]:
        date = item["date"]
        if isinstance(date, str):
            date = _dt.date.fromisoformat(date.strip())
        items.append((date, item["text"]))
    items.sort(key=lambda it: it[0], reverse=True)

    lines = []
    for date, body in items:
        lines += [
            "<li>",
            '  <span class="news-date">',
            '    <span class="month">%s</span>'
            '<span class="day">%d</span>'
            '<span class="year">%d</span>' % (MONTHS[date.month - 1], date.day, date.year),
            "  </span>",
            '  <span class="news-text">%s</span>' % text(body),
            "</li>",
        ]
    return indent(lines, "          ")


def render_research(data: dict) -> str:
    tabs = data["TABS"]
    if not tabs:
        raise SystemExit("content/projects.py: TABS is empty")

    ids, seen = [], {}
    for tab in tabs:
        base = slug(tab["label"])
        seen[base] = seen.get(base, 0) + 1
        ids.append(base if seen[base] == 1 else f"{base}-{seen[base]}")

    lines = ['<div class="tabs" role="tablist" aria-label="Research topics">']
    for i, (tab, tid) in enumerate(zip(tabs, ids)):
        active = i == 0
        lines.append(
            '  <button class="tab%s" role="tab" aria-selected="%s"'
            ' aria-controls="panel-%s" id="tab-%s">%s</button>'
            % (" is-active" if active else "", "true" if active else "false",
               tid, tid, text(tab["label"]))
        )
    lines.append("</div>")

    for i, (tab, tid) in enumerate(zip(tabs, ids)):
        active = i == 0
        lines += [
            "",
            '<div class="panel%s" id="panel-%s" role="tabpanel"'
            ' aria-labelledby="tab-%s"%s>'
            % (" is-active" if active else "", tid, tid, "" if active else " hidden"),
        ]
        for project in tab.get("projects", []):
            lines += ["", *render_project(project)]
        lines += ["", "</div>"]

    return indent(lines, "      ")


def render_figure(project: dict, pad: str, side: bool) -> list[str]:
    """The figure block. `side` means it shares a row with the text."""
    image = rasterise(str(project["image"]))
    alt = project.get("alt") or f"Figure for {project['title']}"
    width = project.get("image_width")
    height = project.get("image_height")

    # Stacked, the width sizes the image. Side by side, it sizes the column.
    figure_style = img_style = ""
    if side and width:
        # Side by side the width sets the figure column, capped so the text
        # column never gets squeezed out of existence.
        w = length(width)
        figure_style = ' style="flex: 0 1 %s; max-width: min(%s, 70%%)"' % (w, w)
    if height or (width and not side):
        img_style = ' style="%s"' % "; ".join([
            "width: " + (length(width) if width and not side else "auto"),
            "height: " + (length(height) if height else "auto"),
        ])

    framed = " is-framed" if project.get("image_frame") else ""
    return [
        '%s<figure class="entry-figure%s"%s>' % (pad, framed, figure_style),
        '%s  <img src="%s" alt="%s"%s>'
        % (pad, url(image), html.escape(alt, quote=True), img_style),
        "%s</figure>" % pad,
    ]


def render_body(project: dict, pad: str) -> list[str]:
    """Summary paragraphs/bullets followed by the link buttons."""
    lines = []

    summary = project.get("summary", project.get("abstract"))
    if summary:
        lines += [ln.replace("<p>", '<p class="abstract">', 1)
                  for ln in blocks(summary, pad, "entry-points")]

    links = project.get("links") or []
    if links:
        lines.append('%s<p class="entry-links">' % pad)
        for link in links:
            icon = ICONS.get(link.get("icon", "paper"), link.get("icon", ICONS["paper"]))
            lines.append(
                '%s  <a href="%s" target="_blank" rel="noopener">'
                '<i class="%s"></i> %s</a>'
                % (pad, url(link["url"]), html.escape(icon, quote=True), text(link["label"]))
            )
        lines.append("%s</p>" % pad)

    return lines


def render_project(project: dict) -> list[str]:
    lines = ['  <article class="entry">',
             '    <div class="entry-body">',
             "      <h3>%s</h3>" % text(project["title"])]

    # byline: authors, then the year
    authors = project.get("authors")
    if isinstance(authors, (list, tuple)):
        authors = ", ".join(str(a) for a in authors)
    year = project.get("year")
    if authors or year:
        lines.append('      <p class="entry-meta">')
        if authors:
            lines.append('        <span class="entry-authors">%s</span>' % text(authors))
        if year:
            lines.append('        <span class="entry-year">%s</span>' % text(year))
        lines.append("      </p>")

    # tags sit above the figure
    tags = project.get("tags") or []
    if tags:
        lines.append('      <ul class="entry-tags">')
        for tag in tags:
            lines.append("        <li>%s</li>" % text(tag))
        lines.append("      </ul>")

    position = str(project.get("image_position", "above")).lower().strip()
    if position in ("side", "beside", "next"):
        position = "left"
    side = position in ("left", "right") and project.get("image")

    if not project.get("image"):
        lines += render_body(project, "      ")
    elif side:
        lines.append('      <div class="entry-split entry-split--%s">' % position)
        lines += render_figure(project, "        ", True)
        lines.append('        <div class="entry-text">')
        lines += render_body(project, "          ")
        lines.append("        </div>")
        lines.append("      </div>")
    else:
        lines += render_figure(project, "      ", False)
        lines += render_body(project, "      ")

    lines += ["    </div>", "  </article>"]
    return lines


def stamp_stylesheet(page: str) -> str:
    """Tag the stylesheet link with a hash of its contents.

    Browsers cache CSS hard - without this, editing styles.css and reloading
    can keep showing the old design. The tag changes only when the file does.
    """
    css = ROOT / "styles.css"
    if not css.exists():
        return page
    digest = hashlib.sha1(css.read_bytes()).hexdigest()[:8]
    return re.sub(r'href="styles\.css(?:\?v=[0-9a-f]+)?"',
                  'href="styles.css?v=%s"' % digest, page, count=1)


# ------------------------------------------------------------------ splicing
def splice(page: str, name: str, body: str) -> str:
    pattern = re.compile(
        r"(<!--\s*content:%s START.*?-->\n)(.*?)(\n[ \t]*<!--\s*content:%s END\s*-->)"
        % (re.escape(name), re.escape(name)),
        re.DOTALL,
    )
    if not pattern.search(page):
        raise SystemExit(
            f"index.html has no <!-- content:{name} START --> / END markers"
        )
    return pattern.sub(lambda m: m.group(1) + body + m.group(3), page, count=1)


def main(argv: list[str]) -> int:
    check_only = "--check" in argv

    page = INDEX.read_text(encoding="utf-8")
    updated = page
    updated = splice(updated, "about", render_about(load("about")))
    updated = splice(updated, "research", render_research(load("projects")))
    updated = splice(updated, "news", render_news(load("news")))
    updated = stamp_stylesheet(updated)

    if updated == page:
        print("index.html is already up to date.")
        return 0
    if check_only:
        print("index.html is OUT OF DATE - run: python3 build.py")
        return 1

    INDEX.write_text(updated, encoding="utf-8")
    print("index.html updated from content/about.py, projects.py, news.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
