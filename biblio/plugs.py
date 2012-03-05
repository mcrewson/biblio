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

from collections import OrderedDict

__all__ = [ 'IDENTIFIERS','PARSERS','SUBSYSTEMS',
            'add_pluggable','find_pluggable','iterate_pluggables' ]

##############################################################################

# Pluggable subsystems

IDENTIFIERS = 'identifiers'
PARSERS     = 'parsers'

SUBSYSTEMS = frozenset((IDENTIFIERS, PARSERS))

class PlugException (Exception):
    pass

##############################################################################

__extra_pluggables   = {}
__builtin_pluggables = {}

def add_pluggable (plugtype, pluggable, subsystem=None, override=True, builtin=False):
    global __extra_pluggables, __builtin_pluggables, SUBSYSTEMS

    if subsystem not in SUBSYSTEMS:
        raise PlugException('Unknown subsystem: %s' % subsystem)

    if builtin:
        pluggables = __builtin_pluggables
    else:
        pluggables = __extra_pluggables

    if plugtype in pluggables.setdefault(subsystem, OrderedDict()):
        if override:
            pluggables[subsystem][plugtype] = pluggable
        else:
            if type(pluggables[subsystem][plugtype]) is not list:
                pluggables[subsystem][plugtype] = [ pluggables[subsystem][plugtype], ]
            pluggables[subsystem][plugtype].append(pluggable)
    else:
        pluggables[subsystem][plugtype] = pluggable

def find_pluggable (subsystem, plugtype):
    global __extra_pluggables, __builtin_pluggables, SUBSYSTEMS

    if subsystem not in SUBSYSTEMS:
        raise PlugException('Unknown subsystem: %s' % subsystem)

    if plugtype is None: return None

    pluggable = None
    if subsystem in __extra_pluggables:
        pluggable = __extra_pluggables[subsystem].get(plugtype)
    if pluggable is None and subsystem in __builtin_pluggables:
        pluggable = __builtin_pluggables[subsystem].get(plugtype)
    return pluggable

def iterate_pluggables (subsystem):
    global __extra_pluggables, __builtin_pluggables, SUBSYSTEMS

    if subsystem not in SUBSYSTEMS:
        raise PlugException("Unknown subsystem: %s" % subsystem)

    if subsystem in __extra_pluggables:
        for plugtype,pluggable in __extra_pluggables[subsystem].iteritems():
            if type(pluggable) is list:
                for p in pluggable:
                    yield plugtype,p
            else:
                yield plugtype,pluggable
    if subsystem in __builtin_pluggables:
        for plugtype,pluggable in __builtin_pluggables[subsystem].iteritems():
            if type(pluggable) is list:
                for p in pluggable:
                    yield plugtype,p
            else:
                yield plugtype,pluggable

##############################################################################

def initialize_builtin_pluggables ():
    global SUBSYSTEMS

    import functools, imp
    import biblio

    for subsys in SUBSYSTEMS:
        try:
            fp, path, desc = imp.find_module(subsys, biblio.__path__)
        except ImportError:
            continue
        try:
            try:
                module = imp.load_module('%s.%s' % (biblio.__name__, subsys), fp, path, desc)
            except ImportError:
                import traceback
                traceback.print_exc()
                continue
        finally:
            if fp: fp.close()

        initializer = getattr(module, 'initialize_builtin_pluggables', None)
        if initializer is None or not callable(initializer):
            continue

        adder = functools.partial(add_pluggable, subsystem=subsys, builtin=True)
        initializer(adder)

try:
    __builtin_pluggables_initialized
except NameError:
    __builtin_pluggables_initialized = False
if __builtin_pluggables_initialized == False:
    initialize_builtin_pluggables()
    __builtin_pluggables_initialized = True

##############################################################################
## THE END
