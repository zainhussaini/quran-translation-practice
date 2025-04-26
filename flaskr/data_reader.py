import sqlite3
import functools
from flaskr.root_fixer import convert_to_lanes_lexicon_root
from config import INFORMATION_DB_PATH


class DatabaseReader:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = sqlite3.connect(INFORMATION_DB_PATH)
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
            
    def validate_connection_open(self):
        if not self.connection:
            raise RuntimeError("Database connection not open")

    def fetchone(self, query, params=()):
        self.validate_connection_open()
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def fetchall(self, query, params=()):
        self.validate_connection_open()
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_surah_names(self) -> list[str]:
        res = self.fetchall("SELECT surah_name FROM surahs ORDER BY surah_number")
        return [row[0] for row in res]

    def get_ayat_count(self, surah_number: int) -> int:
        res = self.fetchone("SELECT ayat_count FROM surahs WHERE surah_number = ?",
                          (surah_number,))
        return res[0]

    def get_quran_text(self, surah_number: int, ayat_number: int) -> str:
        res = self.fetchone(
            "SELECT ayat_text FROM quran_text WHERE surah_number = ? AND ayat_number = ?",
            (surah_number, ayat_number))
        return res[0]

    def get_arabic_translation_pairs(self, surah_number: int,
                                   ayat_number: int) -> list[tuple[str, str]]:
        res = self.fetchall(
            "SELECT arabic, translation FROM word_translations WHERE surah_number = ? AND ayat_number = ? ORDER BY word_number",
            (surah_number, ayat_number))
        assert len(res) > 0
        return res

    def get_word_morphology(self, surah_number: int, ayat_number: int,
                          word_number: int) -> list[tuple[str, str, str]]:
        res = self.fetchall(
            "SELECT form, tag, features FROM morphology WHERE surah_number = ? AND ayat_number = ? AND word_number = ? ORDER BY token_number",
            (surah_number, ayat_number, word_number))
        assert len(res) > 0
        return res

    def get_lanes_lexicon_link(self, lanes_root: str) -> str | None:
        res = self.fetchone("SELECT url FROM lanes_lexicon WHERE root = ?", (lanes_root,))
        return res[0] if res else None

    def get_corpus_dictionary_link(self, corpus_root: str) -> str | None:
        res = self.fetchone("SELECT url FROM quranic_corpus WHERE root = ?", (corpus_root,))
        return res[0] if res else None

    def get_corpus_word_link(self, surah_number: int, ayat_number: int, word_number: int) -> str:
        # This isn't a database query, but it's similar to the other functions.
        return f"https://corpus.quran.com/wordmorphology.jsp?location={surah_number}:{ayat_number}:{word_number}"