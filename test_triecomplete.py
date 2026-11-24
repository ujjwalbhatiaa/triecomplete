import io
import unittest
from contextlib import redirect_stdout

from triecomplete import Trie, demo_words
import cli


class TestTrieBasics(unittest.TestCase):
    def test_insert_and_membership(self):
        t = Trie()
        t.insert("apple")
        self.assertIn("apple", t)
        self.assertNotIn("app", t)
        self.assertNotIn("apples", t)

    def test_len_counts_distinct_words(self):
        t = Trie.from_words(["a", "ab", "a", "abc"])
        self.assertEqual(len(t), 3)

    def test_empty_word_rejected(self):
        t = Trie()
        with self.assertRaises(ValueError):
            t.insert("")

    def test_bad_frequency_rejected(self):
        t = Trie()
        with self.assertRaises(ValueError):
            t.insert("word", 0)

    def test_startswith(self):
        t = Trie.from_words(["canada"])
        self.assertTrue(t.startswith("can"))
        self.assertTrue(t.startswith("canada"))
        self.assertFalse(t.startswith("canadian"))
        self.assertFalse(t.startswith("x"))

    def test_reinsertion_increases_frequency(self):
        t = Trie()
        t.insert("data", 3)
        t.insert("data", 4)
        self.assertEqual(t.autocomplete_with_counts("data")[0], ("data", 7))


class TestAutocomplete(unittest.TestCase):
    def setUp(self):
        self.t = Trie.from_words(demo_words())

    def test_prefix_matches(self):
        self.assertEqual(
            set(self.t.autocomplete("app", 10)),
            {"app", "apple", "application", "apply"},
        )

    def test_no_match_returns_empty(self):
        self.assertEqual(self.t.autocomplete("zzz"), [])

    def test_empty_prefix_ranks_all(self):
        self.assertEqual(len(self.t.autocomplete("", 100)), len(self.t))

    def test_limit_respected(self):
        self.assertEqual(len(self.t.autocomplete("a", 2)), 2)

    def test_zero_limit_returns_empty(self):
        self.assertEqual(self.t.autocomplete("a", 0), [])

    def test_frequency_ranking(self):
        t = Trie()
        t.insert("apple", 1)
        t.insert("app", 50)
        t.insert("application", 10)
        self.assertEqual(t.autocomplete("app", 3), ["app", "application", "apple"])

    def test_tie_breaks_alphabetically(self):
        t = Trie()
        for w in ["beta", "alpha", "gamma"]:
            t.insert(w, 5)
        self.assertEqual(t.autocomplete("", 3), ["alpha", "beta", "gamma"])

    def test_counts_returned(self):
        t = Trie()
        t.insert("word", 9)
        self.assertEqual(t.autocomplete_with_counts("w"), [("word", 9)])

    def test_exact_word_is_included(self):
        self.assertIn("app", self.t.autocomplete("app"))


class TestDelete(unittest.TestCase):
    def test_delete_existing(self):
        t = Trie.from_words(["apple", "app"])
        self.assertTrue(t.delete("apple"))
        self.assertNotIn("apple", t)
        self.assertIn("app", t)

    def test_delete_missing_returns_false(self):
        t = Trie.from_words(["apple"])
        self.assertFalse(t.delete("apples"))
        self.assertFalse(t.delete(""))

    def test_delete_updates_len(self):
        t = Trie.from_words(["a", "ab"])
        t.delete("a")
        self.assertEqual(len(t), 1)

    def test_delete_preserves_shared_prefix_words(self):
        t = Trie.from_words(["canada", "canary"])
        t.delete("canada")
        self.assertEqual(t.autocomplete("can"), ["canary"])

    def test_ranking_after_delete(self):
        t = Trie()
        t.insert("app", 100)
        t.insert("apple", 1)
        t.delete("app")
        self.assertEqual(t.autocomplete("app", 1), ["apple"])


class TestWordsIterator(unittest.TestCase):
    def test_words_sorted(self):
        t = Trie.from_words(["banana", "apple", "cherry"])
        self.assertEqual(list(t.words()), ["apple", "banana", "cherry"])


class TestCLI(unittest.TestCase):
    def run_cli(self, argv, stdin_text=""):
        out = io.StringIO()
        import sys
        old_stdin = sys.stdin
        sys.stdin = io.StringIO(stdin_text)
        try:
            with redirect_stdout(out):
                code = cli.main(argv)
        finally:
            sys.stdin = old_stdin
        return code, out.getvalue()

    def test_demo_prefix(self):
        code, out = self.run_cli(["--demo", "-p", "app"])
        self.assertEqual(code, 0)
        self.assertIn("apple", out)

    def test_stdin_wordlist(self):
        code, out = self.run_cli(["-p", "tr"], "tree\ntrie\nother\n")
        self.assertEqual(code, 0)
        self.assertEqual(sorted(out.split()), ["tree", "trie"])

    def test_counts_flag(self):
        code, out = self.run_cli(["-p", "a", "-c"], "ant\t7\nark\t3\n")
        self.assertEqual(out.splitlines()[0], "ant\t7")

    def test_no_match_exit_code(self):
        code, _ = self.run_cli(["-p", "zzz"], "apple\n")
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
