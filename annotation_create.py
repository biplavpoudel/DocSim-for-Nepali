import pandas as pd
import os
import json

final_val = []
for file_name in os.listdir("output/cheques/"):
    print(file_name)
    temp_dict = {}
    temp = {}
    file_path = os.path.join("output/cheques/", file_name)
    print(file_path)
    with open(file_path, "r") as file:
        json_data = json.load(file)
    final_val.append(json_data)
print(final_val)