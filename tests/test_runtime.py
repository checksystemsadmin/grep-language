import unittest
from grep_lang.runtime import execute

class TestGrepRuntime(unittest.TestCase):
    def test_print(self):
        self.assertEqual(execute('print "Hello"'), ["Hello"])

    def test_variable(self):
        source = 'let name = "GREP"\nprint $name'
        self.assertEqual(execute(source), ["GREP"])

    def test_comments(self):
        self.assertEqual(
            execute('# comment\nprint "Works"'),
            ["Works"]
        )

    def test_unknown_instruction(self):
        with self.assertRaises(ValueError):
            execute("unknown command")

if __name__ == "__main__":
    unittest.main()
