import pandas as pd
import os
import json

final_val = []
for file_name in os.listdir("output/cheques"):
    temp_dict = {}
    temp = {}
    file_path = os.path.join("", file_name)
    with open(file_path, "r") as file:
        json_data = json.load(file)
    temp_dict["file_name"] = file_name
    for info in json_data["words"]:
        temp_dict[info["label"]] = info["value"]
    final_val.append(temp_dict)
final_val