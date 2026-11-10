import tempfile
import unittest
from pathlib import Path

from grep_lang.utilities import IMPLEMENTATIONS, run_utility


class TestUtilities(unittest.TestCase):
    def test_registry_count(self):
        self.assertEqual(len(IMPLEMENTATIONS), 20)

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


if __name__ == "__main__":
    unittest.main()
