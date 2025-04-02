from flaskr.root_fixer import *


class TestConvertToLanesLexiconRoot:

    def test_basic_root(self):
        assert convert_to_lanes_lexicon_root("smw") == "smw"

    def test_repeated_quad_root(self):
        assert convert_to_lanes_lexicon_root("kbkb") == "kb"

    def test_repeated_ending_root(self):
        assert convert_to_lanes_lexicon_root("rbb") == "rb"

    def test_a_starting_root(self):
        assert convert_to_lanes_lexicon_root("Alh") == "Alh"

    def test_a_ending_root(self):
        assert convert_to_lanes_lexicon_root("hzA") == "hzO"

    def test_ay_ending_root(self):
        assert convert_to_lanes_lexicon_root("rAy") == "rOe"

    def test_double_root(self):
        assert convert_to_lanes_lexicon_root("fAy") == "fOw"


class TestSpecialCases:

    def test_correction_root(self):
        assert convert_to_lanes_lexicon_root("hAt") == "Ate"

    def test_unsolved_root(self):
        assert convert_to_lanes_lexicon_root("dhq") is None

    def test_all_roots_evaluate(self):
        corpus_roots = get_all_roots_from_corpus()
        lanes_roots = get_all_roots_from_lanes_lexicon()
        special_cases = get_special_cases()
        for root in corpus_roots:
            converted = convert_to_lanes_lexicon_root(root)
            if converted is not None:
                assert converted in lanes_roots
            else:
                # If a root doesn't evaluate, make sure it is a known special case.
                assert special_cases[root] is None

    def test_all_special_cases_necessary(self):
        lanes_roots = get_all_roots_from_lanes_lexicon()
        special_cases = get_special_cases()

        for root in special_cases:
            converted = basic_convert_to_lanes_lexicon_root(root)
            assert converted not in lanes_roots
