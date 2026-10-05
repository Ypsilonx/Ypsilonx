"""Překlady textů a jazykově závislé formátování čísel a dat."""

from datetime import date

TEXTS: dict[str, dict[str, str]] = {
    "en": {
        "lang_name": "English",
        "tech_title": "Tech stack",
        "stats_title": "GitHub stats · last 12 months",
        "stat_contributions": "Contributions",
        "stat_commits": "Commits",
        "stat_repos": "Public repositories",
        "stat_stars": "Stars earned",
        "stat_current_streak": "Current streak",
        "stat_longest_streak": "Longest streak",
        "days": "days",
        "activity_title": "Weekly contributions · last {weeks} weeks",
        "languages_title": "Most used languages",
        "col_project": "Project",
        "col_language": "Language",
        "col_activity": "Activity ({weeks} wk)",
        "col_commits": "Commits ({weeks} wk)",
        "col_pushed": "Last push",
        "active": "active",
        "no_description": "—",
        "no_repos": "_No public repositories yet._",
        "generated": "Generated file – edit templates/{template} instead.",
    },
    "cs": {
        "lang_name": "Čeština",
        "tech_title": "Technologie",
        "stats_title": "GitHub statistiky · posledních 12 měsíců",
        "stat_contributions": "Příspěvky",
        "stat_commits": "Commity",
        "stat_repos": "Veřejné repozitáře",
        "stat_stars": "Získané hvězdy",
        "stat_current_streak": "Aktuální série",
        "stat_longest_streak": "Nejdelší série",
        "days": "dní",
        "activity_title": "Příspěvky po týdnech · posledních {weeks} týdnů",
        "languages_title": "Nejpoužívanější jazyky",
        "col_project": "Projekt",
        "col_language": "Jazyk",
        "col_activity": "Aktivita ({weeks} týd.)",
        "col_commits": "Commity ({weeks} týd.)",
        "col_pushed": "Poslední push",
        "active": "aktivní",
        "no_description": "—",
        "no_repos": "_Zatím žádné veřejné repozitáře._",
        "generated": "Vygenerovaný soubor – upravuj templates/{template}.",
    },
}

_EN_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

# Česká typografie odděluje tisíce nezlomitelnou mezerou.
_NBSP = " "


def t(lang: str, key: str, **kwargs: object) -> str:
    """Vrátí přeložený text; chybějící klíč je programátorská chyba, proto KeyError."""
    text = TEXTS[lang][key]
    return text.format(**kwargs) if kwargs else text


def format_number(lang: str, value: int) -> str:
    grouped = f"{value:,}"
    return grouped.replace(",", _NBSP) if lang == "cs" else grouped


def format_date(lang: str, value: date) -> str:
    if lang == "cs":
        return f"{value.day}.{_NBSP}{value.month}.{_NBSP}{value.year}"
    return f"{_EN_MONTHS[value.month - 1]} {value.day}, {value.year}"
