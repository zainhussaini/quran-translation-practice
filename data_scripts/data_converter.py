import json
import sqlite3
import jsonpickle
import re
from config import INFORMATION_DB_PATH


# Helper function for writing to the database.
def write_to_table(table_name: str, table_columns: list[str],
                   data: list[list]):
    for data_row in data:
        assert len(data_row) == len(table_columns)

    con = sqlite3.connect(INFORMATION_DB_PATH)
    cur = con.cursor()
    cur.execute(f"DROP TABLE IF EXISTS {table_name}")
    columns_str = ", ".join(table_columns)
    cur.execute(f"CREATE TABLE {table_name}({columns_str})")
    questions_str = ", ".join(["?"] * len(table_columns))
    cur.executemany(f"INSERT INTO {table_name} VALUES ({questions_str})", data)
    con.commit()


# Writes the surahs table.
def surahs():
    table_name = "surahs"

    with open(
            "raw_data/data-quran/surah-translation/en-qurancom.json", encoding='utf-8') as file:
        surah_translation_json = json.load(file)

    with open("raw_data/data-quran/surah/surah.json", encoding='utf-8') as file:
        surah_json = json.load(file)

    # Maps from surah_number to surah_name.
    surah_name_dict = dict()
    for position, information in surah_translation_json.items():
        name = information["name"]
        translation = information["translation"]

        surah_number = int(position)
        surah_name = f"{position}. {name} ({translation})"

        surah_name_dict[surah_number] = surah_name

    # Maps from surah_number to ayat_count.
    ayat_count_dict = dict()
    for position, information in surah_json.items():
        surah_number = int(position)
        ayat_count = information["nAyah"]

        ayat_count_dict[surah_number] = ayat_count

    data = []
    for i in range(1, 115):
        data.append((i, surah_name_dict[i], ayat_count_dict[i]))

    write_to_table(table_name, ["surah_number", "surah_name", "ayat_count"],
                   data)


# Writes the word_translations table.
def word_translations():
    table_name = "word_translations"

    with open("raw_data/data-quran/word/word.json", encoding='utf-8') as file:
        word_json = json.load(file)

    with open("raw_data/data-quran/word-translation/en-quranwbw.json", encoding='utf-8') as file:
        word_translation_json = json.load(file)

    with open("raw_data/data-quran/word-text/uthmani-qurancom.json", encoding='utf-8') as file:
        word_text_json = json.load(file)

    data = []
    for word_index, information in word_json.items():
        surah_number = information["surah"]
        ayat_number = information["ayah"]
        word_position = information["position"]
        word_number = word_position + 1
        arabic = word_text_json[word_index]
        translation = word_translation_json[word_index]
        data.append(
            (surah_number, ayat_number, word_number, arabic, translation))

    write_to_table(table_name, [
        "surah_number", "ayat_number", "word_number", "arabic", "translation"
    ], data)


def quran_text():
    table_name = "quran_text"

    # This is a markdown file and needs to be manually parsed.
    with open("raw_data/data-quran/ayah-text/uthmani-tanzil.md", encoding='utf-8') as file:
        lines = file.read().splitlines()

    with open("raw_data/data-quran/surah/surah.json", encoding='utf-8') as file:
        surah_json = json.load(file)

    # Maps from ayat_number to ayat_text.
    ayat_text_dict = dict()
    for index, line in enumerate(lines):
        if not line.startswith("# "):
            continue

        ayat_number = int(line.split(" ")[1])
        ayat_text = lines[index + 2]
        ayat_text_dict[ayat_number] = ayat_text

    data = []
    for position, information in surah_json.items():
        surah_number = int(position)
        ayat_number_range_start = information["start"]
        ayat_number_range_end = information["end"]
        for ayat_number in range(ayat_number_range_start,
                                 ayat_number_range_end + 1):
            ayat_text = ayat_text_dict[ayat_number]
            ayat_number_relative = ayat_number - ayat_number_range_start + 1
            data.append([surah_number, ayat_number_relative, ayat_text])

    write_to_table(table_name, ["surah_number", "ayat_number", "ayat_text"],
                   data)


def morphology():
    table_name = "morphology"

    with open("raw_data/quranic-corpus-morphology-0.4.txt", encoding='utf-8') as file:
        lines = file.read().splitlines()

    data = []
    for line in lines:
        if not line.startswith("("):
            continue

        location, form, tag, features = line.split("\t")
        # An example location is (2:261:8:2).
        surah_number, ayat_number, word_number, feature_number = [
            int(x) for x in location[1:-1].split(":")
        ]
        data.append([
            surah_number, ayat_number, word_number, feature_number, form, tag,
            features
        ])

    write_to_table(table_name, [
        "surah_number", "ayat_number", "word_number", "feature_number", "form",
        "tag", "features"
    ], data)


def quranic_corpus():
    table_name = "quranic_corpus"

    with open("raw_data/quranic-corpus-morphology-0.4.txt", encoding='utf-8') as file:
        lines = file.read().splitlines()

    found_roots = set()
    data = []
    for line in lines:
        if not line.startswith("("):
            continue

        location, form, tag, features = line.split("\t")
        match = re.search(r'ROOT:([^|]+)', features)
        if not match:
            continue

        root = match.group(1)
        if root in found_roots:
            continue

        found_roots.add(root)
        url = f"https://corpus.quran.com/qurandictionary.jsp?q={root}"
        data.append((root, url))

    data.sort(key=lambda x: x[0])
    write_to_table(table_name, ["root", "url"], data)


def lanes_lexicon():
    table_name = "lanes_lexicon"

    with open("raw_data/lexicon-pages.txt", encoding='utf-8') as file:
        lines = file.read().splitlines()

    data = []
    for url in lines:
        # Ex. gets "Adb" from "https://lexicon.quranic-research.net/data/01_A/039_Adb.html".
        root = re.search(r"/\d+_([^/]+)\.html$", url).group(1)
        data.append((root, url))

    data.sort(key=lambda x: x[0])
    write_to_table(table_name, ["root", "url"], data)


if __name__ == "__main__":
    surahs()
    word_translations()
    quran_text()
    morphology()
    quranic_corpus()
    lanes_lexicon()
