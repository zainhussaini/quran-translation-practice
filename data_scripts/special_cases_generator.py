from flaskr.root_fixer import get_all_roots_from_corpus, get_all_roots_from_lanes_lexicon, basic_convert_to_lanes_lexicon_root
from flaskr.data_reader import get_lanes_lexicon_link, get_corpus_dictionary_link
import os
import re
from config import SPECIAL_CASES_FILE

VERIFIED_LANES_DOUBLES = [
    "HSw", "Tgw", "dhw", "fOw", "ftw", "jbw", "nsw", "qlw", "qnw", "sEw",
    "sdw", "vbw"
]

VERIFIED_CORRECTIONS = ["dsw", "hAt"]


# Creates file with all roots that do not result in a valid conversion using
# basic_convert_to_lanes_lexicon_root.
def generate_special_cases():
    corpus_roots = get_all_roots_from_corpus()
    lanes_roots = get_all_roots_from_lanes_lexicon()

    unmatched_roots = set()
    for root in corpus_roots:
        converted_root = basic_convert_to_lanes_lexicon_root(root)
        if converted_root not in lanes_roots:
            unmatched_roots.add(root)

    if os.path.exists(SPECIAL_CASES_FILE):
        raise Exception(f"file {SPECIAL_CASES_FILE} already exists")
    with open(SPECIAL_CASES_FILE, "w") as file:
        file.write("\n".join(sorted(list(unmatched_roots))))


# Goes through each line in file and checks whether it's valid.  Requires manual
# verification if there's a new entry, then it can be added to the lists below.
def verify_all_cases():
    with open(SPECIAL_CASES_FILE, "r") as file:
        lines = file.read().splitlines()

    corpus_roots = get_all_roots_from_corpus()
    lanes_roots = get_all_roots_from_lanes_lexicon()

    found_corpus_roots = set()
    found_lanes_roots = set()

    for line in lines:
        # Matches a root without a fix.
        if match := re.search(r"^([^ ]+)$", line):
            corpus_root = match.group(1)
            
            if corpus_root not in corpus_roots:
                raise Exception(f"corpus root {corpus_root} is not in corpus_roots")
            if corpus_root in lanes_roots:
                raise Exception(f"corpus root {corpus_root} is in lanes_roots")

        # Matches a fix.
        elif match := re.search(r"^([^ ]+) -> ([^ ]+) \((.+)\)$",
                                line):
            corpus_root = match.group(1)
            lanes_root = match.group(2)
            note = match.group(3)

            if corpus_root not in corpus_roots:
                raise Exception(f"corpus root {corpus_root} is not in corpus_roots")
            if lanes_root not in lanes_roots:
                raise Exception(f"lanes root {lanes_root} is not in lanes_roots")

            # The note indicates what type of fix it is.
            if note == "double":
                verify_double(corpus_root, lanes_root)
            elif note == "special lane encoding":
                pass
            elif match := re.search(r"^correction\: ([^ ]+)$", note):
                corpus_root_correction = match.group(1)
                verify_correction(corpus_root, corpus_root_correction,
                                  lanes_root)
            else:
                raise Exception(f"Invalid note {note}")
        else:
            raise Exception(f"Invalid line {line} in {SPECIAL_CASES_FILE}")


def verify_double(corpus_root, lanes_root):
    # The double root is when the lanes_root should be "HSe", but because "HSw"
    # exists and has a very similar meaning, they're collected into one entry in
    # Lane's Lexicon under "HSw".
    assert corpus_root[-1] == "y"
    assert lanes_root[-1] == "w"

    allowable_transforms = {corpus_root[:-1] + "w"}
    for transformed in allowable_transforms.copy():
        allowable_transforms.add(transformed.replace("A", "O"))
    assert lanes_root in allowable_transforms

    if lanes_root in VERIFIED_LANES_DOUBLES:
        return

    lanes_link = get_lanes_lexicon_link(lanes_root)
    print("Verify that this Lanes root is a double entry:")
    print(f" lanes: {lanes_link}")
    current_file = os.path.basename(__file__)
    print(f"Then add to VERIFIED_LANES_DOUBLES in {current_file}")
    print()


def verify_correction(corpus_root, corpus_root_correction, lanes_root):
    assert lanes_root == basic_convert_to_lanes_lexicon_root(
        corpus_root_correction)

    if corpus_root in VERIFIED_CORRECTIONS:
        return

    print("Verify these all have same meaning:")
    corpus_link = get_corpus_dictionary_link(corpus_root)
    print(f" corpus: {corpus_link}")
    corpus_corrected_link = get_corpus_dictionary_link(corpus_root_correction)
    print(f" corpus corrected: {corpus_corrected_link}")
    lanes_link = get_lanes_lexicon_link(lanes_root)
    print(f" lanes: {lanes_link}")
    print(f"Then add to VERIFIED_CORRECTIONS in {current_file}")
    print()


if __name__ == "__main__":
    if not os.path.exists(SPECIAL_CASES_FILE):
        generate_special_cases()

    verify_all_cases()
