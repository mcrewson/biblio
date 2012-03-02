# vim:set ts=4 sw=4 sts=4 et nowrap syntax=python ff=unix:
#

from __future__ import with_statement

import re
from functools import partial

from datetime import datetime
from dateutil.parser import parse
from dateutil.tz import tzlocal, tzutc

##############################################################################

class SafeLocalTimeZone(tzlocal):
    '''
    Assume DST was not in effect for historical dates, if DST
    data for the local timezone is not present in the operating system.
    '''

    def _isdst(self, dt):
        try:
            return tzlocal._isdst(self, dt)
        except ValueError:
            pass
        return False

def compute_locale_info_for_parse_date():
    try:
        dt = datetime.strptime('1/5/2000', "%x")
    except:
        try:
            dt = datetime.strptime('1/5/01', '%x')
        except:
            return False
    if dt.month == 5:
        return True
    return False

parse_date_day_first = compute_locale_info_for_parse_date()
utc_tz = _utc_tz = tzutc()
local_tz = _local_tz = SafeLocalTimeZone()

UNDEFINED_DATE = datetime(101,1,1, tzinfo=utc_tz)
DEFAULT_DATE = datetime(2000,1,1, tzinfo=utc_tz)

def parse_date(date_string, assume_utc=False, as_utc=True, default=None):
    '''
    Parse a date/time string into a timezone aware datetime object. The timezone
    is always either UTC or the local timezone.

    :param assume_utc: If True and date_string does not specify a timezone,
    assume UTC, otherwise assume local timezone.

    :param as_utc: If True, return a UTC datetime

    :param default: Missing fields are filled in from default. If None, the
    current date is used.
    '''
    if not date_string:
        return UNDEFINED_DATE
    if default is None:
        func = datetime.utcnow if assume_utc else datetime.now
        default = func().replace(hour=0, minute=0, second=0, microsecond=0,
                                 tzinfo=_utc_tz if assume_utc else _local_tz)
    dt = parse(date_string, default=default, dayfirst=parse_date_day_first)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_utc_tz if assume_utc else _local_tz)
    return dt.astimezone(_utc_tz if as_utc else _local_tz)

parse_utc_date = partial(parse_date, assume_utc=True, as_utc=True)
parse_local_date = partial(parse_date, assume_utc=False, as_utc=False)

##############################################################################
## THE END
