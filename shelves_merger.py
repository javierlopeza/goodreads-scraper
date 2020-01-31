import json
import re
from functools import reduce
from termcolor import colored

valid_chars = "".join(map(chr, range(32,  256)))
def clean_string(s):
	r = re.sub('[^{}]+'.format(valid_chars), '', s)
	r = r.strip()
	return r

def validate_review(review):
	c1 = "(hide spoiler)" not in review
	c2 = "[image error]" not in review
	c3 = reduce(lambda r, c: r + review.count(c), "aeiou", 0) - review.count(" ") > 0
	return c1 and c2 and c3

total_reviews = 0
def clean_reviews(reviews):
	clean = []
	for review in reviews:
		clean_review = clean_string(review)
		if validate_review(clean_review):
			clean.append(clean_review)
	global total_reviews
	total_reviews += len(clean)
	return clean

def clean_book(book):
	for k in book:
		if type(book[k]) == str:
			book[k] = clean_string(book[k])
			book[k] = None if book[k] == "" else book[k]
	book["reviews"] = clean_reviews(book["reviews"])
	return book

def clean_isbn(isbn):
	return str(isbn).strip()

def merge_shelf(shelf, n):
	books = []
	# Merge first "n" pages for shelf
	for i in range(1, n + 1):
		try:
			with open("books/{}_{}.json".format(shelf, i), "r", encoding='utf-8') as f:
				json_dict = json.load(f)
				books += json_dict["books"]
		except:
			continue
	with open("books/{}.json".format(shelf), "w") as f:
		json.dump({"books": books}, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
	print(colored("Merged - {}".format(shelf), 'green'))
	return books

def remove_duplicates(books):
	unique_books = {}
	for book in books:
		book["isbn"] = clean_isbn(book["isbn"])
		if book["isbn"] in unique_books and len(book["genres"]) > len(unique_books[book["isbn"]]["genres"]):
			unique_books[book["isbn"]] = book
		elif book["isbn"] not in unique_books:
			unique_books[book["isbn"]] = book
	return [clean_book(unique_books[isbn]) for isbn in unique_books]

def remove_invalid(books):
	return [book for book in books if None not in [book["author"], book["title"]]]

def merge_all(shelves, n=20, minify=False):
	# Merge all shelves
	books = []
	for shelf in shelves:
		books += merge_shelf(shelf, n)
	# Remove duplicates
	print(colored("Cleaning books", 'yellow'))
	books = remove_duplicates(books)
	print(colored("Removing invalid", 'yellow'))
	books = remove_invalid(books)
	# Dump all books
	with open("books/_books.json".format(shelf), "w") as f:
		if minify:
			json.dump({"books": books}, f, ensure_ascii=False)
		else:
			json.dump({"books": books}, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
		
	return len(books)
		
with open("shelves.txt", "r") as f:
	shelves = f.read().splitlines()
total_books = merge_all(shelves, minify=False)

print(colored("{:.0f} reviews per book (on average)".format(total_reviews / total_books), "yellow"))
print(colored("{} unique books in total!".format(total_books), "green", attrs=["bold"]))
