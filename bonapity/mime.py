"""
This module contains useful function to infer mime-type.

@author: VieVie31
"""
from pathlib import Path
from collections import defaultdict


# Complete list : http://www.iana.org/assignments/media-types/media-types.xhtml
# TODO: parse this : https://www.freeformatter.com/mime-types-list.html
COMMON_MIME_TYPES = {
    '': 'application/octet-stream',
    '.': 'application/octet-stream',
    '.aac': 'audio/aac',
    '.abx': 'application/x-abiword',
    '.arc': 'application/octet-stream',
    '.avi': 'video/x-msvideo',
    '.azw': 'application/vnd.amazon.ebook',
    '.bin': 'application/octet-stream',
    '.bmp': 'image/bmp',
    '.bz': 'application/x-bzip',
    '.bz2': 'application/x-bzip2',
    '.csh': 'application/x-csh',
    '.css': 'text/css',
    '.csv': 'text/csv',
    '.doc': 'application/msword',
    '.doc': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.eot': 'application/vnd.ms-fontobject',
    '.epub': 'application/epub+zip',
    '.flac': 'audio/flac',
    '.gif': 'image/gif',
    '.htm': 'text/html',
    '.html': 'text/html',
    '.ico': 'image/x-icon',
    '.ics': 'text/calendar',
    '.jar': 'application/java-archive',
    '.jpeg': 'image/jpeg',
    '.jpg': 'image/jpeg',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.manifest': 'text/cache-manifest',
    '.mid': 'audio/midi',
    '.midi': 'audio/midi',
    '.mpeg': 'video/mpeg',
    '.mpgk': 'application/vnd.apple.installer+xml',
    '.mp3': 'audio/mpeg',
    '.mp4': 'video/mp4',
    '.odp': 'application/vnd.oasis.opendocument.presentation',
    '.ods': 'application/vnd.oasis.opendocument.spreadsheet',
    '.odt': 'application/vnd.oasis.opendocument.text',
    '.oga': 'audio/ogg',
    '.ogg': 'application/ogg',
    '.ogv': 'video/ogg',
    '.ogx': 'application/ogg',
    '.otf': 'font/otf',
    '.pdf': 'application/pdf',
    '.png': 'image/png',
    '.ppt': 'application/vnd.ms-powerpoint',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.rar': 'application/x-rar-compressed',
    '.rtf': 'application/rtf',
    '.sh': 'application/x-sh',
    '.svg': 'image/svg+xml',
    '.swf': 'application/x-shockwave-flash',
    '.tar': 'application/x-tar',
    '.tif': 'image/tiff',
    '.tiff': 'image/tiff',
    '.torrent': 'application/x-bittorrent',
    '.ts': 'application/typescript',
    '.ttf': 'font/ttf',
    '.vsd': 'application/vnd.visio',
    '.wav': 'audio/x-wav',
    '.weba': 'video/webm',
    '.webm': 'video/webm',
    '.webp': 'image/webp',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.xhtml': 'application/xhtml+xml',
    '.xls': 'application/vnd.ms-excel',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xml': 'application/xml',
    '.xul': 'application/vnd.mozilla.xul+xml',
    '.zip': 'application/zip',
    '.3gp': 'video/3gpp',  # Can also be audio/3gpp if no video file is present.
    '.3g2': 'video/3gpp2',  # Can also be audio/3gpp2 if no video file is present.
    '.7z': 'application/x-7z-compressed'
}


def extension_to_mime(extension: str) -> str:
    """
    Return mime-type associated to a given extension.
    If not found, return "application/octet-stream".

    :param extension: extension of the file formated as ".myextension"
    """
    global COMMON_MIME_TYPES

    if extension in COMMON_MIME_TYPES:
        return COMMON_MIME_TYPES[extension]
    else:
        return 'application/octet-stream'


def byte_to_mime(byte_data: bytes) -> str:
    """
    Return mime-type associated to a given bytes array.
    If not found, return "application/octet-stream".

    :param extension: extension of the file formated as ".myextension"
    """
    # https://en.wikipedia.org/wiki/List_of_file_signatures
    # RAR
    # 52 61 72 21 1A 07 00
    # 52 61 72 21 1A 07 01 00

    # Check in decreasing order of the magic number
    # byte length the potential application

    if byte_data[:11] == b'd8:announce':
        return 'application/x-bittorrent'

    f5_mime_type = {
        b'<html': 'text/html',
        b'<?xml': 'application/xml',
        b'%PDF-': 'application/pdf'
    }
    if byte_data[:5] in f5_mime_type:
        return f5_mime_type[byte_data[:5]]

    f4_mime_type = {
        b'\x89PNG': 'image/png',
        b'GIF8': 'image/gif',
        b'%PDF': 'application/pdf',
        b'\xff\xd8\xff\xdb': 'image/jpeg',
        b'\xff\xd8\xff\xe0': 'image/jpeg',
        b'\xff\xd8\xff\xee': 'image/jpeg',
        b'\xff\xd8\xff\xe1': 'image/jpeg',
        b'II*.': 'image/tiff',
        b'MM.*': 'image/tiff',
        b'PK\x03\x04': 'application/zip',
        b'PK\x05\x06': 'application/zip',
        b'\xca\xfe\xba\xbe': 'application/java-byte-code',
        b'OggS': 'application/ogg',
        b'fLaC': 'audio/flac',
        b'MThd': 'audio/rtp-midi',
        b'\x1aE\xdf\xa3': 'video/x-matroska',
        b'\x00asm': 'application/wasm',
        b'\x00\x00\x01\xb3': 'audio/mpeg',
        b'\x00\x00\x01\xba': 'audio/mpeg',
        b'AVI ': 'video/x-msvideo'
    }
    if byte_data[:4] in f4_mime_type:
        return f4_mime_type[byte_data[:4]]

    f3_mime_type = {
        b'ID3': 'audio/mpeg',
        b'RIF': 'video/x-msvideo'
    }
    if byte_data[:3] in f3_mime_type:
        return f3_mime_type[byte_data[:3]]

    # 42 4D #BMP
    # FF FB #MP3
    # 46 ?? ?? ?? ?? #AVI

    # Unknown magic number case
    return "application/octet-stream"


if __name__ == '__main__':
    pass
