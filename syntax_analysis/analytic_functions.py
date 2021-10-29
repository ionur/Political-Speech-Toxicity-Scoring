import sys
import re
from scipy import spatial
import os
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
import save_objects as so
import build_matrix as bm
import ppmi

matrices = []
matrix_filename = ""

""" helper """


def top_k_rank(vector_from, labels, search, k, include_only=None):
    try:
        vector = vector_from[search]  # returns numeric
    except KeyError:
        print(search, "is not present in matrix.")
        return None
    index_into = list(labels.keys())
    if include_only:
        pattern = include_only.format("(.)*")
        reg = re.compile(pattern)
        filtered = [(vector[i], word)
                    for i, word in enumerate(index_into) if reg.match(word)]
        filtered_vector, filtered_ii = zip(*filtered)
        new_vector = np.array(list(filtered_vector))
        top_k = np.argsort(new_vector)[-k:][::-1]
        return [(filtered_vector[i], filtered_ii[i]) for i in top_k]
    else:
        top_k = np.argsort(vector)[-k:][::-1]
        return [(vector[i], index_into[i]) for i in top_k]


""" end helper """


def find_top_k_similar(matrix_tuple, seed_word, k):
    similarities = []
    seed, _, _ = matrix_tuple
    try:
        this_vector = seed[seed_word].reshape(1, -1)
        # TODO: correct normalization?
        if np.sum(this_vector):
            this_vector = np.divide(this_vector, np.sum(this_vector))
    except KeyError:
        print(seed_word, "not in current recorded seed.")
        return None
    for w, v in seed.items():
        if w != seed_word:
            v = v.reshape(1, -1)
            # TODO: correct normalization?
            if np.sum(v):
                v = np.divide(v, np.sum(v))
            cs = cosine_similarity(this_vector, v)[0][0]
            similarities.append((cs, w))
    similarities = sorted(similarities, reverse=True)
    return similarities[:k]

def find_bottom_k_similar(matrix_tuple, seed_word, k):
    similarities = []
    seed, _, _ = matrix_tuple
    try:
        this_vector = seed[seed_word].reshape(1, -1)
        if np.sum(this_vector):
            this_vector = np.divide(this_vector, np.sum(this_vector))
    except KeyError:
        print(seed_word, "not in current recorded seed.")
        return None
    for w, v in seed.items():
        if w != seed_word:
            v = v.reshape(1, -1)
            # TODO: correct normalization?
            if np.sum(v):
                v = np.divide(v, np.sum(v))
            cs = cosine_similarity(this_vector, v)[0][0]
            if cs:
                similarities.append((cs, w))
    similarities = sorted(similarities)
    return similarities[:k]

def top_k_described_as(matrix_tuple, modifier, k, classification=None):
    seed, modifiers, _ = matrix_tuple
    # remove classifications for easy searching
    if not classification:
        modifiers = {bm.extract_mod(mod): vec for mod,
                     vec in modifiers.items()}
    return top_k_rank(modifiers, seed, modifier, k)


def top_k_associated(matrix_tuple, seed_word, k, classification=None):
    seed, modifiers, _ = matrix_tuple
    return top_k_rank(seed, modifiers, seed_word, k, classification)


def dynamic_compute(func, ppmi_tuple, matrix_tuple):
    k = int(input("k: \n==>\t"))
    word = input("word:\n==>\t")
    use_ppmi = input("Use PPMI? (y/n)\n==>\t") == "y"
    if use_ppmi:
        results = func(ppmi_tuple, word, k)
    else:
        results = func(matrix_tuple, word, k)
    if results:
        for score, word in results:
            print("\t", word, ":", score)


def main():
    global matrix_filename
    try:
        matrix_filename = sys.argv[1].split(".pkl")[0]
    except IndexError:
        print("Usage: python run_analysis.py matrix_file")
        exit()
    # load main matrix
    global seed
    global modifiers
    seed, modifiers, matrix = so.load_obj(matrix_filename)

    # ppmi
    ppmi_matrix = so.load_obj(matrix_filename.replace("matrix", "ppmi_matrix"))
    seed_ppmi = {w: vec for w, vec in zip(seed.keys(), ppmi_matrix)}

    matrix_tuple = seed, modifiers, matrix
    ppmi_tuple = seed_ppmi, modifiers, seed_ppmi
    while(1):
        choice = int(input(
            "0: Find k top similar\n1: Top k associated\n2: Top k described as:\n==>\t"))
        if choice == 0:
            print("Finding k top similar to word")
            func = find_top_k_similar
        elif choice == 1:
            print("Finding k top modifiers associated with word")
            func = top_k_associated
        elif choice == 2:
            print("Find top k words described as")
            func = top_k_described_as
        dynamic_compute(func, ppmi_tuple, matrix_tuple)


if __name__ == "__main__":
    main()
