import sqlite3
import pytest
from config import INFORMATION_DB_PATH

class TestDatabaseConsistency:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.con = sqlite3.connect(INFORMATION_DB_PATH)
        self.cur = self.con.cursor()
        yield
        self.con.close()

    def test_surah_count(self):
        """Verify we have exactly 114 surahs"""
        self.cur.execute("SELECT COUNT(*) FROM surahs")
        count = self.cur.fetchone()[0]
        assert count == 114

    def test_ayat_count_consistency(self):
        """Verify ayat counts match between surahs and quran_text tables"""
        # Get ayat counts from surahs table
        self.cur.execute("SELECT surah_number, ayat_count FROM surahs")
        expected_counts = {surah: count for surah, count in self.cur.fetchall()}

        # Compare with actual counts in quran_text
        self.cur.execute("""
            SELECT surah_number, COUNT(*) as actual_count 
            FROM quran_text 
            GROUP BY surah_number
        """)
        actual_counts = {surah: count for surah, count in self.cur.fetchall()}

        assert expected_counts == actual_counts

    def test_word_count_consistency(self):
        """Verify word counts match between word_translations and morphology tables"""
        # Get counts from word_translations
        self.cur.execute("""
            SELECT surah_number, ayat_number, COUNT(*) as word_count 
            FROM word_translations 
            GROUP BY surah_number, ayat_number
        """)
        translation_counts = {(surah, ayat): count 
                            for surah, ayat, count in self.cur.fetchall()}

        # Get counts from morphology
        self.cur.execute("""
            SELECT surah_number, ayat_number, COUNT(DISTINCT word_number) as word_count 
            FROM morphology 
            GROUP BY surah_number, ayat_number
        """)
        morphology_counts = {(surah, ayat): count 
                           for surah, ayat, count in self.cur.fetchall()}

        assert translation_counts == morphology_counts

    def test_total_ayat_count(self):
        """Verify total number of ayat is 6236"""
        self.cur.execute("SELECT COUNT(*) FROM quran_text")
        total_ayat = self.cur.fetchone()[0]
        assert total_ayat == 6236

    def test_root_consistency(self):
        """Verify roots in morphology exist in quranic_corpus and lanes_lexicon"""
        # Get unique roots from morphology
        self.cur.execute("""
            WITH RECURSIVE
            split(features, rest) AS (
                SELECT '', features || '|' FROM morphology
                UNION ALL
                SELECT
                    substr(rest, 0, instr(rest, '|')),
                    substr(rest, instr(rest, '|')+1)
                FROM split WHERE rest <> ''
            )
            SELECT DISTINCT
                substr(features, 6) as root
            FROM split
            WHERE features LIKE 'ROOT:%'
        """)
        morphology_roots = {row[0] for row in self.cur.fetchall()}

        # Get roots from quranic_corpus
        self.cur.execute("SELECT root FROM quranic_corpus")
        corpus_roots = {row[0] for row in self.cur.fetchall()}

        # Get roots from lanes_lexicon
        self.cur.execute("SELECT root FROM lanes_lexicon")
        lanes_roots = {row[0] for row in self.cur.fetchall()}

        # All roots in morphology should be in quranic_corpus
        assert morphology_roots.issubset(corpus_roots), \
            "Some roots in morphology are missing from quranic_corpus"

        # Note: Not all roots need to be in lanes_lexicon, but we can log the difference
        missing_from_lanes = morphology_roots - lanes_roots
        print(f"Info: {len(missing_from_lanes)} roots from morphology not in lanes_lexicon")

    def test_no_duplicate_entries(self):
        """Verify there are no duplicate entries in any table"""
        tables = [
            ("surahs", ["surah_number"]),
            ("quran_text", ["surah_number", "ayat_number"]),
            ("word_translations", ["surah_number", "ayat_number", "word_number"]),
            ("morphology", ["surah_number", "ayat_number", "word_number", "token_number"]),
            ("quranic_corpus", ["root"]),
            ("lanes_lexicon", ["root"])
        ]

        for table, key_columns in tables:
            columns = ", ".join(key_columns)
            self.cur.execute(f"""
                SELECT {columns}, COUNT(*) as count
                FROM {table}
                GROUP BY {columns}
                HAVING count > 1
            """)
            duplicates = self.cur.fetchall()
            assert not duplicates, f"Found duplicates in {table}: {duplicates}"