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

class Storage (dict):
    """
    A storage object is like a dictionary except "obj.foo" can be used in
    addition to "obj['foo']"
    """
    
    def __getattr__ (self, key):
        try:
            return self[key]
        except KeyError, k:
            raise AttributeError(k)

    def __setattr__ (self, key, value):
        self[key] = value

    def __delattr__ (self, key):
        try:
            del self[key]
        except KeyError, k:
            raise AttributeError(k)

    def __repr__ (self):
        return '<Storage ' + dict.__repr__(self) + '>'

##############################################################################

class Metadata (Storage):

    def __init__ (self, filetype):
        super(Metadata, self).__init__()
        self['filetype'] = filetype

##############################################################################

class RestrictedMetadata (Metadata):

    _fields = ()

    def _check_field (self, field):
        if field != 'filetype' and field not in self._fields:
            raise AttributeError("'%s' is not a valid attribute for %s" % (field, self.__class__.__name__))

    def __getattr__ (self, key):
        self._check_field(key)
        try:
            return super(RestrictedMetadata, self).__getattr__(key)
        except AttributeError:
            return None

    def __setattr__ (self, key, value):
        self._check_field(key)
        return super(RestrictedMetadata, self).__setattr__(key, value)

    def __delattr__ (self, key):
        self._check_field(key)
        return super(RestrictedMetadata, self).__delattr__(key)

##############################################################################

class EbookMetadata (RestrictedMetadata):

    _fields = ('title','title_sort','authors','author_sort','contributors',
               'series','series_index','languages','publisher','rights',
               'date_published','date_original','identifiers','description',
               'tags',
              )

##############################################################################
## THE END
