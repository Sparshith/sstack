"""Starter for an explain page: a numbered walk-through of how something works or why it went wrong.

Copy this file, starter.py and the font into the page folder, then replace demo() with the real story.
Each step is one plain sentence or two on the left and one small picture with the real numbers on the right.
"""
from html import escape
from pathlib import Path

from starter import CSS, page

ROOT = Path(__file__).resolve().parent

EXPLAIN_CSS = '''
.step { display: grid; grid-template-columns: 32px minmax(0, 1fr) minmax(0, 1.25fr); gap: 20px; padding: 22px 0; border-top: 1px solid #E5E9ED; align-items: start; }
.step:first-of-type { border-top: 0; }
.num { width: 26px; height: 26px; border-radius: 50%; background: #0D1117; color: #FFFFFF; font-size: 12px; display: grid; place-items: center; }
.words h3 { font-size: 14px; font-weight: 400; margin: 2px 0 8px; }
.words p { font-size: 12px; line-height: 1.7; color: #3D444D; margin: 0; }
.words b { font-weight: 400; color: #0D1117; background: #F6F8FA; padding: 1px 5px; border-radius: 3px; }
.receipt, .card { border: 1px solid #D0D7DE; border-radius: 6px; padding: 10px 14px; font-size: 12px; background: #FFFFFF; }
.r-row { display: flex; justify-content: space-between; gap: 16px; padding: 4px 0; font-variant-numeric: tabular-nums; }
.r-row.muted { color: #8C959F; }
.r-row.sum { border-top: 1px dashed #D0D7DE; margin-top: 4px; padding-top: 8px; }
.r-row.hot { color: #B3471B; }
.r-row.total { border-top: 1px solid #0D1117; margin-top: 4px; padding-top: 8px; font-size: 14px; }
.kv { display: grid; grid-template-columns: 1.3fr 1fr 2fr; gap: 12px; padding: 4px 0; font-variant-numeric: tabular-nums; }
.kv.muted { color: #8C959F; }
.kv.pick { background: #FFF4EE; border-radius: 4px; padding: 4px 6px; margin: 0 -6px; }
.bars { display: grid; gap: 10px; font-size: 12px; }
.bar-row { display: grid; grid-template-columns: 120px minmax(0, 1fr) 90px; gap: 10px; align-items: center; }
.track { position: relative; height: 18px; }
.bar { height: 18px; border-radius: 0 4px 4px 0; }
.band { position: absolute; top: -4px; height: 26px; background: rgba(27,175,122,.18); border: 1px dashed #1baf7a; border-radius: 3px; }
.bar-val { text-align: right; font-variant-numeric: tabular-nums; }
.note { color: #57606A; line-height: 1.6; }
.compare { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.compare .card { text-align: center; } .compare .big { font-size: 22px; margin-top: 6px; }
.bad { color: #B3471B; } .good { color: #1a7f37; }
@media (max-width: 760px) { .step { grid-template-columns: 26px minmax(0, 1fr); } .visual { grid-column: 2; } }
'''


def step(n, title, text, visual):
    """`text` may hold <b> for the one number the step is about; everything else is plain words."""
    return (f'<div class="step"><div class="num">{n}</div><div class="words"><h3>{escape(title)}</h3><p>{text}</p></div>'
            f'<div class="visual">{visual}</div></div>')


def receipt(rows, more=None, sums=()):
    """A document in miniature: a few real rows, '… N more', then summary rows as (label, value, css class)."""
    body = ''.join(f'<div class="r-row"><span>{escape(a)}</span><span>{escape(b)}</span></div>' for a, b in rows)
    if more:
        body += f'<div class="r-row muted"><span>… {escape(more)}</span><span></span></div>'
    body += ''.join(f'<div class="r-row {cls}"><span>{escape(a)}</span><span>{escape(b)}</span></div>' for a, b, cls in sums)
    return f'<div class="receipt">{body}</div>'


def card(rows):
    """Key, value, note per row; style 'muted' or 'pick' marks rows the story skips or chooses."""
    return '<div class="card">' + ''.join(
        f'<div class="kv {style}"><span>{escape(k)}</span><span>{escape(v)}</span><span>{escape(note)}</span></div>'
        for k, v, note, style in rows) + '</div>'


def gap_bars(rows, band=None, start=0.0, end=None, note=''):
    """Bars to one scale. rows = [(label, value, colour)]; band = (low, high) shades an allowed range.
    Start the scale above zero only to make a small gap visible, and say so in `note`."""
    end = end or max(v for _, v, _ in rows) * 1.06
    x = lambda v: 100 * (v - start) / (end - start)
    out = []
    for i, (label, v, colour) in enumerate(rows):
        shade = f'<div class="band" style="left:{x(band[0]):.1f}%;width:{x(band[1]) - x(band[0]):.1f}%"></div>' if band and i == 0 else ''
        out.append(f'<div class="bar-row"><span>{escape(label)}</span><div class="track"><div class="bar" style="width:{x(v):.1f}%;background:{colour}"></div>'
                   f'{shade}</div><span class="bar-val">{v:,.2f}</span></div>')
    return f'<div class="bars">{"".join(out)}<div class="note">{escape(note)}</div></div>'


def compare(left, right):
    """Two big numbers side by side: (label, value, 'good'|'bad'|'')."""
    return '<div class="compare">' + ''.join(
        f'<div class="card">{escape(label)}<div class="big {cls}">{escape(value)}</div></div>' for label, value, cls in (left, right)) + '</div>'


def demo():
    steps = [
        step(1, 'What the order says', 'Three items cost $90.00. A 10% coupon takes off $9.00. The customer should pay <b>$81.00</b>.',
             receipt([('Mug', '$30.00'), ('Notebook', '$40.00'), ('Pen', '$20.00')],
                      sums=[('Items', '$90.00', 'sum'), ('Coupon 10%', '−$9.00', 'hot'), ('To pay', '$81.00', 'total')])),
        step(2, 'The cart applies the coupon', 'The cart takes 10% off each item, so the items now add up to $81.00.',
             card([('Mug', '$27.00', 'coupon applied', ''), ('Notebook', '$36.00', 'coupon applied', ''), ('Pen', '$18.00', 'coupon applied', '')])),
        step(3, 'Checkout applies it again', 'Checkout does not know the cart already did it, and takes 10% off the new total.',
             gap_bars([('Should pay', 81.0, '#1baf7a'), ('Charged', 72.9, '#eb6834')], start=60, note='Scale starts at $60 so the gap is visible.')),
        step(4, 'The result', 'The customer is charged $8.10 too little on every coupon order.',
             compare(('Charged', '$72.90', 'bad'), ('Should pay', '$81.00', 'good'))),
    ]
    return page('Demo explainer', ['<header><h1>How a coupon got applied twice</h1><span class="period">demo data</span></header>' + ''.join(steps)]
                ).replace(CSS, CSS + EXPLAIN_CSS)


if __name__ == '__main__':
    (ROOT / 'index.html').write_text(demo())
    print(ROOT / 'index.html')
