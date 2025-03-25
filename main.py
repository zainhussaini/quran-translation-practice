import streamlit as st
import re
import json
import sqlite3

# DATA ACCESS

@st.cache_data
def get_surah_names():
  con = sqlite3.connect("information.db")
  cur = con.cursor()
  cur.execute("SELECT surah_name FROM surahs ORDER BY surah_number")
  res = cur.fetchall()
  con.close()
  
  surah_names = [row[0] for row in res]
  return surah_names

@st.cache_data
def get_ayat_count(surah_number):
  con = sqlite3.connect("information.db")
  cur = con.cursor()
  cur.execute("SELECT ayat_count FROM surahs WHERE surah_number = ?", (surah_number,))
  res = cur.fetchone()
  con.close()

  ayat_count = res[0]
  return ayat_count

def get_arabic_translation_pairs(surah_number, ayat_number):
  con = sqlite3.connect("information.db")
  cur = con.cursor()
  cur.execute("SELECT arabic, translation FROM word_translations WHERE surah_number = ? AND ayat_number = ? ORDER BY word_position", (surah_number, ayat_number))
  res = cur.fetchall()
  con.close()

  return res

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

def get_image_url_of_ayat(surah_number, ayat_number):
  url = f"https://everyayah.com/data/quranpngs/{surah_number}_{ayat_number}.png"
  return url

# SESSION STATE

def initialize_if_needed(key, default):
  if key not in st.session_state:
    st.session_state[key] = default

def get_surah_ayat():
  surah_number = st.session_state["surah_index"] + 1
  ayat_number = st.session_state["ayat_index"] + 1
  return surah_number, ayat_number

def set_surah_ayat(surah_number, ayat_number):
  st.session_state["surah_index"] = next_surah_number - 1
  st.session_state["ayat_index"] = next_ayat_number - 1

initialize_if_needed("surah_index", 0)
initialize_if_needed("ayat_index", 0)

# WEB PAGE

COLUMN_RATIOS = [1, 3, 3]

st.title("Quran Translation Practice")

col1, col2, col3 = st.columns(COLUMN_RATIOS, vertical_alignment="bottom")
with col1:
  if st.button("next ayat"):
    surah_number, ayat_number = get_surah_ayat()
    next_surah_number, next_ayat_number = get_next_surah_ayat(surah_number, ayat_number)
    set_surah_ayat(next_surah_number, next_ayat_number)
with col2:
  surah_names = get_surah_names()
  surah_selection = st.selectbox("Surah", surah_names, st.session_state["surah_index"])
  st.session_state["surah_index"] = surah_names.index(surah_selection)
with col3:
  surah_number, ayat_number = get_surah_ayat()
  ayat_number_list = range(1, get_ayat_count(surah_number) + 1)
  ayat_selection = st.selectbox("Ayat", ayat_number_list, st.session_state["ayat_index"])
  st.session_state["ayat_index"] = ayat_number_list.index(ayat_selection)

surah_number, ayat_number = get_surah_ayat()
ayat_image_url = get_image_url_of_ayat(surah_number, ayat_number)
st.image(ayat_image_url, use_container_width=True)

col1, col2, col3 = st.columns(COLUMN_RATIOS)
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
  show_answer = st.button("Show answer")

arabic_translation_pairs = get_arabic_translation_pairs(surah_number, ayat_number)
for i, (arabic, translation) in enumerate(arabic_translation_pairs):
  col1, col2, col3 = st.columns(COLUMN_RATIOS)
  with col1:
    st.write("#### " + arabic)
  with col2:
    key=f"word{i}"
    st.text_input(key, key=key, label_visibility="collapsed")
  with col3:
    if show_answer:
      st.write("##### " + translation)
