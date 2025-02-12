from polyfuzz import PolyFuzz

from_list = ["apple", "banana", "cherry"]

to_list = ["apple","strawberry"]

model = PolyFuzz("Levenshtein")
model.match(from_list, to_list)

print(model.get_matches())
