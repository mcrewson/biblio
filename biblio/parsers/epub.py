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

from biblio.metadata           import Metadata
from biblio.identify.filetypes import EPUB2, OPF2
from biblio.parsers            import add_parser, ParserException
from biblio.parsers.file       import FileParser
from biblio.parsers.opf        import parse_opf_xml

##############################################################################

class EPubException (ParserException):
    pass

CONTAINER_PATH = 'META-INF/container.xml'

##############################################################################

class EPubParser (FileParser):

    filetype = EPUB2
    
    def read_metadata (self, filename, metadata=None):
        if metadata is None:
            metadata = Metadata(self.filetype)
        super(EPubParser, self).read_metadata(filename, metadata)

        reader = zip_reader(filename)

        try:
            container = self._parse_container_xml(reader(CONTAINER_PATH))
        except KeyError:
            raise EPubException('missing OCF container.xml')

        try:
            metadata.opf = parse_opf_xml(reader(container[OPF2.mimetype]))
        except KeyError:
            raise EPubException('missing OPF package file')

        return metadata
            
    def _parse_container_xml (self, rawxml):
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
        
##############################################################################

def zip_reader (stream, mode='r'):
    try:
        archive = ZipFile(stream, mode)
    except BadZipfile:
        raise EPubException('not a ZIP .epub OCF container')

    def reader (name, mode='r'):
        return archive.read(name)

    return reader

##############################################################################

add_parser(EPubParser, EPUB2, builtin=True)

##############################################################################
## THE END
