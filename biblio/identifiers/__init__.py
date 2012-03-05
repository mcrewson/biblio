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
from contextlib  import closing
from collections import namedtuple
import functools, re, struct

from biblio.identifiers           import text
from biblio.identifiers.filetypes import *
from biblio.plugs                 import iterate_pluggables, IDENTIFIERS

__all__ = [ 'identifier', 'identify_stream', 'identify_file', 'IdentifierBuilder', ]

##############################################################################

class BiblioIdentifierError (Exception):
    pass

class InvalidBiblioIdentifier (BiblioIdentifierError):
    pass

identifier = namedtuple('identifier', 'text binary rules')

max_data_buffer_size = 0

##############################################################################

def _calc_identifier_sizes (identifier):
    min_size = 4096
    max_size = 0
    cpos = 0
    for rule in identifier.rules:
        off,typ,val = rule
        if type(off) is str:
            if off[0] == '+':
                off = cpos + int(off[1:], 10)
            elif off[0] == '-':
                off = cpos - int(off[1:], 10)
            else:
                off = int(off, 10)

        if typ == 'string':
            cpos = off + len(val)
            minsz = maxsz = cpos
        elif typ == 'struct':
            cpos = off + struct.calcsize(val[0])
            minsz = maxsz = cpos
        elif typ in ('search', 'regex'):
            minsz = cpos = off
            maxsz = off + val[0]
        min_size = min(min_size, minsz)
        max_size = max(max_size, maxsz)
    return min_size, max_size

##############################################################################

def identify_stream (stream):
    global max_data_buffer_size

    data = stream.read(max_data_buffer_size)
    current_pos = 0

    def test_identifier_rules (ident):
        min_size, max_size = _calc_identifier_sizes(ident)
        if len(data) < min_size:
            return False

        for rule in ident.rules:
            off,typ,val = rule
            if type(off) is str:
                if off[0] == '+':
                    off = current_pos + int(off[1:], 10)
                elif off[0] == '-':
                    off = current_pos - int(off[1:], 10)
                else:
                    off = int(off, 10)
                if off < 0:
                    raise RuntimeException('Invalid identifer offset: %d' % off)

            if typ == 'string':
                value = data[off:off+len(val)]
                if value != val:
                    return False
                current_pos = off + len(val)
            elif typ == 'struct':
                pack, testvals = val[0], val[1:]
                value = struct.unpack(pack, data[off:off+struct.calcsize(pack)])
                if value != testvals:
                    return False
                current_pos = off + struct.calcsize(pack)
            elif typ == 'search':
                searchsz, searchval = val
                value = data[off:off+searchsz]
                current_pos = data.find(searchval, off, off+searchsz)
                if current_pos < 0:
                    return False
                current_pos += len(searchval)
            elif typ == 'regex':
                regexsz, regexval = val
                value = data[off:off+regexsz]
                match = re.search(regexval, value)
                if not match:
                    return False
                current_pos = off + match.end(0)
            elif typ == 'func':
                result = val(stream, data[off:])
                if not result:
                    return False
                current_pos = stream.tell()

        return True

    textfile = text.is_text(data)

    for filetype,identifier in iterate_pluggables(IDENTIFIERS):
        if textfile == True and identifier.text == False: continue
        if textfile == False and identifier.binary == False: continue
        if test_identifier_rules(identifier):
            return filetype

    return None

def identify_file (filename):
    with closing(open(filename, 'rb')) as stream:
        return identify_stream(stream)

##############################################################################

class IdentifierBuilder (object):

    def __init__ (self, textonly=False, binaryonly=False):
        self.rules = []
        self.text = True
        self.binary = True

        if textonly and binaryonly:
            raise RuntimeError("Identifier cannot be both text-only and binary-only")
        elif textonly:
            self.binary = False
        elif binaryonly:
            self.text = False

    def _validate_offset (self, off):
        if type(off) not in (int, str):
            raise InvalidBiblioIdentifier("offset must be an string or integer")
        if type(off) is str:
            if off[0] not in ('-','+'):
                raise InvalidBiblioIdentifier("string offsets must begin with '-' or '+'")
            try:
                int(off[1:], 10)
            except ValueError:
                raise InvalidBiblioIdentifier("offset must be a number")

    def string (self, offset, value):
        self._validate_offset(offset)
        self.rules.append((offset, 'string', value))
        return self

    def struct (self, offset, pack, *values):
        self._validate_offset(offset)
        try:
            struct.calcsize(pack)
        except struct.error:
            raise InvalidBiblioIdentifier("invalid struct pattern", id)
        vals = [pack]
        vals.extend(values)
        self.rules.append((offset, 'struct', tuple(vals)))
        return self

    def search (self, offset, searchsize, value):
        self._validate_offset(offset)
        if type(searchsize) is not int:
            raise InvalidBiblioIdentifier("searchsize must be an integer")
        self.rules.append((offset, 'search', (searchsize, value)))
        return self

    def regex (self, offset, regexsize, value):
        self._validate_offset(offset)
        if type(regexsize) is not int:
            raise InvalidBiblioIdentifier("regexsize must be an integer")
        self.rules.append((offset, 'regex', (regexsize, value)))
        return self

    def func (self, offset, func):
        self._validate_offset(offset)
        self.rules.append((offset, 'func', func))
        return self

    def build (self):
        global max_data_buffer_size

        ident = identifier(text=self.text, binary=self.binary,
                           rules=tuple(self.rules))

        minsize,maxsize = _calc_identifier_sizes(ident)
        max_data_buffer_size = max(max_data_buffer_size, maxsize)
        return ident

##############################################################################

def initialize_builtin_pluggables (plug_adder_method):

    # some aliases and shortcuts
    add = functools.partial(plug_adder_method, override=False)
    ib  = functools.partial(IdentifierBuilder, binaryonly=True)
    it  = functools.partial(IdentifierBuilder, textonly=True)

    # EBOOKS #################################################################

    ## EPUB
    add(EPUB2, ib().string(0,'PK\003\004').string(26,'\x08\0\0\0mimetypeapplication/').string(50,'epub+zip').build())

    ## PALM
    add(MOBI         , ib().string(60,'BOOKMOBI').build())
    add(PDB_EREADER  , ib().string(60,'PNRdPPrs').build())
    add(PDB_GUTENPALM, ib().string(60,'zTXT'    ).build())
    add(PDB_PALMDOC  , ib().string(60,'TEXtREAd').build())
    add(PDB_PLUCKER  , ib().string(60,'DataPlkr').build())

    ## Microsoft Reader
    add(LIT, ib().string(0,'ITOLITLS').build())

    # IMAGES #################################################################

    add(GIF87A   , ib().string(0,'GIF87a').build())
    add(GIF89A   , ib().string(0,'GIF89a').build())
    add(JPEG_JFIF, ib().struct(0,'>H',0xffd8).string(6, 'JFIF').build())
    add(JPEG_EXIF, ib().struct(0,'>H',0xffd8).string(6, 'Exif').build())
    add(PNG      , ib().string(0,'\x89PNG\x0d\x0a\x1a\x0a').build())

    # AUDIO ##################################################################

    add(FLAC  , ib().string(0,'fLaC\0').build())
    add(M4A   , ib().string(4,'ftypM4A ').build())
    add(MP3_1 , ib().struct(0,'>H',0xfffb).build())
    add(ID3V22, ib().string(0,'ID3').struct(3,'bb',2,0).build())
    add(ID3V23, ib().string(0,'ID3').struct(3,'bb',3,0).build())
    add(ID3V24, ib().string(0,'ID3').struct(3,'bb',4,0).build())

    # VIDEO ##################################################################

    add(M4V1, ib().string(4,'ftypisom').build())
    add(M4V1, ib().string(4,'ftypmp41').build())
    add(M4V2, ib().string(4,'ftypmp42').build())
    add(M4V , ib().string(4,'ftypM4V ').build())
    add(MKV , ib().struct(0, '>l', 0x1a45dfa3).search(5,4096,'\x42\x82').string('+1','matroska').build())
    add(WEBM, ib().struct(0, '>l', 0x1a45dfa3).search(5,4096,'\x42\x82').string('+1','webm').build())
    add(AVI , ib().string(0, 'RIFF').string(8, 'AVI\040').build())

    # SGML/XML/HTML ##########################################################

    add(OPF2 , it().string(0,'<?xml').regex(20,400,'<package[^>]+xmlns=[\'"]http://www.idpf.org/2007/opf[\'"]').build())
    add(SVG  , it().string(0,'<?xml').regex(20,400,'<svg[^>]+xmlns=[\'"http://www.w3.org/2000/svg[\'"]').build())
    add(XHTML, it().string(0,'<?xml version="').search(19,4096,'<!doctype html').build())
    add(XHTML, it().string(0,'<?xml version=\'').search(19,4096,'<!doctype html').build())
    add(HTML , it().search(0,4096,'<!doctype html').build())
    add(HTML , it().search(0,4096,'<html').build())
    add(HTML , it().search(0,4096,'<head').build())
    add(HTML , it().search(0,4096,'<title').build())
    add(XML  , it().string(0,'<?xml').build())

    # MISC OTHER FILES #######################################################

    ## PDF documents
    add(PDF, ib().string(0,'%PDF-').build())

    ## Generic Zip files
    add(ZIP09, ib().string(0,'PK\003\004').struct(4,'>b',0x09).build())
    add(ZIP10, ib().string(0,'PK\003\004').struct(4,'>b',0x0a).build())
    add(ZIP11, ib().string(0,'PK\003\004').struct(4,'>b',0x0b).build())
    add(ZIP20, ib().string(0,'PK\003\004').struct(4,'>b',0x14).build())
    add(ZIP30, ib().string(0,'PK\003\004').struct(4,'>b',0x2d).build())


##############################################################################
## THE END
