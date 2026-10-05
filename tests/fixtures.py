"""Ukázková data profilu pro testy a lokální náhled bez přístupu k API."""

from datetime import date, datetime, timedelta, timezone

from profile_gen.models import ContributionDay, Language, Profile, Repo

NOW = datetime(2026, 10, 5, 10, 0, tzinfo=timezone.utc)


def _repo(name: str, lang: str, color: str, size: int, days_ago: int, weekly: tuple[int, ...],
          description: str | None = None, archived: bool = False) -> Repo:
    return Repo(
        name=name,
        url=f"https://github.com/Ypsilonx/{name}",
        description=description,
        primary_language=lang,
        pushed_at=NOW - timedelta(days=days_ago),
        stars=1,
        archived=archived,
        languages=(Language(lang, color, size),),
        weekly_commits=weekly,
    )


def sample_profile() -> Profile:
    repos = (
        _repo("factorio_loader-unloader", "Lua", "#000080", 90_000, 3, (0, 0, 0, 0, 0, 0, 0, 0, 2, 9, 14, 6)),
        _repo("ThermoControl_LG_POER_app", "Python", "#3572A5", 400_000, 4,
              (3, 5, 0, 2, 8, 12, 4, 0, 6, 9, 3, 7), "vlastní aplikace na ovládání LG klimatizace"),
        _repo("widget_windows_10", "Python", "#3572A5", 30_000, 8, (0,) * 10 + (4, 2)),
        _repo("Rally-safety-organization-app", "Python", "#3572A5", 500_000, 30,
              (10, 14, 8, 6, 2, 0, 1, 0, 0, 0, 0, 0), "Komisař, Vedení RZ - komunikace | bezpečnost *v jednom*."),
        _repo("StartupDashboard", "PowerShell", "#012456", 25_000, 41, (0,) * 12),
        _repo("CAR_communication_simulator_app", "Python", "#3572A5", 120_000, 42, (0,) * 12),
        _repo("old_archived", "C#", "#178600", 80_000, 1, (0,) * 12, archived=True),
        _repo("Ypsilonx", "Python", "#3572A5", 10_000, 0, (0,) * 12),
    )
    start = date(2025, 10, 5)
    calendar = tuple(
        ContributionDay(start + timedelta(days=i), (i * 7) % 5 if i % 9 else 0)
        for i in range(366)
    )
    return Profile(
        repos=repos,
        calendar=calendar,
        total_contributions=sum(d.count for d in calendar),
        total_commits=612,
        generated_at=NOW,
    )
