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

from biblio.metadata           import Metadata, Storage
from biblio.identify.filetypes import OPF2
from biblio.parsers            import add_parser
from biblio.parsers.file       import FileParser
from biblio.util.xmlunicode    import xml_to_unicode

##############################################################################

NAMESPACES = { 'dc'      : 'http://purl.org/dc/elements/1.1',
               'dcterms' : 'http://purl.org/dc/terms',
               'opf'     : 'http://www.idpf.org/2007/opf',
             }

##############################################################################

class OPFParser (FileParser):

    filetype = OPF2
    
    def read_metadata (self, filename, metadata=None):
        if metadata is None:
            metadata = Metadata(self.filetype)
        super(OPFParser, self).read_metadata(filename, metadata)

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

add_parser(OPFParser, OPF2, builtin=True)

##############################################################################
## THE END
