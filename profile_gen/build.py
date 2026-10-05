"""Sestavení všech výstupů (README + SVG) z dat profilu – bez síťové komunikace."""

from pathlib import Path

from . import config
from .i18n import t
from .markdown import contacts, language_switch, repo_table
from .models import Profile
from .readme import render_template
from .stats import language_shares, select_recent, streaks, weekly_totals
from .svg.badges import render_contact, render_divider, render_sparkline, render_tech_stack
from .svg.cards import render_activity, render_languages, render_stats
from .svg.header import render_header
from .svg.theme import THEMES

# Obrázky, které se generují pro každý jazyk zvlášť (obsahují text).
LOCALIZED_ASSETS = frozenset({"header", "stats", "languages", "activity", "tech"})
SHARED_ASSETS = frozenset({"divider"} | {f"contact-{c.key}" for c in config.CONTACTS})


def readme_filename(lang: str) -> str:
    return "README.md" if lang == config.DEFAULT_LANG else f"README.{lang}.md"


def readme_urls() -> dict[str, str]:
    """Absolutní odkazy – relativní by z profilové stránky nevedly správně."""
    base = f"https://github.com/{config.USERNAME}"
    return {
        lang: base if lang == config.DEFAULT_LANG
        else f"{base}/{config.USERNAME}/blob/main/{readme_filename(lang)}"
        for lang in config.LANGS
    }


def _localized_svgs(profile: Profile, lang: str) -> dict[str, dict[str, str]]:
    """Mapa asset → {téma: svg} pro jazykově závislé obrázky."""
    today = profile.generated_at.date()
    shares = language_shares(profile.repos, config.TOP_LANGUAGES, config.LANGUAGE_EXCLUDE)
    streak = streaks(profile.calendar, today)
    weekly = weekly_totals(profile.calendar, config.ACTIVITY_WEEKS)
    public_repos = [r for r in profile.repos if r.name.lower() != config.USERNAME.lower()]
    stars = sum(r.stars for r in profile.repos)
    return {
        "header": {th.name: render_header(config.HEADER_NAME, config.HEADER_LINES[lang], th) for th in THEMES},
        "stats": {
            th.name: render_stats(
                lang, th, profile.total_contributions, profile.total_commits,
                len(public_repos), stars, streak,
            )
            for th in THEMES
        },
        "languages": {th.name: render_languages(lang, th, shares) for th in THEMES},
        "activity": {th.name: render_activity(lang, th, weekly) for th in THEMES},
        "tech": {th.name: render_tech_stack(lang, th, config.TECH_STACK) for th in THEMES},
    }


def build_outputs(profile: Profile, templates: dict[str, str]) -> dict[Path, str]:
    """Vrátí mapu relativní cesta → obsah pro všechny generované soubory."""
    outputs: dict[Path, str] = {}
    recent = select_recent(profile.repos, config.USERNAME, config.RECENT_REPO_COUNT)

    for theme in THEMES:
        outputs[Path(f"assets/divider.{theme.name}.svg")] = render_divider(theme)
        for contact in config.CONTACTS:
            outputs[Path(f"assets/contact-{contact.key}.{theme.name}.svg")] = render_contact(contact, theme)
        for repo in recent:
            weekly = repo.weekly_commits or (0,) * config.SPARKLINE_WEEKS
            outputs[config.SPARK_SUBDIR / f"{repo.name}.{theme.name}.svg"] = render_sparkline(weekly, theme)

    urls = readme_urls()
    for lang in config.LANGS:
        for stem, variants in _localized_svgs(profile, lang).items():
            for theme_name, svg in variants.items():
                outputs[Path(f"assets/{stem}.{lang}.{theme_name}.svg")] = svg

        template_name = f"README.{lang}.md"
        fragments = {
            "switch": language_switch(lang, config.LANGS, urls),
            "repos": repo_table(lang, recent, config.SPARKLINE_WEEKS, profile.generated_at),
            "contacts": contacts(config.CONTACTS),
        }
        body = render_template(
            templates[template_name], lang, fragments,
            LOCALIZED_ASSETS, LOCALIZED_ASSETS | SHARED_ASSETS,
        )
        notice = f"<!-- {t(lang, 'generated', template=template_name)} -->\n"
        outputs[Path(readme_filename(lang))] = notice + body
    return outputs
