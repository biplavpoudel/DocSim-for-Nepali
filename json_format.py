import os
import pandas as pd
import json

final_val = []
for file_name in os.listdir("json/"):
    temp_dict = {}
    temp = {}
    file_path = os.path.join("json", file_name)
    with open(file_path, "r") as file:
        json_data = json.load(file)
    temp_dict["file_name"] = file_name
    for info in json_data["words"]:
        temp_dict[info["label"]] = info["value"]
    final_val.append(temp_dict)


df = pd.DataFrame(final_val)
import json
import os
import shutil
from tqdm import tqdm
import pandas as pd
from io import StringIO


def create_sets(df, train=0.7, val=0.2, test=0.1):
    """
    train, val and test are the proportions of the images
    that go in each split.
    """
    if round(train + val + test, 1) != 1:
        print(train + val + test)
        raise ValueError("train + val + test != 1")

    # Create the folders
    train_folder = "data/train"
    val_folder = "data/val"
    test_folder = "data/test"
    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(val_folder, exist_ok=True)
    os.makedirs(test_folder, exist_ok=True)

    # Shuffle your data
    samples = df.sample(frac=1.).reset_index(drop=True)
    print(samples)

    # Compute the number of image for each split
    n = len(samples)
    n_train = train * n
    n_val = val * n
    n_test = test * n

    for idx, row in tqdm(samples.iterrows(), total=samples.shape[0]):
        data = {
            "date": row["date"],
            "payee": row["payee"],
            "sum": row["sum"],
            "amount": row["amount"],
            "account_number": row["account_number"],
            "micr": row["micr"],
            "A/C_Payee": row["A/C Payee"]
        }
        file_name = row["image"]

        gt_parse = {"gt_parse": {
            "cheque_details": [data]
        }
        }

        line = {
            "file_name": file_name,
            "ground_truth": json.dumps(gt_parse)
        }

        # We assume that your images are in
        # a folder named "images/"; correct if necessary
        image_path = os.path.join("images", file_name)

        # Copy the image in one of the folders
        # and append a line to metadata.jsonl
        if idx < n_train:
            dest_path = os.path.join("data/train/", file_name)
            shutil.copyfile(image_path, dest_path)
            with open("data/train/metadata.jsonl", "a") as f:
                f.write(json.dumps(line) + "\n")

        elif n_train <= idx < n_train + n_val:
            dest_path = os.path.join("data/val/", file_name)
            shutil.copyfile(image_path, dest_path)
            with open("data/val/metadata.jsonl", "a") as f:
                f.write(json.dumps(line) + "\n")

        elif n_train + n_val <= idx < n_train + n_val + n_test:
            dest_path = os.path.join("data/test/", file_name)
            shutil.copyfile(image_path, dest_path)
            with open("data/test/metadata.jsonl", "a") as f:
                f.write(json.dumps(line) + "\n")


df_data = pd.read_csv("annotations.csv", index_col=False, na_values=['', ' '], quotechar='"',
                      dtype={'date': str, 'account_number': str, 'image': int}, delimiter=",")

create_sets(df_data)

import os
count = 0
for file_ in os.listdir("images/"):
    os.rename(os.path.join("images", file_), os.path.join("images", f"{count}.jpg"))
    count += 1