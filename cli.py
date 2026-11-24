#!/usr/bin/env python3
"""Command-line interface for triecomplete.

Usage:
    python cli.py words.txt --prefix app --limit 5
    python cli.py --demo --prefix can
    cat words.txt | python cli.py --prefix dat

Word lists are plain text, one word per line. Optionally each line may be
"word<TAB>frequency" to seed ranking counts.
"""

from __future__ import annotations

import argparse
import sys

from triecomplete import Trie, demo_words


def load_trie(path: str | None, demo: bool) -> Trie:
    t = Trie()
    if demo:
        words = demo_words()
    else:
        src = open(path, encoding="utf-8") if path else sys.stdin
        with src:
            words = src.read().splitlines()
    for line in words:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "\t" in line:
            word, _, freq = line.partition("\t")
            t.insert(word.strip().lower(), int(freq))
        else:
            t.insert(line.lower())
    return t


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Trie autocomplete: prefix search with frequency ranking.")
    p.add_argument("wordlist", nargs="?", help="word list file (one word per line; '-' or omit for stdin)")
    p.add_argument("--demo", action="store_true", help="use the built-in demo word list")
    p.add_argument("--prefix", "-p", default="", help="prefix to complete (default: list all)")
    p.add_argument("--limit", "-n", type=int, default=10, help="max suggestions (default 10)")
    p.add_argument("--counts", "-c", action="store_true", help="show frequencies next to words")
    args = p.parse_args(argv)

    if not args.demo and not args.wordlist and sys.stdin.isatty():
        p.error("provide a word list file, pipe words on stdin, or use --demo")

    trie = load_trie(None if args.wordlist in (None, "-") else args.wordlist, args.demo)
    matches = trie.autocomplete_with_counts(args.prefix.lower(), args.limit)
    if not matches:
        print(f"no words start with {args.prefix!r}", file=sys.stderr)
        return 1
    for word, freq in matches:
        print(f"{word}\t{freq}" if args.counts else word)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
