from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path
from typing import Optional

import click
import textstat
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "of", "at", "by",
    "for", "with", "about", "against", "between", "into", "through",
    "to", "from", "in", "on", "off", "over", "under", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "do",
    "does", "did", "will", "would", "could", "should", "may", "might",
    "must", "shall", "can", "this", "that", "these", "those", "i",
    "you", "he", "she", "it", "we", "they", "them", "his", "her",
    "its", "their", "our", "my", "your", "as", "so", "not", "no",
    "yes", "up", "down", "out", "there", "here", "when", "where",
    "how", "why", "what", "which", "who", "whom", "than", "then",
}


def tokenize_words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z']+", text.lower())


def count_sentences(text: str) -> int:
    parts = re.split(r"[.!?]+", text)
    return sum(1 for part in parts if part.strip())


def format_number(value: float, decimals: int = 2) -> str:
    return f"{value:,.{decimals}f}"


def build_overview_table(
    word_count: int,
    char_count: int,
    char_count_no_spaces: int,
    line_count: int,
    sentence_count: int,
    avg_word_length: float,
    avg_sentence_length: float,
) -> Table:
    table = Table(
        title="Text Overview",
        border_style="cyan",
        title_style="bold cyan",
    )
    table.add_column("Metric", style="yellow")
    table.add_column("Value", style="green", justify="right")
    table.add_row("Word count", f"{word_count:,}")
    table.add_row("Character count", f"{char_count:,}")
    table.add_row("Characters (no whitespace)", f"{char_count_no_spaces:,}")
    table.add_row("Line count", f"{line_count:,}")
    table.add_row("Sentence count", f"{sentence_count:,}")
    table.add_row("Average word length", format_number(avg_word_length))
    table.add_row("Average sentence length", format_number(avg_sentence_length))
    return table


def safe_readability(func, text: str, default: float = 0.0) -> float:
    try:
        return float(func(text))
    except Exception as exc:
        logger.debug(f"Readability metric failed: {exc}")
        return default


def build_readability_table(text: str) -> Table:
    table = Table(
        title="Readability Metrics",
        border_style="magenta",
        title_style="bold magenta",
    )
    table.add_column("Metric", style="yellow")
    table.add_column("Score", style="green", justify="right")
    table.add_row(
        "Flesch Reading Ease",
        format_number(safe_readability(textstat.flesch_reading_ease, text)),
    )
    table.add_row(
        "Flesch-Kincaid Grade",
        format_number(safe_readability(textstat.flesch_kincaid_grade, text)),
    )
    table.add_row(
        "Gunning Fog Index",
        format_number(safe_readability(textstat.gunning_fog, text)),
    )
    table.add_row(
        "SMOG Index",
        format_number(safe_readability(textstat.smog_index, text)),
    )
    table.add_row(
        "Automated Readability",
        format_number(safe_readability(textstat.automated_readability_index, text)),
    )
    table.add_row(
        "Coleman-Liau Index",
        format_number(safe_readability(textstat.coleman_liau_index, text)),
    )
    table.add_row(
        "Difficult Words",
        f"{int(safe_readability(textstat.difficult_words, text)):,}",
    )
    try:
        table.add_row("Estimated Grade", str(textstat.text_standard(text, float_output=False)))
    except Exception:
        pass
    return table


def build_top_words_table(
    words: list[str],
    top_n: int,
    include_stopwords: bool,
) -> Table:
    filtered = words if include_stopwords else [w for w in words if w not in STOPWORDS]
    counter = Counter(filtered)
    top = counter.most_common(top_n)
    label = "including stopwords" if include_stopwords else "stopwords excluded"
    table = Table(
        title=f"Top {top_n} Most Common Words ({label})",
        border_style="green",
        title_style="bold green",
    )
    table.add_column("Rank", style="dim", justify="right", width=5)
    table.add_column("Word", style="cyan")
    table.add_column("Count", style="green", justify="right")
    if not top:
        table.add_row("-", "(none)", "0")
        return table
    for rank, (word, count) in enumerate(top, start=1):
        table.add_row(str(rank), word, f"{count:,}")
    return table


def build_longest_words_table(words: list[str], top_n: int) -> Table:
    unique = sorted(set(words), key=lambda w: (-len(w), w))
    longest = unique[:top_n]
    table = Table(
        title=f"Top {top_n} Longest Unique Words",
        border_style="blue",
        title_style="bold blue",
    )
    table.add_column("Rank", style="dim", justify="right", width=5)
    table.add_column("Word", style="cyan")
    table.add_column("Length", style="green", justify="right")
    if not longest:
        table.add_row("-", "(none)", "0")
        return table
    for rank, word in enumerate(longest, start=1):
        table.add_row(str(rank), word, str(len(word)))
    return table


def read_input(source: Optional[str]) -> str:
    if source is None or source == "-":
        if sys.stdin.isatty():
            raise click.UsageError(
                "No input provided. Supply a file path or pipe text via stdin."
            )
        return sys.stdin.read()
    path = Path(source)
    if not path.exists():
        raise click.UsageError(f"File not found: {source}")
    if not path.is_file():
        raise click.UsageError(f"Not a file: {source}")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            raise click.UsageError(f"Failed to read {source}: {exc}") from exc


@click.command(
    help="Compute detailed statistics and readability metrics for a text file or stdin.",
)
@click.argument("source", required=False, default=None)
@click.option(
    "--top-words",
    default=20,
    show_default=True,
    type=click.IntRange(1, 500),
    help="How many most-common words to display.",
)
@click.option(
    "--longest",
    default=10,
    show_default=True,
    type=click.IntRange(1, 500),
    help="How many longest unique words to display.",
)
@click.option(
    "--include-stopwords",
    is_flag=True,
    help="Include common stopwords in the most-common list.",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose logging to stderr.",
)
def main(
    source: Optional[str],
    top_words: int,
    longest: int,
    include_stopwords: bool,
    verbose: bool,
) -> None:
    logger.remove()
    logger.add(sys.stderr, level="DEBUG" if verbose else "WARNING")

    text = read_input(source)
    if not text.strip():
        console.print("[yellow]The input is empty. Nothing to analyze.[/yellow]")
        return

    words = tokenize_words(text)
    word_count = len(words)
    char_count = len(text)
    char_count_no_spaces = sum(1 for c in text if not c.isspace())
    line_count = text.count("\n") + (0 if text.endswith("\n") else 1)
    sentence_count = max(count_sentences(text), 1)
    avg_word_length = (sum(len(w) for w in words) / word_count) if word_count else 0.0
    avg_sentence_length = (word_count / sentence_count) if sentence_count else 0.0

    label = source if source and source != "-" else "stdin"
    console.print(
        Panel.fit(
            f"Statistics for [cyan]{label}[/cyan]",
            border_style="blue",
        )
    )
    console.print(
        build_overview_table(
            word_count,
            char_count,
            char_count_no_spaces,
            line_count,
            sentence_count,
            avg_word_length,
            avg_sentence_length,
        )
    )
    console.print(build_readability_table(text))
    if word_count:
        console.print(build_top_words_table(words, top_words, include_stopwords))
        console.print(build_longest_words_table(words, longest))
    console.print("[bold green]Done.[/bold green]")


if __name__ == "__main__":
    main()
