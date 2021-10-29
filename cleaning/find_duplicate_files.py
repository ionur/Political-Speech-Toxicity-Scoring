import sys
import os
import hashlib

def chunk_reader(fobj, chunk_size=1024):
    """Generator that reads a file in chunks of bytes"""
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk
"""
Returns list of duplicate files in a directory-- can recurse to subdirs
"""
def check_for_duplicates(path, hash=hashlib.sha1):
    hashes = {}
    dups = []
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            hashobj = hash()
            for chunk in chunk_reader(open(full_path, 'rb')):
                hashobj.update(chunk)
                file_id = (hashobj.digest(), os.path.getsize(full_path))
                duplicate = hashes.get(file_id, None)
                if duplicate:
                    dups.append((full_path, duplicate))
                else:
                    hashes[file_id] = full_path
    return list(set(dups))
