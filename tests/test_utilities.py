import tempfile
import unittest
from pathlib import Path

from grep_lang.utilities import IMPLEMENTATIONS, run_utility


class TestUtilities(unittest.TestCase):
    def test_registry_count(self):
        self.assertEqual(len(IMPLEMENTATIONS), 40)

    def test_file_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "a.txt").write_text("GREP")
            result = run_utility("file_hasher", {"path": "a.txt"}, directory)
            self.assertEqual(len(result["digest"]), 64)

    def test_json_validator(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "a.json").write_text('{"ok":true}')
            self.assertTrue(
                run_utility("json_validator", {"path": "a.json"}, directory)["valid"]
            )

    def test_path_traversal(self):
        with self.assertRaises(ValueError):
            run_utility("file_hasher", {"path": "../outside.txt"})

    def test_normalizer(self):
        self.assertEqual(
            run_utility("text_normalizer", {"text": "GREP, Hello!"}),
            "grep hello",
        )

    def test_chunker(self):
        self.assertEqual(
            run_utility("text_chunker", {
                "text": "abcdefgh", "chunk_size": 4, "overlap": 1
            }),
            ["abcd", "defg", "gh"],
        )

    def test_unknown_utility(self):
        with self.assertRaises(KeyError):
            run_utility("not_real")


    def test_batch2_registry(self):
        expected = {
            "directory_size", "duplicate_finder", "large_file_finder",
            "empty_file_finder", "file_age_analyzer", "permission_auditor",
            "symlink_inspector", "archive_inspector", "encoding_detector",
            "line_counter", "extension_report", "git_change_analyzer",
            "git_blame_reader", "source_file_classifier",
            "code_symbol_extractor", "import_graph", "dead_file_detector",
            "project_tree", "file_diff_engine", "file_snapshot",
        }
        self.assertTrue(expected.issubset(IMPLEMENTATIONS))

    def test_directory_size_and_line_counter(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "sample.txt").write_text("one\ntwo\n")
            self.assertEqual(
                run_utility("directory_size", {"path": "."}, directory)["file_count"],
                1,
            )
            result = run_utility("line_counter", {"path": "sample.txt"}, directory)
            self.assertEqual(result["lines"], 2)

    def test_duplicate_finder(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "a.txt").write_text("same")
            Path(directory, "b.txt").write_text("same")
            result = run_utility("duplicate_finder", {"path": "."}, directory)
            self.assertEqual(len(result), 1)
            self.assertEqual(len(result[0]["files"]), 2)

    def test_encoding_detector(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "utf.txt").write_text("hello", encoding="utf-8")
            result = run_utility("encoding_detector", {"path": "utf.txt"}, directory)
            self.assertEqual(result["encoding"], "utf-8-sig")

    def test_file_diff_engine(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "a.txt").write_text("old\n")
            Path(directory, "b.txt").write_text("new\n")
            result = run_utility(
                "file_diff_engine",
                {"path_a": "a.txt", "path_b": "b.txt"},
                directory,
            )
            self.assertTrue(any("-old" in line for line in result))
            self.assertTrue(any("+new" in line for line in result))

    def test_python_symbol_extractor(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "sample.py").write_text(
                "class Example:\n    def run(self):\n        pass\n"
            )
            result = run_utility(
                "code_symbol_extractor", {"path": "sample.py"}, directory
            )
            names = {item["name"] for item in result}
            self.assertEqual(names, {"Example", "run"})

    def test_file_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "a.txt").write_text("GREP")
            result = run_utility("file_snapshot", {"path": "a.txt"}, directory)
            self.assertEqual(len(result["sha256"]), 64)
            self.assertEqual(result["size_bytes"], 4)


if __name__ == "__main__":
    unittest.main()
