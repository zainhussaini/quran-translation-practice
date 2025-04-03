from flask import Flask, render_template, request, jsonify
from flaskr.data_reader import get_surah_names, get_ayat_count, get_quran_text, get_arabic_translation_pairs, get_word_morphology, get_lanes_lexicon_link, get_corpus_dictionary_link

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        selected_surah_number = int(request.form.get('surah'))
        selected_ayat = int(request.form.get('ayat'))

        result = {
            'surah': selected_surah_number,
            'ayat': selected_ayat,
            'quran_text': get_quran_text(selected_surah_number, selected_ayat),
            'translation_pairs': get_arabic_translation_pairs(selected_surah_number, selected_ayat)
        }
    else:
        # Show initial selection (first surah and first ayat)
        selected_surah_number = 2
        selected_ayat = 255
        result = {
            'surah': selected_surah_number,
            'ayat': selected_ayat,
            'quran_text': get_quran_text(selected_surah_number, selected_ayat),
            'translation_pairs': get_arabic_translation_pairs(selected_surah_number, selected_ayat)
        }

    # Get ayat numbers for the selected surah
    ayat_numbers = list(range(1, get_ayat_count(selected_surah_number) + 1))

    return render_template("index.html",
                           surah_names=get_surah_names(),
                           ayat_numbers=ayat_numbers,
                           result=result)


@app.route('/get_ayat_count/<int:surah_number>')
def get_ayat_count_for_surah(surah_number):
    count = get_ayat_count(surah_number)
    return jsonify({'count': count})


if __name__ == '__main__':
    app.run(debug=True)
