import json
from functools import reduce
from termcolor import colored

print(colored("Retrieving books", 'yellow'))
with open("books/_books.json", "r", encoding='utf-8') as f:
    json_dict = json.load(f)

books = json_dict["books"]
print(colored("Listing authors", 'yellow'))
genres = sorted(reduce(lambda r, c: r.union(c), map(lambda b: set(b["genres"]), books)))
print(colored("{} unique genres in total!".format(len(genres)), 'green', attrs=["bold"]))

with open("books/_genres.json", "w") as f:
    json.dump({"genres": genres}, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
