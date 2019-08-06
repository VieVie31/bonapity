"""
This module contains useful function to infer mime-type.

@author: VieVie31
"""
from pathlib import Path
from collections import defaultdict

def extension_to_mime(extension: str) -> str:
    """
    Return mime-type associated to a given extension.
    If not found, return "application/octet-stream".

    :param extension: extension of the file formated as ".myextension"
    """
    mime_type = {
        '.manifest': 'text/cache-manifest',
        '.html': 'text/html',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.tif': 'image/tiff',
        '.bmp': 'image/bmp',
        '.ico': 'image/x-icon',
        '.svg':	'image/svg+xml',
        '.css':	'text/css',
        '.js':	'application/javascript',
        '.zip': 'application/zip',
        '.rar': 'application/x-rar-compressed',
        '.csv': 'text/csv',
        '.mp4': 'video/mp4',
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/x-wav',
        '.ogg': 'application/ogg',
        '.flac': 'audio/flac',
        '.pdf': 'application/pdf',
        '.': 'application/octet-stream',
        '': 'application/octet-stream'
    }
    if extension in mime_type:
        return mime_type[extension]
    else: 
        return 'application/octet-stream'


def byte_to_mime(byte_data: bytes) -> str:
    """
    Return mime-type associated to a given bytes array.
    If not found, return "application/octet-stream".

    :param extension: extension of the file formated as ".myextension"
    """
    #https://en.wikipedia.org/wiki/List_of_file_signatures
    # RAR
    # 52 61 72 21 1A 07 00
    # 52 61 72 21 1A 07 01 00
    f4bytes = byte_data[:4] # first 4 bytes
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
        b'\x00\x00\x01\xba': 'audio/mpeg'
    }
    if f4bytes in f4_mime_type:
        return f4_mime_type[f4bytes]
    # 42 4D #BMP
    # FF FB #MP3
    # 49 44 33 #MP3
    # 52 49 46 #AVI
    # 46 ?? ?? ?? ?? #AVI
    # 41 56 49 20 #AVI
    return "application/octet-stream"

