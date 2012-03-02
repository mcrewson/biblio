#!/usr/bin/python2

import sys, pprint
sys.path.insert(0, '.')

from biblio.parsers import find_parser

for f in sys.argv[1:]:
    parser = find_parser(f)
    if parser is None:
        print "%s: cannot identify this file" % f
        continue

    p = parser()
    m = p.read_metadata(f)
    print m
