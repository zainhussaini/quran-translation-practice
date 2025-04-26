from flask import Flask, render_template, request, jsonify
from flaskr.data_reader import DatabaseReader
from flaskr.morphology_parser import get_links

DEFAULT_SURAH_NUMBER = 2
DEFAULT_AYAT_NUMBER = 255

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        selected_surah_number = int(request.form.get('surah'))
        selected_ayat = int(request.form.get('ayat'))
    else:
        # Show initial selection (first surah and first ayat)
        selected_surah_number = DEFAULT_SURAH_NUMBER
        selected_ayat = DEFAULT_AYAT_NUMBER

    with DatabaseReader() as db:
        translation_pairs = db.get_arabic_translation_pairs(
            selected_surah_number, selected_ayat)
        words_data = []
        for i, (arabic, translation) in enumerate(translation_pairs, start=1):
            link_dict = get_links(db, selected_surah_number, selected_ayat, i)
            words_data.append((arabic, translation, link_dict))

        result = {
            'surah': selected_surah_number,
            'ayat': selected_ayat,
            'quran_text': db.get_quran_text(selected_surah_number, selected_ayat),
            'words_data': words_data
        }

        # Get ayat numbers for the selected surah
        ayat_numbers = list(range(1, db.get_ayat_count(selected_surah_number) + 1))

        return render_template("index.html",
                           surah_names=db.get_surah_names(),
                           ayat_numbers=ayat_numbers,
                           result=result)


@app.route('/get_ayat_count/<int:surah_number>')
def get_ayat_count_for_surah(surah_number):
    with DatabaseReader() as db:
        count = db.get_ayat_count(surah_number)
        return jsonify({'count': count})


@app.route('/get_next_ayat/<int:surah_number>/<int:ayat_number>')
def get_next_ayat(surah_number, ayat_number):
    with DatabaseReader() as db:
        ayat_count = db.get_ayat_count(surah_number)
        
        if ayat_number < ayat_count:
            # Next ayat in the same surah
            return jsonify({
                'surah': surah_number,
                'ayat': ayat_number + 1
            })
        elif surah_number < 114:
            # First ayat of the next surah
            return jsonify({
                'surah': surah_number + 1,
                'ayat': 1
            })
        else:
            # Already at the last ayat of the last surah
            return jsonify({
                'surah': surah_number,
                'ayat': ayat_number
            })


if __name__ == '__main__':
    app.run(debug=True)
