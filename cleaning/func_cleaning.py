import io
import sys
import string
import re
import os
import find_duplicate_files as fd
from operator import methodcaller

FILE_ENCODING = "ISO-8859-1"
WHITESPACE = ' '
EMPTY = ''
TO_REMOVE_LIST = ["Show Less Text"]
CHAIN_OF_ASTERISKS = "********************************************************************************";
CHAIN_OF_DASHES = "-----------------";

'''
Generates a new filename from an old path: inserts '_clean' before .txt extension in old_path.
'''
def generate_new_file_name(old_path):
    return re.sub(r'(\w+.)(\w+)', r'\1_clean.\2', old_path)

'''
Compares all files in root directory by hashing their contents using sh1, then
takes the pairs of duplicate files and removes one.
'''
def remove_duplicate_files(path):
    print("Removing duplicates in " + path);
    dups = fd.check_for_duplicates(path)
    i = 1
    for orig, dup in dups:
        os.remove(dup)
        # Log to console.
        print(i + ". Removed file '" + dup + "', was duplicate of " + orig + ".");
        i += 1
    print("Removed " + str(i) + " files.")

'''
All non-ascii characters in the string are replaced by spaces.
'''
def handle_non_ascii_chars(line):
    return line.replace(line, ''.join([i if ord(i) < 128 else WHITESPACE for i in line]))

'''
Cases like "... end.Begin..." are turned into "... end. Begin ...".
'''
def handle_sandwiched_punctuation(line):
    return re.sub(r'(\w+[.!?]+)(\w+)', r'\1 \2', line)

'''
All common non-metadata phrases from TO_REMOVE_LIST (e.g. SHOW_LESS_TEXT) are replaced by empty strings in the string.
'''
def remove_common_non_metadata_phrases(line):
    for rm in TO_REMOVE_LIST:
        line = line.replace(rm, EMPTY)
    return line

'''
All asterisks are replaced by spaces in the string.
'''
def handle_asterisks(line):
    return line.replace('*', EMPTY)


funcs = [handle_non_ascii_chars, handle_asterisks, handle_sandwiched_punctuation, remove_common_non_metadata_phrases]

'''
Instructions: run with first command line arg equal to the directory that you want to clean.
'''
def main():
    try:
        root = sys.argv[1]
    except IndexError:
        print("argument: root directory that you want cleaned")
        exit()

    print("Cleaning all files in " + root)
    print(CHAIN_OF_ASTERISKS)

    # Remove duplicates in root path.
    # WARNING: make sure there is a copy of root path if duplicates need to be kept.
    remove_duplicate_files(root)
    print(CHAIN_OF_DASHES)

    # Iterate through root, and clean each file.
    for dirpath, dirnames, filenames in os.walk(root):
        for filename in filenames:
            curr_path = os.path.join(dirpath, filename)
            # Generate new file name from old file name.
            new_file = generate_new_file_name(curr_path)
            # Open file to clean.
            with io.open(curr_path, "rt", encoding=FILE_ENCODING) as fin:
                with io.open(output_filename, "wt") as fout:
                    # Apply all cleaning functions to one line.
                    for line in fin:
                        new_line = map(methodcaller('__call__', line), funcs)
                    fout.write(new_line)

if __name__ == "__main__":
    main()
