from flask import Flask, render_template, request, jsonify
from flaskr.data_reader import get_surah_names, get_ayat_count, get_quran_text, get_arabic_translation_pairs, get_word_morphology, get_lanes_lexicon_link, get_corpus_dictionary_link
from flaskr.morphology_parser import get_links

app = Flask(__name__)

def get_next_surah_ayat(surah_number, ayat_number):
    if ayat_number < get_ayat_count(surah_number):
        return surah_number, ayat_number + 1
    elif surah_number < 114:
        return surah_number + 1, 1
    else:
        # There is no next ayat.
        return surah_number, ayat_number


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        selected_surah_number = int(request.form.get('surah'))
        selected_ayat = int(request.form.get('ayat'))
    else:
        # Show initial selection (first surah and first ayat)
        selected_surah_number = 2
        selected_ayat = 255
        
    translation_pairs = get_arabic_translation_pairs(selected_surah_number, selected_ayat)
    words_data = []
    for i, (arabic, translation) in enumerate(translation_pairs, start=1):
        corpus_dict_link, corpus_word_link, lanes_link = get_links(selected_surah_number, selected_ayat, i)
        words_data.append((arabic, translation, corpus_dict_link, corpus_word_link, lanes_link))
    
    result = {
        'surah': selected_surah_number,
        'ayat': selected_ayat,
        'quran_text': get_quran_text(selected_surah_number, selected_ayat),
        'words_data': words_data
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
