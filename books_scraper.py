import requests
import bs4 as bs

from multiprocessing import cpu_count
from joblib import Parallel, delayed

import json

import os.path
import traceback

from termcolor import colored

from dotenv import load_dotenv
load_dotenv()

BASE_URL = "https://www.goodreads.com"
COOKIE = os.getenv("SESSION_ID")
# COOKIE = "_session_id2=83f123e4e12000a123f2bc6ff12da123"
PAGES_PER_SHELF = int(os.getenv("PAGES_PER_SHELF"))
# PAGES_PER_SHELF = 3


def print_book(book):
    print("-" * 30)
    print(book["title"])
    print(book["isbn"])


class GoodreadsScraper():
    def __init__(self):
        self.shelves = []

    def load_shelves(self):
        with open("shelves.txt", "r") as f:
            self.shelves = f.read().splitlines()

    def scrap_shelf(self, i, shelf):
        print(colored("Started - {} - page {}".format(shelf, i), 'yellow', attrs=['bold']))

        if os.path.isfile("books/{}_{}.json".format(shelf, i)):
            print(colored("Finished - {} - page {} - already exists...".format(shelf, i), "green", attrs=['bold']))
            return -1

        shelf_url = BASE_URL + "/shelf/show/{}?page={}".format(shelf, i)
        headers = {"Cookie": COOKIE}
        try:
            source = requests.get(shelf_url, timeout=5, headers=headers)
        except Exception:
            return 0
        soup = bs.BeautifulSoup(source.content, features="html.parser")

        books_urls = []
        for elem in soup.find_all(class_="bookTitle"):
            url = elem.get("href")
            books_urls.append(BASE_URL + url)
        books = Parallel(n_jobs=1)(delayed(self.scrap_book)(book_url) for book_url in books_urls)
        books = list(filter(lambda x: x is not None, books))

        with open("books/{}_{}.json".format(shelf, i), "w") as f:
            json.dump(
                {"books": books},
                f,
                indent=4,
                separators=(',', ': '),
                sort_keys=True,
                ensure_ascii=False
            )

        print(colored("Finished - {} - page {} with {}/{} books".format(shelf, i, len(books), len(books_urls)), 'green', attrs=['bold']))
        return len(books)

    def scrap_book(self, book_url):
        try:
            source_book = requests.get(book_url, timeout=5)
            soup_book = bs.BeautifulSoup(source_book.content, features="html.parser")

            isbn = soup_book.find("meta", {"property": "books:isbn"}).get("content")
            if isbn == "null":
                raise Exception("Null ISBN error")

            metacol = soup_book.find(id="metacol")
            title = metacol.find(id="bookTitle").text.strip()
            author = metacol.find(class_="authorName").text.strip()

            description_div = metacol.find(id="description")
            description = description_div.find_all("span")[-1].text.strip() if description_div else ""

            img = soup_book.find(id="coverImage")
            img_url = img.get("src") if img else ""

            rating_count = metacol.find("meta", {"itemprop": "ratingCount"}).get("content")
            rating_average = metacol.find("span", {"itemprop": "ratingValue"}).text

            pages = soup_book.find("meta", {"property": "books:page_count"}).get("content")

            details = metacol.find(id="details")

            book_format_div = details.find("span", {"itemprop": "bookFormat"}) if details else None
            book_format = book_format_div.text if book_format_div else ""

            language_div = details.find("div", {"itemprop": "inLanguage"}) if details else None
            language = language_div.text if language_div else ""

            publication = details.find_all(class_="row")[1].text.strip() if details else ""
            date_published = publication.split("\n")[1].strip() if publication else ""
            publisher = publication.split("\n")[2].strip()[3:] if publication else ""

            genres = soup_book.find_all(class_="actionLinkLite bookPageGenreLink")
            genres = [genre.text for genre in genres]

            reviews_divs = soup_book.find_all(class_="reviewText stacked")
            reviews = [review_div.find("span").find_all("span")[-1].text for review_div in reviews_divs]
            book = {
                "title": title,
                "author": author,
                "description": description,
                "img_url": img_url,
                "isbn": str(isbn),
                "rating_count": int(rating_count),
                "rating_average": float(rating_average),
                "date_published": str(date_published),
                "publisher": publisher,
                "genres": genres,
                "book_format": book_format,
                "pages": int(pages),
                "language": language,
                "goodreads_url": book_url,
                "reviews": reviews
            }
            print_book(book)
            return book

        except Exception as e:
            print("-" * 30)
            print(colored("ERROR: {}\n{}URL: {}".format(e, traceback.format_exc(), book_url), 'red'))
            return

    def run(self):
        self.load_shelves()
        Parallel(n_jobs=cpu_count())(
            delayed(self.scrap_shelf)(i, shelf)
            for shelf in self.shelves
            for i in range(1, PAGES_PER_SHELF + 1)
        )


scraper = GoodreadsScraper()
scraper.run()
