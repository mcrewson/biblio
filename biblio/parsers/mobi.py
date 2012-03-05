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

from biblio.metadata              import EbookMetadata, Metadata, Storage
from biblio.identifiers.filetypes import MOBI
from biblio.parsers               import parser
from biblio.parsers.pdb           import PDBException, read_pdb_metadata
from biblio.util.xmlunicode       import replace_entities

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

def process_mobi_metadata (metadata):
    ebook = EbookMetadata(metadata.filetype)

    if 'mobi' not in metadata:
        return ebook

    # Determine the codec used for strings. Defaults to 'cp1252'
    codec = 'cp1252'
    if 'text_encoding' in metadata.mobi:
        try:
            codec = {1252:'cp1252', 65001:'utf-8'}[metadata.mobi.text_encoding]
        except (IndexError, KeyError):
            print "Unknown codepage %d. Assuming '%s'" % (metadata.mobi.text_encoding, codec)

    try:
        ebook.title = metadata.mobi.fullname.decode(codec, 'replace')
    except AttributeError:
        ebook.title = re.sub('[^-A-Za-z0-9\"";:., ]+', '_', metadata.pdb.name.replace('\x00', ''))

    ebook.setdefault('languages', []).append(mobi2iana_language(metadata.mobi.locale))

    if 'exth' in metadata.mobi:
        for record in metadata.mobi.exth.records:
            if record.type == 100:
                from biblio.ebook import parse_ebook_authors
                authors = parse_ebook_authors(record.data.decode(codec, 'ignore').strip())
                ebook.setdefault('authors', []).extend(authors)
            elif record.type == 101:
                ebook.publisher = record.data.decode(codec, 'ignore').strip()
            elif record.type == 103:
                ebook.description = record.data.decode(codec, 'ignore')
            elif record.type == 104:
                ebook.setdefault('identifiers', {})['isbn'] = record.data.decode(codec, 'ignore').strip().replace('-', '')
            elif record.type == 105:
                tags = [ t.strip() for t in record.data.decode(codec, 'ignore').split(';') ]
                ebook.setdefault('tags', []).extend(tags)
                ebook.tags = list(set(ebook.tags))
            elif record.type == 106:
                from biblio.ebook import parse_ebook_date
                ebook.date_published = parse_ebook_date(record.data.decode(codec, 'ignore'))
            elif record.type == 108:
                pass # contributor
            elif record.type == 109:
                ebook.rights = record.data.decode(codec, 'ignore')
            elif record.type == 503:
                ebook.title = record.data.decode(codec, 'ignore')

    if ebook.title:
        ebook.title = replace_entities(ebook.title, codec)

    return ebook

##############################################################################

IANA_MOBI = { None: {None: (0, 0)},
              'af': {None: (54, 0)},
              'ar': {None: (1, 0),
                     'AE': (1, 56),
                     'BH': (1, 60),
                     'DZ': (1, 20),
                     'EG': (1, 12),
                     'JO': (1, 44),
                     'KW': (1, 52),
                     'LB': (1, 48),
                     'MA': (1, 24),
                     'OM': (1, 32),
                     'QA': (1, 64),
                     'SA': (1, 4),
                     'SY': (1, 40),
                     'TN': (1, 28),
                     'YE': (1, 36)},
              'as': {None: (77, 0)},
              'az': {None: (44, 0)},
              'be': {None: (35, 0)},
              'bg': {None: (2, 0)},
              'bn': {None: (69, 0)},
              'ca': {None: (3, 0)},
              'cs': {None: (5, 0)},
              'da': {None: (6, 0)},
              'de': {None: (7, 0),
                     'AT': (7, 12),
                     'CH': (7, 8),
                     'LI': (7, 20),
                     'LU': (7, 16)},
              'el': {None: (8, 0)},
              'en': {None: (9, 0),
                     'AU': (9, 12),
                     'BZ': (9, 40),
                     'CA': (9, 16),
                     'GB': (9, 8),
                     'IE': (9, 24),
                     'JM': (9, 32),
                     'NZ': (9, 20),
                     'PH': (9, 52),
                     'TT': (9, 44),
                     'US': (9, 4),
                     'ZA': (9, 28),
                     'ZW': (9, 48)},
              'es': {None: (10, 0),
                     'AR': (10, 44),
                     'BO': (10, 64),
                     'CL': (10, 52),
                     'CO': (10, 36),
                     'CR': (10, 20),
                     'DO': (10, 28),
                     'EC': (10, 48),
                     'ES': (10, 4),
                     'GT': (10, 16),
                     'HN': (10, 72),
                     'MX': (10, 8),
                     'NI': (10, 76),
                     'PA': (10, 24),
                     'PE': (10, 40),
                     'PR': (10, 80),
                     'PY': (10, 60),
                     'SV': (10, 68),
                     'UY': (10, 56),
                     'VE': (10, 32)},
              'et': {None: (37, 0)},
              'eu': {None: (45, 0)},
              'fa': {None: (41, 0)},
              'fi': {None: (11, 0)},
              'fo': {None: (56, 0)},
              'fr': {None: (12, 0),
                     'BE': (12, 8),
                     'CA': (12, 12),
                     'CH': (12, 16),
                     'FR': (12, 4),
                     'LU': (12, 20),
                     'MC': (12, 24)},
              'gu': {None: (71, 0)},
              'he': {None: (13, 0)},
              'hi': {None: (57, 0)},
              'hr': {None: (26, 0)},
              'hu': {None: (14, 0)},
              'hy': {None: (43, 0)},
              'id': {None: (33, 0)},
              'is': {None: (15, 0)},
              'it': {None: (16, 0),
                     'CH': (16, 8),
                     'IT': (16, 4)},
              'ja': {None: (17, 0)},
              'ka': {None: (55, 0)},
              'kk': {None: (63, 0)},
              'kn': {None: (75, 0)},
              'ko': {None: (18, 0)},
              'kok': {None: (87, 0)},
              'lt': {None: (39, 0)},
              'lv': {None: (38, 0)},
              'mk': {None: (47, 0)},
              'ml': {None: (76, 0)},
              'mr': {None: (78, 0)},
              'ms': {None: (62, 0)},
              'mt': {None: (58, 0)},
              'ne': {None: (97, 0)},
              'nl': {None: (19, 0),
                     'BE': (19, 8)},
              'no': {None: (20, 0)},
              'or': {None: (72, 0)},
              'pa': {None: (70, 0)},
              'pl': {None: (21, 0)},
              'pt': {None: (22, 0),
                     'BR': (22, 4),
                     'PT': (22, 8)},
              'rm': {None: (23, 0)},
              'ro': {None: (24, 0)},
              'ru': {None: (25, 0)},
              'sa': {None: (79, 0)},
              'se': {None: (59, 0)},
              'sk': {None: (27, 0)},
              'sl': {None: (36, 0)},
              'sq': {None: (28, 0)},
              'sr': {None: (26, 12),
                     'RS': (26, 12)},
              'st': {None: (48, 0)},
              'sv': {None: (29, 0),
                     'FI': (29, 8)},
              'sw': {None: (65, 0)},
              'ta': {None: (73, 0)},
              'te': {None: (74, 0)},
              'th': {None: (30, 0)},
              'tn': {None: (50, 0)},
              'tr': {None: (31, 0)},
              'ts': {None: (49, 0)},
              'tt': {None: (68, 0)},
              'uk': {None: (34, 0)},
              'ur': {None: (32, 0)},
              'uz': {None: (67, 0),
                     'UZ': (67, 8)},
              'vi': {None: (42, 0)},
              'wen': {None: (46, 0)},
              'xh': {None: (52, 0)},
              'zh': {None: (4, 0),
                     'CN': (4, 8),
                     'HK': (4, 12),
                     'SG': (4, 16),
                     'TW': (4, 4)},
              'zu': {None: (53, 0)} }

def iana2mobi_language(icode):
    langdict, subtags = IANA_MOBI[None], []
    if icode:
        subtags = list(icode.split('-'))
        while len(subtags) > 0:
            lang = subtags.pop(0).lower()
            lang = lang_as_iso639_1(lang)
            if lang and lang in IANA_MOBI:
                langdict = IANA_MOBI[lang]
                break

    mcode = langdict[None]
    while len(subtags) > 0:
        subtag = subtags.pop(0)
        if subtag not in langdict:
            subtag = subtag.title()
        if subtag not in langdict:
            subtag = subtag.upper()
        if subtag in langdict:
            mcode = langdict[subtag]
            break
    return pack('>HBB', 0, mcode[1], mcode[0])

def mobi2iana_language (mobi_locale):
    langcode = mobi_locale & 0xff
    sublangcode = (mobi_locale >> 10) & 0xff

    prefix = suffix = None
    for code, d in IANA_MOBI.items():
        for subcode, t in d.items():
            cc, cl = t
            if cc == langcode:
                prefix = code
            if cl == sublangcode:
                suffix = subcode.lower() if subcode else None
                break
        if prefix is not None:
            break
    if prefix is None:
        return 'und'
    if suffix is None:
        return prefix
    return prefix + '-' + suffix

##############################################################################

def initialize_parser ():
    return parser(filetype=MOBI, 
                  reader=read_mobi_metadata, 
                  writer=None, 
                  processor=process_mobi_metadata)

##############################################################################
## THE END
