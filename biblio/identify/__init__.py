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

import re, struct

from biblio.identify import text

__all__ = [ 'identify_stream', 'identify_file', 'add_magic_identifier', 'identifier', 'BiblioIdentifierError' ]

##############################################################################

class BiblioIdentifierError (Exception):
    pass

class InvalidBiblioIdentifier (BiblioIdentifierError):
    def __init__ (self, message, identifer):
        self.message = message
        self.identifier = identifier
    def __str__ (self):
        return "%s: %s" % (self.message, str(self.identifier))

__builtin_magic_identifiers = []
__extra_magic_identifiers   = []

__max_data_buffer_size = 0

__ident_types = ('string','struct','search','regex','func')

##############################################################################

def _calc_identifier_sizes (identifier):
    min_size = 4096
    max_size = 0
    cpos = 0
    for id in identifier:
        off,typ,val = id
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
    global __builtin_magic_identifiers, __extra_magic_identifiers
    global __max_data_buffer_size

    data = stream.read(__max_data_buffer_size)
    current_pos = 0

    def test_identifier (ident):
        min_size, max_size = _calc_identifier_sizes(ident)
        if len(data) < min_size:
            return False

        for id in ident:
            off,typ,val = id
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

    for identifier in __extra_magic_identifiers:
        if textfile == True and identifier[2] == False: continue
        if textfile == False and identifier[3] == False: continue
        if test_identifier(identifier[0]):
            return identifier[1]
    for identifier in __builtin_magic_identifiers:
        if textfile == True and identifier[2] == False: continue
        if textfile == False and identifier[3] == False: continue
        if test_identifier(identifier[0]):
            return identifier[1]

    return None

def identify_file (filename):
    with closing(open(filename, 'rb')) as stream:
        return identify_stream(stream)

##############################################################################

def add_magic_identifier (identifier, filetype, text=True, binary=True, builtin=False):
    global __builtin_magic_identifiers, __extra_magic_identifiers
    global __max_data_buffer_size, __ident_types

    if builtin:
        identifiers = __builtin_magic_identifiers
        skip_validation = True
    else:
        identifirs = __extra_magic_identifiers
        skip_validation = False

    if not skip_validation:
        if type(identifier) not in (list, tuple):
            raise InvalidBiblioIdentifier("identifier must be a sequence", identifier)
        for id in identifier:
            off,typ,val = id
            if type(off) not in (int, str):
                raise InvalidBiblioIdentifier("offset must be an string or integer", id)
            if type(off) is str:
                if off[0] not in ('-','+'):
                    raise InvalidBiblioIdentifier("string offsets must begin with '-' or '+'", id)
                try:
                    int(off[1:], 10)
                except ValueError:
                    raise InvalidBiblioIdentifier("offset must be a number", id)
            if typ not in __ident_types:
                raise InvalidBiblioIdentifier("idtype must be one of string,struct,search", id)
            if typ == 'struct':
                if type(val) not in (list,tuple):
                    raise InvalidBiblioIdentifier("struct values must be a sequence", id)
                try:
                    struct.calcsize(val[0])
                except struct.error:
                    raise InvalidBiblioIdentifier("invalid struct pattern", id)
            if typ == 'search':
                if type(val) not in (list,tuple):
                    raise InvalidBiblioIdentifier("search values must be a sequence", id)
                if not type(val[0]) is int:
                    raise InvalidBiblioIdenfifier("search size must be an integer", id)
            if typ == 'regex':
                if type(val) not in (list,tuple):
                    raise InvalidBiblioIdentifier("regex values must be a sequence", id)
                if not type(val[0]) is int:
                    raise InvalidBiblioIdenfifier("regex size must be an integer", id)

    min_size, max_size = _calc_identifier_sizes(identifier)
    __max_data_buffer_size = max(__max_data_buffer_size, max_size)
    identifiers.append((identifier, filetype, text, binary))

##############################################################################

class identifier (object):

    def __init__ (self):
        self.parts = []

    def string (self, offset, value):
        self.parts.append((offset, 'string', value))
        return self

    def struct (self, offset, pack, *values):
        vals = [pack]
        vals.extend(values)
        self.parts.append((offset, 'struct', tuple(vals)))
        return self

    def search (self, offset, searchsize, value):
        self.parts.append((offset, 'search', (searchsize, value)))
        return self

    def regex (self, offset, regexsize, value):
        self.parts.append((offset, 'regex', (regexsize, value)))
        return self

    def func (self, offset, func):
        self.parts.append((offset, 'func', func))
        return self

    def make (self):
        return tuple(self.parts)

##############################################################################

import biblio.identify.builtins

##############################################################################
## THE END
