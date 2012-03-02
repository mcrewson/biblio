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

#  0 = character never appears in text
#  1 = character appears in plain ASCII text
#  2 = character appears in ISO-8859 text
#  3 = character appears in non-ISO extended ASCII

text_chars = ( 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0,  # 0x00 - 0x0f
               0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,  # 0x10 - 0x1f
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 0x20 - 0x2f
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 0x30 - 0x3f
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 0x40 - 0x4f
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 0x50 - 0x5f
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 0x60 - 0x6f
               1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0,  # 0x70 - 0x7f
               3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,  # 0x80 - 0x8f
               3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,  # 0x90 - 0x9f
               2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,  # 0xa0 - 0xaf
               2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,  # 0xb0 - 0xbf
               2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,  # 0xc0 - 0xcf
               2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,  # 0xd0 - 0xdf
               2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,  # 0xe0 - 0xef
               2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,  # 0xf0 - 0xff
             )

##############################################################################

def looks_like_ascii (buffer):
    for c in buffer:
        t = text_chars[ord(c)]
        if t != 1:
            return False
    return True

def looks_like_latin1 (buffer):
    for c in buffer:
        t = text_chars[ord(c)]
        if t not in (1,2):
            return False
    return True

def looks_like_extended (buffer):
    for c in buffer:
        t = text_chars[ord(c)]
        if t not in (1,2,3):
            return False
    return True

##############################################################################

def looks_like_utf8 (buffer):
    """
    Decide whether some text looks like UTF-8. Returns

      -1: invalid UTF-8
       0: uses odd control characters, so doesn't look like txt
       1: 7-bit text
       2: definitely UTF-8 text (valid high-bit set bytes)
    """
    n = len(buffer)
    i = 0
    found_utf8_char = 1
    while i < n:
        c = ord(buffer[i])
        if (c & 0x80) == 0:           # 0xxxxxxx is plain ASCII
            # reject ctrl character
            if text_chars[ord(buffer[i])] != 1:
                return 0
            i += 1
        elif (c & 0x40) == 0:         # 10xxxxxx never 1st byte
            return -1
        else:
            if (c & 0x20) == 0:       # 110xxxxx
                following = 1
            elif (c & 0x10) == 0:     # 1110xxxx
                following = 2
            elif (c & 0x08) == 0:     # 11110xxx
                following = 3
            elif (c & 0x04) == 0:     # 111110xx
                following = 4
            elif (c & 0x02) == 0:     # 1111110x
                following = 5
            else:
                return -1
            
            nn = 0
            while nn < following:
                i += 1
                if i >= n:
                    return found_utf8_char

                c = ord(buffer[i])
                if (c & 0x80) == 0 or (c & 0x40):
                    return -1
                nn += 1
            found_utf8_char = 2
            i += 1

    return found_utf8_char

##############################################################################

def is_text (buff):
    if looks_like_utf8(buff) > 0:
        return True
    return False

##############################################################################
## THE END
