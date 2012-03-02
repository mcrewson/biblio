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

##############################################################################

filetype = namedtuple('filetype', 'type mimetype description')

##############################################################################

# AUDIO types

FLAC   = filetype('audio.flac'             , 'audio/x-flac', 'FLAC audio')
ID3V22 = filetype('audio.id3v220'          , 'audio/mpeg'  , 'Audio file with ID3 version 2.2 tags')
ID3V23 = filetype('audio.id3v230'          , 'audio/mpeg'  , 'Audio file with ID3 version 2.3 tags')
ID3V24 = filetype('audio.id3v240'          , 'audio/mpeg'  , 'Audio file with ID3 version 2.4 tags')
M4A    = filetype('audio.mp4.itunes-aac-lc', 'audio/mp4'   , 'MPEG v4 audio, iTunes AAC-LC')
MP3_1  = filetype('audio.mp3.1'            , 'audio/mpeg'  , 'MPEG v1 audio, layer 3')
MP3_2  = filetype('audio.mp3.2'            , 'audio/mpeg'  , 'MPEG v2 audio, layer 3')
MP3_25 = filetype('audio.mp3.2.5'          , 'audio/mpeg'  , 'MPEG v2.5 audio, layer 3')

def is_audio (ftype):
    return ftype.type.startswith('audio.')

##############################################################################

# IMAGE types

GIF87A    = filetype('image.gif.87a'  , 'image/gif'    , 'GIF image, version 87a')
GIF89A    = filetype('image.gif.89a'  , 'image/gif'    , 'GIF image, version 89a')
JPEG_JFIF = filetype('image.jpeg.jfif', 'image/jpeg'   , 'JPEG image, JFIF standard')
JPEG_EXIF = filetype('image.jpeg.exif', 'image/jpeg'   , 'JPEG image, EXIF standard')
PNG       = filetype('image.png'      , 'image/png'    , 'PNG image')
SVG       = filetype('image.sbg'      , 'image/svg+xml', 'SVG image')

def is_image (ftype):
    return ftype.type.startswith('image.')

##############################################################################

# DOCUMENT types

# OpenOffice.org 1.x
OPENOFFICE1_WRITER   = filetype('document.openoffice1.writer'  , 'application/vnd.sun.xml.writer'  , 'OpenOffice.org 1.x Writer document')
OPENOFFICE1_CALC     = filetype('document.openoffice1.calc'    , 'application/vnd.sun.xml.calc'    , 'OpenOffice.org 1.x Calc document')
OPENOFFICE1_DRAW     = filetype('document.openoffice1.draw'    , 'application/vnd.sun.xml.draw'    , 'OpenOffice.org 1.x Draw document')
OPENOFFICE1_IMPRESS  = filetype('document.openoffice1.impress' , 'application/vnd.sun.xml.impress' , 'OpenOffice.org 1.x Impress document')
OPENOFFICE1_MATH     = filetype('document.openoffice1.math'    , 'application/vnd.sun.xml.math'    , 'OpenOffice.org 1.x Math document')
OPENOFFICE1_DATABASE = filetype('document.openoffice1.database', 'application/vnd.sun.xml.database', 'OpenOffice.org 1.x Database document')

# Portable Document Format (PDF)
PDF = filetype('document.pdf', 'application/pdf', 'PDF document')

##############################################################################

# EBOOK types

EPUB2 = filetype('ebook.epub.2', 'application/epub+zip', 'Epub ebook, version 2')
EPUB3 = filetype('ebook.epub.3', 'application/epub+zip', 'Epub ebook, version 3')
LIT   = filetype('ebook.lit'   , 'application/x-ms-reader', 'Microsoft Reader eboook')

# Palm
MOBI          = filetype('ebook.palm.mobi'     , 'application/x-mobipocket-ebook', 'Mobipocket ebook')
PDB_EREADER   = filetype('ebook.palm.ereader'  , 'application/vnd.palm', 'eReader ebook')
PDB_GUTENPALM = filetype('ebook.palm.gutenpalm', 'applicatino/vnd.palm', 'Gutenpalm ebook')
PDB_PALMDOC   = filetype('ebook.palm.palmdoc'  , 'application/vnd.palm', 'PalmDOC ebook')
PDB_PLUCKER   = filetype('ebook.palm.plucker'  , 'application/vnd.palm', 'Plucker ebook')

def is_ebook (ftype):
    return ftype.type.startswith('ebook.')

##############################################################################

# VIDEO types

AVI  = filetype('video.msvideo'          , 'video/x-msvideo' , 'AVI video')
M4V1 = filetype('video.mp4.v1'           , 'video/mp4'       , 'MPEG v4 video, version 1')
M4V2 = filetype('video.mp4.v2'           , 'video/mp4'       , 'MPEG v4 video, version 2')
M4V  = filetype('video.mp4.itunes-avc-lc', 'video/mp4'       , 'MPEG v4 video, iTunes AVC-LC')
MKV  = filetype('video.matroska'         , 'video/x-matroska', 'Matroska video')
WEBM = filetype('video.webm'             , 'video-webm'      , 'WebM video')

def is_video (ftype):
    return ftype.type.startswith('video.')

##############################################################################

# ZIP types

ZIP09 = filetype('zip.09', 'application/zip', 'ZIP file, version 0.9')
ZIP10 = filetype('zip.10', 'application/zip', 'ZIP file, version 1.0')
ZIP11 = filetype('zip.11', 'application/zip', 'ZIP file, version 1.1')
ZIP20 = filetype('zip.20', 'application/zip', 'ZIP file, version 2.0')
ZIP30 = filetype('zip.30', 'application/zip', 'ZIP file, version 3.0')

# XML types

OPF2  = filetype('xml.opf.2', 'application/oebps-package+xml', 'Open packaging format xml, version 2')
XHTML = filetype('xml.xhtml', 'application/xhtml+xml'        , 'XHTML document')
HTML  = filetype('html'     , 'text/html'                    , 'HTML document')
XML   = filetype('xml'      , 'text/xml'                     , 'XML document')

##############################################################################
## THE END
