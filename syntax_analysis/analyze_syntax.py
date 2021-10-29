"""
Analyses speeches in root syntactially and saves analysis to data structure:

entity -> (grammatical role -> (verb_inf -> count))
string [ent] -> map()
................string [verb_inf] -> map()
.................................string [grammatical role]-> int (count)
"""
import spacy
import save_objects as so
import nltk
import sys
import string
import re
from nltk.stem.wordnet import WordNetLemmatizer
import os
import read_data_utils as rs
import build_matrix as bm
import string

# stop words
stop_words = ['the', 'an', 'a', 's', 't', 'of',
              'in', 'on', '\'s', '--', 'and', 'or', '\'ll']
stop_words.extend(list(string.punctuation))
stop_words.extend(list(string.whitespace))

# Load tools
nlp = spacy.load("en_core_web_sm")  # Load spacy dependencies.
lemmatizer = WordNetLemmatizer()

# main data structure
word_features = dict()
seed = []


def log(filename, parsed):
    with open("analyze_syntax_log.txt", "a+") as fout:
        fout.write("**** {} ****\n".format(filename))
        fout.write("S:\t{}\n".format(parsed))
        fout.write("TEXT\t|\tPOS\t|\tDEP\t|\tHEAD TEXT\n-----\n")
        for token in parsed:
            fout.write(
                "{}\t|\t{}\t|\t{}\t|\t{}\n".format(
                    normalized_token, token.pos_, token.dep_, token.head.text
                )
            )


def get_corresponding_noun_chunk(parsed, token):
    for chunk in parsed.noun_chunks:
        if token in chunk:
            return chunk


def has_verb_relation(token):
    return "nsubj" in token.dep_ or token.dep_ == "dobj" or token.dep_ == "iobj" or token.dep_ == "dative"


def record_verb(token, adjectives):
    normalized_token = rs.normalize_word(token.text)
    if "verbs" not in word_features[normalized_token]:
        word_features[normalized_token]["verbs"] = dict()
    verb = token.head
    verb_inf = lemmatizer.lemmatize(verb.orth_, "v")
    # deal with GERUNDS and ADJ
    if verb_inf == "be":
        for c in verb.children:
            if c.dep_ == "acomp":
                if c.pos_ == "VERB":  # GERUNDS, replace "to be"
                    verb_inf = lemmatizer.lemmatize(c.orth_, "v")
                if c.pos_ == "ADJ":  # ADJS
                    adjectives.append(c.orth_)
    if verb_inf not in stop_words:
        # make new verb_inf entry under word if need
        if verb_inf not in word_features[normalized_token]["verbs"]:
            word_features[normalized_token]["verbs"][verb_inf] = dict()
        # make new grammar role entry
        if token.dep_ not in word_features[normalized_token]["verbs"][verb_inf]:
            word_features[normalized_token]["verbs"][verb_inf][token.dep_] = 1
        else:
            # increase counter of numbers seen
            word_features[normalized_token]["verbs"][verb_inf][token.dep_] += 1


def record_head(token):
    normalized_token = rs.normalize_word(token.text)
    if "heads" not in word_features[normalized_token]:
        word_features[normalized_token]["heads"] = dict()
    # don't record if already in "verbs" or a preposition
    if (token.head.pos_ == "VERB" and has_verb_relation(token)) or token.head.dep_ == "prep":
        return
    lower = token.head.text.lower()
    if lower not in stop_words:  # avoid stop words
        if lower not in word_features[normalized_token]["heads"]:
            word_features[normalized_token]["heads"][lower] = 1
        else:
            word_features[normalized_token]["heads"][lower] += 1


def record_children(token, adjectives):
    normalized_token = rs.normalize_word(token.text)
    if "children" not in word_features[normalized_token]:
        word_features[normalized_token]["children"] = dict()
    for child in token.children:
        lower = child.text.lower()
        # TODO: excludes 2-word stuff
        if lower not in stop_words and lower.isalnum():  # avoid stop words
            # add adjectives
            if child.pos_ == "ADJ" and child.dep_ == "amod" or child.dep_ == "compound":
                adjectives.append(lower)
            else:
                if lower not in word_features[normalized_token]["children"]:
                    word_features[normalized_token]["children"][lower] = 1
                else:
                    word_features[normalized_token]["children"][lower] += 1


def add_adjectives(normalized_token, adjectives):
    if "adjectives" not in word_features[normalized_token]:
        word_features[normalized_token]["adjectives"] = dict()
    for adj in adjectives:
        if adj not in word_features[normalized_token]["adjectives"]:
            word_features[normalized_token]["adjectives"][adj] = 1
        else:
            word_features[normalized_token]["adjectives"][adj] += 1


def analyze_sentence_structure(sentence):
    parsed = nlp(sentence)
    adjectives = []
    for token in parsed:
        normalized_token = rs.normalize_word(token.text)
        if normalized_token in seed:
            # VERBS: put into grammatical role data structure (word_features)
            if has_verb_relation(token):  # is subj, dobj, dative, etc
                record_verb(token, adjectives)
            # HEADS: add parent dependency
            record_head(token)
            # CHILDREN + ADJ: add children dependencies
            record_children(token, adjectives)
            # ADJECTIVES: add adjectives to data structure
            add_adjectives(normalized_token, adjectives)


def analyze(root, seed_file, save_path):
    # get seed for load and analysis
    global seed
    seed = rs.load_seed(seed_file)

    # Read in files if new seed or root, or load relevant files
    relevant_sents_file = save_path + "read"
    if not os.path.isfile("{}.pkl".format(relevant_sents_file)):
        print("Reading relevant sentences into", relevant_sents_file)
        # read and make
        speech_files = rs.load_sentences_that_contain_seeds(root, seed)
        # save
        so.save_obj(speech_files, relevant_sents_file)
    else:
        speech_files = so.load_obj(relevant_sents_file)

    # Analyze relevant sentences if not done before
    results_file = save_path + "results"
    global word_features
    if not os.path.isfile("{}.pkl".format(results_file)):
        print("Analyzing speeches syntactically...")
        # add all seed words to facilitate addition
        for s_w in seed:
            word_features[s_w] = dict()
        for file, sentences in speech_files.items():
            for sentence in sentences:
                analyze_sentence_structure(sentence)
            # Save results
        so.save_obj(word_features, results_file)  # as a ds
        so.save_obj_json(word_features, results_file)
    else:
        word_features = so.load_obj(results_file)

    # Compute matrix
    matrix_file = save_path + "matrix"
    if not os.path.isfile("{}.pkl".format(matrix_file)):
        print("Computing matrix...")
        matrix_tuple = bm.make_matrix(word_features)
        # Save results
        so.save_obj(matrix_tuple, matrix_file)  # save matrix
    else:
        matrix_tuple = so.load_obj(matrix_file)

    # print data
    print("\tnum modifiers: found", len(matrix_tuple[1]))


if __name__ == "__main__":
    print("use main.py instead , the script version of this is outdated")
