#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
"""

get_image_size.py
====================

    :Name:        get_image_size
    :Purpose:     extract image dimensions given a file path

    :Author:      Paulo Scardine (based on code from Emmanuel VAÏSSE)

    :Created:     26/09/2013
    :Copyright:   (c) Paulo Scardine 2013
    :Licence:     MIT

"""
import collections
import json
import os
import struct

FILE_UNKNOWN = "Sorry, don't know how to get size for this file."


class UnknownImageFormat(Exception):
    pass


types = collections.OrderedDict()
BMP = types['BMP'] = 'BMP'
GIF = types['GIF'] = 'GIF'
ICO = types['ICO'] = 'ICO'
JPEG = types['JPEG'] = 'JPEG'
PNG = types['PNG'] = 'PNG'
TIFF = types['TIFF'] = 'TIFF'

image_fields = ['path', 'type', 'file_size', 'width', 'height']


class Image(collections.namedtuple('Image', image_fields)):

    def to_str_row(self):
        return ("%d\t%d\t%d\t%s\t%s" % (
            self.width,
            self.height,
            self.file_size,
            self.type,
            self.path.replace('\t', '\\t'),
        ))

    def to_str_row_verbose(self):
        return ("%d\t%d\t%d\t%s\t%s\t##%s" % (
            self.width,
            self.height,
            self.file_size,
            self.type,
            self.path.replace('\t', '\\t'),
            self))

    def to_str_json(self, indent=None):
        return json.dumps(self._asdict(), indent=indent)


def get_image_size(file_path):
    """
    Return (width, height) for a given img file content - no external
    dependencies except the os and struct builtin modules
    """
    img = get_image_metadata(file_path)
    return img.width, img.height


def get_image_metadata(file_path):
    """
    Return an `Image` object for a given img file content - no external
    dependencies except the os and struct builtin modules

    Args:
        file_path (str): path to an image file

    Returns:
        Image: (path, type, file_size, width, height)
    """
    size = os.path.getsize(file_path)

    # be explicit with open arguments - we need binary mode
    with open(file_path, "rb") as inpt:
        height = -1
        width = -1
        data = inpt.read(26)
        msg = " raised while trying to decode as JPEG."

        if (size >= 10) and data[:6] in ('GIF87a', 'GIF89a'):
            # GIFs
            imgtype = GIF
            w, h = struct.unpack("<HH", data[6:10])
            width = int(w)
            height = int(h)
        elif (size >= 24) and data.startswith('\211PNG\r\n\032\n') and (data[12:16] == 'IHDR'):
            # PNGs
            imgtype = PNG
            w, h = struct.unpack(">LL", data[16:24])
            width = int(w)
            height = int(h)
        elif (size >= 16) and data.startswith('\211PNG\r\n\032\n'):
            # older PNGs
            imgtype = PNG
            w, h = struct.unpack(">LL", data[8:16])
            width = int(w)
            height = int(h)
        elif (size >= 2) and data.startswith('\377\330'):
            # JPEG
            imgtype = JPEG
            inpt.seek(0)
            inpt.read(2)
            b = inpt.read(1)
            try:
                while b and ord(b) != 0xDA:
                    while ord(b) != 0xFF:
                        b = inpt.read(1)
                    while ord(b) == 0xFF:
                        b = inpt.read(1)
                    if 0xC0 <= ord(b) <= 0xC3:
                        inpt.read(3)
                        h, w = struct.unpack(">HH", inpt.read(4))
                        break
                    else:
                        inpt.read(int(struct.unpack(">H", inpt.read(2))[0]) - 2)
                    b = inpt.read(1)
                width = int(w)
                height = int(h)
            except struct.error:
                raise UnknownImageFormat("StructError" + msg)
            except ValueError:
                raise UnknownImageFormat("ValueError" + msg)
            except Exception as e:
                raise UnknownImageFormat(e.__class__.__name__ + msg)
        elif (size >= 26) and data.startswith('BM'):
            # BMP
            imgtype = BMP
            headersize = struct.unpack("<I", data[14:18])[0]
            if headersize == 12:
                w, h = struct.unpack("<HH", data[18:22])
                width = int(w)
                height = int(h)
            elif headersize >= 40:
                w, h = struct.unpack("<ii", data[18:26])
                width = int(w)
                # as h is negative when stored upside down
                height = abs(int(h))
            else:
                raise UnknownImageFormat(
                    "Unkown DIB header size:" +
                    str(headersize))
        elif (size >= 8) and data[:4] in ("II\052\000", "MM\000\052"):
            # Standard TIFF, big- or little-endian
            # BigTIFF and other different but TIFF-like formats are not
            # supported currently
            imgtype = TIFF
            byteorder = data[:2]
            bochar = ">" if byteorder == "MM" else "<"
            # maps TIFF type id to size (in bytes)
            # and python format char for struct
            tifftypes = {
                1: (1, bochar + "B"),  # BYTE
                2: (1, bochar + "c"),  # ASCII
                3: (2, bochar + "H"),  # SHORT
                4: (4, bochar + "L"),  # LONG
                5: (8, bochar + "LL"),  # RATIONAL
                6: (1, bochar + "b"),  # SBYTE
                7: (1, bochar + "c"),  # UNDEFINED
                8: (2, bochar + "h"),  # SSHORT
                9: (4, bochar + "l"),  # SLONG
                10: (8, bochar + "ll"),  # SRATIONAL
                11: (4, bochar + "f"),  # FLOAT
                12: (8, bochar + "d")   # DOUBLE
            }
            ifdoffset = struct.unpack(bochar + "L", data[4:8])[0]
            try:
                countsize = 2
                inpt.seek(ifdoffset)
                ec = inpt.read(countsize)
                ifdentrycount = struct.unpack(bochar + "H", ec)[0]
                # 2 bytes: TagId + 2 bytes: type + 4 bytes: count of values + 4
                # bytes: value offset
                ifdentrysize = 12
                for i in range(ifdentrycount):
                    entryoffset = ifdoffset + countsize + i * ifdentrysize
                    inpt.seek(entryoffset)
                    tag = inpt.read(2)
                    tag = struct.unpack(bochar + "H", tag)[0]
                    if tag == 256 or tag == 257:
                        # if type indicates that value fits into 4 bytes, value
                        # offset is not an offset but value itself
                        ttype = inpt.read(2)
                        ttype = struct.unpack(bochar + "H", ttype)[0]
                        if ttype not in tifftypes:
                            raise UnknownImageFormat(
                                "Unkown TIFF field type:" +
                                str(ttype))
                        typesize = tifftypes[ttype][0]
                        typechar = tifftypes[ttype][1]
                        inpt.seek(entryoffset + 8)
                        value = inpt.read(typesize)
                        value = int(struct.unpack(typechar, value)[0])
                        if tag == 256:
                            width = value
                        else:
                            height = value
                    if width > -1 and height > -1:
                        break
            except Exception as e:
                raise UnknownImageFormat(str(e))
        elif size >= 2:
                # see http://en.wikipedia.org/wiki/ICO_(file_format)
            imgtype = 'ICO'
            inpt.seek(0)
            reserved = inpt.read(2)
            if 0 != struct.unpack("<H", reserved)[0]:
                raise UnknownImageFormat(FILE_UNKNOWN)
            fmt = inpt.read(2)
            assert 1 == struct.unpack("<H", fmt)[0]
            num = inpt.read(2)
            num = struct.unpack("<H", num)[0]
            if num > 1:
                import warnings
                warnings.warn("ICO File contains more than one image")
            # http://msdn.microsoft.com/en-us/library/ms997538.aspx
            w = inpt.read(1)
            h = inpt.read(1)
            width = ord(w)
            height = ord(h)
        else:
            raise UnknownImageFormat(FILE_UNKNOWN)

    return Image(path=file_path,
                 type=imgtype,
                 file_size=size,
                 width=width,
                 height=height)


