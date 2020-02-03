from glob import glob
import json
from termcolor import colored
import argparse

SHELVES_PAGES_DIR = "./shelves_pages"


class ShelvesMerger():
    def __init__(self, load_merged_books):
        self.load_merged_books = load_merged_books
        self.shelves_pages_paths = glob("{}/*.json".format(SHELVES_PAGES_DIR))
        self.books = []

    def merge_shelves_pages(self):
        print(colored("Merging {} shelves pages...".format(len(self.shelves_pages_paths)), 'yellow'))
        for shelf_page_path in self.shelves_pages_paths:
            with open(shelf_page_path, "r", encoding="utf-8") as f:
                self.books += json.load(f)["books"]
        print(colored("Shelves merged to get a total of {} books".format(len(self.books)), 'green', attrs=["bold"]))

    def remove_duplicated_books(self):
        print(colored("Removing duplicated books...", 'yellow'))
        unique_books = {book["goodreads_url"]: book for book in self.books}
        self.books = list(unique_books.values())
        print(colored("Duplicates removed to get a total of {} books".format(len(self.books)), 'green', attrs=["bold"]))

    def nullify_empty_attrs(self):
        print(colored("Nullifying empty attributes...", 'yellow'))
        for book in self.books:
            for attr in book:
                if book[attr] == "":
                    book[attr] = None

    def clean_reviews(self):
        print(colored("Cleaning reviews...", 'yellow'))
        for book in self.books:
            book["reviews"] = [r for r in book["reviews"] if r != "[image error]"]

    def dump_books(self):
        with open("_data/merged_books.json", "w") as f:
            json.dump(
                {"books": self.books},
                f,
                indent=4,
                separators=(',', ': '),
                sort_keys=True,
                ensure_ascii=False
            )

    def run(self):
        self.merge_shelves_pages()
        self.remove_duplicated_books()
        self.nullify_empty_attrs()
        self.clean_reviews()
        self.dump_books()


parser = argparse.ArgumentParser(description='Goodreads books scraper')
parser.add_argument('--load_merged_books', action='store_true', help='Skip merging and use saved books file.')
args = parser.parse_args()

shelves_merger = ShelvesMerger(args.load_merged_books)
shelves_merger.run()
