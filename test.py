#!/usr/bin/python2

import sys, pprint
sys.path.insert(0, '.')

from biblio.ebook import ebook_metadata

for f in sys.argv[1:]:
    m = ebook_metadata(f)
    if m is None:
        print "%s: not an ebook file" % f
        continue

    print f
    print "  ebook type  :", m.filetype.description
    print "  title       :", m.title
    print "  series      :", m.series, m.series_index
    print "  author(s)   :", '; '.join(m.authors)
    print "  published   :", m.date_published
    print "  publisher   :", m.publisher
    print "  rights      :", m.rights
    print "  langauge(s) :", m.languages
    print "  identifiers :", m.identifiers
    print "  tags        :", m.tags
    print "  description :", m.description
