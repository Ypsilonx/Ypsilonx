"""Konfigurace generátoru profilu – jediné místo s daty, která se ručně mění."""

from dataclasses import dataclass
from pathlib import Path

USERNAME = "Ypsilonx"

# Jazyk, který se zobrazí přímo na profilu (README.md). Druhý jazyk jde do README.<lang>.md.
DEFAULT_LANG = "en"
LANGS = ("en", "cs")

# Kolik naposledy aktivních repozitářů ukázat v tabulce a kolik týdnů zahrnout do sparkline.
RECENT_REPO_COUNT = 6
SPARKLINE_WEEKS = 12

# Kolik týdnů zobrazit v grafu aktivity a kolik jazyků v kartě jazyků.
ACTIVITY_WEEKS = 26
TOP_LANGUAGES = 6

# Jazyky, které se nezapočítávají do karty jazyků (např. vygenerované HTML).
LANGUAGE_EXCLUDE: frozenset[str] = frozenset()

# Repozitář je „aktivní“, pokud do něj přišel push za posledních N dní.
ACTIVE_DAYS = 14

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "templates"
SPARK_SUBDIR = Path("assets/spark")

HEADER_NAME = "Ypsilonx"
HEADER_LINES = {
    "en": (
        "Python developer",
        "Embedded · desktop apps · integrations",
        "From Wallachia to the digital world",
    ),
    "cs": (
        "Python vývojář",
        "Embedded · desktop aplikace · integrace",
        "Z Valašska do digitálního světa",
    ),
}


@dataclass(frozen=True)
class Tech:
    name: str
    color: str


@dataclass(frozen=True)
class TechGroup:
    title: dict[str, str]
    items: tuple[Tech, ...]


TECH_STACK: tuple[TechGroup, ...] = (
    TechGroup(
        {"en": "Daily", "cs": "Denně"},
        (
            Tech("Python", "#3776AB"),
            Tech("Tkinter", "#3776AB"),
            Tech("PyQt", "#41CD52"),
            Tech("SQLite", "#0F80CC"),
            Tech("Git", "#F05032"),
            Tech("VS Code", "#0078D4"),
        ),
    ),
    TechGroup(
        {"en": "At work", "cs": "V práci"},
        (
            Tech("C#", "#9B4F96"),
            Tech("VBScript", "#4A6FA5"),
            Tech("PowerShell", "#5391FE"),
        ),
    ),
    TechGroup(
        {"en": "Embedded", "cs": "Embedded"},
        (
            Tech("ESP32", "#E7352C"),
            Tech("Raspberry Pi Pico", "#C51A4A"),
            Tech("C++", "#00599C"),
            Tech("PlatformIO", "#F5822A"),
        ),
    ),
    TechGroup(
        {"en": "Exploring", "cs": "Zkoumám"},
        (
            Tech("Rust", "#DEA584"),
            Tech("Lua", "#000080"),
        ),
    ),
)


@dataclass(frozen=True)
class Contact:
    key: str
    label: str
    url: str
    color: str


CONTACTS: tuple[Contact, ...] = (
    Contact("linkedin", "LinkedIn", "https://www.linkedin.com/in/ypsilonxpython/", "#0A66C2"),
    Contact("discord", "Discord", "https://discord.com/users/311947085278740480", "#5865F2"),
)

LANG_EMOJI = {
    "Python": "🐍",
    "C#": "💜",
    "C++": "⚡",
    "Rust": "🦀",
    "Lua": "🌙",
    "PowerShell": "💠",
    "JavaScript": "📜",
    "TypeScript": "💙",
    "HTML": "🌐",
    "CSS": "🎨",
}
DEFAULT_LANG_EMOJI = "📁"
