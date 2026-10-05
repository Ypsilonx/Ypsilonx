"""Minimalistický klient GitHub GraphQL API nad standardní knihovnou (urllib)."""

import json
from dataclasses import replace
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from typing import Any

from .models import ContributionDay, Language, Profile, Repo
from .stats import select_recent

GRAPHQL_URL = "https://api.github.com/graphql"
TIMEOUT_S = 30
RETRIES = 3

_REPOS_QUERY = """
query($login: String!, $after: String) {
  user(login: $login) {
    repositories(first: 100, after: $after, ownerAffiliations: OWNER, isFork: false,
                 privacy: PUBLIC, orderBy: {field: PUSHED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        name url description isArchived pushedAt createdAt stargazerCount
        primaryLanguage { name }
        languages(first: 20, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""

_CONTRIBUTIONS_QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


class GitHubApiError(RuntimeError):
    """Chyba komunikace s API nebo chyba vrácená GraphQL serverem."""


class GitHubClient:
    def __init__(self, token: str) -> None:
        if not token:
            raise GitHubApiError("GraphQL API vyžaduje token (PROFILE_TOKEN nebo GITHUB_TOKEN).")
        self._token = token

    def query(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        body = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
        request = urllib.request.Request(
            GRAPHQL_URL,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
                "User-Agent": "profile-gen",
            },
        )
        payload = self._send_with_retry(request)
        if payload.get("errors"):
            messages = "; ".join(e.get("message", "?") for e in payload["errors"])
            raise GitHubApiError(f"GraphQL chyba: {messages}")
        return payload["data"]

    @staticmethod
    def _send_with_retry(request: urllib.request.Request) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(RETRIES):
            try:
                with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
                    return json.load(response)
            except urllib.error.HTTPError as exc:
                # 4xx (špatný token, chybný dotaz) opakováním nespravíme.
                if exc.code < 500:
                    detail = exc.read().decode("utf-8", errors="replace")[:500]
                    raise GitHubApiError(f"HTTP {exc.code}: {detail}") from exc
                last_error = exc
            except (urllib.error.URLError, TimeoutError) as exc:
                last_error = exc
            time.sleep(2 ** (attempt + 1))
        raise GitHubApiError(f"API nedostupné po {RETRIES} pokusech: {last_error}")


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _parse_repo(node: dict[str, Any]) -> Repo:
    languages = tuple(
        Language(edge["node"]["name"], edge["node"]["color"], edge["size"])
        for edge in node["languages"]["edges"]
    )
    primary = node["primaryLanguage"]
    return Repo(
        name=node["name"],
        url=node["url"],
        description=node["description"],
        primary_language=primary["name"] if primary else None,
        # Prázdný repozitář nemá pushedAt, použijeme datum vytvoření.
        pushed_at=_parse_dt(node["pushedAt"] or node["createdAt"]),
        stars=node["stargazerCount"],
        archived=node["isArchived"],
        languages=languages,
    )


def fetch_repos(client: GitHubClient, login: str) -> list[Repo]:
    repos: list[Repo] = []
    after: str | None = None
    while True:
        data = client.query(_REPOS_QUERY, {"login": login, "after": after})
        if data["user"] is None:
            raise GitHubApiError(f"Uživatel {login} neexistuje.")
        page = data["user"]["repositories"]
        repos.extend(_parse_repo(node) for node in page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            return repos
        after = page["pageInfo"]["endCursor"]


def fetch_contributions(client: GitHubClient, login: str) -> tuple[list[ContributionDay], int, int]:
    """Vrátí (kalendář po dnech, celkem příspěvků, celkem commitů) za posledních 12 měsíců."""
    data = client.query(_CONTRIBUTIONS_QUERY, {"login": login})
    collection = data["user"]["contributionsCollection"]
    calendar = collection["contributionCalendar"]
    days = [
        ContributionDay(date.fromisoformat(day["date"]), day["contributionCount"])
        for week in calendar["weeks"]
        for day in week["contributionDays"]
    ]
    return days, calendar["totalContributions"], collection["totalCommitContributions"]


def week_windows(now: datetime, weeks: int) -> list[tuple[datetime, datetime]]:
    """Klouzavá týdenní okna končící v `now`, od nejstaršího po nejnovější."""
    return [
        (now - timedelta(weeks=weeks - i), now - timedelta(weeks=weeks - i - 1))
        for i in range(weeks)
    ]


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_weekly_commits(
    client: GitHubClient, owner: str, repo_names: list[str], now: datetime, weeks: int
) -> dict[str, tuple[int, ...]]:
    """Počty commitů na výchozí větvi po týdnech – jeden dotaz s aliasy pro všechny repozitáře."""
    if not repo_names:
        return {}
    windows = week_windows(now, weeks)
    history = " ".join(
        f'w{i}: history(since: "{_iso(since)}", until: "{_iso(until)}") {{ totalCount }}'
        for i, (since, until) in enumerate(windows)
    )
    var_defs = ", ".join(f"$n{i}: String!" for i in range(len(repo_names)))
    repos = " ".join(
        f"r{i}: repository(owner: $owner, name: $n{i}) "
        f"{{ defaultBranchRef {{ target {{ ... on Commit {{ {history} }} }} }} }}"
        for i in range(len(repo_names))
    )
    query = f"query($owner: String!, {var_defs}) {{ {repos} }}"
    variables: dict[str, Any] = {"owner": owner}
    variables.update({f"n{i}": name for i, name in enumerate(repo_names)})
    data = client.query(query, variables)

    result: dict[str, tuple[int, ...]] = {}
    for i, name in enumerate(repo_names):
        ref = (data.get(f"r{i}") or {}).get("defaultBranchRef")
        target = ref["target"] if ref else None
        if not target:
            result[name] = (0,) * weeks
            continue
        result[name] = tuple(target[f"w{w}"]["totalCount"] for w in range(weeks))
    return result


def fetch_profile(client: GitHubClient, login: str, recent_count: int, weeks: int) -> Profile:
    now = datetime.now(timezone.utc)
    repos = fetch_repos(client, login)
    days, total_contributions, total_commits = fetch_contributions(client, login)

    recent = select_recent(repos, login, recent_count)
    weekly = fetch_weekly_commits(client, login, [r.name for r in recent], now, weeks)
    enriched = tuple(
        replace(r, weekly_commits=weekly[r.name]) if r.name in weekly else r for r in repos
    )
    return Profile(
        repos=enriched,
        calendar=tuple(days),
        total_contributions=total_contributions,
        total_commits=total_commits,
        generated_at=now,
    )
