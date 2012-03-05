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

# MOBI FORMAT
#
# MOBI was originally an extension of the PalmDOC by adding certain HTML like
# tags to the data, and many MOBI formatted documents still use this form.
# However there is also a high compression version of this file format that 
# compresses data to a larger degree in a proprietary manner. There are some 
# third party programs that can read the eBooks in the original MOBI format 
# but there are only a few third party program that can read the eBooks in the 
# new compressed form. The higher compression mode is using a huffman coding 
# scheme that has been called the Huff/cdic algorithm.
#
# Like PalmDOC, the MOBI file format is that of a standard Palm Database file.
# The header of that database includes the name of the database (usually the
# book title and sometimes a portion of the author's name) which is up to 31
# bytes of data. The files are identified as Creator ID of 'MOBI' and a Type
# of 'BOOK'.
#
# The first record of the database gives more information about the MOBI file.
# The first 16 bytes are almost identical to the sixteen bytes of a PalmDOC
# file.
#
# Offset Bytes Field                Comments
# ------ ----- -------------------- -------------------------------------------
# 00     2     Compression          1 = no compression, 2 = PalmDOC, 17480 = huff/dic
# 02     2     Unused               always zero
# 04     4     Text length          uncompressed length of the entire text
# 08     2     Record count         number of pdb text records
# 10     2     Record size          max size of each text record, always 4096
# 12     2     Encryption type      0 = no encryption, 1 = old mobipocket, 2 = new mobipocket
# 14     2     Unknown              usually zero
#
# The old mobipocket encryption scheme only allows the file to be registered
# with PID, unlike the current scheme which allows multiple PIDs to be used in
# a single file.
#
# Most MOBI files also have a MOBI header in record 0 that follows these 16
# bytes, and newer formats also have an EXTH header following the MOBI header,
# again all in record 0 of the PDB file.
#
# Offset Bytes Field                Comments
# ------ ----- -------------------- -------------------------------------------
# 16     4     Identifier           the characters 'M' 'O' 'B' 'I'
# 20     4     Header length        length of the MOBI header, include previous 4 bytes
# 24     4     Mobi type            the kind of MOBI file this is
# 28     4     Text encoding        1252 = CP1252 (Win Latin 1), 65001 = UTF-8
# 32     4     Unique id            some kind of unique id number (random?)
# 36     4     File version         version of the mobipocket format used in this file
# 40     4     Ortographic index    record number of the ortographic meta index
# 44     4     Inflection index     record number of the inflection meta index
# 48     4     Index names          
# 52     4     Index keys
# 56     4     Extra index 0        record number of extra 0 meta index
# 60     4     Extra index 1        record number of extra 1 meta index
# 64     4     Extra index 2        record number of extra 2 meta index
# 68     4     Extra index 3        record number of extra 3 meta index
# 72     4     Extra index 4        record number of extra 4 meta index
# 76     4     Extra index 5        record number of extra 5 meta index
# 80     4     First non-book idx   first record number that's not the book's text
# 84     4     Full name offset     offset in record 0 of the full name of the book
# 88     4     Full name length     length in bytes of the full name of the book
# 92     4     Locale               Book locale code. low byte = main lang, hi byte = dialect
# 96     4     Input language       Input language for a dictionary
# 100    4     Output language      Output language for a dictionary
# 104    4     Min version          Minimum mobipocket version support needed to read this file
# 108    4     First image          First record number that contains an image
# 112    4     Huffman record       Record number of the first huffman compression record
# 116    4     Huffman count        Number of huffman compression records
# 120    4     Huffman table
# 124    4     Huffman table length
# 128    4     EXTH flags           bit field. if bit 6 (0x40) is set, there is an EXTH record
# 132    32    ?                    32 unknown bytes, if MOBI header is long enough
# 164    4     DRM offset           offset to DRM key info (in DRMed files)
# 168    4     DRM count            number of entires in DRM info
# 172    4     DRM size             number of bytes in DRM info
# 176    4     DRM flags            some flags concerning the DRM info
# 180    ?     ?                    bytes to the end of MOBI header
# 242    2     Extra data flags     
# 244    4     INDX record          record number of the first INDX record
#
# Some possible Mobi type field values:
#  2    Mobipocket book
#  3    PalmDOC book
#  4    Audio
#  232  mobipocket? (generated by kindlegen 1.2)
#  248  KF8 (generated by kindlegen 1.2)
#  257  News
#  258  News Feed
#  259  News Magazine
#  513  PICS
#  514  WORD
#  515  XLS
#  516  PPT
#  517  TEXT
#  518  HTML
#
# EXTH Header
#  If the MOBI header indicates that there is an EXTH header, it follows immediately
#  after the MOBI header in record 0. Since the MOBI header is of variable length,
#  this isn't at any fixed offset. Note that some readers will ignore any EXTH header
#  info if the mobipocket version number specified in the MOBI header is 2 or less
#  (perhaps 3 or less).
#
#  Bytes Field                      Comments
#  ----- ------------               -------------------------------------------
#  4     identifier                 the characters 'E' 'X' 'T' 'H'
#  4     header length              the length of the EXTH header, includ previous 4 bytes
#  4     record count               number of record in EXTH header.
#  --------------------------------
#  start of exth records            repeat until done
#  --------------------------------
#  4     record type                EXTH record type. see below.
#  4     record length              length of EXTH record, includ the 8 bytes in type and length fields
#  L-8   data                       
#  --------------------------------
#  end of exth records
#  --------------------------------
#  p     Padding                    null bytes to pad EXTH header to multiple of four bytes
#
# There are lots of different EXTH record types. Some of the most common ones:
#  1    drm_server_id
#  2    drm_commerce_id
#  3    drm_ebookbase_book_id
#  100  author
#  101  publisher
#  102  imprint
#  103  description
#  104  isbn
#  105  subject
#  106  publishing date
#  107  review
#  108  contributor
#  109  rights
#  110  subject code
#  111  type
#  112  source
#  113  asin
#  114  version number
#  115  sample                  (0x0001 if the book content is only a sample of the full book)
#  116  start reading           position (4-byte offset) in file at which to open when first opened
#  117  adult                   Mobipocket creator adds this if 'Adult only' is checked. Contents: "yes"
#  118  retail price
#  119  retail price currency
#  200  dictionary short name
#  201  cover offset
#  202  thumb offset
#  203  has fake cover
#  204  creator software
#  205  creator major version
#  206  creator minor version
#  207  creator build number
#  208  watermark
#  209  tamper proof keys
#  300  font signature
#  401  clipping limit
#  402  publisher limit
#  403  (unknown)
#  404  tts flag
#  405  (unknown)
#  406  (unknown)
#  407  (unknown)
#  450  (unknown)
#  451  (unknown)
#  452  (unknown)
#  453  (unknown)
#  501  cde type
#  502  last update time
#  503  updated titlte
#  504  asin
#
# At the end of record 0 of the PDB file, we usually get the full file name, the
# offset of which is given in the MOBI header.
#
# There might be data of unknown used between the end of the EXTH records and the name.
#
# The name is usually followed by two null bytes, and then padded with null bytes to
# a four-byte boundary

from __future__ import with_statement
from contextlib import closing
import re, struct

from biblio.metadata              import Metadata, Storage
from biblio.identifiers.filetypes import MOBI
from biblio.parsers               import parser
from biblio.parsers.pdb           import PDBException, read_pdb_metadata

##############################################################################

class MobiException (PDBException):
    pass

##############################################################################

def read_mobi_metadata (filename, metadata=None):
    if metadata is None:
        metadata = Metadata(MOBI)
    read_pdb_metadata(filename, metadata)

    if metadata.pdb.num_records < 2:
        # No mobi header record !?
        return metadata

    offset, length = metadata.pdb.records[0]
    with closing(open(filename, 'rb')) as stream:
        stream.seek(offset)
        raw = stream.read(length)

    metadata.mobi = _parse_mobi_header(raw)

    return metadata

def _parse_mobi_header (raw):
    mobiheader = Storage()

    mobiheader.compression, \
    _unused, \
    mobiheader.text_length, \
    mobiheader.record_count, \
    mobiheader.record_size, \
    mobiheader.encryption, \
    _unknown, \
        = struct.unpack('>HHLHHHH', raw[0:0x10])

    # Some ancient MOBI files have no more metadata than this
    if len(raw) <= 16:
        return mobiheader

    mobiheader.identifier, \
    mobiheader.header_length, \
    mobiheader.mobi_type, \
    mobiheader.text_encoding, \
    mobiheader.unique_id, \
    mobiheader.file_version, \
    mobiheader.ortographic_index_record, \
    mobiheader.inflection_index_record, \
    mobiheader.index_names_record, \
    mobiheader.index_keys_record, \
    mobiheader.extra_index0_record, \
    mobiheader.extra_index1_record, \
    mobiheader.extra_index2_record, \
    mobiheader.extra_index3_record, \
    mobiheader.extra_index4_record, \
    mobiheader.extra_index5_record, \
    mobiheader.first_nonbook_record, \
    mobiheader.fullname_offset, \
    mobiheader.fullname_length, \
    mobiheader.locale, \
    mobiheader.dictionary_input_language, \
    mobiheader.dictionary_output_language, \
    mobiheader.min_version, \
    mobiheader.first_image_record, \
    mobiheader.huffman_record, \
    mobiheader.huffman_record_count, \
    mobiheader.huffman_table_record, \
    mobiheader.huffman_table_length, \
    mobiheader.exth_flags, \
        = struct.unpack('>4sLLLLLLLLLLLLLLLLLLLLLLLLLLLL', raw[0x10:0x84])

    if len(raw) >= 0xb4:
        mobiheader.drm_offset, \
        mobiheader.drm_count, \
        mobiheader.drm_size, \
        mobiheader.drm_flags, \
            = struct.unpack('>LLLL', raw[0xa4:0xb4])

    if mobiheader.header_length < 0xe4 or \
       mobiheader.header_length > 0xf8:
        mobiheader.extra_flags = 0
    else:
        mobiheader.extra_flags, = struct.unpack('>H', raw[0xf2:0xf4])

    fullname_end = mobiheader.fullname_offset + mobiheader.fullname_length
    if fullname_end < len(raw):
        mobiheader.fullname = raw[mobiheader.fullname_offset:fullname_end]
    else:
        mobiheader.fullname = None

    if mobiheader.exth_flags & 0x40:
        mobiheader.exth = _parse_exth_header(raw[16 + mobiheader.header_length:])

    return mobiheader

def _parse_exth_header (raw):
    exth = Storage()

    exth.identifier, \
    exth.header_length, \
    exth.record_count, \
        = struct.unpack('>4sLL', raw[:12])

    exthdata = raw[12:]
    pos = 0

    records = []
    records_left = exth.record_count
    while records_left > 0:
        records_left -= 1
        record = Storage()
        record.type, \
        record.length, \
            = struct.unpack('>LL', exthdata[pos:pos + 8])
        record.data = exthdata[pos+8:pos+record.length]
        pos += record.length
        records.append(record)
    exth.records = records
    return exth

##############################################################################

class MOBIEbook (object):

    def to_ebook (metadata):
        ebook = EbookMetadata(metadata.filetype)
        try:
            ebook.title = raw_metadata.mobi.fullname
        except AttributeError:
            ebook.title = re.sub('[^-A-Za-z0-9\"";:., ]+', '_', raw_metadata.pdb.name.replace('\x00', ''))

        return ebook

    def to_metadata (ebook):
        pass

##############################################################################

def initialize_parser ():
    return parser(filetype=MOBI, reader=read_mobi_metadata, writer=None, processor=None)

##############################################################################
## THE END
