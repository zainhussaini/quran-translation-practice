from flaskr.data_reader import get_word_morphology, get_corpus_dictionary_link, get_corpus_word_link, get_lanes_lexicon_link
from flaskr.root_fixer import convert_to_lanes_lexicon_root
import re
import sqlite3

INFORMATION_DB_PATH = "information.db"


# TODO: In a test, confirm that no word has more than one root.
def extract_root(morphology: list[tuple[str, str, str]]) -> str | None:
    """Extracts the quranic corpus root from the morphology list.
    Args:
        morphology (list[tuple[str, str, str]]): The morphology of the word in the format (form, tag, features).

    Returns:
        str | None: The root of the word if found, otherwise None.
    """
    pattern = r'ROOT:([A-Za-z]+)'
    for form, tag, features in morphology:
        match = re.search(pattern, features)
        if match:
            return match.group(1)
    return None


def get_links(surah_number: int, ayat_number: int, word_number: int) -> tuple[str | None, str | None, str | None]:
    """Determines helpful links for a word.

    Args:
        surah_number (int): The surah number.
        ayat_number (int): The ayat number.
        word_number (int): The word number.

    Returns:
        tuple[str, str, str]: A tuple of the corpus word link, corpus dictionary link, and lanes lexicon link.
    """
    corpus_word_link = get_corpus_word_link(
        surah_number, ayat_number, word_number)
    
    morphology = get_word_morphology(surah_number, ayat_number, word_number)
    corpus_root = extract_root(morphology)
    if corpus_root is None:
        return corpus_word_link, None, None
    corpus_dictionary_link = get_corpus_dictionary_link(corpus_root)

    lanes_root = convert_to_lanes_lexicon_root(corpus_root)
    if lanes_root is None:
        return corpus_word_link, corpus_dictionary_link, None
    lanes_lexicon_link = get_lanes_lexicon_link(lanes_root)
    return corpus_word_link, corpus_dictionary_link, lanes_lexicon_link


if __name__ == "__main__":
    print(get_unique_tags())
