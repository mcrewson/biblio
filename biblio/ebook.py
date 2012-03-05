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

from biblio.metadata import RestrictedMetadata
from biblio.identify import identify_file
from biblio.identify.filetypes import is_ebook
from biblio.parsers  import find_parser

##############################################################################

class EbookMetadata (RestrictedMetadata):

    _fields = ('title','title_sort','authors','author_sort','contributors',
               'series','series_index','language','publisher',
               'date_published','date_original','identifiers','description',
               'tags',
              )


##############################################################################

def ebook_metadata (filename):
    filetype = identify_file(filename)
    if not is_ebook(filetype):
        return None

    processor = find_ebook_processor (filetype)
    if processor is None:
        return None

    parser = find_parser(filetype)
    if parser is None:
        return None

    return processor().to_ebook(parser().read_metadata(filename))

##############################################################################

__builtin_processors = {}
__extra_processors   = {}

class ProcessorException (Exception):
    pass

def find_ebook_processor (filetype):
    global __builtin_processors, __extra_processors

    if filetype is None: return None
    processor = __extra_processors.get(filetype)
    if processor is None:
        processor = __builtin_processors.get(filetype)
    return processor

def add_processor (processor, filetype, builtin=False):
    global __builtin_processors, __extra_processors

    if builtin:
        processors = __builtin_processors
    else:
        processors = __extra_processors

    processors[filetype] = processor

##############################################################################
## THE END
