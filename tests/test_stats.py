import unittest
from datetime import date, timedelta

from profile_gen.models import ContributionDay
from profile_gen.stats import language_shares, select_recent, streaks, weekly_totals
from tests.fixtures import sample_profile


def _calendar(counts: list[int], end: date) -> tuple[ContributionDay, ...]:
    start = end - timedelta(days=len(counts) - 1)
    return tuple(ContributionDay(start + timedelta(days=i), c) for i, c in enumerate(counts))


class StreakTests(unittest.TestCase):
    TODAY = date(2026, 10, 5)

    def test_today_without_contribution_does_not_break_streak(self):
        result = streaks(_calendar([1, 1, 1, 0], self.TODAY), self.TODAY)
        self.assertEqual(result.current, 3)

    def test_yesterday_without_contribution_breaks_streak(self):
        result = streaks(_calendar([1, 1, 0, 0], self.TODAY), self.TODAY)
        self.assertEqual(result.current, 0)

    def test_longest_streak(self):
        result = streaks(_calendar([1, 1, 1, 1, 0, 1, 1], self.TODAY), self.TODAY)
        self.assertEqual((result.current, result.longest), (2, 4))

    def test_future_days_are_ignored(self):
        calendar = _calendar([1, 1, 0], self.TODAY + timedelta(days=1))
        self.assertEqual(streaks(calendar, self.TODAY).current, 2)


class WeeklyTotalsTests(unittest.TestCase):
    def test_weeks_start_on_sunday(self):
        # 2026-10-03 je sobota, 2026-10-04 neděle.
        calendar = _calendar([2, 3, 5], date(2026, 10, 5))
        self.assertEqual(
            weekly_totals(calendar, 10),
            [(date(2026, 9, 27), 2), (date(2026, 10, 4), 8)],
        )

    def test_limits_number_of_weeks(self):
        calendar = _calendar([1] * 70, date(2026, 10, 5))
        self.assertEqual(len(weekly_totals(calendar, 4)), 4)


class LanguageShareTests(unittest.TestCase):
    def test_shares_sum_to_hundred_and_skip_archived(self):
        shares = language_shares(sample_profile().repos, top=2)
        self.assertAlmostEqual(sum(s.percent for s in shares), 100.0)
        self.assertNotIn("C#", [s.name for s in shares])
        self.assertEqual(shares[-1].name, "Other")

    def test_exclude(self):
        shares = language_shares(sample_profile().repos, top=5, exclude=frozenset({"Python"}))
        self.assertNotIn("Python", [s.name for s in shares])

    def test_empty(self):
        self.assertEqual(language_shares((), top=3), [])


class SelectRecentTests(unittest.TestCase):
    def test_skips_archived_and_profile_repo(self):
        names = [r.name for r in select_recent(sample_profile().repos, "ypsilonx", 10)]
        self.assertNotIn("old_archived", names)
        self.assertNotIn("Ypsilonx", names)
        self.assertEqual(names[0], "factorio_loader-unloader")


if __name__ == "__main__":
    unittest.main()
