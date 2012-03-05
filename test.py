#!/usr/bin/python2

import sys, pprint
sys.path.insert(0, '.')

from biblio.ebook import ebook_metadata

for f in sys.argv[1:]:
    m = ebook_metadata(f)
    if m is None:
        print "%s: not an ebook file" % f
        continue

    print m
