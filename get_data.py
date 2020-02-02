from termcolor import colored
import json
from functools import reduce

print(colored("Retrieving books...", 'yellow'))
with open("_data/books.json", "r", encoding='utf-8') as f:
    books = json.load(f)["books"]

authors = sorted(set(map(lambda b: b["author"], books)))
print(colored("{} unique authors in total!".format(len(authors)), 'green', attrs=["bold"]))
with open("_data/authors.json", "w") as f:
    json.dump({"authors": authors}, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)

genres = sorted(reduce(lambda r, c: r.union(c), map(lambda b: set(b["genres"]), books)))
print(colored("{} unique genres in total!".format(len(genres)), 'green', attrs=["bold"]))
with open("_data/genres.json", "w") as f:
    json.dump({"genres": genres}, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
