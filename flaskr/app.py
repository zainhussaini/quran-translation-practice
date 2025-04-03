from flask import Flask, render_template, request
from flaskr.data_reader import get_surah_names, get_ayat_count, get_quran_text, get_arabic_translation_pairs, get_word_morphology, get_lanes_lexicon_link, get_corpus_dictionary_link

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    surah_names = get_surah_names()
    selected_surah = surah_names[0]
    selected_ayat = 1
    surah_number = surah_names.index(selected_surah) + 1
    max_ayat_number = get_ayat_count(surah_number) + 1
    ayat_numbers = list(range(1, max_ayat_number))

    if request.method == 'POST':
        selected_surah = request.form.get('surah')
        selected_ayat = request.form.get('ayat')

    return render_template("index.html",
                           surah_names=surah_names,
                           ayat_numbers=ayat_numbers,
                           selected_surah=selected_surah,
                           selected_ayat=selected_ayat)


if __name__ == '__main__':
    app.run(debug=True)
