import json
import math
import random
import re
from datetime import date, timedelta
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SLOTS = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#6250d6']
X0, X1, Y0, Y1 = 58, 928, 38, 330


def money(v):
    return f'${v:,.0f}' if v >= 10 or v == int(v) else f'${v:,.2f}'


def nice_top(v, ticks=4):
    step = 10 ** math.floor(math.log10(v / ticks))
    return ticks * next(step * m for m in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10) if step * m * ticks >= v)


def tip(title, rows):
    return f'data-tip="{escape(title)}" data-rows="{escape(json.dumps(rows))}"'


def top_rounded(x, y, w, h, r=4):
    r = min(r, h, w / 2)
    return f'M{x:.1f} {y + h:.1f}V{y + r:.1f}Q{x:.1f} {y:.1f} {x + r:.1f} {y:.1f}H{x + w - r:.1f}Q{x + w:.1f} {y:.1f} {x + w:.1f} {y + r:.1f}V{y + h:.1f}Z'


def y_axis(top, fmt, ticks=4):
    out = []
    for i in range(ticks + 1):
        y = Y1 - (Y1 - Y0) * i / ticks
        out.append(f'<line class="grid" x1="{X0}" x2="{X1}" y1="{y:.1f}" y2="{y:.1f}"/>'
                   f'<text class="axis" x="{X0 - 14}" y="{y + 4:.1f}" text-anchor="end">{fmt(top * i / ticks)}</text>')
    return ''.join(out)


def tint(hex_color, amount):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return '#' + ''.join(f'{round(c + (255 - c) * amount):02x}' for c in (r, g, b))


def squarify(values, x, y, w, h):
    """Squarified treemap (Bruls et al.): one (x, y, w, h) per value, in input order (values sorted desc)."""
    rects, total = [], sum(values)
    values = [v * w * h / total for v in values]
    i = 0
    while i < len(values):
        side = min(w, h)
        row, j = [values[i]], i + 1
        def worst(r):
            s = sum(r)
            return max(max(v * side * side / (s * s), s * s / (v * side * side)) for v in r)
        while j < len(values) and worst(row + [values[j]]) <= worst(row):
            row.append(values[j])
            j += 1
        s = sum(row)
        if w >= h:
            rw, cy = s / h, y
            for v in row:
                rects.append((x, cy, rw, v / rw))
                cy += v / rw
            x, w = x + rw, w - rw
        else:
            rh, cx = s / w, x
            for v in row:
                rects.append((cx, y, v / rh, rh))
                cx += v / rh
            y, h = y + rh, h - rh
        i = j
    return rects


def wrap(name, width, char=7.3):
    """Break a snake_case name after underscores so each line fits; split a word only if it alone is too long."""
    room, lines = max(int(width / char), 4), ['']
    for part in re.findall(r'[^_\s]*_|\S+\s*', name):
        if len(lines[-1]) + len(part.rstrip()) > room and lines[-1]:
            lines.append('')
        lines[-1] += part
    return [chunk for line in lines for chunk in (line.rstrip()[i:i + room] for i in range(0, len(line.rstrip()), room))]


def daily_bars(days, series, values, events=(), missing=()):
    slot = (X1 - X0) / len(days)
    top = nice_top(max(sum(values[d].values()) for d in days if d not in missing))
    scale = (Y1 - Y0) / top
    out = [y_axis(top, money)]
    for i, d in enumerate(days):
        x = X0 + slot * i
        if d in missing:
            out.append(f'<rect class="gap" x="{x:.1f}" y="{Y0}" width="{slot:.1f}" height="{Y1 - Y0}"/>')
            continue
        y, w = Y1, slot * .55
        stack = [(k, c, values[d][k]) for k, _, c in series if values[d][k]]
        for n, (k, c, v) in enumerate(stack):
            h = v * scale - (2 if n else 0)
            y -= v * scale
            shape = f'd="{top_rounded(x + (slot - w) / 2, y, w, h)}"' if n == len(stack) - 1 else ''
            mark = f'<path {shape}' if shape else f'<rect x="{x + (slot - w) / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"'
            out.append(f'{mark} fill="{c}" {tip(f"{d:%b %d} · {k}", [["Spend", money(v)], ["Day total", money(sum(values[d].values()))]])}/>')
        if i % 2 == 0:
            out.append(f'<text class="axis" x="{x + slot / 2:.1f}" y="356" text-anchor="middle">{d:%b %d}</text>')
    if missing:
        first = days.index(missing[0])
        out.append(f'<text class="muted" x="{X0 + slot * (first + len(missing) / 2):.1f}" y="{Y1 - 8}" text-anchor="middle">no data</text>')
    for d, label in events:
        x = X0 + slot * (days.index(d) + .5)
        out.append(f'<line class="event" x1="{x:.1f}" x2="{x:.1f}" y1="{Y0 - 14}" y2="{Y1}"/><text class="axis label" x="{x + 6:.1f}" y="{Y0 - 6}">{escape(label)}</text>')
    out.append(f'<line class="domain" x1="{X0}" x2="{X1}" y1="{Y1}" y2="{Y1}"/>')
    return f'<svg viewBox="0 0 960 370" role="img">{"".join(out)}</svg>'


def treemap(groups, w=960, h=380):
    """groups: [(name, colour, [(item, value), ...]), ...]"""
    total = sum(v for _, _, items in groups for _, v in items)
    groups = sorted(groups, key=lambda g: -sum(v for _, v in g[2]))
    out, hidden = [], []
    for (name, colour, items), (gx, gy, gw, gh) in zip(groups, squarify([sum(v for _, v in g[2]) for g in groups], 0, 0, w, h)):
        items = sorted(items, key=lambda i: -i[1])
        out.append(f'<rect x="{gx:.1f}" y="{gy:.1f}" width="{gw:.1f}" height="3" fill="{colour}"/>'
                   f'<text class="tile-head" x="{gx + 8:.1f}" y="{gy + 20:.1f}">{escape(name)}</text>')
        for (item, v), (x, y, iw, ih) in zip(items, squarify([v for _, v in items], gx, gy + 28, gw, gh - 28)):
            out.append(f'<rect x="{x + 1:.1f}" y="{y + 1:.1f}" width="{iw - 2:.1f}" height="{ih - 2:.1f}" rx="3" fill="{tint(colour, .8)}" '
                       f'{tip(item, [["Spend", money(v)], ["Share", f"{v / total:.0%} of total"], ["Group", name]])}/>')
            lines = wrap(item, iw - 16)
            if max(map(len, item.split('_'))) + 1 > (iw - 16) / 7.3 or ih < 30 + 15 * len(lines):
                hidden.append(f'{item} {money(v)} ({v / total:.1%})')
                continue
            out += [f'<text class="tile-name" x="{x + 8:.1f}" y="{y + 18 + 15 * n:.1f}">{escape(line)}</text>' for n, line in enumerate(lines)]
            out.append(f'<text class="tile-value" x="{x + 8:.1f}" y="{y + 22 + 15 * len(lines) + 4:.1f}">{money(v)}</text>')
    note = f'<p class="note">Too small to draw: {escape(", ".join(hidden))}</p>' if hidden else ''
    return f'<svg viewBox="0 0 {w} {h}" role="img">{"".join(out)}</svg>{note}'


def table(head, rows):
    cells = lambda tag, row: ''.join(f'<{tag}>{escape(str(c))}</{tag}>' for c in row)
    body = ''.join(f'<tr>{cells("td", r)}</tr>' for r in rows)
    return f'<details><summary>Table</summary><div class="table-wrap"><table><thead><tr>{cells("th", head)}</tr></thead><tbody>{body}</tbody></table></div></details>'


CSS = '''
@font-face { font-family: 'JetBrains Mono'; src: url('assets/JetBrainsMono-Regular.woff2') format('woff2'); font-weight: 400; font-display: swap; }
:root { color-scheme: light; font-family: 'JetBrains Mono', Consolas, monospace; color: #0D1117; background: #FAFBFC; font-synthesis: none; }
* { box-sizing: border-box; }
body { margin: 0; padding: 40px 24px; }
main { max-width: 1060px; margin: auto; display: grid; gap: 24px; }
section { background: #FFFFFF; border: 1px solid #D0D7DE; border-radius: 6px; padding: 28px 32px 24px; }
header { display: flex; justify-content: space-between; align-items: baseline; gap: 16px; flex-wrap: wrap; }
h1 { font-size: 20px; font-weight: 400; margin: 0; letter-spacing: -.5px; }
h2 { font-size: 15px; font-weight: 400; margin: 0; letter-spacing: -.3px; }
.period { font-size: 12px; color: #57606A; }
.tiles { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: #E5E9ED; border: 1px solid #E5E9ED; border-radius: 6px; margin-top: 22px; overflow: hidden; }
.tile { background: #FFFFFF; padding: 16px 18px; }
.big { font-size: 24px; letter-spacing: -.8px; font-variant-numeric: tabular-nums; }
.small { font-size: 11px; color: #57606A; margin-top: 6px; }
.legend { display: flex; gap: 24px; flex-wrap: wrap; margin-top: 22px; font-size: 11px; color: #57606A; }
.legend span { display: inline-flex; align-items: center; gap: 8px; }
.swatch { width: 10px; height: 10px; background: var(--color); border-radius: 2px; }
svg { display: block; width: 100%; height: auto; overflow: visible; margin-top: 8px; }
.grid { stroke: #E5E9ED; stroke-dasharray: 3 3; stroke-width: 1; }
.domain { stroke: #D0D7DE; stroke-width: 1; fill: none; }
.event { stroke: #8C959F; stroke-dasharray: 2 3; stroke-width: 1; }
.gap { fill: #F6F8FA; }
.axis { fill: #57606A; font-size: 11px; }
.axis.label { fill: #0D1117; }
.muted { fill: #8C959F; font-size: 10px; }
.note { margin: 12px 0 0; font-size: 11px; color: #57606A; }
.tile-head { fill: #0D1117; font-size: 12px; letter-spacing: .4px; pointer-events: none; }
.tile-name { fill: #0D1117; font-size: 12px; pointer-events: none; }
.tile-value { fill: #0D1117; font-size: 16px; letter-spacing: -.4px; pointer-events: none; }
[data-tip] { cursor: default; }
path[data-tip]:hover, rect[data-tip]:hover { opacity: .8; }
details { margin-top: 14px; }
summary { font-size: 11px; color: #57606A; cursor: pointer; }
.table-wrap { overflow-x: auto; margin-top: 12px; }
table { width: 100%; border-collapse: collapse; font-size: 11px; font-variant-numeric: tabular-nums; }
th, td { padding: 10px 8px; border-bottom: 1px solid #E5E9ED; text-align: right; font-weight: 400; white-space: nowrap; }
thead th { color: #57606A; background: #F6F8FA; border-bottom-color: #D0D7DE; }
th:first-child, td:first-child { text-align: left; }
tbody tr:last-child > * { border-bottom: 0; }
#tip { position: fixed; pointer-events: none; background: #0D1117; color: #FFFFFF; font-size: 11px; padding: 10px 12px; border-radius: 6px; max-width: 360px; line-height: 1.5; display: none; z-index: 10; box-shadow: 0 4px 14px rgba(13,17,23,.18); }
#tip .t-title { font-size: 12px; margin-bottom: 6px; }
#tip .t-grid { display: grid; grid-template-columns: auto auto; gap: 2px 16px; }
#tip .t-key { color: #8C959F; }
@media (max-width: 650px) { body { padding: 16px; } section { padding: 22px 14px; } .tiles { grid-template-columns: repeat(2, 1fr); } h1 { font-size: 18px; } }
@media print { body { padding: 0; background: white; } section { border: 0; } }
'''

HOVER = '''
const tip = document.getElementById('tip');
document.addEventListener('pointermove', e => {
  const t = e.target.closest('[data-tip]');
  if (!t) { tip.style.display = 'none'; return; }
  tip.replaceChildren();
  const title = document.createElement('div'), grid = document.createElement('div');
  title.className = 't-title'; title.textContent = t.dataset.tip; grid.className = 't-grid';
  for (const [k, v] of JSON.parse(t.dataset.rows || '[]')) {
    const a = document.createElement('span'), b = document.createElement('span');
    a.className = 't-key'; a.textContent = k; b.textContent = v; grid.append(a, b);
  }
  tip.append(title, grid);
  tip.style.display = 'block';
  tip.style.left = Math.min(e.clientX + 14, innerWidth - tip.offsetWidth - 8) + 'px';
  tip.style.top = (e.clientY + 16) + 'px';
});
'''


def page(title, sections):
    body = ''.join(f'<section>{s}</section>' for s in sections)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<!-- Colour tokens follow minusxai/artifactbin's light theme. -->
<style>{CSS}</style>
</head>
<body>
<main>{body}</main>
<div id="tip" role="tooltip"></div>
<script>{HOVER}</script>
</body>
</html>
'''


def demo():
    rng = random.Random(7)
    first = date(2026, 1, 5)
    days = [first + timedelta(n) for n in range(28)]
    series = [('Prod', 'Prod', SLOTS[0]), ('Staging', 'Staging', SLOTS[1]), ('Batch jobs', 'Batch jobs', SLOTS[2])]
    values = {d: {k: rng.uniform(lo, hi) for (k, _, _), (lo, hi) in zip(series, [(40, 90), (5, 25), (0, 30)])} for d in days}
    missing = days[17:19]
    groups = [('extract', SLOTS[0], [('read_header', 410), ('read_line_items', 980), ('normalise_units', 120), ('ocr_fallback', 60)]),
              ('match', SLOTS[1], [('vendor_lookup_and_match', 520), ('price_check', 230), ('dedupe', 45)]),
              ('review', SLOTS[2], [('flag_for_human', 180), ('summarise', 90)])]
    total = sum(v for d in days if d not in missing for v in values[d].values())
    window = f'{days[0]:%b %d} – {days[-1]:%b %d, %Y} · UTC · demo data'
    tiles = [(money(total), 'Spend in window'), (money(total / (len(days) - len(missing))), 'Spend per day'),
             ('3', 'Environments'), (f'{len(missing)}', 'Days with no data')]
    return page('Demo cost page', [
        f'<header><h1>Demo cost page</h1><span class="period">{window}</span></header>'
        '<div class="tiles">' + ''.join(f'<div class="tile"><div class="big">{v}</div><div class="small">{escape(k)}</div></div>' for v, k in tiles) + '</div>',
        f'<header><h2>Spend by group and step</h2><span class="period">{window}</span></header>{treemap(groups)}'
        + table(['Group', 'Step', 'Spend'], [(g, i, money(v)) for g, _, items in groups for i, v in items]),
        f'<header><h2>Daily spend by environment</h2><span class="period">US dollars</span></header>'
        '<div class="legend">' + ''.join(f'<span><i class="swatch" style="--color:{c}"></i>{escape(l)}</span>' for _, l, c in series) + '</div>'
        + daily_bars(days, series, values, events=[(days[9], 'v2 deploy')], missing=missing)
        + table(['Day'] + [l for _, l, _ in series], [(f'{d:%b %d}', *(money(values[d][k]) for k, _, _ in series)) for d in days if d not in missing]),
    ])


if __name__ == '__main__':
    (ROOT / 'index.html').write_text(demo())
    print(ROOT / 'index.html')
