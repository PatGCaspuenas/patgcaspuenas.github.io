# Editing the site content

All the text on the site lives in this folder. Edit a file, then run the
build from the project root:

```bash
python3 build.py
```

That rewrites the marked regions of `index.html`. Everything else in
`index.html` (layout, styles, the sidebar identity block) stays untouched,
so you can still hand-edit the page as before.

| File | What it controls |
| --- | --- |
| `about.py` | The paragraphs of the **About** section |
| `projects.py` | The **Research** tabs and the projects inside each one |
| `news.py` | The **News** items in the sidebar |

Each file has instructions and examples at the top.

## Quick recipes

**Add a news item** — put a line anywhere in `NEWS` (it is sorted newest-first
for you):

```python
{"date": "2026-10-02", "text": "Paper accepted in *JFM*."},
```

**Add a project** — copy an existing block inside the tab you want:

```python
{
    "title":   "Learning ROMs for turbulent wakes",
    "authors": "**P. García Caspueñas**, A. Coauthor, B. Coauthor",
    "year":    2026,
    "tags":    ["POD", "Deep learning", "Wakes"],
    "image":   "images/wake.png",
    "image_width": "70%",          # optional: "60%", 420, "420px"
    "image_position": "left",      # optional: "above" (default), "left", "right"
    "image_frame": True,           # optional: thin border around the figure, off by default
    "summary": "What the work does and what the key contributions are.",
    "links": [
        {"label": "Paper", "url": "docs/wake.pdf", "icon": "paper"},
        {"label": "Code",  "url": "https://github.com/...", "icon": "code"},
    ],
},
```

The card renders in this order:

    title  →  authors · year  →  tags  →  figure  →  summary  →  link buttons

Set `"image_position": "left"` (or `"right"`) and the figure moves into a
column beside the summary instead:

    title  →  authors · year  →  tags  →  [ figure | summary + buttons ]

Every field except `title` is optional — leave one out and that row simply
disappears. For a project with no code release, drop the `Code` line from
`links`; drop `links` altogether for no buttons at all.

The figure spans the card by default. Set `image_width` or `image_height` to
size it — give one and the other follows the aspect ratio — and a figure
narrower than the card is centred. In a side-by-side layout `image_width`
sizes the figure *column* (capped at 70%, so the text always keeps room), and
on phones the two columns stack with the figure on top.

`.png`, `.jpg`, `.svg`, `.gif` and `.webp` are used as they are. A `.pdf`
figure is **converted for you**: `build.py` writes an `.svg` beside the
original and links that instead, re-converting only when the PDF changes.
Because the result is still vector, the figure stays perfectly sharp at any
size and on a retina screen. (If the file is secretly an SVG with a `.pdf`
name, it is simply copied to `.svg`.) Commit the generated file along with
the PDF — GitHub Pages serves what is in the repository.

Conversion prefers `pdftocairo` or Inkscape for vector output and falls back
to a 300 dpi PNG via `pdftoppm`, ImageMagick or `sips` if neither is
installed. To force a fresh conversion, delete the generated file and run
`python3 build.py` again. Wrap your own name in `** **` so it reads bold in the author
list. `authors` also accepts a list of names.

**Bullet lists in a summary** — pass a list for `summary`: a string in it is a
paragraph, a nested list is a bullet list.

```python
"summary": [
    "What the work does, in two or three sentences.",
    ["Key contribution one",
     "Key contribution two"],
],
```

The same works for `ABOUT` in `about.py`.

**Add a research tab** — copy a whole `{...}` topic block in `TABS`. The tab
button, its panel and the ids that wire them together are generated.

## Formatting

Anywhere you write text you can use `**bold**`, `*italic*` and
`[link text](https://example.com)`. Accents, quotes and `&` are handled
automatically — write them normally.

## Before pushing

```bash
python3 build.py --check
```

exits with an error if `index.html` is out of date with respect to these files.
