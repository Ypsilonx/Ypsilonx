"""Vykreslení README ze šablon s jednoduchými zástupnými značkami.

Podporované značky (v šabloně):
    {{switch}}                         přepínač jazyků
    {{repos}}                          tabulka naposledy aktivních repozitářů
    {{contacts}}                       kontaktní odznaky s odkazy
    {{picture:<asset>|<alt>[|<šířka>]}} obrázek s variantou pro světlý/tmavý režim
"""

import re

from .markdown import picture

_PLACEHOLDER = re.compile(r"\{\{\s*([a-z_]+)(?::([^}]*))?\s*\}\}")


class TemplateError(ValueError):
    """Neznámá značka nebo chybné argumenty v šabloně."""


def render_template(
    template: str,
    lang: str,
    fragments: dict[str, str],
    localized_assets: frozenset[str],
    known_assets: frozenset[str],
) -> str:
    def replace(match: re.Match[str]) -> str:
        name, arg = match.group(1), match.group(2)
        if name == "picture":
            return _picture(arg, lang, localized_assets, known_assets)
        if arg is not None or name not in fragments:
            raise TemplateError(f"Neznámá značka v šabloně: {match.group(0)}")
        return fragments[name]

    return _PLACEHOLDER.sub(replace, template)


def _picture(
    arg: str | None, lang: str, localized_assets: frozenset[str], known_assets: frozenset[str]
) -> str:
    parts = [p.strip() for p in (arg or "").split("|")]
    if len(parts) not in (2, 3) or not parts[0]:
        raise TemplateError(f"Značka picture vyžaduje 'asset|alt[|šířka]', dostala: {arg!r}")
    stem, alt = parts[0], parts[1]
    if stem not in known_assets:
        raise TemplateError(f"Neznámý obrázek v šabloně: {stem}")
    width = parts[2] if len(parts) == 3 else None
    return picture(stem, alt, lang if stem in localized_assets else None, width)
