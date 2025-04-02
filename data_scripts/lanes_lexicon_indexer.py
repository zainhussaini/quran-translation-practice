import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

FILE_PATH = "raw_data/lexicon-pages.txt"
if os.path.exists(FILE_PATH):
    raise Exception("Overwriting existing file")

with open(FILE_PATH, "w") as file:
    next_url = "https://lexicon.quranic-research.net/data/01_A/000_A.html"
    while True:
        print(next_url)
        file.write(next_url + "\n")

        response = requests.get(next_url)
        soup = BeautifulSoup(response.text, "html.parser")
        try:
            next_relative_url = soup.find("h2").find(
                "span", class_="next").find("a")["href"]
        except:
            print("done!")
            break

        next_url = urljoin(next_url, next_relative_url)
