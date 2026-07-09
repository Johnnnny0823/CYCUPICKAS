from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8-sig")


class ExtensionUiContractTests(unittest.TestCase):
    def test_filter_bar_omits_redundant_parsed_filter(self):
        content = read("extension/content.js")
        self.assertNotIn("課綱已解析", content)
        self.assertNotIn('data-filter="parsed"', content)

    def test_compare_table_expands_grading_and_uses_time_fallbacks(self):
        content = read("extension/content.js")
        self.assertIn("function displayCourseTime", content)
        self.assertIn("依實習單位指定", content)
        self.assertIn("依指導老師排定", content)
        self.assertIn("非同步遠距", content)
        self.assertNotIn("compactCell(cell)", content)

    def test_blue_syllabus_button_keeps_white_text(self):
        styles = read("extension/styles.css")
        self.assertIn(".aiwatch-link-button", styles)
        self.assertIn("color: #fff !important", styles)


if __name__ == "__main__":
    unittest.main()
