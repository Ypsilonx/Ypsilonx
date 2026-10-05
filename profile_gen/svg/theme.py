"""Barevné palety pro světlý a tmavý režim GitHubu."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    name: str
    background: str
    border: str
    text: str
    muted: str
    accent: str
    accent2: str
    track: str


DARK = Theme(
    name="dark",
    background="#0d1117",
    border="#30363d",
    text="#e6edf3",
    muted="#8b949e",
    accent="#00d4ff",
    accent2="#a371f7",
    track="#21262d",
)

LIGHT = Theme(
    name="light",
    background="#ffffff",
    border="#d0d7de",
    text="#1f2328",
    muted="#656d76",
    accent="#0969da",
    accent2="#8250df",
    track="#eaeef2",
)

THEMES = (DARK, LIGHT)
