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

# PALM DATABASE FILES
#
# A Palm Database is not a file when stored on the Palm in memory, however
# it will be synced as a file to a computer. The file name will always be
# the database name. Multi-byte numeric fields are stored in big-endian
# order, with the most significant byte first.
#
# Offset Bytes Field                Comments
# ------ ----- -------------------- -------------------------------------------
# 00     32    name                 database name. \x00 terminated in the field
# 32     2     attributes           bit field (see below)
# 34     2     version              file version
# 36     4     creation date        Num seconds since start of Jan 1. 1974
# 40     4     modification date    Num seconds since start of Jan 1. 1974
# 44     4     last backup date     Num seconds since start of Jan 1. 1974
# 48     4     modification number 
# 52     4     appInfoId            offset to start of AppInfo (if present)
# 56     4     sortInfoId           offset to start of SortInfo (if present)
# 60     4     type                 see database type-creator table below
# 64     4     creator              see database type-creator table below
# 68     4     uniqueIdSeed         used internally to identify record
# 72     4     nextRecordListId     only used in-memory on Palm OS. Always zero
# 76     2     number of records    number of records in the file (N)
# 78-    8 * N record info list     
# ---------------------------------
# start of record info entries      repeat N times to end of record info enties
# ---------------------------------
#        4     record data offset   offset of record from start of the PDB
#        1     record attributes    bit field.
#        3     unique id            the unique id for this record
# ---------------------------------
# end of record info entries
# ---------------------------------
#        2?    gap to data          traditionally 2 zero bytes to info or raw data
#        ...   records              actual data in the file. AppInfo (if present), SortInfo, the records
#
#
# PDB attribute bit field:
#  0x0002 Read-Only
#  0x0004 Dirty AppInfo
#  0x0008 Backup this database (i.e., no conduit exists)
#  0x0010 Okay to install newer over existing copy, if present on PalmPilot
#  0x0020 Force the PalmPilot to reset after this database is installed
#  0x0040 Don't allow copy of file to be beamed to another PalmPilot
#
# Common PDB type-creator fields:
#  Type  Creator Reader
#  ----- ------- -----------
#  TEXt  REAd    PalmDOC
#  PNRd  PPrs    eReader
#  Data  Plkr    Plucker
#  BOOK  MOBI    Mobipocket
#
# Record attribute bit field:
#  The least significant four bits are used to represent the category values.
#  These categories are used to split the database for viewing on screen. A
#  few of the 16 categories are predefined but the user can add their own.
#  There is an undefined category for use if the user or programmer has not
#  set this.
#
#  0x10 Secret record
#  0x20 Record in use (busy bit)
#  0x30 Dirty record
#  0x40 Delete record on next hotsync
#
# PDB Times:
#  The original PDB format uses times counted in seconds from Jan 1, 1904, the
#  base time used by the original Mac OS, using an unsigned 32-bit integer. 
#  However, a PDB tool written in Perl says that the time should be counted
#  from Jan 1, 1970 the unix base time, and uses a signed 32-bit integer.
#  This conflict is unfortunate, but simple to sort out: if the time has the
#  top bit set, it's an unsigned 32-bit number counting from Jan 1, 1904; or
#  if the top bit is clear, it's a signed 32-bit number countring from
#  Jan 1, 1970
#

from __future__ import with_statement

import datetime, re, struct
from contextlib import closing

from biblio.metadata           import Metadata, Storage
from biblio.identify.filetypes import PDB_EREADER, PDB_GUTENPALM, \
                                      PDB_PALMDOC, PDB_PLUCKER
from biblio.parsers            import add_parser, ParserException
from biblio.parsers.file       import FileParser

##############################################################################

class PDBException (ParserException):
    pass

class EReaderException (PDBException):
    pass

class PalmDOCException (PDBException):
    pass

class PluckerException (PDBException):
    pass

PDB_TIMESTAMP_OFFSET = long(-2082844800.0)

##############################################################################

class PDBParser (FileParser):

    def read_metadata (self, filename, metadata=None):
        if metadata is None:
            metadata = Metadata(self.filetype)
        super(PDBParser, self).read_metadata(filename, metadata)

        with closing(open(filename, 'rb')) as stream:
            metadata.pdb = self._parse_pdb_header(stream)

        return metadata

    def _parse_pdb_header (self, stream):
        pdbheader = Storage()

        # PDB fields
        pdbheader.name, \
        pdbheader.attributes, \
        pdbheader.version, \
        pdbheader.creation_timestamp, \
        pdbheader.modification_timestamp, \
        pdbheader.last_backup_timestamp, \
        pdbheader.modification_number, \
        pdbheader.appinfo_offset, \
        pdbheader.sortinfo_offset, \
        pdbheader.type, \
        pdbheader.creator, \
        pdbheader.uniqueidseed, \
        pdbheader.nextrecordlistid, \
        pdbheader.num_records, \
            = struct.unpack('>32sHHLLLLLL4s4sLLH', stream.read(78))

        # record offsets and lengths
        records = []
        start = struct.unpack('>LBBBB', stream.read(8))[0]
        for n in range(1, pdbheader.num_records):
            next_start = struct.unpack('>LBBBB', stream.read(8))[0]
            records.append((start, next_start - start))
            start = next_start
        stream.seek(0, 2)
        end = stream.tell()
        records.append((start, end - start))
        pdbheader.records = records

        # Clean up some of the fields
        pdbheader.name = re.sub('[^-A-Za-z0-9\'";:,. ]+', '_', pdbheader.name.replace('\x00', ''))

        return pdbheader

##############################################################################

# eReader Format
#
#

class EReaderParser (PDBParser):
    
    filetype = PDB_EREADER

    def read_metadata (self, filename, metadata=None):
        if metadata is None:
            metadata = Metadata(self.filetype)
        super(EReaderParser, self).read_metadata(filename, metadata)

        offset, length = metadata.pdb.records[0]
        with closing(open(filename, 'rb')) as stream:
            stream.seek(offset)
            raw = stream.read(length)

        header_size = len(raw)
        if header_size == 132:
            metadata.ereader = self._parse_ereader_header132(raw)
        elif header_size in (116,202):
            metadata.ereader = self._parse_ereader_header202(raw)
        else:
            raise EReaderException('Size mismatch. eReader header record size %s bytes is not supported' % header_size)

        return metadata

    def _parse_ereader_header132 (self, raw):
        h = Storage()
        h.compression, \
        _unknown1, \
        h.encoding, \
        h.number_small_pages, \
        h.number_large_pages, \
        h.non_text_records, \
        h.number_chapters, \
        h.number_small_index, \
        h.number_large_index, \
        h.number_images, \
        h.number_links, \
        h.metadata_available, \
        _unknown2, \
        h.number_footnotes, \
        h.number_sidebars, \
        h.chapter_index_records, \
        h.magic_2560, \
        h.small_page_index_record, \
        h.large_page_index_record, \
        h.image_data_record, \
        h.links_record, \
        h.metadata_record, \
        _unknown3, \
        h.footnote_record, \
        h.sidebar_record, \
        h.last_data_record, \
            = struct.unpack('>HLHHHHHHHHHHHHHHHHHHHHHHH', raw[:54])

        return h

    def _parse_ereader_header202 (self, raw):
        # Unfortunately, this header format is mostly unknown
        h = Storage()
        h.version, \
        _unknown, \
        h.non_text_records, \
            = struct.unpack('>H6sH', raw[:10])

        return h

##############################################################################

# PalmDOC Format
#
# PalmDOC is a standard PDB file. Record 0 contains the following additional
# metadata:
#
# Offset Bytes Field                Comments
# ------ ----- -------------------- -------------------------------------------
# 00     2     Compression          1 = no compression, 2 = PalmDOC, 17480 = huff/dic
# 02     2     Unused               always zero
# 04     4     Text length          uncompressed length of the entire text
# 08     2     Record count         number of pdb text records
# 10     2     Record size          max size of each text record, always 4096
# 12     4     Current position     current reading position, offset into uncompressed text

class PalmDOCParser (PDBParser):

    filetype = PDB_PALMDOC

    def read_metadata (self, filename, metadata=None):
        if metadata is None:
            metadata = Metadata(self.filetype)
        super(PalmDOCParser, self).read_metadata(filename, metadata)

        offset, length = metadata.pdb.records[0]
        with closing(open(filename, 'rb')) as stream:
            stream.seek(offset)
            raw = stream.read(length)

        metadata.palmdoc = self._parse_palmdoc_header(raw)

        return metadata

    def _parse_palmdoc_header (self, raw):
        h = Storage()

        h.compression, \
        _unused, \
        h.text_length, \
        h.record_count, \
        h.record_size, \
        h.current_position, \
            = struct.unpack('>HHLHHL', raw[0:0x10])

        return h

##############################################################################

# Plucker Format
#
#

class PluckerParser (PDBParser):

    filetype = PDB_PLUCKER

    def read_metadata (self, filename, metadata=None):
        if metadata is None:
            metadata = Metadata(self.filetype)
        super(PluckerParser, self).read_metadata(filename, metadata)

        offset, length = metadata.pdb.records[0]
        with closing(open(filename, 'rb')) as stream:
            stream.seek(offset)
            raw = stream.read(length)

        metadata.plucker = self._parse_plucker_header(raw)

        return metadata

    def _parse_plucker_header (self, raw):
        h = Storage()

        h.uid, \
        h.compression, \
        h.records, \
            = struct.unpack('>HHH', raw[0:6])
        h.home_html = None

        reserved = {}
        for i in xrange(h.records):
            adv = 4 * i
            name, = struct.unpack('>H', raw[6+adv:8+adv])
            id,   = struct.unpack('>H', raw[8+adv:10+adv])
            reserved[id] = name
            if name == 0:
                h.home_html = id
        h.reserved = reserved

        return h

##############################################################################

# PalmDOC Format
#
# PalmDOC is a standard PDB file. Record 0 contains the following additional
# metadata:
#
# Offset Bytes Field                Comments
# ------ ----- -------------------- -------------------------------------------
# 00     2     Version              file version
# 02     2     Record count         number of data records
# 04     4     Text length          uncompressed length of the entire text
# 08     2     Record size          max size of each text record, always 4096
# 10     2     Bookmarks count      number of bookmarks in the bookmark index
# 12     2     Bookmark record      record number of bookmark index. 0 if none
# 14     2     Annotations count    number of annotation in the annotation index
# 16     2     Annotation record    record number of annotation index. 0 if none
# 18     1     Flags                bit field.
# 19     1     (reserved)
# 20     4     Crc 32               CRC-32 value of text data
# 24     8     Padding              null bytes

class ZTxtParser (PDBParser):

    filetype = PDB_GUTENPALM

    def read_metadata (self, filename, metadata=None):
        if metadata is None:
            metadata = Metadata(self.filetype)
        super(ZTxtParser, self).read_metadata(filename, metadata)

        offset, length = metadata.pdb.records[0]
        with closing(open(filename, 'rb')) as stream:
            stream.seek(offset)
            raw = stream.read(length)

        metadata.ztxt = self._parse_ztxt_header(raw)

        return metadata

    def _parse_ztxt_header (self, raw):
        h = Storage()
        h.version, \
        h.record_count, \
        h.data_size, \
        h.record_size, \
        h.number_bookmarks, \
        h.bookmark_record, \
        h.number_annotations, \
        h.annotation_record, \
        h.flags, \
        _reserved, \
        h.crc32, \
            = struct.unpack('>HHLHHHHHBBL', raw[0:24])
        return h

##############################################################################

add_parser (EReaderParser, PDB_EREADER  , builtin=True)
add_parser (PalmDOCParser, PDB_PALMDOC  , builtin=True)
add_parser (PluckerParser, PDB_PLUCKER  , builtin=True)
add_parser (ZTxtParser   , PDB_GUTENPALM, builtin=True)

##############################################################################
## THE END
