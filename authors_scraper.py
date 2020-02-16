import bs4 as bs
import json
from urllib.parse import quote
import requests
import os.path

from multiprocessing import cpu_count
from joblib import Parallel, delayed

from termcolor import colored
from tqdm import tqdm

from dotenv import load_dotenv
load_dotenv()

BOOKS_SOURCE_PAGES_DIR = "./books_source_pages"
JOBS = cpu_count()
BATCH_SIZE = 10000


class GoodreadsAuthorsScraper():
    def __init__(self):
        self.books = []
        self.authors_urls = {}
        self.authors = []

    def load_authors_urls(self):
        with open("./authors_urls/authors_urls.json", "r", encoding='utf-8') as f:
            self.authors_urls = json.load(f)["authors_urls"]

    def load_books(self):
        with open("_data/books.json", "r", encoding='utf-8') as f:
            self.books = json.load(f)["books"]
        self.books = [
            {
                "author": book["author"],
                "goodreads_url": book["goodreads_url"]
            } for book in self.books
        ]

    def scrap_authors_urls(self):
        for i in range(0, len(self.books), BATCH_SIZE):
            print(colored("Batch {}/{}".format(i // BATCH_SIZE + 1, len(self.books) // BATCH_SIZE + 1), 'yellow', attrs=['bold']))
            results = Parallel(n_jobs=JOBS)(delayed(self.scrap_author_url)(book) for book in tqdm(self.books[i:min(i + BATCH_SIZE, len(self.books))]))
            self.authors_urls.update({author_name: author_url for r in results for author_name, author_url in r.items()})
            self.dump_authors_urls()

    def scrap_author_url(self, book):
        if book["author"] in self.authors_urls:
            return {}

        book_source_page_path = book_source_page_path = "./books_source_pages/{}".format(quote(book["goodreads_url"], safe=""))
        soup_book = bs.BeautifulSoup(open(book_source_page_path), "html.parser")
        try:
            metacol = soup_book.find(id="metacol")
            author_name = self.clean_author_name(metacol.find(class_="authorName").text.strip())
            author_url = metacol.find(class_="authorName").get("href")
            return {author_name: author_url}
        except:
            return {}

    def clean_author_name(self, name):
        return " ".join(name.strip().split())

    def dump_authors_urls(self):
        with open("./authors_urls/authors_urls.json", "w") as f:
            json.dump({"authors_urls": self.authors_urls}, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)

    def scrap_authors(self):
        print(colored("Scraping authors", "yellow", attrs=['bold']))
        self.authors = Parallel(n_jobs=JOBS)(delayed(self.scrap_author)(author_url) for author_url in tqdm(self.authors_urls.values()))

    def scrap_author(self, author_url):
        author_source_page_path = "./authors_source_pages_mobile/{}".format(quote(author_url, safe=""))
        if os.path.isfile(author_source_page_path):
            soup_author = bs.BeautifulSoup(open(author_source_page_path), "html.parser")
        else:
            try:
                headers = {"Cookie": "mobvious.device_type=mobile"}
                source_author = requests.get(author_url, timeout=10, headers=headers)
                soup_author = bs.BeautifulSoup(source_author.content, features="html.parser")
                with open(author_source_page_path, "w") as author_source_page:
                    author_source_page.write(str(soup_author))
            except:
                print(colored("Timeout Error", "magenta", attrs=['bold']))

        try:
            name = self.clean_author_name(soup_author.find("h1", {"class": "authorName"}).text)
        except:
            name = None

        try:
            short_bio = soup_author.find("div", {"class": "authorShortBio"}).text
            birth_place, birth_date, death_date = self.parse_short_bio(short_bio)
        except:
            birth_place, birth_date, death_date = None, None, None

        try:
            gender = soup_author.find("dt", string="Gender").find_next("dd").text
        except:
            gender = None

        return {
            "name": name,
            "gender": gender,
            "birth_date": birth_date,
            "birth_place": birth_place,
            "death_date": death_date,
            "goodreads_url": author_url
        }

    def parse_short_bio(self, bio):
        birth_place, birth_date, death_date = None, None, None
        bio_elements = bio.strip().split("\n")
        if bio_elements[0] == "Born":
            if bio_elements[1].startswith("in"):
                birth_place = self.clean_place_name(bio_elements[1][3:])
            if len(bio_elements) >= 2 and bio_elements[1].startswith("on"):
                birth_date = bio_elements[2][:-1]
            elif len(bio_elements) >= 3 and bio_elements[2].startswith("on"):
                birth_date = bio_elements[3][:-1]
        try:
            death_date_idx = bio_elements.index("Died on") + 1
            death_date = bio_elements[death_date_idx][:-1]
        except:
            death_date = None
        return birth_place, birth_date, death_date

    def clean_place_name(self, place):
        if place.endswith("."):
            place = place[:-1]
        place = " ".join(place.strip().split())
        return place

    def dump_authors(self):
        print(colored("Dumping authors...", 'yellow'))
        with open("_data/authors.json", "w") as f:
            json.dump({"authors": self.authors}, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
        print(colored("Saved all {} authors!".format(len(self.authors)), 'green', attrs=["bold"]))

    def run(self):
        self.load_authors_urls()
        self.load_books()
        # self.scrap_authors_urls()
        self.scrap_authors()
        self.dump_authors()


scraper = GoodreadsAuthorsScraper()
scraper.run()
