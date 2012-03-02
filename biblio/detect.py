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

##############################################################################

import os

from biblio.formats.plug import all_formats_iterator, all_formats_of_type_iterator

##############################################################################

def find_format (filename, hint=None, skip_content_check=False, skip_extension_check=False):
    if hint is None:
        iterator = all_formats_iterator()
    else:
        iterator = all_formats_of_type_iterator(hint)
        if iterator is None:
            iterator = all_formats_iterator()

    # Detect the format based on file content
    if not skip_content_check:
        for form in iterator():
            if form.can_detect() and form.can_read(filename):
                return form

    # Detect the format based on filename extension
    if not skip_extension_check:
        extension = os.path.splitext(filename)[1]
        if extension.startswith('.'):
            extension = extension[1:]
        for form in iterator():
            if extension in form.extensions():
                return form

    return None

def detect_type (filename, hint=None, skip_content_check=False, skip_extension_check=False):
    form = find_format(filename, hint, skip_content_check, skip_extension_check)
    if form is not None:
        return form.MAJOR_TYPE, form.MINOR_TYPE
    return None, None

##############################################################################
## THE END
