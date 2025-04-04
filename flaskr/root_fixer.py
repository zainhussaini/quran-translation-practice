import sqlite3
import re
import functools
import os
from config import INFORMATION_DB_PATH, SPECIAL_CASES_FILE


@functools.cache
def get_all_roots_from_corpus() -> set[str]:
    con = sqlite3.connect(INFORMATION_DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT root FROM quranic_corpus", ())
    res = cur.fetchall()
    con.close()

    roots = set()
    for res_item in res:
        roots.add(res_item[0])

    return roots


@functools.cache
def get_all_roots_from_lanes_lexicon() -> set[str]:
    con = sqlite3.connect(INFORMATION_DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT root FROM lanes_lexicon", ())
    res = cur.fetchall()
    con.close()

    roots = set()
    for res_item in res:
        roots.add(res_item[0])

    return roots


# Returns a dictionary for special case mappings from corpus_root to lanes_root.
# Whenever a corpus_root is in this dictionary, this should be used instead of
# basic_convert_to_lanes_lexicon_root because
# basic_convert_to_lanes_lexicon_root doesn't return a valid result.
@functools.cache
def get_special_cases() -> dict[str, str | None]:
    with open(SPECIAL_CASES_FILE, "r") as file:
        lines = file.read().splitlines()

    # Maps from corpus_root to lanes_root.
    mapping = dict()
    for line in lines:
        match = re.search(r"([^ ]+) -> ([^ ]+)", line)
        if match:
            corpus_root, lanes_root = match.group(1), match.group(2)
            mapping[corpus_root] = lanes_root
            continue

        match = re.search(r"([^ ]+)", line)
        if match:
            corpus_root = match.group(1)
            mapping[corpus_root] = None
            continue

        raise Exception(f"Invalid line {line} in {SPECIAL_CASES_FILE}")

    return mapping


# A simple approach to converting between corpus_roots and lanes_roots, because
# my default there are some differences in how they are encoded in English
# characters.
def basic_convert_to_lanes_lexicon_root(corpus_root: str) -> str:
    modified_root = corpus_root

    # Replace "$" with "X" (both stand for sheen).
    modified_root = modified_root.replace("$", "X")
    
    # Replace "*" with "c" (both stand for thal).
    modified_root = modified_root.replace("*", "c")

    # If the last letter is repeated (shadda), remove it.
    if len(modified_root) == 3 and modified_root[1] == modified_root[2]:
        modified_root = modified_root[:2]

    # If the root is quadliteral with repetition, only keep first part.
    if len(modified_root) == 4 and modified_root[:2] == modified_root[2:]:
        modified_root = modified_root[:2]

    # Replace occurrences of "A" with "O" after the first character.
    if "A" in modified_root[1:]:
        modified_root = modified_root[0] + modified_root[1:].replace("A", "O")

    # Replace "y" with "e" when it's the last letter (both stand for "ya").
    if modified_root[-1] == "y":
        modified_root = modified_root[:-1] + "e"

    return modified_root


# A rigorous approach to converting between corpus_roots and lanes_roots, that
# considers special cases.
def convert_to_lanes_lexicon_root(corpus_root: str) -> str | None:
    special_cases = get_special_cases()
    if corpus_root in special_cases:
        return special_cases[corpus_root]
    return basic_convert_to_lanes_lexicon_root(corpus_root)
