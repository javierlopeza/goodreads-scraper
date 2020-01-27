import json

with open("books/_books.json", "r", encoding='utf-8') as f:
    json_dict = json.load(f)

books = json_dict["books"]
authors = list(set(map(lambda b: b["author"], books)))

with open("books/_authors.json", "w") as f:
	json.dump({"authors": authors}, f, indent=4, separators=(',', ': '), sort_keys=True, ensure_ascii=False)
