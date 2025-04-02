from flaskr.data_reader import get_surah_names, get_ayat_count, get_quran_text, get_arabic_translation_pairs, get_word_morphology, get_lanes_lexicon_link, get_corpus_dictionary_link
from flaskr.root_fixer import convert_to_lanes_lexicon_root
import streamlit as st
import re

# CONVENIENCE FUNCTIONS


def surah_name_to_surah_number(surah_name):
    surah_names = get_surah_names()
    return surah_name.index(surah_name) + 1


def get_next_surah_ayat(surah_number, ayat_number):
    if ayat_number < get_ayat_count(surah_number):
        return surah_number, ayat_number + 1
    elif surah_number < 114:
        return surah_number + 1, 1
    else:
        # There is no next ayat.
        return surah_number, ayat_number


def get_corpus_root(features):
    pattern = r'ROOT:([A-Za-z]+)'
    if match := re.search(pattern, features):
        return match.group(1)
    else:
        return None


# SESSION STATE


def initialize_if_needed():
    for key in ["surah_index", "ayat_index"]:
        if key not in st.session_state:
            st.session_state[key] = 0


def get_surah_ayat():
    surah_number = st.session_state["surah_index"] + 1
    ayat_number = st.session_state["ayat_index"] + 1
    return surah_number, ayat_number


def set_surah_ayat(surah_number, ayat_number):
    st.session_state["surah_index"] = next_surah_number - 1
    st.session_state["ayat_index"] = next_ayat_number - 1


if __name__ == "__main__":
    COLUMN_RATIOS = [1, 2, 2]

    initialize_if_needed()

    st.title("Quran Translation Practice")

    col1, col2, col3 = st.columns(COLUMN_RATIOS, vertical_alignment="bottom")
    with col1:
        if st.button("Next ayat"):
            surah_number, ayat_number = get_surah_ayat()
            next_surah_number, next_ayat_number = get_next_surah_ayat(
                surah_number, ayat_number)
            set_surah_ayat(next_surah_number, next_ayat_number)
    with col2:
        surah_names = get_surah_names()
        surah_selection = st.selectbox("Surah", surah_names,
                                       st.session_state["surah_index"])
        st.session_state["surah_index"] = surah_names.index(surah_selection)
    with col3:
        surah_number, ayat_number = get_surah_ayat()
        ayat_number_list = range(1, get_ayat_count(surah_number) + 1)
        ayat_selection = st.selectbox("Ayat", ayat_number_list,
                                      st.session_state["ayat_index"])
        st.session_state["ayat_index"] = ayat_number_list.index(ayat_selection)

    surah_number, ayat_number = get_surah_ayat()
    st.header(get_quran_text(surah_number, ayat_number))

    st.divider()

    col1, col2, col3 = st.columns(COLUMN_RATIOS)
    with col1:
        show_arabic_words = st.toggle("Show words", True)
    with col2:

        def clear_text():
            for key in st.session_state:
                if key.startswith("word"):
                    st.session_state[key] = ""

        st.button("Clear entries", on_click=clear_text)
    with col3:
        show_answer = st.toggle("Show answer", True)

    arabic_translation_pairs = get_arabic_translation_pairs(
        surah_number, ayat_number)
    for i, (arabic, translation) in enumerate(arabic_translation_pairs):
        col1, col2, col3 = st.columns(COLUMN_RATIOS)
        with col1:
            st.write("#### " + arabic)
        with col2:
            key = f"word{i}"
            st.text_input(key, key=key, label_visibility="collapsed")
        with col3:
            if show_answer:
                st.write("##### " + translation)
                word_number = i + 1
                word_morphology = get_word_morphology(surah_number,
                                                      ayat_number, word_number)
                for form, tag, features in word_morphology:
                    corpus_root = get_corpus_root(features)
                    if not corpus_root:
                        continue
                    corpus_url = get_corpus_dictionary_link(corpus_root)

                    lanes_root = convert_to_lanes_lexicon_root(corpus_root)
                    if not lanes_root:
                        st.markdown(f"[Quranic Corpus]({corpus_url})")
                        continue
                    lanes_url = get_lanes_lexicon_link(lanes_root)
                    st.markdown(
                        f"[Quranic Corpus]({corpus_url}), [Lanes Lexicon]({lanes_url})"
                    )
