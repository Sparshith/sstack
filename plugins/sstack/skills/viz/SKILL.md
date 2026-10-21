---
name: viz
description: House style for any chart, dashboard or report page with charts. Use before you write chart code, pick chart colours, or lay out a stat tile, hover or table. Charts explain themselves, the form fits the question, hovers are a key/value grid, pages are static inline SVG built by a Python script. Use together with the dataviz skill; where they conflict, this skill wins.
---

# Viz

Rules for every chart page. Start a new page from `assets/starter.py`: it holds the CSS, the hover script and the SVG helpers. Copy it and the font into the page folder, then replace the demo chart.

## 1. A chart explains itself

- Remove any sentence that explains how to read the chart ("Area = …", "Hover a tile for …"). If the chart needs one, change the chart.
- Leave out a legend when each mark carries its own label.
- Leave out methodology footnotes. Definitions go in the README or the report, not on the chart.
- Each mark shows one name and one number. Every other detail goes in the hover and the table.
- The header carries the context: the title on the left; n, the window and the source on the right (for example "277 orders · Oct 12 – Oct 18").

## 2. Choose the form for the question

Do not reuse one chart type for every question.

| Question | Form |
|---|---|
| Change over days | Vertical bars, one bar or a stack per day |
| Compare two series per day | Paired bars, same axis |
| One level of part-to-whole | One stacked bar, or sorted horizontal bars |
| Two levels of part-to-whole (group → item) | Treemap: a region per parent, tiles inside |
| A single headline number | A stat tile, not a chart |

- Use one y-axis only. Two measures with different scales get two charts.
- Mark events (deploys, releases) with a thin dashed vertical line and a short label.
- Mark missing data with a light grey band and one "no data" label. Never draw a gap as a zero bar.
- Repeated small horizontal-bar panels for a two-level breakdown look bad. Use the treemap.

## 3. Text and overflow

- Never cut a label with "…" when there is room to wrap. Wrap snake_case names after underscores (`wrap()` in the starter).
- If a mark is too small for a label, draw no label, and list it once under the chart ("Too small to draw: Setup 0.1¢ (0.4%)").
- Do not cram a tile with many lines of text. A tile shows a name and a number; the rest goes in the hover.
- Fold parts under about 4% of the total into one "N smaller items" mark, and list them in its hover. Never fold a single item; draw it as itself.
- Text uses ink colours, never the series colour.

## 4. Hover

- Every mark has a hover.
- The hover is a title plus a key/value grid, not a sentence. Example:

  ```
  step_name
  Per unit      15.8¢ · 49% of total
  Calls         6.1 per unit × 2.6¢
  Model         model-a
  Setting       default
  ```
- Dark box (#0D1117), white text, muted keys (#8C959F), 6px radius, soft shadow. Build it with DOM nodes and `textContent`, never with `innerHTML`. The starter does this: put `data-tip="<title>"` and `data-rows='[[key, value], …]'` on a mark.

## 5. Style

- Font: JetBrains Mono (local woff2 in `assets/`). Light theme only.
- Page #FAFBFC. Cards #FFFFFF with a 1px #D0D7DE border, 6px radius.
- Ink #0D1117, secondary text #57606A, grid #E5E9ED dashed 3/3, axis line #D0D7DE.
- Bars: thin, 4px rounded data end, 2px white gap between stacked segments.
- Tables sit under the chart, inside a closed `<details>`, with tabular numbers.

## 6. Colour

- Give each colour one meaning per page. If blue means "prod" in one chart, it cannot mean "input tokens" in the next.
- Use the validated categorical slots: `#2a78d6` blue, `#eb6834` orange, `#1baf7a` aqua, `#eda100` yellow, `#e87ba4` magenta, `#008300` green, `#6250d6` purple.
- Run the palette validator from the dataviz skill before you ship a new combination: `scripts/validate_palette.js "<hex,hex>" --mode light --surface "#FFFFFF"`. Fix every FAIL. A contrast WARN means every value must also appear in a label or the table.
- Treemap tiles use a light tint (about 80% toward white) of their parent's colour, with a 3px line of the full colour above the region.

## 7. Data honesty

- Bucket days in the timezone of the people whose work the data shows, not your own. Name the timezone in the header.
- Leave out partial days. Count unique entities (documents, orders, users), not events or calls.
- Name the data source in the header. If two sources disagree, say which one the chart uses.

## 8. Build and check

- A Python script (`build.py`) builds a static HTML page from saved data. Use inline SVG and no chart library. Rebuilding never calls a live API.
- Before you show a page, render it and look at it:

  ```sh
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
    --hide-scrollbars --window-size=1110,1000 --screenshot=/tmp/check.png "file://$PWD/index.html"
  ```

  Check it for overlapping labels, cut-off text, empty tiles and marks that are too thin to see.
