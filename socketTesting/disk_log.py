import json

file = open("file.json", "w+")
str_ = json.dumps({"key":123})
file.write(str_)
file