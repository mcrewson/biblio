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

from datetime import datetime
from dateutil.tz import tzlocal, tzutc
import re

from biblio.identifiers import identify_file
from biblio.identifiers.filetypes import is_ebook
from biblio.parsers  import read_processed_metadata

##############################################################################

def ebook_metadata (filename):
    filetype = identify_file(filename)
    if not is_ebook(filetype):
        return None

    return read_processed_metadata(filename, filetype=filetype)

##############################################################################

AUTHORS_PATTERN = re.compile(r'(?i),?\s+(and|with|&)\s+')

def parse_ebook_authors (authors_string):
    if not authors_string:
        return []
    authors_string = AUTHORS_PATTERN.sub(';', authors_string)
    authors = [ a.strip() for a in authors_string.split(';') ]
    return [ a for a in authors if a ]

##############################################################################

UNDEFINED_DATE = datetime(101,1,1, tzinfo=tzutc())

def parse_ebook_date (date_string, assume_utc=False, as_utc=True):
    from dateutil.parser import parse
    if not date_string:
        return UNDEFINED_DATE
    dt = parse(date_string)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tzutc() if assume_utc else tzlocal())
    return dt.astimezone(tzutc() if as_utc else tzlocal()).date()

##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################
## THE END
