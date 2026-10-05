"""Statistické karty: přehled čísel, jazyky a týdenní aktivita."""

from datetime import date

from ..i18n import format_number, t
from ..stats import LanguageShare, Streaks
from .base import FADE_IN_STYLE, REDUCED_MOTION_STYLE, SANS, card, esc, fmt
from .theme import Theme

HALF_WIDTH = 425
FULL_WIDTH = 860
SMALL_HEIGHT = 200


def render_stats(
    lang: str,
    theme: Theme,
    contributions: int,
    commits: int,
    repos: int,
    stars: int,
    streak: Streaks,
) -> str:
    days = t(lang, "days")
    items = (
        (format_number(lang, contributions), t(lang, "stat_contributions")),
        (format_number(lang, commits), t(lang, "stat_commits")),
        (format_number(lang, repos), t(lang, "stat_repos")),
        (format_number(lang, stars), t(lang, "stat_stars")),
        (f"{streak.current} {days}", t(lang, "stat_current_streak")),
        (f"{streak.longest} {days}", t(lang, "stat_longest_streak")),
    )
    body = []
    for i, (value, label) in enumerate(items):
        col, row = i % 2, i // 2
        x = 24 + col * 200
        y = 82 + row * 44
        body.append(
            f'<g class="fade" style="animation-delay:{i * 0.12:.2f}s">'
            f'<text x="{x}" y="{y}" font-family="{SANS}" font-size="20" font-weight="700" '
            f'fill="{theme.text}">{esc(value)}</text>'
            f'<text x="{x}" y="{y + 17}" font-family="{SANS}" font-size="12" '
            f'fill="{theme.muted}">{esc(label)}</text></g>'
        )
    return card(HALF_WIDTH, SMALL_HEIGHT, t(lang, "stats_title"), "".join(body), theme, FADE_IN_STYLE)


def render_languages(lang: str, theme: Theme, shares: list[LanguageShare]) -> str:
    bar_x, bar_y, bar_w = 24, 56, HALF_WIDTH - 48
    clip = f'<clipPath id="bar"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="10" rx="5"/></clipPath>'
    segments = [f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="10" fill="{theme.track}"/>']
    x = float(bar_x)
    for share in shares:
        width = bar_w * share.percent / 100
        segments.append(
            f'<rect x="{fmt(x)}" y="{bar_y}" width="{fmt(width)}" height="10" fill="{share.color}"/>'
        )
        x += width

    legend = []
    for i, share in enumerate(shares):
        col, row = i % 2, i // 2
        lx = 24 + col * 190
        ly = 96 + row * 26
        legend.append(
            f'<g class="fade" style="animation-delay:{i * 0.1:.2f}s">'
            f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{share.color}"/>'
            f'<text x="{lx + 16}" y="{ly}" font-family="{SANS}" font-size="13" fill="{theme.text}">'
            f'{esc(share.name)} <tspan fill="{theme.muted}">{share.percent:.1f} %</tspan></text></g>'
        )
    body = f"<defs>{clip}</defs><g clip-path=\"url(#bar)\">{''.join(segments)}</g>{''.join(legend)}"
    return card(HALF_WIDTH, SMALL_HEIGHT, t(lang, "languages_title"), body, theme, FADE_IN_STYLE)


def render_activity(lang: str, theme: Theme, weekly: list[tuple[date, int]]) -> str:
    height = 200
    left, right, top, bottom = 24, 24, 60, 40
    chart_w = FULL_WIDTH - left - right
    chart_h = height - top - bottom
    peak = max((count for _, count in weekly), default=0) or 1
    slot = chart_w / max(len(weekly), 1)
    bar_w = max(slot * 0.68, 2)

    parts = [
        f'<line x1="{left}" y1="{top + chart_h}" x2="{FULL_WIDTH - right}" y2="{top + chart_h}" '
        f'stroke="{theme.border}"/>',
        f'<text x="{FULL_WIDTH - right}" y="{top - 8}" text-anchor="end" font-family="{SANS}" '
        f'font-size="11" fill="{theme.muted}">max {format_number(lang, peak)}</text>',
    ]
    previous_month = None
    for i, (week_start, count) in enumerate(weekly):
        x = left + i * slot + (slot - bar_w) / 2
        bar_h = max(chart_h * count / peak, 2 if count else 1)
        fill = theme.accent if count else theme.track
        parts.append(
            f'<rect class="grow" style="animation-delay:{i * 0.03:.2f}s" x="{fmt(x)}" '
            f'y="{fmt(top + chart_h - bar_h)}" width="{fmt(bar_w)}" height="{fmt(bar_h)}" rx="2" '
            f'fill="{fill}"><title>{week_start.isoformat()}: {count}</title></rect>'
        )
        if week_start.month != previous_month:
            previous_month = week_start.month
            parts.append(
                f'<text x="{fmt(x)}" y="{height - 18}" font-family="{SANS}" font-size="11" '
                f'fill="{theme.muted}">{week_start.month}/{week_start.year % 100:02d}</text>'
            )
    style = (
        "@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}"
        ".grow{transform-box:fill-box;transform-origin:bottom;animation:grow .5s ease-out both}"
        + REDUCED_MOTION_STYLE
    )
    title = t(lang, "activity_title", weeks=len(weekly))
    return card(FULL_WIDTH, height, title, "".join(parts), theme, style)
