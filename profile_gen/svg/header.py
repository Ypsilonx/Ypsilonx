"""Animovaná hlavička s efektem psacího stroje (SMIL, bez JavaScriptu)."""

from .base import MONO, REDUCED_MOTION_STYLE, SANS, document, esc, fmt, text_width
from .theme import Theme

WIDTH = 860
HEIGHT = 130
TYPE_SIZE = 20
TYPE_STEP = 0.08    # s na napsaný znak
DELETE_STEP = 0.035  # s na smazaný znak
HOLD = 1.8          # s, jak dlouho je řádek celý vidět
GAP = 0.4           # s pauza před dalším řádkem


def _timeline(lines: tuple[str, ...]) -> tuple[list[float], float]:
    """Začátky jednotlivých řádků a délka celého cyklu."""
    starts: list[float] = []
    cursor = 0.0
    for line in lines:
        starts.append(cursor)
        cursor += len(line) * TYPE_STEP + HOLD + len(line) * DELETE_STEP + GAP
    return starts, cursor


def _keyframes(n_chars: int, start: float, total: float, char_w: float) -> tuple[str, str]:
    """keyTimes a values pro diskrétní animaci šířky ořezu jednoho řádku."""
    frames: list[tuple[float, float]] = [(0.0, 0.0)]
    t = start
    for k in range(1, n_chars + 1):
        t += TYPE_STEP
        frames.append((t, k * char_w))
    t += HOLD
    for k in range(n_chars - 1, -1, -1):
        t += DELETE_STEP
        frames.append((t, k * char_w))
    key_times = ";".join(f"{min(ft / total, 1):.4f}" for ft, _ in frames)
    values = ";".join(fmt(v) for _, v in frames)
    return key_times, values


def render_header(name: str, lines: tuple[str, ...], theme: Theme) -> str:
    starts, total = _timeline(lines)
    char_w = text_width("x", TYPE_SIZE, mono=True)
    baseline = 104

    defs = (
        f'<linearGradient id="g" x1="0" x2="1">'
        f'<stop offset="0" stop-color="{theme.accent}"/>'
        f'<stop offset="1" stop-color="{theme.accent2}"/></linearGradient>'
    )
    parts: list[str] = []
    for i, (line, start) in enumerate(zip(lines, starts)):
        x0 = (WIDTH - len(line) * char_w) / 2
        key_times, values = _keyframes(len(line), start, total, char_w)
        anim = (
            f'dur="{fmt(total)}s" repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="{key_times}" values="{values}"'
        )
        cursor_x = ";".join(fmt(x0 + float(v)) for v in values.split(";"))
        defs += (
            f'<clipPath id="c{i}"><rect x="{fmt(x0)}" y="{baseline - 24}" width="0" height="32">'
            f'<animate attributeName="width" {anim}/></rect></clipPath>'
        )
        end = min((start + len(line) * (TYPE_STEP + DELETE_STEP) + HOLD) / total, 1)
        if start:
            visible_times, visible_values = f"0;{start / total:.4f};{end:.4f}", "hidden;visible;hidden"
        else:
            visible_times, visible_values = f"0;{end:.4f}", "visible;hidden"
        parts.append(
            f'<text x="{fmt(x0)}" y="{baseline}" clip-path="url(#c{i})" font-family="{MONO}" '
            f'font-size="{TYPE_SIZE}" fill="{theme.text}" xml:space="preserve">{esc(line)}</text>'
            f'<rect class="cursor" x="{fmt(x0)}" y="{baseline - 19}" width="2" height="24" '
            f'fill="{theme.accent}" visibility="hidden">'
            f'<animate attributeName="x" dur="{fmt(total)}s" repeatCount="indefinite" '
            f'calcMode="discrete" keyTimes="{key_times}" values="{cursor_x}"/>'
            f'<animate attributeName="visibility" dur="{fmt(total)}s" repeatCount="indefinite" '
            f'calcMode="discrete" keyTimes="{visible_times}" values="{visible_values}"/></rect>'
        )

    body = (
        f"<defs>{defs}</defs>"
        f'<text x="{WIDTH / 2}" y="52" text-anchor="middle" font-family="{SANS}" font-size="40" '
        f'font-weight="700" fill="url(#g)">{esc(name)}</text>'
        f'<rect class="bar" x="{WIDTH / 2 - 60}" y="64" width="120" height="3" rx="1.5" fill="url(#g)"/>'
        + "".join(parts)
    )
    style = (
        "@keyframes blink{50%{opacity:0}}.cursor{animation:blink 1s step-end infinite}"
        "@keyframes pulse{0%,100%{opacity:.35}50%{opacity:1}}.bar{animation:pulse 3s ease-in-out infinite}"
        + REDUCED_MOTION_STYLE
    )
    return document(WIDTH, HEIGHT, body, f"{name} – {lines[0]}", style)
