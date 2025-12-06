# Local Offline Note Search Engine

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

A fast, dependency-free command-line search tool for local text and Markdown notes.
The system builds an inverted index to support efficient queries, including keyword search, exact phrase search, AND/OR logic, and contextual snippet extraction.

This project demonstrates text processing, stopword filtering, boolean search evaluation, and search-engine index structures—all implemented with the Python standard library.

---

## Features

* Search across all `.txt` and `.md` files in the `notes/` directory
* Inverted index with word-position tracking
* Stopword filtering for cleaner, more meaningful indexing
* Exact phrase search using `"` quotes
* OR search using the `OR` keyword
* AND logic applied automatically within query groups
* Relevance ranking based on term frequency
* Snippet extraction with highlighted keyword matches
* Zero third-party dependencies

---

## Project Structure

```
/
├── index.py              # Builds the inverted index
├── search.py             # Executes keyword, phrase, AND/OR search queries
├── utils.py              # Tokenization and stopword utilities
├── inverted_index.json   # Generated index file
└── notes/                # User-provided notes (.txt and .md)
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

Ensure Python 3.8 or newer is installed.

Populate the `notes/` folder:

Add any `.txt` or `.md` files you want indexed.

---

## Building the Index

Run:

```bash
python3 index.py
```

Indexing will:

* Recursively scan the `notes/` directory
* Tokenize content and remove stopwords
* Build a word → filepath → positions mapping
* Save the index to `inverted_index.json`

Re-run this script any time you modify files in the `notes/` directory.

---

## Running Searches

### Keyword Search

```bash
python3 search.py mitochondria
```

### Exact Phrase Search

```bash
python3 search.py "cellular respiration"
```

### OR Search

```bash
python3 search.py biology OR chemistry
```

### Combined Query Example

```bash
python3 search.py "citric acid cycle" OR glycolysis energy
```

---

## Example Output

```
Searching for: 'cellular respiration'

Found 2 matching notes:

--- biology.md (Score: 12) ---
...organisms generate energy through cellular respiration in the mitochondria...
------------------------------------

--- unit3_summary.txt (Score: 7) ---
...ATP production increases during cellular respiration...
------------------------------------
```

---

## Query Logic Overview

* **Quoted text** = exact phrase (consecutive words)
* **OR** separates groups of search conditions
* Words within a group use **implicit AND**
* Stopwords are removed during tokenization
* Scoring is based on total term frequency across all matched terms

Examples:

| Query                                      | Interpretation                    |
| ------------------------------------------ | --------------------------------- |
| `photosynthesis chlorophyll`               | chlorophyll AND photosynthesis    |
| `"cellular respiration" ATP`               | phrase AND ATP                    |
| `biology OR chemistry`                     | biology OR chemistry              |
| `"citric acid cycle" OR glycolysis energy` | phrase OR (glycolysis AND energy) |

---

## How It Works

### Tokenization

`tokenize_text()` converts text to lowercase, extracts alphanumeric tokens, and removes common English stopwords.

### Inverted Index

Maps words to:

```
word → {
    filepath: [positions]
}
```

Positions are word indices inside each document, enabling phrase detection by checking consecutive positions.

### Query Parsing

The parser:

1. Splits on `OR` to create OR-groups
2. Extracts quoted phrases
3. Tokenizes remaining words
4. Applies AND logic inside each OR-group

### Phrase Search

A phrase matches only if all words in the phrase appear consecutively in a file.

### Snippet Extraction

The search engine:

* Reloads the raw file from disk
* Locates the first matched keyword or phrase
* Extracts ~150 characters of surrounding context
* Highlights the matched terms inside the snippet

---

## Requirements

* Python 3.8 or later
* Terminal with ANSI escape code support

---

## License

This project is licensed under the MIT License.

---
