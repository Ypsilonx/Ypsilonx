"""Čisté výpočty nad daty z API – bez I/O, snadno testovatelné."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

from .models import ContributionDay, Repo

FALLBACK_LANGUAGE_COLOR = "#8b949e"


@dataclass(frozen=True)
class LanguageShare:
    name: str
    color: str
    percent: float


@dataclass(frozen=True)
class Streaks:
    current: int
    longest: int


def select_recent(repos: list[Repo] | tuple[Repo, ...], login: str, count: int) -> list[Repo]:
    """Naposledy aktivní repozitáře bez archivovaných a bez profilového repozitáře."""
    candidates = [r for r in repos if not r.archived and r.name.lower() != login.lower()]
    return sorted(candidates, key=lambda r: r.pushed_at, reverse=True)[:count]


def language_shares(
    repos: tuple[Repo, ...], top: int, exclude: frozenset[str] = frozenset()
) -> list[LanguageShare]:
    """Podíl jazyků podle velikosti kódu; vše za `top` se sloučí do položky „Other“."""
    sizes: dict[str, int] = defaultdict(int)
    colors: dict[str, str] = {}
    for repo in repos:
        if repo.archived:
            continue
        for lang in repo.languages:
            if lang.name in exclude:
                continue
            sizes[lang.name] += lang.size
            colors[lang.name] = lang.color or FALLBACK_LANGUAGE_COLOR
    total = sum(sizes.values())
    if not total:
        return []
    ranked = sorted(sizes.items(), key=lambda item: item[1], reverse=True)
    shares = [LanguageShare(n, colors[n], 100 * s / total) for n, s in ranked[:top]]
    rest = sum(s for _, s in ranked[top:])
    if rest:
        shares.append(LanguageShare("Other", FALLBACK_LANGUAGE_COLOR, 100 * rest / total))
    return shares


def streaks(calendar: tuple[ContributionDay, ...], today: date) -> Streaks:
    """Aktuální a nejdelší série dní s příspěvkem.

    Aktuální série se nepřeruší dnešním dnem bez příspěvku – den ještě neskončil.
    """
    days = sorted((d for d in calendar if d.day <= today), key=lambda d: d.day)
    longest = run = 0
    for day in days:
        run = run + 1 if day.count > 0 else 0
        longest = max(longest, run)

    current = 0
    for index, day in enumerate(reversed(days)):
        if day.count > 0:
            current += 1
        elif index == 0 and day.day == today:
            continue
        else:
            break
    return Streaks(current=current, longest=longest)


def weekly_totals(calendar: tuple[ContributionDay, ...], weeks: int) -> list[tuple[date, int]]:
    """Součty příspěvků po týdnech, posledních `weeks` týdnů.

    Týden začíná nedělí jako v kalendáři GitHubu; první a poslední týden může být neúplný.
    """
    buckets: dict[date, int] = defaultdict(int)
    for day in calendar:
        week_start = day.day - timedelta(days=(day.day.weekday() + 1) % 7)
        buckets[week_start] += day.count
    return sorted(buckets.items())[-weeks:]
