import requests
import bs4 as bs

from multiprocessing import cpu_count
from joblib import Parallel, delayed

import json

import os.path
import traceback

from dotenv import load_dotenv
load_dotenv()

from termcolor import colored

BASE_URL = "https://www.goodreads.com"
COOKIE = os.getenv("SESSION_ID")
# COOKIE = "_session_id2=83f123e4e12000a123f2bc6ff12da123"
PAGES_PER_SHELF = int(os.getenv("PAGES_PER_SHELF"))
# PAGES_PER_SHELF = 3

def print_book(book):
	print("-"*30)
	print(book["title"])
	print(book["isbn"])
	# print(book["author"])
	# print(book["description"])
	# print(book["date_published"])
	# print(book["publisher"])
	# print(book["img_url"])
	# print(book["rating_count"])
	# print(book["rating_average"])
	# print(book["genres"])
	# print(book["book_format"])
	# print(book["pages"])
	# print(book["language"])
	# print(len(book["reviews"]))

def scrap_book(url):
	try:
		source_book = requests.get(url, timeout=5)
		soup_book = bs.BeautifulSoup(source_book.content, features="html.parser")
		metacol = soup_book.find(id="metacol")

		isbn = soup_book.find("meta", {"property":"books:isbn"}).get("content")
		if isbn == "null":
			raise Exception("Null ISBN error")

		title = metacol.find(id="bookTitle").text.strip()
		author = metacol.find(class_="authorName").text.strip()

		description_div = metacol.find(id="description")
		description = description_div.find_all("span")[-1].text.strip() if description_div else ""

		img = soup_book.find(id="coverImage")
		img_url = img.get("src") if img else ""

		rating_count = metacol.find("meta", {"itemprop":"ratingCount"}).get("content")
		rating_average = metacol.find("span", {"itemprop":"ratingValue"}).text

		pages = soup_book.find("meta", {"property":"books:page_count"}).get("content")

		details = metacol.find(id="details")

		book_format_div = details.find("span", {"itemprop":"bookFormat"}) if details else None
		book_format = book_format_div.text if book_format_div else ""

		language_div = details.find("div", {"itemprop":"inLanguage"}) if details else None
		language = language_div.text if language_div else ""

		publication = details.find_all(class_="row")[1].text.strip() if details else ""
		date_published = publication.split("\n")[1].strip()	if publication else ""
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
			"isbn": isbn,
			"rating_count": int(rating_count),
			"rating_average": float(rating_average),
			"date_published": date_published,
			"publisher": publisher,
			"genres": genres,
			"book_format": book_format,
			"pages": int(pages),
			"language": language,
			"goodreads_url": url,
			"reviews": reviews
		}
		print_book(book)
		return book

	except Exception as e:
		print("-"*30)
		print(colored("ERROR: {}\n{}URL: {}".format(e, traceback.format_exc(), url), 'red'))
		return

def scrap(i, shelf):
	print(colored("Started - {} - page {}".format(shelf, i), 'yellow', attrs=['bold']))

	if os.path.isfile("books/{}_{}.json".format(shelf, i)):
		print(colored("Finished - {} - page {} - already exists...".format(shelf, i), "green", attrs=['bold']))
		return -1

	page_url = BASE_URL + "/shelf/show/{}?page={}".format(shelf, i)
	headers = {"Cookie":COOKIE}
	try:
		source = requests.get(page_url, timeout=5, headers=headers)
	except:
		return 0
	soup = bs.BeautifulSoup(source.content, features="html.parser") 
	
	books_urls = []
	for elem in soup.find_all(class_="bookTitle"):
		url = elem.get("href")
		books_urls.append(BASE_URL + url)
	books = Parallel(n_jobs=1)(delayed(scrap_book)(book_url) for book_url in books_urls)
	books = list(filter(lambda x: x != None, books))

	with open("books/{}_{}.json".format(shelf, i), "w") as f:
		json.dump({"books": books}, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)

	print(colored("Finished - {} - page {} with {}/{} books".format(shelf, i, len(books), len(books_urls)), 'green', attrs=['bold']))
	return len(books)

START = 1
END = PAGES_PER_SHELF
with open("shelves.txt", "r") as f:
	shelves = f.read().splitlines()
results = Parallel(n_jobs=cpu_count())(delayed(scrap)(i, shelf) for shelf in shelves for i in range(START, END + 1))
