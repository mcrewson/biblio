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

from biblio.identify import add_magic_identifier as ami, identifier as ident
from biblio.identify.filetypes import *

import struct

##############################################################################

# ORDER OF THESE DEFINITIONS IS SIGNIFICANT!

# AUDIO
ami(ident().string(0,'fLaC\0').make(), FLAC, text=False, builtin=True)
ami(ident().string(4,'ftypM4A ').make(), M4A, text=False, builtin=True)
ami(ident().struct(0,'>H',0xfffb).make(), MP3_1, text=False, builtin=True)
ami(ident().string(0,'ID3').struct(3,'bb',2,0).make(), ID3V22, text=False, builtin=True)
ami(ident().string(0,'ID3').struct(3,'bb',3,0).make(), ID3V23, text=False, builtin=True)
ami(ident().string(0,'ID3').struct(3,'bb',4,0).make(), ID3V24, text=False, builtin=True)

# Audio files wrapped in an ID3 container
def identify_inside_id3 (stream, data):
    value = data[:4]
    bytes = [ ord(byte) & 0x7f for byte in value]
    bytes.reverse()
    numeric_value = 0
    for shift, byte in zip(range(0, len(bytes)*7, 7), bytes):
        numeric_value += byte << shift
    numeric_value += 10

    from biblio.identify import identify_stream
    stream.seek(numeric_value, 0)
    return identify_stream(stream)

#ami(ident().string(0,'ID3').func(6, identify_inside_id3).make(), MP3_1_ID3, builtin=True)
#ami(ident().string(0,'ID3').seek('(6.I)').struct('+0', '>H',0xfffb).make(), MP3_1_ID3, builtin=True)

# IMAGES
ami(ident().string(0,'GIF87a',).make(), GIF87A, text=False, builtin=True)
ami(ident().string(0,'GIF89a',).make(), GIF89A, text=False, builtin=True)
ami(ident().struct(0,'>H',0xffd8).string(6, 'JFIF').make(), JPEG_JFIF, text=False, builtin=True)
ami(ident().struct(0,'>H',0xffd8).string(6, 'Exif').make(), JPEG_EXIF, text=False, builtin=True)
ami(ident().string(0,'\x89PNG\x0d\x0a\x1a\x0a').make(), PNG, text=False, builtin=True)

# PALM
ami(ident().string(60,'BOOKMOBI').make(), MOBI,          text=False, builtin=True)
ami(ident().string(60,'PNRdPPrs').make(), PDB_EREADER,   text=False, builtin=True)
ami(ident().string(60,'zTXT'    ).make(), PDB_GUTENPALM, text=False, builtin=True)
ami(ident().string(60,'TEXtREAd').make(), PDB_PALMDOC,   text=False, builtin=True)
ami(ident().string(60,'DataPlkr').make(), PDB_PLUCKER,   text=False, builtin=True)

ami(ident().string(0,'%PDF-').make(), PDF, text=False, builtin=True)
ami(ident().string(0,'ITOLITLS').make(), LIT, text=False, builtin=True)

# Zipped documents
ami(ident().string(0,'PK\003\004').string(26,'\x08\0\0\0mimetypeapplication/').string(50,'epub+zip').make(), EPUB2, text=False, builtin=True)
ami(ident().string(0,'PK\003\004').string(26,'\x08\0\0\0mimetypeapplication/').string(50,'vnd.sun.xml.writer').make(), OPENOFFICE1_WRITER, text=False, builtin=True)
ami(ident().string(0,'PK\003\004').string(26,'\x08\0\0\0mimetypeapplication/').string(50,'vnd.sun.xml.calc').make(), OPENOFFICE1_CALC, text=False, builtin=True)
ami(ident().string(0,'PK\003\004').string(26,'\x08\0\0\0mimetypeapplication/').string(50,'vnd.sun.xml.draw').make(), OPENOFFICE1_DRAW, text=False, builtin=True)
ami(ident().string(0,'PK\003\004').string(26,'\x08\0\0\0mimetypeapplication/').string(50,'vnd.sun.xml.impress').make(), OPENOFFICE1_IMPRESS, text=False, builtin=True)
ami(ident().string(0,'PK\003\004').string(26,'\x08\0\0\0mimetypeapplication/').string(50,'vnd.sun.xml.math').make(), OPENOFFICE1_MATH, text=False, builtin=True)
ami(ident().string(0,'PK\003\004').string(26,'\x08\0\0\0mimetypeapplication/').string(50,'vnd.sun.xml.base').make(), OPENOFFICE1_DATABASE, text=False, builtin=True)

# VIDEO
ami(ident().string(4,'ftypisom').make(), M4V1, text=False, builtin=True)
ami(ident().string(4,'ftypmp41').make(), M4V1, text=False, builtin=True)
ami(ident().string(4,'ftypmp42').make(), M4V2, text=False, builtin=True)
ami(ident().string(4,'ftypM4V ').make(), M4V,  text=False, builtin=True)
ami(ident().struct(0, '>l', 0x1a45dfa3).search(5,4096,'\x42\x82').string('+1','matroska').make(), MKV, text=False, builtin=True)
ami(ident().struct(0, '>l', 0x1a45dfa3).search(5,4096,'\x42\x82').string('+1','webm').make(), WEBM, text=False, builtin=True)
ami(ident().string(0, 'RIFF').string(8, 'AVI\040').make(), AVI, text=False, builtin=True)

# Generic Zip files
ami(ident().string(0,'PK\003\004').struct(4,'>b',0x09).make(), ZIP09, text=False, builtin=True)
ami(ident().string(0,'PK\003\004').struct(4,'>b',0x0a).make(), ZIP10, text=False, builtin=True)
ami(ident().string(0,'PK\003\004').struct(4,'>b',0x0b).make(), ZIP11, text=False, builtin=True)
ami(ident().string(0,'PK\003\004').struct(4,'>b',0x14).make(), ZIP20, text=False, builtin=True)
ami(ident().string(0,'PK\003\004').struct(4,'>b',0x2d).make(), ZIP30, text=False, builtin=True)

# SGML/XML/HTML files
ami(ident().string(0,'<?xml').regex(20,400,'<package[^>]+xmlns=[\'"]http://www.idpf.org/2007/opf[\'"]').make(), OPF2, binary=False, builtin=True)
ami(ident().string(0,'<?xml').regex(20,400,'<svg[^>]+xmlns=[\'"http://www.w3.org/2000/svg[\'"]').make(), SVG, binary=False, builtin=True)
ami(ident().string(0,'<?xml version="').search(19,4096,'<!doctype html').make(), XHTML, binary=False, builtin=True)
ami(ident().string(0,'<?xml version=\'').search(19,4096,'<!doctype html').make(), XHTML, binary=False, builtin=True)
ami(ident().search(0,4096,'<!doctype html').make(), HTML, binary=False, builtin=True)
ami(ident().search(0,4096,'<html').make(), HTML, binary=False, builtin=True)
ami(ident().search(0,4096,'<head').make(), HTML, binary=False, builtin=True)
ami(ident().search(0,4096,'<title').make(), HTML, binary=False, builtin=True)
ami(ident().string(0,'<?xml').make(), XML, binary=False, builtin=True)

##############################################################################
## THE END
