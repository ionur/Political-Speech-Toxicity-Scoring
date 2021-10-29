import io
import os
import sys
import string
import re

FILE_ENCODING = "ISO-8859-1"
OPEN_PAREN_ASCII = 40
CLOSE_PAREN_ASCII = 41
OPEN_BRACKET_ASCII = 91
CLOSE_BRACKET_ASCII = 93
OPEN_CURLY_BRACE_ASCII = 123
CLOSE_CURLY_BRACE_ASCII = 125
CHAIN_OF_ASTERISKS = "********************************************************************************";

'''
Input: text file that is already cleaned (i.e. ready to be tokenized and processed by an NLP parser)
-Note: function assumes no nested brackets or parentheses in file.
-Note: function removes all phrases within (), {}, []

Behavior: produces the following files:
1. File 1: A copy of the input file with *all* phrases within (), {}, [] removed.
2. File 2: A file with all phrases within (), {}, [] (i.e. all phrases excluded from File 1).
Each phrase is mapped to the index of the token (in File 1) that appears directly before
the phrase in the original input file.

Note: an 'annotation' here is synonymous with all phrases within (), {}, [].
'''
def handle_speech_annotations(filename):
    # define new path to put cleaned data in
    # WARNING: assumes you're passing in .../data/speeches_clean/....
    pattern_to_find = r'([\w+\.+]/data/speeches)(_\w+)(/\w+)'
    to_insert = r'\1_no_annotations\3'
    out_directory = re.sub(pattern_to_find, to_insert, filename)
    # Opens input_filename with FILE_ENCODING for reading.
    with io.open(filename, "rt", encoding=FILE_ENCODING) as fin:
        # Defines two file names: one for a copy of the file after annotations are removed,
        # and one with the annotations themselves (mapped to index).
        cleaned_file = filename[:-4] + "_without_speech_annotations.txt";
        annotations_file = filename[:-4] + "_speech_annotations.txt";

        # Reads in entire data and splits on whitespace.
        data = fin.read();
        tokens = data.split();

        # Opens new file for the mapping between token index and annotations themselves.
        # makes subdirectories if they don't exist
        subdirs = '/'.join(annotations_file.split('/')[:-1])
        try:
            os.makedirs(subdirs)
        except OSError:
            if not os.path.isdir(subdirs):
                raise
        with io.open(annotations_file, "wt") as speech_annotations:
            # We iterate through file tokens, keeping track of whether current token is in an annotation,
            # the part of the annotation that we have seen so far, and a list of all indices of tokens
            # in the input file that appear in an annotation.
            annotation = []
            annotation_indices = []
            in_annotation = False
            for index, token in enumerate(tokens, start = 0):
                # If we see the beginning of an annotation, then we begin building annotation.
                if token_begins_in_open(token):
                    in_annotation = True
                    # If we are within an annotation, concatenate token to annotation and
                    # make note that current token index appears in an annotation.
                    if in_annotation:
                        annotation.append(token)
                        annotation_indices.append(index)
                        # If we see the end of an annotation, then we write annotation to file,
                        # clear annotation, in_annotation is false.
                        if token_ends_in_close(token):
                            speech_annotations.write("After token {}: {}\n\n".format(index - len(annotation_indices),
                                                                                     join_list_with_spaces(annotation)))
                            annotation = []
                            in_annotation = False
                        # Remove all annotation indices from the list of tokens.
                        for i, annotation_index in enumerate(annotation_indices, start = 0):
                            # Note: indices shift during polling, so we offset the index by the number
                            # of annotation tokens that we have already removed.
                            tokens.pop(annotation_index - i)

                # Opens new file for the copy of the file after annotations are removed.
                # makes subdirectories if they don't exist
                subdirs = '/'.join(cleaned_file.split('/')[:-1])
                try:
                    os.makedirs(subdirs)
                except OSError:
                    if not os.path.isdir(subdirs):
                        raise
                with io.open(cleaned_file, "wt") as speech_without_annotations:
                    speech_without_annotations.write(join_list_with_spaces(tokens))

                # Log creation of new files to console.
                print(CHAIN_OF_ASTERISKS);
                print("New file '" + cleaned_file + "' created with annotations removed.");
                print(CHAIN_OF_ASTERISKS);
                print("New file '" + annotations_file + " created with mapping of token index to " +
                      "annotation that comes directly after that index in " +  cleaned_file);
                print(CHAIN_OF_ASTERISKS);

# Returns list elements as a space-separated string.
def join_list_with_spaces(list):
    return ' '.join(list)

# Returns true if input character is [ or ( or {.
def char_is_open(c):
    c_ascii = ord(c)
    return c_ascii == OPEN_PAREN_ASCII or c_ascii == OPEN_BRACKET_ASCII or c_ascii == OPEN_CURLY_BRACE_ASCII

# Returns true if input character is ] or ) or }.
def char_is_close(c):
    c_ascii = ord(c)
    return c_ascii == CLOSE_PAREN_ASCII or c_ascii == CLOSE_BRACKET_ASCII or c_ascii == CLOSE_CURLY_BRACE_ASCII

# Returns true if the input string ends begins with [ or ( or {.
def token_begins_in_open(token):
    return char_is_open(token[0])

# Returns true if the input string ends ends with ] or ) or }.
def token_ends_in_close(token):
    return char_is_close(token[len(token) - 1])
