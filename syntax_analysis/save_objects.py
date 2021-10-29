import pickle
import json
import numpy as np

"""
source : https://stackoverflow.com/questions/19201290/how-to-save-a-dictionary-to-a-file
"""


def save_obj(obj, name):
    with open(name + ".pkl", "wb") as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open(name + ".pkl", "rb") as f:
        return pickle.load(f)


def save_obj_json(obj, name):
    with open(name + ".json", "w") as f:
        json.dump(obj, f)


def load_obj_json(name):
    with open(name + ".json", "rb") as f:
        return json.load(f)
