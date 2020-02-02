# Goodreads Scraper

Python script to scrap [Goodreads](https://www.goodreads.com) books shelves.

- [Installation](#installation)

- [Usage](#usage)

    1. [Select shelves](#step-1-select-shelves)
    2. [Get your cookies](#step-2-get-your-cookies)
    3. [Run books scraper](#step-3-run-books-scraper)
    4. [Run shelves merger](#step-4-run-shelves-merger)
    5. [Retrieve all unique authors and genres](#step-5-retrieve-all-unique-authors-and-genres)

## Installation

```
mkvirtualenv --python=`which python3` goodreads-scraper
pip install -r requirements.txt
```

## Usage

### **Step 1: Select shelves**

Go to https://www.goodreads.com/shelf and select the shelves you want to scrap from.

Say you want _fantasy_, _adventure_ and _thriller_ books. Go to the `shelves.txt` file and fill it with one shelf name per line. 

This is how `shelves.txt` would look like:

```
fantasy
adventure
thriller
```

### **Step 2: Get your cookies**

To retrieve all pages you want you'll need to log in into Goodreads and check the value of your `_session_id2` cookie that will be set automatically in your web browser after making a request logged in. Set the value of the constant COOKIE in `books_scraper.py` with the one you obtained from your browser (or set it on your `.env` file).

If you skip this step, every request you make to get a shelf will return the first page, even if you ask for the second one.

### **Step 3: Run books scraper**

In this step you will scrap books from the selected shelves by running the following command:

```
python books_scaper.py
```

You can set how many pages you want to scrap from each shelf by changing the value of the constant `PAGES_PER_SHELF` to whatever you want.

By the end of this step you will end up with 1 json file per page per shelf inside the `shelves_pages` folder. Something like this:

```
fantasy_1.json
fantasy_2.json
fantasy_3.json
adventure_1.json
adventure_2.json
adventure_3.json
thriller_1.json
thriller_2.json
thriller_3.json
```

So `adventure_2.json` corresponds to page number 2 of the _adventure_ books shelf.

### **Step 4: Run shelves merger**

But we just want one big `books.json` file...

Just run the following command to merge all generated files into one big clean `books.json` file:

```
python shelves_merger.py
```

This script will collect all books, remove duplicates, clean the attributes of the books and clean all reviews.

### **Step 5: Retrieve all unique authors and genres**

The final step is to generate json files containing all authors names and genres by running the following command:

```
python get_data.py
```

With this you will end up with a json file called `authors.json` containing a list of all unique authors and one for the genres called `genres.json`.
