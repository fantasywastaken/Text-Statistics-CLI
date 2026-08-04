# Text Statistics CLI

A polished command-line utility that reads a text file (or stdin) and prints a rich report of word, character, sentence, and readability statistics, plus the most common and longest words.

---

### How It Works

- **Input handling**: Reads a UTF-8 file path or pipes text from stdin (`cat file.txt | python main.py`).
- **Tokenization**: Splits words with a Unicode-aware regex and counts sentences by terminal punctuation (`.!?`).
- **Overview table**: Word count, character count (with and without whitespace), line count, sentence count, and average word / sentence length.
- **Readability table**: Powered by `textstat` and includes Flesch Reading Ease, Flesch-Kincaid grade, Gunning Fog, SMOG, Automated Readability, Coleman-Liau, difficult-word count, and a consensus grade estimate.
- **Top words**: Ranks the most common words (default 20). A built-in stopword list is applied unless `--include-stopwords` is passed.
- **Longest words**: Ranks the longest unique words (default 10) by length.
- **Colored output**: Uses `rich` for panels and tables, so results are readable in any modern terminal.

---

## Setup

### Requirements

- Python 3.10 or newer
- Dependencies listed in `requirements.txt`

### Installation

```bash
git clone https://github.com/yourname/Text-Statistics-CLI.git
cd Text-Statistics-CLI
pip install -r requirements.txt
```

---

### Usage

```bash
python main.py article.txt
python main.py article.txt --top-words 30 --longest 15
python main.py article.txt --include-stopwords
cat speech.md | python main.py
python main.py - < notes.txt
```

Example output:

```
Statistics for article.txt

              Text Overview
+-----------------------------+---------+
| Metric                      | Value   |
+-----------------------------+---------+
| Word count                  |   1,842 |
| Character count             |  11,203 |
| Characters (no whitespace)  |   9,412 |
| Line count                  |      45 |
| Sentence count              |     127 |
| Average word length         |    5.11 |
| Average sentence length     |   14.50 |
+-----------------------------+---------+

           Readability Metrics
+------------------------+---------+
| Metric                 | Score   |
+------------------------+---------+
| Flesch Reading Ease    |   58.12 |
| Flesch-Kincaid Grade   |    9.34 |
| Gunning Fog Index      |   11.02 |
| SMOG Index             |   10.11 |
| Automated Readability  |    9.87 |
| Coleman-Liau Index     |   10.62 |
| Difficult Words        |     187 |
| Estimated Grade        | 10th... |
+------------------------+---------+
```

---

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `SOURCE` | Path to a text file (or `-` for stdin) | stdin |
| `--top-words N` | Number of most common words to show | `20` |
| `--longest N` | Number of longest unique words to show | `10` |
| `--include-stopwords` | Do not filter out common English stopwords | off |
| `--verbose` | Enable verbose logging to stderr | off |

---

### Features

- Word, character, sentence, and line counts
- Average word length and average sentence length in words
- Flesch Reading Ease and Flesch-Kincaid grade level
- Gunning Fog, SMOG, Automated Readability, and Coleman-Liau indices
- Difficult-word count and consensus grade estimate
- Top-N most common words with stopword filtering
- Top-N longest unique words by length
- Rich panels and tables for readable terminal output
- Loguru-based verbose logging behind `--verbose`
- Works with both file paths and stdin pipelines
