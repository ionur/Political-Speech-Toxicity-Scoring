#!/bin/bash
# put mispellings into misspells.txt
# find data/speeches -type f -exec ./collect_misspelled.sh {} \;

get_bad_words() {
    echo $1
    cat "$1" | aspell -a | cut -d ' ' -f 2 | grep -v '*' | sort -u >> misspells.txt
}
export -f get_bad_words

echo "Reading data/speeches/*.. and extracting misspellings"
find data/speeches -type f -exec bash -c 'get_bad_words "$0"' {} \;

echo "Finding words in spanish to exclude them"
sort misspells.txt | uniq | aspell -a --lang=es | cut -d ' ' -f 2 | grep -v '*' | sort -u > total_misspelled.txt
echo "Done"

