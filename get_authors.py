import json
from termcolor import colored

print(colored("Retrieving books", 'yellow'))
with open("books/_books.json", "r", encoding='utf-8') as f:
    json_dict = json.load(f)

books = json_dict["books"]
print(colored("Listing authors", 'yellow'))
authors = list(set(map(lambda b: b["author"], books)))
print(colored("{} unique authors in total!".format(len(authors)), 'green', attrs=["bold"]))

with open("books/_authors.json", "w") as f:
	json.dump({"authors": authors}, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
