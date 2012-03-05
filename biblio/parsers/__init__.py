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

from collections import namedtuple

from biblio.identifiers import identify_file
from biblio.plugs       import find_pluggable, PARSERS

##############################################################################

class ParserException (Exception):
    pass

parser = namedtuple('parser', 'filetype reader writer processor')

ALL_PARSERS = [ 'epub','mobi','pdb','opf' ]

##############################################################################

def find_parser (filetype):
    return find_pluggable(PARSERS, filetype)

def read_metadata (filename):
    filetype = identify_file(filename)
    if filetype is None:
        return None

    parser = find_parser(filetype)
    return parser.reader(filename)

def read_processed_metadata (filename, filetype=None):
    if filetype is None:
        filetype = identify_file(filename)
    if filetype is None:
        return None

    parser = find_parser(filetype)
    return parser.processor(parser.reader(filename))

def write_metadata (filename, metadata):
    filetype = identify_file(filename)
    if filetype is None:
        raise ParserException('Unknown file type: %s' % filename)

    if filetype != metadata.filetype:
        raise ParserException('Metadata is not for this file type: %s' % filename)

    parser = find_parser(filetype)
    if parser.writer is None:
        raise ParserException('Cannot write metadata for this file type: %s' % filename)

    return parser.writer(filename, metadata)

##############################################################################

def initialize_builtin_pluggables (add):
    global ALL_PARSERS

    import imp

    for pluggable in ALL_PARSERS:
        try:
            fp, path, desc = imp.find_module(pluggable, __path__)
        except ImportError:
            continue
        try:
            try:
                module = imp.load_module('%s.%s' % (__name__, pluggable), fp, path, desc)
            except ImportError:
                import traceback
                traceback.print_exc()
                continue
        finally:
            if fp: fp.close()

        initializer = getattr(module, 'initialize_parser', None)
        if initializer is None or not callable(initializer):
            continue
        
        parsers = initializer()
        if type(parsers) in (list,tuple):
            for p in parsers:
                add(p.filetype, p)
        else:
            add(parsers.filetype, parsers)

##############################################################################
## THE END
