import re
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from profile_gen import config
from profile_gen.build import build_outputs
from profile_gen.github_api import week_windows
from profile_gen.i18n import format_date, format_number
from profile_gen.markdown import escape_md
from profile_gen.readme import TemplateError, render_template
from tests.fixtures import sample_profile


def _templates() -> dict[str, str]:
    return {
        f"README.{lang}.md": (config.TEMPLATES_DIR / f"README.{lang}.md").read_text(encoding="utf-8")
        for lang in config.LANGS
    }


class BuildOutputsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = build_outputs(sample_profile(), _templates())

    def test_all_svgs_are_well_formed_xml(self):
        svgs = [p for p in self.outputs if p.suffix == ".svg"]
        self.assertTrue(svgs)
        for path in svgs:
            with self.subTest(path=str(path)):
                ET.fromstring(self.outputs[path])

    def test_every_referenced_asset_is_generated(self):
        generated = {str(p) for p in self.outputs}
        for lang in config.LANGS:
            readme = self.outputs[next(p for p in self.outputs if p.name == self._readme(lang))]
            for ref in re.findall(r'(?:src|srcset)="(assets/[^"]+)"', readme):
                with self.subTest(lang=lang, ref=ref):
                    self.assertIn(ref, generated)

    def test_no_placeholders_left(self):
        for lang in config.LANGS:
            readme = self.outputs[next(p for p in self.outputs if p.name == self._readme(lang))]
            self.assertNotIn("{{", readme)

    def test_default_language_goes_to_readme_md(self):
        names = {p.name for p in self.outputs if p.suffix == ".md"}
        self.assertIn("README.md", names)
        self.assertEqual(len(names), len(config.LANGS))

    def test_description_is_escaped_in_table(self):
        readme = next(v for p, v in self.outputs.items() if p.name == "README.md")
        self.assertIn(r"komunikace \| bezpečnost \*v jednom\*", readme)

    def test_support_link_in_every_language(self):
        for lang in config.LANGS:
            readme = self.outputs[next(p for p in self.outputs if p.name == self._readme(lang))]
            with self.subTest(lang=lang):
                self.assertIn(f'<a href="{config.SUPPORT.url}">', readme)

    @staticmethod
    def _readme(lang: str) -> str:
        return "README.md" if lang == config.DEFAULT_LANG else f"README.{lang}.md"


class TemplateTests(unittest.TestCase):
    def test_unknown_placeholder_raises(self):
        with self.assertRaises(TemplateError):
            render_template("{{nope}}", "en", {}, frozenset(), frozenset())

    def test_unknown_picture_raises(self):
        with self.assertRaises(TemplateError):
            render_template("{{picture:nope|alt}}", "en", {}, frozenset(), frozenset())

    def test_localized_picture(self):
        out = render_template("{{picture:header|Hi|100%}}", "cs", {}, frozenset({"header"}),
                              frozenset({"header"}))
        self.assertIn('srcset="assets/header.cs.dark.svg"', out)
        self.assertIn('src="assets/header.cs.light.svg"', out)
        self.assertIn('width="100%"', out)


class FormattingTests(unittest.TestCase):
    def test_numbers(self):
        self.assertEqual(format_number("en", 8876), "8,876")
        self.assertEqual(format_number("cs", 8876), "8 876")

    def test_dates(self):
        day = datetime(2026, 10, 2).date()
        self.assertEqual(format_date("en", day), "Oct 2, 2026")
        self.assertEqual(format_date("cs", day), "2. 10. 2026")

    def test_escape_md(self):
        self.assertEqual(escape_md("a|b*c_<x>"), r"a\|b\*c\_&lt;x&gt;")

    def test_week_windows_are_contiguous_and_end_now(self):
        now = datetime(2026, 10, 5, tzinfo=timezone.utc)
        windows = week_windows(now, 3)
        self.assertEqual(windows[-1][1], now)
        for (_, end), (start, _) in zip(windows, windows[1:]):
            self.assertEqual(end, start)


if __name__ == "__main__":
    unittest.main()
