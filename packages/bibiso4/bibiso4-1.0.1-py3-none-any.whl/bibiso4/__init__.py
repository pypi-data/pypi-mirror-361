"""
Replaces journal and series names by ISO-4 names
================================================
"""

import json
import os
import re
import sys


RM_IGNORE = ["part", "series", "section", "a", "an", "the", "from", "of", "and", "or", "on", "in"]
ALLOW_TRAILING = ["A"]
FIELDS = ["journal", "series"]

DATA = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(DATA, 'exact.json'), 'r') as handle:
    EXACT = json.load(handle)

with open(os.path.join(DATA, 'prefix.json'), 'r') as handle:
    PREFIX = json.load(handle)

with open(os.path.join(DATA, 'suffix.json'), 'r') as handle:
    SUFFIX = json.load(handle)


def lookup_exact(token):
    lower = token.lower()
    return EXACT.get(lower)


def lookup_prefix(token):

    lower = token.lower()

    for i in reversed(range(1, len(lower))):

        substr = lower[:i + 1]
        abbrv = PREFIX.get(substr)

        if abbrv is not None:
            return abbrv


def lookup_suffix(token):

    lower = token.lower()

    for i in reversed(range(len(lower))):

        substr = lower[-i:]
        abbrv = SUFFIX.get(substr)

        if abbrv is not None:
            return lower[:len(lower) - len(abbrv)] + abbrv


def find_abbrv(token):
    
    lower = token.lower()

    # remove ignored words

    if lower in RM_IGNORE:
        return None

    # look up word in database

    if abbrv := lookup_exact(token):
        return abbrv

    # check for plurals

    if token[-1] == "s":
        if abbrv := lookup_exact(token[:-1]):
            return abbrv

    # look for prefix/suffix

    if abbrv := lookup_prefix(token):
        EXACT[lower] = abbrv
        return abbrv

    if abbrv := lookup_suffix(token):
        EXACT[lower] = abbrv
        return abbrv

    # do nothing

    return token


def replace(sentence):

    # remove brackets and commas

    sentence = re.sub("\(.*?\)|,", "", sentence)

    # strip bibtex syntax

    sentence = sentence.strip().strip("{}\"")

    # split into words

    tokens = sentence.split()

    # don't abbreviate single word journals

    if len(tokens) == 1:
        return sentence

    # find abbreviations

    abbrvs = [find_abbrv(token) for token in tokens]

    # hack to avoid removing trailing A

    if tokens[-1] in ALLOW_TRAILING:
        abbrvs[-1] = tokens[-1]

    # title case

    abbrvs = [a.title() if a.islower() else a for a in abbrvs if a]

    # join them

    return " ".join(abbrvs)



def replace_bibtex_line(line):

    try:
        key, value = line.split("=", 1)
    except ValueError:
        return line

    sanitized = key.strip().lower()

    if sanitized in FIELDS:
        replacement = replace(value)
        return f"{key}= \"{replacement}\","

    return line


def replace_bibtex(file_name):

    with open(file_name) as f:
        lines = [replace_bibtex_line(line) for line in f.read().splitlines()]

    print('\n'.join(lines))


def cli_replace_bibtex():
    file_name = sys.argv[1]
    return replace_bibtex(file_name)


def cli_replace_str():
    str_ = ' '.join(sys.argv[1:])
    return replace(str_)
