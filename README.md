# triecomplete

Dependency-free trie (prefix tree) autocomplete for Python, with frequency-ranked
suggestions and a small CLI. Pure standard library, Python 3.9+, no installation
beyond copying the module.

## What it does

- Stores words in a trie and answers "what words start with this prefix?" fast.
- Ranks suggestions by frequency: insert a word more often (or with a bigger
  count) and it floats to the top of its prefix completions. Ties break
  alphabetically.
- Supports membership tests, `startswith` prefix probes, deletion with
  pruning, and alphabetical iteration over all stored words.

## Quick start

```python
from triecomplete import Trie

trie = Trie()
trie.insert("apple", 1)
trie.insert("app", 50)
trie.insert("application", 10)

trie.autocomplete("app", 3)        # ['app', 'application', 'apple']
trie.autocomplete_with_counts("app", 1)  # [('app', 50)]
"app" in trie                      # True
trie.startswith("appl")            # True
trie.delete("apple")               # True
```

## CLI

```console
$ python cli.py --demo --prefix app
app
apple
application
apply

$ printf 'ant\t7\nark\t3\n' | python cli.py --prefix a --counts
ant	7
ark	3

$ python cli.py words.txt --prefix dat --limit 5
```

Word lists are one word per line; add a TAB and a number to seed a frequency
(`word<TAB>frequency`). Lines starting with `#` are ignored. Pipe a list on
stdin or pass a file path.

## API

| Method | Description |
| --- | --- |
| `insert(word, frequency=1)` | Add a word; re-inserting increases its frequency. |
| `autocomplete(prefix, limit=10)` | Up to `limit` completions, most frequent first. |
| `autocomplete_with_counts(prefix, limit=10)` | Same, as `(word, frequency)` pairs. |
| `startswith(prefix)` | True if any stored word begins with `prefix`. |
| `delete(word)` | Remove a word; returns True if it was present. |
| `words()` | Iterate every word in alphabetical order. |
| `len(trie)` | Number of distinct words. `word in trie` for membership. |
| `Trie.from_words(iterable)` | Build a trie from an iterable of words. |

## How it works

Each node stores its children, a terminal flag, the frequency of the word
ending there, and `best`, the highest frequency in its subtree. Prefix lookup
walks the prefix's path, then explores children best-first so the top-k
suggestions surface without sorting the whole subtree. Deletion prunes nodes
that no longer lead anywhere and recomputes the `best` pointers.

## Tests

```console
$ python -m unittest test_triecomplete -v
```

25 tests cover insertion, ranking, deletion, iteration, and the CLI.

## License

MIT — see [LICENSE](LICENSE).
