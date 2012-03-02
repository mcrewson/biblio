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
## THE END
