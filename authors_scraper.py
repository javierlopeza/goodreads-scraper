import bs4 as bs
import json
from urllib.parse import quote

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
        return " ".join(name.split())

    def dump_authors_urls(self):
        with open("./authors_urls/authors_urls.json", "w") as f:
            json.dump({"authors_urls": self.authors_urls}, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)

    def run(self):
        self.load_authors_urls()
        self.load_books()
        self.scrap_authors_urls()


scraper = GoodreadsAuthorsScraper()
scraper.run()
