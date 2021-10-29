import os
import io
import sys
import string
import re

FILE_ENCODING = "ISO-8859-1"
WHITESPACE = ' '
EMPTY = ''
CHAIN_OF_ASTERISKS = "*******************************************************************************";
CHAIN_OF_DASHES = "-----------------";

def percent_capitalized(file_obj):
    """
    Input: file object to count the percentage of uppercase strings for
    Output: percentage (decimal) of uppercased tokens in file
    """
    cap = 0
    total = 0
    for line in file_obj:
        for token in line.split():
            if token.isupper():
                cap += 1
            total += 1
    return cap / total

def fix_capitalization(in_file_obj, output_file_name):
    """
    Input: in_file_obj, the file to be read; output_file_name, the outfile to write
    the corrected senteces
    Output: -

    Effects: writes to outfile
    """
    with io.open(output_filename, "wt") as fout:
        for line in in_file_obj:
            # Capitalize first letter after punctuation
            fout.write(line.capitalize())
