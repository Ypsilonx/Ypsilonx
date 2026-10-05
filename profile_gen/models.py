"""Datové struktury předávané mezi API vrstvou, výpočty a renderem."""

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass(frozen=True)
class Language:
    name: str
    color: str | None
    size: int


@dataclass(frozen=True)
class Repo:
    name: str
    url: str
    description: str | None
    primary_language: str | None
    pushed_at: datetime
    stars: int
    archived: bool
    languages: tuple[Language, ...] = ()
    # Počty commitů na výchozí větvi po týdnech, od nejstaršího po nejnovější.
    weekly_commits: tuple[int, ...] = ()


@dataclass(frozen=True)
class ContributionDay:
    day: date
    count: int


@dataclass(frozen=True)
class Profile:
    repos: tuple[Repo, ...]
    calendar: tuple[ContributionDay, ...]
    total_contributions: int
    total_commits: int
    generated_at: datetime = field(compare=False)
