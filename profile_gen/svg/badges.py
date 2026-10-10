"""Karta technologií, kontaktní odznaky, sparkline a dekorativní oddělovač."""

from ..config import Contact, TechGroup
from ..i18n import t
from .base import FADE_IN_STYLE, SANS, card, document, esc, fmt, text_width
from .theme import Theme

STACK_WIDTH = 860
PILL_HEIGHT = 28
PILL_GAP = 8
PILL_FONT = 13
GROUP_LABEL_WIDTH = 120


def _pill(x: float, y: float, label: str, color: str, theme: Theme, delay: float) -> tuple[str, float]:
    width = text_width(label, PILL_FONT) + 36
    svg = (
        f'<g class="fade" style="animation-delay:{delay:.2f}s">'
        f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(width)}" height="{PILL_HEIGHT}" rx="14" '
        f'fill="{theme.background}" stroke="{theme.border}"/>'
        f'<circle cx="{fmt(x + 15)}" cy="{fmt(y + PILL_HEIGHT / 2)}" r="5" fill="{color}" '
        f'stroke="{theme.muted}" stroke-opacity=".4"/>'
        f'<text x="{fmt(x + 26)}" y="{fmt(y + 18.5)}" font-family="{SANS}" font-size="{PILL_FONT}" '
        f'fill="{theme.text}">{esc(label)}</text></g>'
    )
    return svg, width


def render_tech_stack(lang: str, theme: Theme, groups: tuple[TechGroup, ...]) -> str:
    parts: list[str] = []
    y = 56.0
    max_x = STACK_WIDTH - 24
    delay = 0.0
    for group in groups:
        parts.append(
            f'<text x="24" y="{fmt(y + 18.5)}" font-family="{SANS}" font-size="13" font-weight="600" '
            f'fill="{theme.muted}">{esc(group.title[lang])}</text>'
        )
        x = 24.0 + GROUP_LABEL_WIDTH
        for tech in group.items:
            width = text_width(tech.name, PILL_FONT) + 36
            if x + width > max_x:  # zalomení na další řádek
                x = 24.0 + GROUP_LABEL_WIDTH
                y += PILL_HEIGHT + PILL_GAP
            pill, width = _pill(x, y, tech.name, tech.color, theme, delay)
            parts.append(pill)
            x += width + PILL_GAP
            delay += 0.05
        y += PILL_HEIGHT + PILL_GAP + 6
    height = y + 12
    return card(STACK_WIDTH, height, t(lang, "tech_title"), "".join(parts), theme, FADE_IN_STYLE)


def _contact_icon(contact: Contact) -> str:
    box = f'<rect x="8" y="8" width="24" height="24" rx="6" fill="{contact.color}"/>'
    if contact.key == "linkedin":
        glyph = (
            f'<text x="20" y="26" text-anchor="middle" font-family="{SANS}" font-size="15" '
            f'font-weight="700" fill="#fff">in</text>'
        )
    elif contact.key == "discord":
        glyph = (
            '<ellipse cx="20" cy="21" rx="8" ry="6" fill="#fff"/>'
            f'<circle cx="17" cy="21" r="1.6" fill="{contact.color}"/>'
            f'<circle cx="23" cy="21" r="1.6" fill="{contact.color}"/>'
        )
    elif contact.key == "buymeacoffee":
        # Hrnek s ouškem a párou; tmavá kresba, protože značková barva je světle žlutá.
        glyph = (
            '<path d="M13 17h11l-1.4 9.2a1.6 1.6 0 0 1-1.6 1.3h-5a1.6 1.6 0 0 1-1.6-1.3z" fill="#0d0c22"/>'
            '<path d="M24 19h1.3a2.2 2.2 0 0 1 0 4.4H23.4" fill="none" stroke="#0d0c22" stroke-width="1.6"/>'
            '<path d="M16.5 14.5c-.8-1 .8-1.6 0-2.6M20.5 14.5c-.8-1 .8-1.6 0-2.6" fill="none" '
            'stroke="#0d0c22" stroke-width="1.3" stroke-linecap="round"/>'
        )
    else:
        glyph = (
            f'<text x="20" y="26" text-anchor="middle" font-family="{SANS}" font-size="15" '
            f'font-weight="700" fill="#fff">{esc(contact.label[:1])}</text>'
        )
    return box + glyph


def render_contact(contact: Contact, theme: Theme) -> str:
    width = text_width(contact.label, 14) + 56
    body = (
        f'<rect x="0.5" y="0.5" width="{fmt(width - 1)}" height="39" rx="10" '
        f'fill="{theme.background}" stroke="{theme.border}"/>'
        + _contact_icon(contact)
        + f'<text x="42" y="25" font-family="{SANS}" font-size="14" font-weight="600" '
        f'fill="{theme.text}">{esc(contact.label)}</text>'
    )
    return document(width, 40, body, contact.label)


def render_sparkline(weekly: tuple[int, ...], theme: Theme) -> str:
    width, height = 120, 28
    slot = width / max(len(weekly), 1)
    peak = max(weekly, default=0) or 1
    bars = []
    for i, count in enumerate(weekly):
        bar_h = max((height - 4) * count / peak, 2) if count else 1.5
        bars.append(
            f'<rect x="{fmt(i * slot + 1)}" y="{fmt(height - bar_h)}" width="{fmt(slot - 2)}" '
            f'height="{fmt(bar_h)}" rx="1" fill="{theme.accent if count else theme.border}"/>'
        )
    return document(width, height, "".join(bars), f"{sum(weekly)} / {len(weekly)}")


def render_divider(theme: Theme) -> str:
    """Animovaný „signál“ – průběh vlny, který se plynule posouvá."""
    width, height, period, amp = 860, 40, 80, 9
    mid = height / 2
    segments = [f"M0 {mid}"]
    # Dvojnásobná délka, aby posun o jednu periodu navazoval bez skoku.
    for x in range(0, width * 2, period):
        segments.append(
            f"Q{x + period / 4} {mid - amp} {x + period / 2} {mid} T{x + period} {mid}"
        )
    body = (
        # Maska pracuje s jasem, proto bílá s proměnnou průhledností (ztmavení k okrajům).
        '<defs><linearGradient id="f" x1="0" x2="1">'
        '<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".5" stop-color="#fff"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        f'<mask id="m"><rect width="{width}" height="{height}" fill="url(#f)"/></mask></defs>'
        f'<g mask="url(#m)"><path d="{" ".join(segments)}" fill="none" stroke="{theme.accent}" '
        f'stroke-width="2"><animateTransform attributeName="transform" type="translate" '
        f'from="0 0" to="-{period} 0" dur="2.5s" repeatCount="indefinite"/></path></g>'
    )
    return document(width, height, body, "divider")
