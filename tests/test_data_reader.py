from flaskr.data_reader import DatabaseReader
import pytest
import re


class TestSurahNames:

    def test_number_of_surahs(self):
        with DatabaseReader() as db:
            assert len(db.get_surah_names()) == 114

    def test_first_surah(self):
        with DatabaseReader() as db:
            assert db.get_surah_names()[0] == "1. Al-Fatihah (The Opener)"

    def test_last_surah(self):
        with DatabaseReader() as db:
            assert db.get_surah_names()[-1] == "114. An-Nas (Mankind)"

    def test_surah_name_format(self):
        # Regular expression pattern explanation:
        # ^\d+          -> Matches one or more digits at the start (e.g., "1", "2", "10").
        # \.            -> Matches a literal period (".") after the number.
        #  [^\(\)]+     -> Matches one or more characters that are NOT parentheses (allows any special characters in the name).
        #  \(           -> Matches an opening parenthesis "(".
        # [^\(\)]+      -> Matches one or more characters that are NOT parentheses (allows any special characters inside parentheses).
        #  \)           -> Matches a closing parenthesis ")".
        # $             -> Ensures the string ends right after the closing parenthesis.
        pattern = r'^\d+\. [^\(\)]+ \([^\(\)]+\)$'

        with DatabaseReader() as db:
            for surah_name in db.get_surah_names():
                assert re.match(pattern, surah_name)


class TestAyatCount:

    def test_first_surah(self):
        with DatabaseReader() as db:
            assert db.get_ayat_count(1) == 7

    def test_invalid_surah_too_low(self):
        with DatabaseReader() as db:
            with pytest.raises(Exception):
                db.get_ayat_count(0)

    def test_invalid_surah_too_high(self):
        with DatabaseReader() as db:
            with pytest.raises(Exception):
                db.get_ayat_count(115)

    def test_all_surahs(self):
        with DatabaseReader() as db:
            for surah_number in range(1, 115):
                db.get_ayat_count(surah_number)

    def test_ayat_total(self):
        with DatabaseReader() as db:
            total = 0
            for surah_number in range(1, 115):
                total += db.get_ayat_count(surah_number)

            assert total == 6236


class TestQuranText:

    def test_first_ayat(self):
        with DatabaseReader() as db:
            ayat_text = db.get_quran_text(1, 1)
            assert ayat_text == "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"

    def test_last_ayat(self):
        with DatabaseReader() as db:
            ayat_text = db.get_quran_text(114, 6)
            assert ayat_text == "مِنَ الْجِنَّةِ وَالنَّاسِ"

    def test_invalid_surah(self):
        with DatabaseReader() as db:
            with pytest.raises(Exception):
                print(db.get_quran_text(115, 1))

    def test_invalid_ayat(self):
        with DatabaseReader() as db:
            with pytest.raises(Exception):
                print(db.get_quran_text(1, 8))


class TestArabicTranslationPairs:

    def test_first_ayat(self):
        with DatabaseReader() as db:
            pairs = db.get_arabic_translation_pairs(1, 1)
            assert len(pairs) == 4

            assert pairs[0][0] == "بِسْمِ"
            assert pairs[1][0] == "اللَّهِ"
            assert pairs[2][0] == "الرَّحْمَٰنِ"
            assert pairs[3][0] == "الرَّحِيمِ"

            assert pairs[0][1] == "In (the) name"
            assert pairs[1][1] == "(of) Allah"
            assert pairs[2][1] == "the Most Gracious"
            assert pairs[3][1] == "the Most Merciful"

    def test_last_ayat(self):
        with DatabaseReader() as db:
            pairs = db.get_arabic_translation_pairs(114, 6)
            assert len(pairs) == 3

            assert pairs[0][0] == "مِنَ"
            assert pairs[1][0] == "الْجِنَّةِ"
            assert pairs[2][0] == "وَالنَّاسِ"

            assert pairs[0][1] == "From"
            assert pairs[1][1] == "the jinn"
            assert pairs[2][1] == "and men"

    def test_invalid_surah(self):
        with DatabaseReader() as db:
            with pytest.raises(Exception):
                print(db.get_arabic_translation_pairs(115, 1))

    def test_invalid_ayat(self):
        with DatabaseReader() as db:
            with pytest.raises(Exception):
                print(db.get_arabic_translation_pairs(1, 8))


class TestWordMorphology:

    def test_first_word(self):
        with DatabaseReader() as db:
            morphology = db.get_word_morphology(1, 1, 1)

            form, tag, features = morphology[0]
            assert form == "bi"
            assert tag == "P"
            assert features == "PREFIX|bi+"

            form, tag, features = morphology[1]
            assert form == "somi"
            assert tag == "N"
            assert features == "STEM|POS:N|LEM:{som|ROOT:smw|M|GEN"

    def test_last_word(self):
        with DatabaseReader() as db:
            morphology = db.get_word_morphology(114, 6, 3)

            form, tag, features = morphology[0]
            assert form == "wa"
            assert tag == "CONJ"
            assert features == "PREFIX|w:CONJ+"

            form, tag, features = morphology[1]
            assert form == "{l"
            assert tag == "DET"
            assert features == "PREFIX|Al+"

            form, tag, features = morphology[2]
            assert form == "n~aAsi"
            assert tag == "N"
            assert features == "STEM|POS:N|LEM:n~aAs|ROOT:nws|MP|GEN"

    def test_invalid_surah(self):
        with DatabaseReader() as db:
            with pytest.raises(Exception):
                print(db.get_word_morphology(115, 1, 1))

    def test_invalid_ayat(self):
        with DatabaseReader() as db:
            with pytest.raises(Exception):
                print(db.get_word_morphology(1, 8, 1))

    def test_invalid_word(self):
        with DatabaseReader() as db:
            with pytest.raises(Exception):
                print(db.get_word_morphology(1, 1, 5))


def get_all_roots() -> set[str]:
    with DatabaseReader() as db:
        res = db.fetchall("SELECT features FROM morphology", ())
        
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


class TestLanesLexiconLinks:

    def test_first_root(self):
        with DatabaseReader() as db:
            link = "https://lexicon.quranic-research.net/data/01_A/000_A.html"
            assert db.get_lanes_lexicon_link("A") == link

    def test_last_root(self):
        with DatabaseReader() as db:
            link = "https://lexicon.quranic-research.net/data/28_e/035_ye.html"
            assert db.get_lanes_lexicon_link("ye") == link

    def test_invalid_root(self):
        with DatabaseReader() as db:
            assert db.get_lanes_lexicon_link("qqq") is None


class TestQuranicCorpusLinks:

    def test_first_root(self):
        with DatabaseReader() as db:
            link = "https://corpus.quran.com/qurandictionary.jsp?q=$Am"
            assert db.get_corpus_dictionary_link("$Am") == link

    def test_last_root(self):
        with DatabaseReader() as db:
            link = "https://corpus.quran.com/qurandictionary.jsp?q=zyt"
            assert db.get_corpus_dictionary_link("zyt") == link
