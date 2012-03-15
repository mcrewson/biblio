# vim:set ts=4 sw=4 sts=4 et nowrap syntax=python ff=unix:
#
# Copyright 2011 Mark Crewson <mark@crewson.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import with_statement
from contextlib import closing

from lxml import etree

from biblio.metadata              import Metadata, Storage
from biblio.identifiers.filetypes import OPF2
from biblio.parsers               import parser
from biblio.parsers.file          import read_file_metadata
from biblio.util.xmlunicode       import xml_to_unicode

##############################################################################

NAMESPACES = { 'dc'      : 'http://purl.org/dc/elements/1.1',
               'dcterms' : 'http://purl.org/dc/terms',
               'opf'     : 'http://www.idpf.org/2007/opf',
             }

##############################################################################

def read_opf_metadata (filename, metadata=None):
    if metadata is None:
        metadata = Metadata(OPF2)
    read_file_metadata(filename, metadata)

    with closing(open(filename, 'r')) as stream:
        metadata.opf = parse_opf_xml(stream.read())

    return metadata
            
##############################################################################

def parse_opf_xml (rawxml):
    rawxml, encoding = xml_to_unicode(rawxml, strip_encoding_pats=True, resolve_entities=True, assume_utf8=True)
    rawxml = rawxml[rawxml.find('<'):]
    tree = etree.fromstring(rawxml, etree.XMLParser(recover=True))

    opf = Storage()

    for section in ('metadata', 'manifest', 'spine', 'guide'):
        subtree = tree.find('opf:%s' % section, namespaces=NAMESPACES)
        if subtree is not None:
            for el in subtree.getchildren():
                opf.setdefault(section, []).append((el.tag, el.attrib, el.text))

    return opf

##############################################################################

def process_opf_metadata (metadata, ebook):
    for tag,attribs,text in metadata.metadata:
        if tag == '{http://purl.org/dc/elements/1.1/}title':
            ebook.title = text.strip()
        elif tag == '{http://purl.org/dc/elements/1.1/}publisher':
            ebook.publisher = text.strip()
        elif tag == '{http://purl.org/dc/elements/1.1/}date':
            from biblio.ebook import parse_ebook_date
            ebook.date_published = parse_ebook_date(text.strip())
        elif tag == '{http://purl.org/dc/elements/1.1/}description':
            ebook.description = text.strip()
        elif tag == '{http://purl.org/dc/elements/1.1/}rights':
            ebook.rights = text.strip()
        elif tag == '{http://purl.org/dc/elements/1.1/}language':
            ebook.setdefault('languages', []).append(text.strip())
        elif tag == '{http://purl.org/dc/elements/1.1/}subject':
            if text and text.strip():
                ebook.setdefault('tags', []).extend([ x.strip() for x in text.split(',')])
        elif tag == '{http://purl.org/dc/elements/1.1/}identifier':
            if text and text.strip():
                for attr,val in attribs.iteritems():
                    if attr.endswith('scheme'):
                        typ = val.lower()
                        ebook.setdefault('identifiers', {})[typ] = text.strip()
        elif tag == '{http://purl.org/dc/elements/1.1/}creator':
            if ('role' in attribs and attribs['role'] == 'aut') or \
               ('{http://www.idpf.org/2007/opf}role' in attribs and 
                attribs['{http://www.idpf.org/2007/opf}role'] == 'aut') or \
               ('role' not in attribs and 
                '{http://www.idpf.org/2007/opf}role' not in attribs):
                from biblio.ebook import parse_ebook_authors
                ebook.setdefault('authors', []).extend(parse_ebook_authors(text))
        elif tag == '{http://www.idpf.org/2007/opf}meta':
            if not ('name' in attribs and 'content' in attribs): continue
            name = attribs['name']
            content = attribs['content']
            if name == 'calibre:series':
                ebook.series = content.strip()
            elif name == 'calibre:series_index':
                ebook.series_index = float(content.strip())

    return ebook

##############################################################################
def initialize_parser ():
    return parser(filetype=OPF2, reader=read_opf_metadata, writer=None, processor=None)

##############################################################################
## THE END
