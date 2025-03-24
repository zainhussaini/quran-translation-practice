import streamlit as st
import re
import json

def get_surah_names_list():
  with open("data-quran/surah-translation/en-qurancom.json") as file:
    surah_translation_json = json.load(file)

  surah_names = []
  for index, information in surah_translation_json.items():
    name = information["name"]
    translation = information["translation"]

    surah_name = f"{index}. {name} ({translation})"

    surah_names.append(surah_name)

  return surah_names

def get_number_of_ayat(surah_number):
  with open("data-quran/surah/surah.json") as file:
    surah_json = json.load(file)

  return surah_json[str(surah_number)]["nAyah"]

def get_surah_number_from_name(surah_name):
  surah_names = get_surah_names_list()
  return surah_name.index(surah_name)+1

def get_next_surah_ayat_number(surah_number, ayat_number):
  if ayat_number < get_number_of_ayat(surah_number):
    return surah_number, ayat_number+1
  elif surah_number < 114:
    return surah_number+1, 1
  else:
    return surah_number, ayat_number

def get_words_translated(surah_number, ayat_number):
  with open("data-quran/word/word.json") as file:
    word_json = json.load(file)
  
  word_indeces = []
  for index, information in word_json.items():
    if information["surah"] == surah_number and information["ayah"] == ayat_number:
      word_indeces.append(index)

  with open("data-quran/word-translation/en-quranwbw.json") as file:
    word_translation_json = json.load(file)
    
  word_translations = []
  for word_index in word_indeces:
    word_translation = word_translation_json[word_index]
    word_translations.append(word_translation)

  return word_translations

def get_words_arabic(surah_number, ayat_number):
  with open("data-quran/word/word.json") as file:
    word_json = json.load(file)
  
  word_indeces = []
  for index, information in word_json.items():
    if information["surah"] == surah_number and information["ayah"] == ayat_number:
      word_indeces.append(index)

  with open("data-quran/word-text/uthmani-quranwbw.json") as file:
    word_text_json = json.load(file)
    
  word_texts = []
  for word_index in word_indeces:
    word_text = word_text_json[word_index]
    word_texts.append(word_text)

  return word_texts


def get_image_url_of_ayat(surah_number, ayat_number):
  url = f"https://everyayah.com/data/quranpngs/{surah_number}_{ayat_number}.png"
  return url

# Session state

def initialize_if_needed(key, default):
  if key not in st.session_state:
    st.session_state[key] = default

initialize_if_needed("surah_index", 0)
initialize_if_needed("ayat_index", 0)

# Display

st.title("Quran Translation Practice")

col1, col2, col3 = st.columns(3, vertical_alignment="bottom")
with col1:
  surah_names_list = get_surah_names_list()
  surah_selection = st.selectbox("Surah", surah_names_list, st.session_state["surah_index"])

  st.session_state["surah_index"] = surah_names_list.index(surah_selection)
with col2:
  surah_number = st.session_state["surah_index"]+1
  ayat_number = st.session_state["ayat_index"]+1
  
  ayat_number_list = range(1, get_number_of_ayat(surah_number)+1)
  ayat_selection = st.selectbox("Ayat", ayat_number_list, st.session_state["ayat_index"])

  st.session_state["ayat_index"] = ayat_number_list.index(ayat_selection)
with col3:
  if st.button("next ayat"):
    current_surah_number = st.session_state["surah_index"]+1
    current_ayat_number = st.session_state["ayat_index"]+1

    next_surah_number, next_ayat_number = get_next_surah_ayat_number(current_surah_number, current_ayat_number)

    st.session_state["surah_index"] = next_surah_number-1
    st.session_state["ayat_index"] = next_ayat_number-1

surah_number = st.session_state["surah_index"]+1
ayat_number = st.session_state["ayat_index"]+1
ayat_image_url = get_image_url_of_ayat(surah_number, ayat_number)
st.image(ayat_image_url, use_container_width=True)

col1, col2, col3 = st.columns(3)
with col1:
  # show_arabic_words = st.toggle("show Arabic words")
  pass
with col2:
  def clear_text():
    for key in st.session_state:
      if key.startswith("word"):
        st.session_state[key] = ""
  st.button("Clear", on_click=clear_text)
with col3:
  show_answer = st.button("show answer")

translations = get_words_translated(surah_number, ayat_number)
arabic_words = get_words_arabic(surah_number, ayat_number)
for i in range(len(translations)):
  col1, col2, col3 = st.columns(3)
  with col1:
    # if show_arabic_words:
    if True:
      st.write("#### " + arabic_words[i])
  with col2:
    key = f"word{i}"
    st.text_input(key, key=key, label_visibility="collapsed")
  with col3:
    if show_answer:
      st.write("#### " + translations[i])
