import json
import ppmi
import numpy as np
import collections


def get_all_modifiers(d):
    # Compute add up all usages
    verbs = []
    children = []
    heads = []
    adjectives = []
    for seed_word in d:
        if 'children' in d[seed_word]:
            children.extend(d[seed_word]['children'].keys())
        if 'heads' in d[seed_word]:
            heads.extend(d[seed_word]['heads'].keys())
        if 'adjectives' in d[seed_word]:
            adjectives.extend(d[seed_word]['adjectives'].keys())
        if 'verbs' in d[seed_word]:
            for v in d[seed_word]['verbs']:
                for mode in d[seed_word]['verbs'][v]:
                    verbs.append('{}:{}'.format(v, mode))
    # take unique only and sort
    u_verbs = set(verbs)
    verbs = [('verb:{}'.format(v)) for v in sorted(list(u_verbs))]
    u_children = set(children)
    children = [('child:{}'.format(c)) for c in sorted(list(u_children))]
    u_heads = set(heads)
    heads = [('head:{}'.format(h)) for h in sorted(list(u_heads))]
    u_adjs = set(adjectives)
    adjectives = [('adj:{}'.format(a)) for a in sorted(list(u_adjs))]
    # define cols of matrix with indeces
    return sorted(verbs + adjectives + children + heads)


def make_matrix(d):
    # get all modifiers in data structure
    all_mods = get_all_modifiers(d)
    # associate each mod with its index in the list for easy lookup, both sorted
    seed = {w: idx for idx, w in enumerate(sorted(d.keys()))}
    mod_idx = {mod: idx for idx, mod in enumerate(all_mods)}
    # make matrix, rows are seed words and cols are modifiers
    matrix = np.zeros((len(seed), len(all_mods)))
    # fill matrix
    for word in seed.keys():
        x = seed[word]
        if 'verbs' in d[word]:
            for verb in d[word]['verbs']:
                for mode in d[word]['verbs'][verb]:
                    v = 'verb:{}:{}'.format(verb, mode)
                    y = mod_idx[v]
                    matrix[x][y] = + d[word]['verbs'][verb][mode]
        if 'adjectives' in d[word]:
            for adj in d[word]['adjectives']:
                a = 'adj:{}'.format(adj)
                y = mod_idx[a]
                matrix[x][y] += d[word]['adjectives'][adj]
        if 'children' in d[word]:
            for child in d[word]['children']:
                c = 'child:{}'.format(child)
                y = mod_idx[c]
                matrix[x][y] += d[word]['children'][child]
        if 'heads' in d[word]:
            for head in d[word]['heads']:
                h = 'head:{}'.format(head)
                y = mod_idx[h]
                matrix[x][y] += d[word]['heads'][head]
    seed = {w: vec for w, vec in zip(seed.keys(), matrix)}  # word to row
    modifiers = {m: vec for m, vec in zip(
        mod_idx.keys(), matrix.T)}  # word to col
    return (seed, modifiers, matrix)


def extract_mod(mod):
    # example: verb:[some_verb]:[role], adj:[some_adj], etc
    try:
        cuttout = mod.split(":")[1].strip()
    except IndexError:
        return mod
    return cuttout


def normalize_matrix(matrix_tuple):
    seed, modifiers, matrix = matrix_tuple
    # divide each term by the sum of all terms -> count to freq
    matrix = np.divide(matrix, np.sum(matrix))
    seed = {w: vec for w, vec in zip(seed.keys(), matrix)}  # word to row
    modifiers = {m: vec for m, vec in zip(
        modifiers.keys(), matrix.T)}  # word to col
    return (seed, modifiers, matrix)


def get_related_to_mod(matrix_tuple, mod):
    seed, modifiers, matrix = matrix_tuple
    # list for easy indexing
    seed_list = list(seed.keys())

    mods_list = list(modifiers.keys())
    embeddings = ["verb:{}:nsubj", "verb:{}:dobj", "verb:{}:dative",
                  "verb:{}:nsubjpass ", "verb:{}:iobj", "adj:{}", "child:{}", "head:{}"]

    # find all possible ways some_word can be in matrix
    possible_indeces = [e.format(mod) for e in embeddings]

    # find all vectors related to some_word
    related = []
    for pi in possible_indeces:
        try:
            existing_vector = modifiers[pi]
        except KeyError:  # do nothing if not present
            continue
        related.append(existing_vector)
    return related


def get_num_common_between(matrix_tuple, seed_word, some_word):
    seed, modifiers, matrix = matrix_tuple
    # list for easy indexing
    seed_list = list(seed.keys())
    mods_list = list(modifiers.keys())

    related = get_related_to_mod(matrix_tuple, some_word)

    # index to look for seed_word in related vectors
    row_idx = seed_list.index(seed_word)
    return sum([vec[row_idx] for vec in related])


def get_num_syntactic_constr_containing(matrix_tuple, word):
    seed, modifiers, matrix = matrix_tuple
    # get sums
    as_seed = sum(seed[word]) if word in seed else 0
    as_mod = sum(map(sum, get_related_to_mod(matrix_tuple, word)))
    return as_seed + as_mod