import io
import sys
import string
import re
import os, errno
import find_duplicate_files as fd
from operator import methodcaller
from speech_annotation_builder import handle_speech_annotations
import capitalization as cap

FILE_ENCODING = "ISO-8859-1"
ASTERISKS_ASCII = 42
COLON_ASCII = 58
WHITESPACE = ' '
EMPTY = ''
EMPTY_STRING = ""
TO_REMOVE_LIST = ["Show Less Text"]
CHAIN_OF_ASTERISKS = "********************************************************************************"

'''
Currently runs locally on one file.
Input: file name of file to be cleaned.

Behavior:
-Input file remains in tact. (e.g. "file.txt")
-Produces three files:
File 1: Cleaned file (e.g. "file_after_basic_cleaning.txt")
File 2: File 1 *without* annotations (e.g. "file_after_basic_cleaning_without_speech_annotations.txt")
File 3: File 1 annotations map. (e.g. "file_after_basic_cleaning_speech_annotations.txt")

GOAL[Elena and Tamara]: run over S3 bucket on entire directory

def main():
remove_duplicate_files()
perform_basic_cleaning("speech_audience_parens.txt")
handle_speech_annotations("speech_audience_parens_after_basic_cleaning.txt")
'''

'''
Instructions: run with first command line arg equal to the directory that you want to clean.
'''
def main():
    try:
        root = sys.argv[1]
    except IndexError:
        print("Please run with root directory that you want cleaned as first argument.")
        exit()

    print("Cleaning all files in " + root)
    print(CHAIN_OF_ASTERISKS)

    # Remove duplicates in root path.
    # WARNING: make sure there is a copy of root path if duplicates need to be kept
    remove_duplicate_files(root)
    print(CHAIN_OF_ASTERISKS)

    # Iterate through root, and perform basic cleaning on each file.
    exclude_files = set(['Campaign _Speech_Overview.xlsx', 'Icon?', '.dropbox'])
    for dirpath, dirnames, filenames in os.walk(root):
        for filename in filenames:
            curr_path = os.path.join(dirpath, filename)
            if filename not in exclude_files:
                perform_basic_cleaning(curr_path)
    # DEFINE new root
    # WARNING: assumes you're passing in .../data/speeches/....
    pattern_to_find = r'([\w+\.+]/data/speeches)(/\w*)'
    to_insert = r'\1_clean\2' 
    new_root = re.sub(pattern_to_find, to_insert, root)
    # Iterate through basic cleaning and create annotations directory and without annotations directory
    for dirpath, dirnames, filenames in os.walk(new_root):
        for filename in filenames:
            curr_path = os.path.join(dirpath, filename)
            if filename not in exclude_files:
                handle_speech_annotations(curr_path)

'''
# Generate new file name from old file name.
new_file = generate_new_file_name(curr_path)
# Open file to clean.
with io.open(curr_path, "rt", encoding=FILE_ENCODING) as fin:
with io.open(output_filename, "wt") as fout:
# Apply all cleaning functions to one line.
for line in fin:
new_line = map(methodcaller('__call__', line), funcs)
fout.write(new_line)
'''

'''
Compares all files in directory specified by path parameter by hashing their contents using sh1.
Then takes the pairs of duplicate files and removes one.
'''
def remove_duplicate_files(root):
    print("Removing duplicates.");
    dups = fd.check_for_duplicates(root)
    for orig, dup in dups:
        try:
            os.remove(dup)
        except FileNotFoundError:
            continue
        # Log to console.
        print(CHAIN_OF_ASTERISKS);
        print("Removed file '" + dup + "', was duplicate of " + orig + ".");
        print(CHAIN_OF_ASTERISKS);

'''
Performs several basic cleaning functions line-by-line on input file.
Input file remains in-tact. Resultant file created and stored on-disk.
'''
def perform_basic_cleaning(input_filename):
    # define new path to put cleaned data in
    # WARNING: assumes you're passing in .../data/speeches/....
    pattern_to_find = r'([\w+\.+]/data/speeches)(/\w+)'
    to_insert = r'\1_clean\2'
    new_directory = re.sub(pattern_to_find, to_insert, input_filename)
    # Opens input_filename with FILE_ENCODING for reading.
    with io.open(input_filename, "rt", encoding=FILE_ENCODING) as fin:
        output_filename =  re.sub(r'(\w+)(.txt)', r'\1_after_basic_cleaning\2', new_directory)
        # Opens new file called [input_filename]_after_basic_cleaning.txt for writing,
        # makes subdirectories if they don't exist
        subdirs = '/'.join(output_filename.split('/')[:-1])
        try:
            os.makedirs(subdirs)
        except OSError:
            if not os.path.isdir(subdirs):
                raise
        with io.open(output_filename, "wt") as fout:
            # For each line in input file, perform the following functions.
            for line in fin:
                new_line = map_clean(line)
                fout.write(new_line)

        # check if capitalization needs to be fixed in cleaned file
        # if more than 80% of words are capitalized
        if cap.percent_capitalized(output_filename) > .8:
            cap.fix_capitalization(output_filename)
        print(CHAIN_OF_ASTERISKS)
        print("New file '" + output_filename + "' created as a result of performing " + "basic cleaning functions on each line of file.")
        print(CHAIN_OF_ASTERISKS)

'''
All non-ascii characters in the string are replaced by spaces.
'''
def handle_non_ascii_chars(line):
    return line.replace(line, ''.join([i if ord(i) < 128 else WHITESPACE for i in line]))

'''
All asterisks are replaced by spaces in the string.
'''
def handle_asterisks(line):
    return line.replace('*', EMPTY)

'''
Cases like "... end.Begin..." are turned into "... end. Begin ...".
'''
def handle_sandwiched_punctuation(line):
    return re.sub(r'(\w+[.!?]+)(\w+)', r'\1 \2', line)

'''
Replace all common non- metadata phrases (e.g. SHOW_LESS_TEXT) with empty strings.
'''
def remove_common_non_metadata_phrases(line):
    for rm in TO_REMOVE_LIST:
        line = line.replace(rm, EMPTY)
    return line

'''
Replace all timestamps of the form hh:mm:ss with empty strings.
'''
def remove_timestamps(line):
    # Tokenize line by splitting on whitespace.
    line_tokens = line.split()
    # Add all timestamps in the line to a list.
    timestamps = []
    for token in line_tokens:
        if is_timestamp(token):
            timestamps.append(token)
        # Remove all detected timestamps from line.
        for timestamp in timestamps:
            line = line.replace(timestamp, EMPTY)
        return line

'''
Returns true if input token is of the form hh:mm:ss.
'''
def is_timestamp(token):
    # Return false if the token isn't of length 8.
    if len(token) != 8:
        return False
    # Return false if the token doesn't have colon at index 2 and index 5.
    if (ord(token[2]) != COLON_ASCII) or (ord(token[5]) != COLON_ASCII):
        return False
    # Return false if token does not have digits at all non-colon indices.
    token_chars = list(token)
    for index, token_char in enumerate(token_chars, start = 0):
        if index != 2 and index != 5:
            if not token_char.isdigit():
                return False
        return True

'''
Apply cleaning functions to a line. If a function makes a line none, stop.
'''
def map_clean(line):
    funcs = [handle_non_ascii_chars,
             handle_asterisks,
             handle_sandwiched_punctuation,
             remove_common_non_metadata_phrases,
             remove_timestamps]
    for fun in funcs:
        if not fun(line):
            return line
        else:
            line = fun(line)
    return line

# new_line = handle_non_ascii_chars(line)
# new_line = handle_asterisks(new_line)
# new_line = handle_sandwiched_punctuation(new_line)
# new_line = remove_common_non_metadata_phrases(new_line)
# new_line = remove_timestamps(new_line)

if __name__ == "__main__":
    main()
