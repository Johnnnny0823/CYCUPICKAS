import json
import tempfile
import unittest
from pathlib import Path

from tools.build_course_summaries import merge_course
from tools.common import build_preview_url, build_syllabus_url
from tools.validate_course_summaries import validate_summary_data


class ToolTests(unittest.TestCase):
    def test_build_syllabus_url_escapes_course_code(self):
        self.assertEqual(
            build_syllabus_url("1142", " MI123H "),
            "https://cmap.cycu.edu.tw:8443/Syllabus/syllabus/outPutCoursePreView.action?yearTerm=1142&opCode=MI123H&langId=zh_TW",
        )

    def test_build_preview_url_uses_course_preview_page(self):
        self.assertEqual(
            build_preview_url("1142", " MI123H "),
            "https://cmap.cycu.edu.tw:8443/Syllabus/CoursePreview.html?yearTerm=1142&opCode=MI123H",
        )

    def test_manual_override_wins_and_marks_reviewed(self):
        seed = {"courseCode": "MI123H", "courseName": "資訊管理", "teacher": "王小明", "yearTerm": "1142"}
        parsed = {"plainSummary": "自動摘要", "courseOutputs": ["平時作業"], "grading": []}
        merged = merge_course(seed, parsed, {"plainSummary": "人工摘要"})
        self.assertEqual(merged["plainSummary"], "人工摘要")
        self.assertTrue(merged["manualReviewed"])
        self.assertEqual(merged["courseOutputs"], ["平時作業"])

    def test_validate_rejects_forbidden_words(self):
        data = {
            "metadata": {"yearTerm": "1142"},
            "courses": {
                "MI123H": {
                    "courseCode": "MI123H",
                    "courseName": "資訊管理",
                    "teacher": "王小明",
                    "syllabusUrl": build_syllabus_url("1142", "MI123H"),
                    "plainSummary": "這是一門甜課。",
                    "grading": [],
                }
            },
        }
        errors, warnings = validate_summary_data(data)
        self.assertTrue(any("禁止詞" in error for error in errors), warnings)


if __name__ == "__main__":
    unittest.main()


