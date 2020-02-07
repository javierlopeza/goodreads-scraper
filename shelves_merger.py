from glob import glob
import json
from termcolor import colored
import argparse
from functools import reduce
from tqdm import tqdm

SHELVES_PAGES_DIR = "./shelves_pages"


class ShelvesMerger():
    def __init__(self, load_merged_books):
        self.load_merged_books = load_merged_books
        self.shelves_pages_paths = glob("{}/*.json".format(SHELVES_PAGES_DIR))
        self.books = []

    def merge_shelves_pages(self):
        print(colored("Merging {} shelves pages...".format(len(self.shelves_pages_paths)), 'yellow'))
        for shelf_page_path in tqdm(self.shelves_pages_paths):
            with open(shelf_page_path, "r", encoding="utf-8") as f:
                self.books += json.load(f)["books"]
        print(colored("Shelves merged to get a total of {} books".format(len(self.books)), 'green', attrs=["bold"]))

    def remove_duplicated_books(self):
        print(colored("Removing duplicated books...", 'yellow'))
        unique_books = {book["goodreads_url"]: book for book in self.books}
        self.books = list(unique_books.values())
        print(colored("Duplicates removed to get a total of {} books".format(len(self.books)), 'green', attrs=["bold"]))

    def remove_invalid_books(self):
        print(colored("Removing invalid books...", 'yellow'))
        self.books = [book for book in self.books if None not in [book["title"], book["author"]]]
        print(colored("{} valid books".format(len(self.books)), 'green', attrs=["bold"]))

    def nullify_empty_attrs(self):
        print(colored("Nullifying empty attributes...", 'yellow'))
        for book in self.books:
            for attr in book:
                if type(book[attr]) is str and book[attr].strip() == "":
                    book[attr] = None

    def clean_reviews(self):
        print(colored("Cleaning reviews...", 'yellow'))
        for book in self.books:
            book["reviews"] = [r for r in book["reviews"] if r != "[image error]"]

    def clean_genres(self):
        print(colored("Cleaning genres...", 'yellow'))
        for book in self.books:
            # Remove duplicates
            book["genres"] = list(set(book["genres"]))
            # Fix bad-written genres
            book["genres"] = [self.fix_genre(genre) for genre in book["genres"]]

    def fix_genre(self, genre):
        fixes = [
            ("Hi...", "History"),
            ("Lite...", "Literature"),
            ("International Rel...", "International Relations"),
            ("Science Fiction R...", "Science Fiction Romance"),
            ("Complementary Med...", "Complementary Medicine")
        ]
        for (old, new) in fixes:
            genre = genre.replace(old, new)
        return genre

    def clean_authors(self):
        print(colored("Cleaning authors names...", 'yellow'))
        for book in self.books:
            # Clean multiple spaces
            book["author"] = " ".join(book["author"].split())

    def dump_authors(self):
        print(colored("Dumping authors...", 'yellow'))
        authors = sorted(set(map(lambda b: b["author"], self.books)))
        print(colored("{} unique authors in total!".format(len(authors)), 'green', attrs=["bold"]))
        with open("_data/authors.json", "w") as f:
            json.dump({"authors": authors}, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)

    def dump_genres(self):
        print(colored("Dumping genres...", 'yellow'))
        genres = sorted(reduce(lambda r, c: r.union(c), map(lambda b: set(b["genres"]), self.books)))
        print(colored("{} unique genres in total!".format(len(genres)), 'green', attrs=["bold"]))
        with open("_data/genres.json", "w") as f:
            json.dump({"genres": genres}, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)

    def dump_reviews(self):
        print(colored("Dumping reviews...", 'yellow'))
        reviews = {b["goodreads_url"]: b["reviews"] for b in self.books}
        with open("_data/reviews.json", "w") as f:
            json.dump({"reviews": reviews}, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
        print(colored("Saved all books reviews!", 'green', attrs=["bold"]))

    def dump_books(self):
        print(colored("Dumping books...", 'yellow'))
        for b in self.books:
            del b["reviews"]
        with open("_data/books.json", "w") as f:
            json.dump({"books": self.books}, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
        print(colored("Saved all {} books!".format(len(self.books)), 'green', attrs=["bold"]))

    def run(self):
        self.merge_shelves_pages()
        self.remove_duplicated_books()
        self.remove_invalid_books()
        self.nullify_empty_attrs()
        self.clean_reviews()
        self.clean_genres()
        self.clean_authors()
        self.dump_authors()
        self.dump_genres()
        self.dump_reviews()
        self.dump_books()


parser = argparse.ArgumentParser(description='Goodreads books scraper')
parser.add_argument('--load_merged_books', action='store_true', help='Skip merging and use saved books file.')
args = parser.parse_args()

shelves_merger = ShelvesMerger(args.load_merged_books)
shelves_merger.run()
