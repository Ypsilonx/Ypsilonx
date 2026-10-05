"""Vstupní bod: python -m profile_gen

Stáhne data z GitHub GraphQL API, vygeneruje README.md, README.<lang>.md a SVG do assets/.
Soubory zapisuje až po úspěšném sestavení všech výstupů; při chybě skončí nenulovým kódem.
"""

import os
import sys
from pathlib import Path

from . import config
from .build import build_outputs
from .github_api import GitHubApiError, GitHubClient, fetch_profile
from .readme import TemplateError


def load_templates() -> dict[str, str]:
    return {
        f"README.{lang}.md": (config.TEMPLATES_DIR / f"README.{lang}.md").read_text(encoding="utf-8")
        for lang in config.LANGS
    }


def write_outputs(outputs: dict[Path, str], root: Path) -> list[Path]:
    """Zapíše jen změněné soubory a smaže sparkline repozitářů, které už nejsou v tabulce."""
    changed: list[Path] = []
    for relative, content in outputs.items():
        target = root / relative
        if target.exists() and target.read_text(encoding="utf-8") == content:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")
        changed.append(relative)

    expected = {root / path for path in outputs}
    spark_dir = root / config.SPARK_SUBDIR
    if spark_dir.exists():
        for stale in spark_dir.glob("*.svg"):
            if stale not in expected:
                stale.unlink()
                changed.append(stale.relative_to(root))
    return changed


def main() -> int:
    token = os.environ.get("PROFILE_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
    try:
        client = GitHubClient(token)
        profile = fetch_profile(client, config.USERNAME, config.RECENT_REPO_COUNT, config.SPARKLINE_WEEKS)
        outputs = build_outputs(profile, load_templates())
    except (GitHubApiError, TemplateError, OSError) as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1

    changed = write_outputs(outputs, config.REPO_ROOT)
    print(f"Repozitářů: {len(profile.repos)}, změněných souborů: {len(changed)}")
    for path in changed:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
