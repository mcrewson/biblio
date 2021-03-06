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
from zipfile    import ZipFile, BadZipfile

from lxml import etree

from biblio.metadata              import Metadata, EbookMetadata
from biblio.identifiers.filetypes import EPUB2, OPF2
from biblio.parsers               import ParserException, parser
from biblio.parsers.file          import read_file_metadata
from biblio.parsers.opf           import parse_opf_xml, process_opf_metadata

##############################################################################

class EPubException (ParserException):
    pass

CONTAINER_PATH = 'META-INF/container.xml'

##############################################################################

def read_epub_metadata (filename, metadata=None):
    if metadata is None:
        metadata = Metadata(EPUB2)
    read_file_metadata(filename, metadata)

    reader = zip_reader(filename)

    try:
        container = _parse_container_xml(reader(CONTAINER_PATH))
    except KeyError:
        raise EPubException('missing OCF container.xml')

    try:
        metadata.opf = parse_opf_xml(reader(container[OPF2.mimetype]))
    except KeyError:
        raise EPubException('missing OPF package file')

    return metadata
        
def _parse_container_xml (rawxml):
    if not rawxml: return

    tree = etree.fromstring(rawxml)
    rootfiles = tree.xpath('/ns:container/ns:rootfiles/ns:rootfile', 
                           namespaces={'ns':'urn:oasis:names:tc:opendocument:xmlns:container'})
    if not rootfiles:
        raise EPubException("Invalid container.xml")

    container_files = {}
    for rootfile in rootfiles:
        try:
            container_files[rootfile.attrib['media-type']] = rootfile.attrib['full-path']
        except KeyError:
            raise EPubException("<rootfile/> element malformed")

    return container_files
        
def zip_reader (stream, mode='r'):
    try:
        archive = ZipFile(stream, mode)
    except BadZipfile:
        raise EPubException('not a ZIP .epub OCF container')

    def reader (name, mode='r'):
        return archive.read(name)

    return reader

##############################################################################

def process_epub_metadata (metadata):
    ebook = EbookMetadata(metadata.filetype)

    if 'opf' not in metadata:
        return ebook

    process_opf_metadata(metadata.opf, ebook)
    return ebook

##############################################################################

def initialize_parser ():
    return parser(filetype=EPUB2, 
                  reader=read_epub_metadata, 
                  writer=None, 
                  processor=process_epub_metadata)

##############################################################################
## THE END
