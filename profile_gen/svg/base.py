"""Společné stavební bloky SVG: escapování, odhad šířky textu, rámeček karty."""

from xml.sax.saxutils import escape as _xml_escape

from .theme import Theme

SANS = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Ubuntu, Arial, sans-serif"
MONO = "'Fira Code', 'Cascadia Code', Consolas, 'DejaVu Sans Mono', Menlo, monospace"

# Průměrná šířka znaku vůči velikosti písma. Fonty se v <img> nedají načíst,
# rozměry proto jen odhadujeme – u monospace je 0.6 velmi přesné.
SANS_CHAR_RATIO = 0.56
MONO_CHAR_RATIO = 0.6


def esc(text: str) -> str:
    return _xml_escape(text, {'"': "&quot;"})


def text_width(text: str, size: float, mono: bool = False) -> float:
    return len(text) * size * (MONO_CHAR_RATIO if mono else SANS_CHAR_RATIO)


def fmt(value: float) -> str:
    """Kompaktní zápis čísla do atributu (bez zbytečných desetinných míst)."""
    return f"{value:.2f}".rstrip("0").rstrip(".")


def document(width: float, height: float, body: str, title: str, style: str = "") -> str:
    style_block = f"<style>{style}</style>" if style else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(width)}" height="{fmt(height)}" '
        f'viewBox="0 0 {fmt(width)} {fmt(height)}" role="img" aria-label="{esc(title)}">'
        f"<title>{esc(title)}</title>{style_block}{body}</svg>\n"
    )


def card(width: float, height: float, title: str, body: str, theme: Theme, style: str = "") -> str:
    """Karta s rámečkem a nadpisem; obsah začíná zhruba na y = 56."""
    frame = (
        f'<rect x="0.5" y="0.5" width="{fmt(width - 1)}" height="{fmt(height - 1)}" rx="10" '
        f'fill="{theme.background}" stroke="{theme.border}"/>'
        f'<text x="24" y="36" font-family="{SANS}" font-size="17" font-weight="600" '
        f'fill="{theme.accent}">{esc(title)}</text>'
    )
    return document(width, height, frame + body, title, style)


# Výchozí stav je vždy viditelný; neviditelnost během zpoždění zajistí až fill-mode „both“.
# Bez podpory animací (nebo při prefers-reduced-motion) se tak obsah zobrazí rovnou.
REDUCED_MOTION_STYLE = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"

FADE_IN_STYLE = (
    "@keyframes fadeIn{from{opacity:0}to{opacity:1}}"
    ".fade{animation:fadeIn .6s ease-out both}" + REDUCED_MOTION_STYLE
)
