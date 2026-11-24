"""triecomplete: dependency-free trie (prefix tree) autocomplete.

A compact, well-tested implementation of a frequency-ranked trie for
prefix search and autocomplete, with a command-line interface.

Pure standard library; Python 3.9+.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Iterator, List, Optional, Tuple


@dataclass
class _Node:
    children: Dict[str, "_Node"] = field(default_factory=dict)
    terminal: bool = False
    frequency: int = 0          # number of times the word ending here was inserted
    best: int = 0               # max frequency in this subtree (for ranked search)


class Trie:
    """Frequency-ranked trie supporting autocomplete queries."""

    def __init__(self) -> None:
        self._root = _Node()
        self._size = 0

    def __len__(self) -> int:
        """Number of distinct words stored."""
        return self._size

    def __contains__(self, word: str) -> bool:
        node = self._find(word)
        return node is not None and node.terminal

    def insert(self, word: str, frequency: int = 1) -> None:
        """Insert *word*, adding *frequency* to its count.

        Inserting an existing word increases its frequency, which affects
        ranking in :meth:`autocomplete`.
        """
        if not word:
            raise ValueError("cannot insert an empty word")
        if frequency < 1:
            raise ValueError("frequency must be >= 1")
        node = self._root
        for ch in word:
            node = node.children.setdefault(ch, _Node())
        if not node.terminal:
            self._size += 1
        node.terminal = True
        node.frequency += frequency
        self._recompute_best()

    def _find(self, prefix: str) -> Optional[_Node]:
        node = self._root
        for ch in prefix:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node

    def startswith(self, prefix: str) -> bool:
        """True if any stored word begins with *prefix*."""
        return self._find(prefix) is not None

    def delete(self, word: str) -> bool:
        """Remove *word*. Returns True if the word was present."""
        path: List[Tuple[_Node, str]] = []
        node = self._root
        for ch in word:
            if ch not in node.children:
                return False
            path.append((node, ch))
            node = node.children[ch]
        if not node.terminal:
            return False
        node.terminal = False
        node.frequency = 0
        self._size -= 1
        # prune nodes no longer needed, walking back up
        for parent, ch in reversed(path):
            child = parent.children[ch]
            if child.terminal or child.children:
                break
            del parent.children[ch]
        self._recompute_best()
        return True

    def _recompute_best(self) -> None:
        def rec(n: _Node) -> int:
            best = n.frequency if n.terminal else 0
            for c in n.children.values():
                best = max(best, rec(c))
            n.best = best
            return best
        rec(self._root)

    def autocomplete(self, prefix: str, limit: int = 10) -> List[str]:
        """Up to *limit* words starting with *prefix*, most frequent first.

        Ties break alphabetically. An empty prefix ranks all words.
        """
        return [w for w, _ in self.autocomplete_with_counts(prefix, limit)]

    def autocomplete_with_counts(self, prefix: str, limit: int = 10) -> List[Tuple[str, int]]:
        """Like :meth:`autocomplete` but returns (word, frequency) pairs."""
        if limit < 1:
            return []
        start = self._find(prefix)
        if start is None:
            return []
        results: List[Tuple[str, int]] = []

        def walk(node: _Node, path: List[str]) -> None:
            if len(results) >= limit:
                return
            # visit children in best-first order for early termination quality
            for ch, child in sorted(node.children.items(), key=lambda kv: (-kv[1].best, kv[0])):
                path.append(ch)
                if child.terminal:
                    results.append(("".join(path), child.frequency))
                    if len(results) >= limit:
                        path.pop()
                        break
                walk(child, path)
                path.pop()
            else:
                return

        buf = list(prefix)
        if start.terminal:
            results.append((prefix, start.frequency))
        walk(start, buf)
        results.sort(key=lambda wf: (-wf[1], wf[0]))
        return results[:limit]

    def words(self) -> Iterator[str]:
        """Yield all words in alphabetical order."""
        def rec(node: _Node, path: List[str]) -> Iterator[str]:
            if node.terminal:
                yield "".join(path)
            for ch in sorted(node.children):
                yield from rec(node.children[ch], path + [ch])
        yield from rec(self._root, [])

    @classmethod
    def from_words(cls, words: Iterable[str]) -> "Trie":
        t = cls()
        for w in words:
            w = w.strip()
            if w:
                t.insert(w.lower())
        return t


def demo_words() -> List[str]:
    return [
        "apple", "app", "application", "apply", "ape", "banana", "band",
        "bandana", "can", "canada", "canary", "candidate", "data",
        "database", "dataframe", "python", "trie", "tree", "triecomplete",
    ]
