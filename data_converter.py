import json
import sqlite3
import jsonpickle

def surahs():
  with open("data-quran/surah-translation/en-qurancom.json") as file:
    surah_translation_json = json.load(file)

  with open("data-quran/surah/surah.json") as file:
    surah_json = json.load(file)

  # maps from position to surah number
  surah_names = dict()
  for position, information in surah_translation_json.items():
    name = information["name"]
    translation = information["translation"]

    surah_name = f"{position}. {name} ({translation})"

    surah_names[int(position)] = surah_name

  # maps from position to number of ayat
  surah_ayat = dict()
  for position, information in surah_json.items():
    surah_ayat[int(position)] = information["nAyah"]

  # surah_number, surah_name, ayat_count
  data = []
  for i in range(1,115):
    data.append((i, surah_names[i], surah_ayat[i]))

  con = sqlite3.connect("information.db")
  cur = con.cursor()
  cur.execute("DROP TABLE IF EXISTS surahs")
  cur.execute("CREATE TABLE surahs(surah_number, surah_name, ayat_count)")
  cur.executemany(f"INSERT INTO surahs VALUES (?, ?, ?)", data)
  con.commit()

def word_translations():
  with open("data-quran/word/word.json") as file:
    word_json = json.load(file)

  with open("data-quran/word-translation/en-quranwbw.json") as file:
    word_translation_json = json.load(file)

  with open("data-quran/word-text/uthmani-quranwbw.json") as file:
    word_text_json = json.load(file)
  
  # surah_number, ayat_number, word_position, arabic, translation
  data = []
  for word_index, information in word_json.items():
    surah_number = information["surah"]
    ayat_number = information["ayah"]
    word_position = information["position"]
    arabic = word_text_json[word_index]
    translation = word_translation_json[word_index]
    data.append((surah_number, ayat_number, word_position, arabic, translation))
  
  con = sqlite3.connect("information.db")
  cur = con.cursor()
  cur.execute("DROP TABLE IF EXISTS word_translations")
  cur.execute("CREATE TABLE word_translations(surah_number, ayat_number, word_position, arabic, translation)")
  cur.executemany(f"INSERT INTO word_translations VALUES (?, ?, ?, ?, ?)", data)
  con.commit()

surahs()
word_translations()
