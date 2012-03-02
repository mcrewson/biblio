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

from biblio.identify import identify_file

##############################################################################

__builtin_parsers = {}
__extra_parsers   = {}

##############################################################################

class ParserException (Exception):
    pass

##############################################################################

def find_parser (filename):
    global __builtin_parsers, __extra_parsers

    filetype = identify_file(filename)
    if filetype is None: return None
    parser = __extra_parsers.get(filetype)
    if parser is None:
        parser = __builtin_parsers.get(filetype)
    return parser

##############################################################################

def add_parser (parser, filetype, builtin=False):
    global __builtin_parsers, __extra_parsers

    if builtin:
        parsers = __builtin_parsers
    else:
        parsers = __extra_parsers

    parsers[filetype] = parser

##############################################################################

import biblio.parsers.epub
import biblio.parsers.mobi
import biblio.parsers.pdb
import biblio.parsers.opf

##############################################################################
## THE END
