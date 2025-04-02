import sqlite3
import re
import functools
import os

INFORMATION_DB_PATH = "information.db"


@functools.cache
def get_all_roots_from_corpus() -> set[str]:
    con = sqlite3.connect(INFORMATION_DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT features FROM morphology", ())
    res = cur.fetchall()
    con.close()

    # Regular expression pattern to extract the value after 'ROOT:'
    pattern = r'ROOT:([A-Za-z0-9]+)'

    roots = set()
    for features in res:
        match = re.search(pattern, features[0])
        if not match:
            continue
        root = match.group(1)
        roots.add(root)

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


def generate_special_cases():
    corpus_roots = get_all_roots_from_corpus()
    lanes_roots = get_all_roots_from_lanes_lexicon()

    unmatched_roots = set()
    for root in corpus_roots:
        converted_root = basic_convert_to_lanes_lexicon_root(root)
        if converted_root not in lanes_roots:
            unmatched_roots.add(root)

    if os.path.exists("special_cases.txt"):
        raise Exception(f"file special_cases.txt already exists")
    with open("special_cases.txt", "w") as file:
        file.write("\n".join(sorted(list(unmatched_roots))))


@functools.cache
def get_special_cases() -> dict[str, str | None]:
    with open("special_cases.txt", "r") as file:
        lines = file.read().splitlines()

    # maps from corpus root to lanes root
    mapping = dict()
    for line in lines:
        match = re.search(r"([a-zA-Z]+) -> ([a-zA-Z]+)", line)
        if match:
            corpus_root, lanes_root = match.group(1), match.group(2)
            mapping[corpus_root] = lanes_root
            continue

        match = re.search(r"([a-zA-Z]+)", line)
        if match:
            corpus_root = match.group(1)
            mapping[corpus_root] = None
            continue

        raise Exception(f"Invalid line {line} in special_cases.txt")

    return mapping


def basic_convert_to_lanes_lexicon_root(corpus_root) -> str:
    modified_root = corpus_root

    # If the last letter is repeated (shadda), remove it
    if len(modified_root) == 3 and modified_root[1] == modified_root[2]:
        modified_root = modified_root[:2]

    # If the root is quadliteral with repetition, only keep first part.
    if len(modified_root) == 4 and modified_root[:2] == modified_root[2:]:
        modified_root = modified_root[:2]

    # Replace occurrences of "A" with "O" after the first character.
    if "A" in modified_root[1:]:
        modified_root = modified_root[0] + modified_root[1:].replace("A", "O")

    if modified_root[-1] == "y":
        modified_root = modified_root[:-1] + "e"

    return modified_root


def convert_to_lanes_lexicon_root(corpus_root) -> str | None:
    special_cases = get_special_cases()
    if corpus_root in special_cases:
        return special_cases[corpus_root]
    return basic_convert_to_lanes_lexicon_root(corpus_root)


if __name__ == "__main__":
    generate_special_cases()
