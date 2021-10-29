import io
import sys
import string
from langdetect import detect_langs

FILE_ENCODING = "ISO-8859-1"
CHAIN_OF_ASTERISKS = "********************************************************************************";

'''
Input: text file that is already cleaned (i.e. ready to be tokenized and processed by an NLP parser)

Behavior: produces the following files:
1. File 1: A copy of the input file with spanish removed
1. File 2: A file with all spanish phrases detected; Each phrase is mapped to the index of the token (in File 1) that appears directly before the phrase in the original input file.
'''
def handle_speech_annotations(filename):
    # output files
    cleaned_file = filename[:-4] + "_no_spanish.txt"
    annotations_file = filename[:-4] + "_spanish_annotations.txt";
    # open files
    input_file = open(filename, "rt", encoding=FILE_ENCODING)
    ann_file = open(annotations_file, "wt")
    clean_file = open(cleaned_file, "wt")
    # search through input file
    lines = input_file.read().splitlines()

            annotation = []
            annotation_indices = []
            in_annotation = False
            curr_idx = 0
            # detect lang per line, annotate per token
            for line in fin:
                lang = detect(line)

                if lang == 'es':
                    pass
                tokens = line.split()
                for index, token in enumerate(tokens, start = curr_idx):
                    if token_begins_in_open(token):
                        in_annotation = True
                        if in_annotation:
                            annotation.append(token)
                            # clear annotation, in_annotation is false.
                        if token_ends_in_close(token):
                            speech_annotations.write("After token {}: {}\n\n".format(index - len(annotation_indices),join_list_with_spaces(annotation)))
                            annotation = []
                            in_annotation = False
                            # Remove all annotation indices from the list of tokens.
                            for i, annotation_index in enumerate(annotation_indices, start = 0):
                                # Note: indices shift during polling, so we offset the index by the number
                                # of annotation tokens that we have already removed.
                                tokens.pop(annotation_index - i)

                # Opens new file for the copy of the file after annotations are removed.
                with io.open(cleaned_file, "wt") as speech_without_annotations:
                    speech_without_annotations.write(join_list_with_spaces(tokens))

                # Log creation of new files to console.
                print(CHAIN_OF_ASTERISKS);
                print("New file '" + cleaned_file + "' created with annotations removed.");
                print(CHAIN_OF_ASTERISKS);
                print("New file '" + annotations_file + " created with mapping of token index to " +
                      "annotation that comes directly after that index in " +  cleaned_file);
                print(CHAIN_OF_ASTERISKS);
