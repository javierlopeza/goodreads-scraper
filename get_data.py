from termcolor import colored
import json
from functools import reduce

print(colored("Retrieving books...", 'yellow'))
with open("_data/merged_books.json", "r", encoding='utf-8') as f:
    books = json.load(f)["books"]

# Authors
authors = sorted(set(map(lambda b: b["author"], books)))
print(colored("{} unique authors in total!".format(len(authors)), 'green', attrs=["bold"]))
with open("_data/authors.json", "w") as f:
    json.dump({"authors": authors}, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)

# Genres
genres = sorted(reduce(lambda r, c: r.union(c), map(lambda b: set(b["genres"]), books)))
print(colored("{} unique genres in total!".format(len(genres)), 'green', attrs=["bold"]))
with open("_data/genres.json", "w") as f:
    json.dump({"genres": genres}, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)

# Reviews
reviews = {b["goodreads_url"]: b["reviews"] for b in books}
with open("_data/reviews.json", "w") as f:
    json.dump({"reviews": reviews}, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
print(colored("Saved all books reviews!", 'green', attrs=["bold"]))

# Books basic info
for b in books:
    del b["reviews"]
with open("_data/books.json", "w") as f:
    json.dump({"books": books}, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
print(colored("Saved all {} books!".format(len(books)), 'green', attrs=["bold"]))
