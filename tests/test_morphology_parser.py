import pytest
from flaskr.morphology_parser import extract_root, get_links


class TestExtractRoot:
    def test_single_root(self):
        morphology = [
            ("bi", "P", "PREFIX|bi+"),
            ("somi", "N", "STEM|POS:N|LEM:{som|ROOT:smw|M|GEN")
        ]
        assert extract_root(morphology) == "smw"

    def test_no_root(self):
        morphology = [
            ("wa", "CONJ", "PREFIX|w:CONJ+"),
            ("<iy~aAka", "PRON", "STEM|POS:PRON|LEM:<iy~aA|2MS")
        ]
        assert extract_root(morphology) is None

    def test_multiple_roots(self):
        morphology = [
            ("form1", "tag1", "STEM|POS:N|LEM:kitAb|ROOT:ktb|M|GEN"),
            ("form2", "tag2", "STEM|POS:N|LEM:kitAb|ROOT:ktw|M|GEN")
        ]
        # Should return the first root found
        assert extract_root(morphology) == "ktb"


class MockDatabaseReader:
    def __init__(self, morphology=None, corpus_link=None, lanes_link=None):
        self.morphology = morphology or []
        self.corpus_link = corpus_link
        self.lanes_link = lanes_link

    def get_word_morphology(self, surah_number: int, ayat_number: int, word_number: int) -> list[tuple[str, str, str]]:
        return self.morphology

    def get_corpus_dictionary_link(self, corpus_root: str) -> str | None:
        return self.corpus_link

    def get_lanes_lexicon_link(self, lanes_root: str) -> str | None:
        return self.lanes_link
    
    def get_corpus_word_link(self, surah_number: int, ayat_number: int, word_number: int) -> str:
        return f"https://corpus.quran.com/wordmorphology.jsp?location={surah_number}:{ayat_number}:{word_number}"


class TestGetLinks:
    def test_all_links_present(self):
        db = MockDatabaseReader(
            morphology=[("form1", "tag1", "STEM|POS:N|LEM:kitAb|ROOT:ktb|M|GEN")],
            corpus_link="https://corpus.quran.com/qurandictionary.jsp?q=ktb",
            lanes_link="https://lexicon.quranic-research.net/data/11_k/001_ktb.html"
        )
        
        links = get_links(db, 1, 1, 1)
        assert links == {
            'corpus_word_link': 'https://corpus.quran.com/wordmorphology.jsp?location=1:1:1',
            'corpus_dictionary_link': 'https://corpus.quran.com/qurandictionary.jsp?q=ktb',
            'lanes_lexicon_link': 'https://lexicon.quranic-research.net/data/11_k/001_ktb.html'
        }

    def test_no_root(self):
        db = MockDatabaseReader(
            morphology=[("form1", "tag1", "STEM|POS:N|LEM:kitAb|M|GEN")]
        )
        
        links = get_links(db, 1, 1, 1)
        assert links == {
            'corpus_word_link': 'https://corpus.quran.com/wordmorphology.jsp?location=1:1:1'
        }

    def test_no_lanes_link(self):
        db = MockDatabaseReader(
            morphology=[("form1", "tag1", "STEM|POS:N|LEM:kitAb|ROOT:ktb|M|GEN")],
            corpus_link="https://corpus.quran.com/qurandictionary.jsp?q=ktb",
            lanes_link=None
        )
        
        links = get_links(db, 1, 1, 1)
        assert links == {
            'corpus_word_link': 'https://corpus.quran.com/wordmorphology.jsp?location=1:1:1',
            'corpus_dictionary_link': 'https://corpus.quran.com/qurandictionary.jsp?q=ktb',
            'lanes_lexicon_link': None
        } 