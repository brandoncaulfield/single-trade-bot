import sys
import json

source_file = (sys.argv[1])

print(source_file)

with open(source_file, 'r') as file:
    file_contents = json.load(file)

print(file_contents)