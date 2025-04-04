import sqlite3
from flaskr.root_fixer import convert_to_lanes_lexicon_root
from config import INFORMATION_DB_PATH


# Returns an ordered list of surah names.
def get_surah_names() -> list[str]:
    con = sqlite3.connect(INFORMATION_DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT surah_name FROM surahs ORDER BY surah_number")
    res = cur.fetchall()
    con.close()

    surah_names = [row[0] for row in res]
    return surah_names


# Returns the number of ayat in surah specified by its number.
def get_ayat_count(surah_number: int) -> int:
    con = sqlite3.connect(INFORMATION_DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT ayat_count FROM surahs WHERE surah_number = ?",
                (surah_number, ))
    res = cur.fetchone()
    con.close()

    ayat_count = res[0]
    return ayat_count


# Returns the arabic text of an ayat.
def get_quran_text(surah_number: int, ayat_number: int) -> str:
    con = sqlite3.connect(INFORMATION_DB_PATH)
    cur = con.cursor()
    cur.execute(
        "SELECT ayat_text FROM quran_text WHERE surah_number = ? AND ayat_number = ?",
        (surah_number, ayat_number))
    res = cur.fetchone()
    con.close()

    return res[0]


# Returns (arabic, translation) pairs for every word in an ayat.
def get_arabic_translation_pairs(surah_number: int,
                                 ayat_number: int) -> list[tuple[str, str]]:
    con = sqlite3.connect(INFORMATION_DB_PATH)
    cur = con.cursor()
    cur.execute(
        "SELECT arabic, translation FROM word_translations WHERE surah_number = ? AND ayat_number = ? ORDER BY word_number",
        (surah_number, ayat_number))
    res = cur.fetchall()
    con.close()

    assert len(res) > 0
    return res


def get_word_morphology(surah_number: int, ayat_number: int,
                        word_number: int) -> list[tuple[str, str, str]]:
    con = sqlite3.connect(INFORMATION_DB_PATH)
    cur = con.cursor()
    cur.execute(
        "SELECT form, tag, features FROM morphology WHERE surah_number = ? AND ayat_number = ? AND word_number = ? ORDER BY feature_number",
        (surah_number, ayat_number, word_number))
    res = cur.fetchall()
    con.close()

    assert len(res) > 0
    return res


# Returns link to lanes lexicon page (from lexicon.quranic-research.net).
def get_lanes_lexicon_link(lanes_root: str) -> str | None:
    con = sqlite3.connect(INFORMATION_DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT url FROM lanes_lexicon WHERE root = ?", (lanes_root, ))
    res = cur.fetchone()
    con.close()

    if res is None:
        return None

    return res[0]


def get_corpus_dictionary_link(corpus_root: str) -> str | None:
    con = sqlite3.connect(INFORMATION_DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT url FROM quranic_corpus WHERE root = ?", (corpus_root, ))
    res = cur.fetchone()
    con.close()

    if res is None:
        return None

    return res[0]

def get_corpus_word_link(surah_number: int, ayat_number: int, word_number: int) -> str:
    return f"https://corpus.quran.com/wordmorphology.jsp?location={surah_number}:{ayat_number}:{word_number}"
