import requests
import bs4 as bs

import multiprocessing
from joblib import Parallel, delayed

import json

import os.path
import traceback

from termcolor import colored

def scrap_book(url):
	try:
		source_book = requests.get(url, timeout=5)
		soup_book = bs.BeautifulSoup(source_book.content, features="html.parser")
		metacol = soup_book.find(id="metacol")

		title = metacol.find(id="bookTitle").text.strip()
		author = metacol.find(class_="authorName").text.strip()

		description_div = metacol.find(id="description")
		description = description_div.find_all("span")[-1].text.strip() if description_div else ""

		img = soup_book.find(id="coverImage")
		img_url = img.get("src") if img else ""

		isbn = soup_book.find("meta", {"property":"books:isbn"}).get("content")
		if isbn == "null":
			raise Exception("Null ISBN error")

		rating_count = metacol.find("meta", {"itemprop":"ratingCount"}).get("content")
		rating_average = metacol.find(class_="average").text

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
		print("-"*30)
		print(title)
		# print(author)
		# print(description)
		# print(date_published)
		# print(publisher)
		# print(isbn)
		# print(img_url)
		# print(rating_count)
		# print(rating_average)
		# print(genres)
		# print(book_format)
		# print(pages)
		# print(language)
		# print(len(reviews))
		book = {
			"title": title,
			"author": author,
			"description": description,
			"img_url": img_url,
			"isbn": int(isbn),
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

	BASE_URL = "https://www.goodreads.com"
	page_url = BASE_URL + "/shelf/show/{}?page={}".format(shelf, i)
	headers = {"Cookie":"csid=BAhJIhg5NzMtMTI1ODAzNi0zOTExMTkxBjoGRVQ%3D--c294349af6f6db36545ed72bef68a96b0d086ed6; locale=en; csm-sid=931-1667412-9657167; __utmc=250562704; __qca=P0-1082142114-1535571428658; never_show_interstitial=true; fbm_2415071772=base_domain=.goodreads.com; __utmz=250562704.1535640557.6.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utma=250562704.1463770531.1535571425.1535666757.1535678979.10; fblo_2415071772=y; u=MaEICRr8zxSTNf40VGNonARVJ6aPeASZYnVsBaBt8zjU5odQ; p=tVkv2BoNXkosOxiHmEDSpI-uF6IFEzQnSIcw85N6KSN-X9Xd; _session_id2=bf455c1f36a867eb1037f3db9e0207c5; __utmt=1; __utmb=250562704.17.10.1535678979"}
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
END = 8
with open("shelves.txt", "r") as f:
	shelves = f.read().splitlines()
results = Parallel(n_jobs=4)(delayed(scrap)(i, shelf) for shelf in shelves for i in range(START, END + 1))
print(results)