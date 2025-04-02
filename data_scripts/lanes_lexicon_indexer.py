import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

FILE_PATH = "raw_data/lexicon-pages.txt"
START_URL = "https://lexicon.quranic-research.net/data/01_A/000_A.html"


def file_started():
    return os.path.exists(FILE_PATH)


def get_last_url():
    with open(FILE_PATH, "r") as file:
        urls = file.read().splitlines()

    return urls[-1]


def get_next_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    try:
        next_relative_url = soup.find("h2").find(
            "span", class_="next").find("a")["href"]
        next_url = urljoin(url, next_relative_url)
        return next_url
    except:
        return None


def write_url(ulr):
    with open(FILE_PATH, "a") as file:
        file.write(ulr + "\n")


if __name__ == "__main__":
    if file_started():
        next_url = get_last_url()
    else:
        next_url = START_URL

    while next_url := get_next_url(next_url):
        write_url(next_url)
    print("Done!")
