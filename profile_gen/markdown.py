"""Markdown/HTML fragmenty vkládané do šablon README."""

import html
import re
from datetime import datetime, timedelta

from .config import ACTIVE_DAYS, DEFAULT_LANG_EMOJI, LANG_EMOJI, Contact
from .i18n import format_date, format_number, t
from .models import Repo

# Znaky, které by v buňce tabulky nebo v textu změnily význam Markdownu.
_MD_SPECIAL = re.compile(r"([\\`*_\[\]|~])")


def escape_md(text: str) -> str:
    return _MD_SPECIAL.sub(r"\\\1", html.escape(text, quote=False))


def asset_path(stem: str, theme: str, lang: str | None) -> str:
    return f"assets/{stem}.{lang}.{theme}.svg" if lang else f"assets/{stem}.{theme}.svg"


def picture(stem: str, alt: str, lang: str | None, width: str | None = None) -> str:
    """<picture>, který GitHub přepíná podle světlého/tmavého režimu."""
    width_attr = f' width="{html.escape(width)}"' if width else ""
    return (
        f'<picture><source media="(prefers-color-scheme: dark)" '
        f'srcset="{asset_path(stem, "dark", lang)}">'
        f'<img src="{asset_path(stem, "light", lang)}" alt="{html.escape(alt)}"{width_attr}></picture>'
    )


def contacts(items: tuple[Contact, ...]) -> str:
    return "\n".join(
        f'<a href="{html.escape(c.url)}">{picture(f"contact-{c.key}", c.label, None)}</a>'
        for c in items
    )


def language_switch(lang: str, langs: tuple[str, ...], urls: dict[str, str]) -> str:
    links = [
        f"<b>{t(code, 'lang_name')}</b>" if code == lang
        else f'<a href="{urls[code]}">{t(code, "lang_name")}</a>'
        for code in langs
    ]
    return "🌐 " + " · ".join(links)


def repo_table(lang: str, repos: list[Repo], weeks: int, now: datetime) -> str:
    if not repos:
        return t(lang, "no_repos")
    header = (
        f"| {t(lang, 'col_project')} | {t(lang, 'col_language')} | "
        f"{t(lang, 'col_activity', weeks=weeks)} | {t(lang, 'col_commits', weeks=weeks)} | "
        f"{t(lang, 'col_pushed')} |\n|:--|:--|:--:|--:|:--|"
    )
    rows = []
    for repo in repos:
        description = escape_md(repo.description) if repo.description else t(lang, "no_description")
        language = repo.primary_language or "—"
        emoji = LANG_EMOJI.get(language, DEFAULT_LANG_EMOJI)
        pushed = format_date(lang, repo.pushed_at.date())
        if now - repo.pushed_at <= timedelta(days=ACTIVE_DAYS):
            pushed += f"<br><sub>🟢 {t(lang, 'active')}</sub>"
        spark = picture(f"spark/{repo.name}", f"{sum(repo.weekly_commits)}", None, "120")
        rows.append(
            f"| **[{escape_md(repo.name)}]({repo.url})**<br><sub>{description}</sub> "
            f"| {emoji} {escape_md(language)} | {spark} "
            f"| {format_number(lang, sum(repo.weekly_commits))} | {pushed} |"
        )
    return header + "\n" + "\n".join(rows)
