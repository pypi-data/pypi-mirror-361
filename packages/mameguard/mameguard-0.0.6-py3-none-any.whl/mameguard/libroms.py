#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import binascii  # CRC32
import hashlib
import os
import zipfile
from typing import TypedDict


class ScannedRomEntry(TypedDict):
    """
    Represents the data extracted for a single ROM file found within a scanned ZIP archive.
    This structure is used by the folder scanning function to detail the actual ROMs on disk.

    Attributes:
        name (str): The filename of the ROM inside the ZIP (e.g., "pacman.rom").
        size (int): The size of the ROM file in bytes.
        crc (str): The calculated CRC32 checksum of the ROM content (hexadecimal string).
        sha1 (str): The calculated SHA-1 hash of the ROM content (hexadecimal string).
    """
    name: str
    size: int
    crc: str
    sha1: str


ScannedRomsDictionary = dict[str, list[ScannedRomEntry]]
"""
A dictionary mapping MAME game names (derived from ZIP filenames) to a list
of ScannedRomEntry objects found within that ZIP file.

This dictionary represents the actual ROMs present on disk after scanning
a ROMs folder.
"""


def calculate_hashes(file_content: bytes) -> dict[str, str]:
    """
    Calculates MD5, SHA1, and CRC32 hashes for given binary content.

    Args:
        file_content (bytes): The binary content of a file (e.g., a ROM).

    Returns:
        Dict[str, str]: A dictionary containing the calculated hashes with keys
                        'md5', 'sha1', and 'crc'. Hash values are hexadecimal strings.
    """
    md5_hash = hashlib.md5(file_content).hexdigest()
    sha1_hash = hashlib.sha1(file_content).hexdigest()
    crc32_hash = f"{binascii.crc32(file_content) & 0xFFFFFFFF:08x}"  # CRC32

    return {
        'md5': md5_hash,
        'sha1': sha1_hash,
        'crc': crc32_hash
    }


def scan_rom_folder(rom_folder_path: str) -> ScannedRomsDictionary:
    """
    Scans a specified folder for MAME ROM ZIP files, extracts information
    about the ROMs contained within each ZIP, and calculates their hashes.

    This function recursively walks through the provided folder path.

    Args:
        rom_folder_path (str): The absolute or relative path to the directory
                                containing MAME ROM ZIP files.

    Returns:
        ScannedRomsDictionary: A dictionary where keys are the names of the
                               ZIP files (without extension, e.g., 'pacman')
                               and values are lists of ScannedRomEntry objects,
                               each detailing a ROM file found inside that ZIP.
                               Returns an empty dictionary if no ZIP files are found
                               or if errors occur during processing.
    """
    found_roms: ScannedRomsDictionary = {}  # key: zip_name (e.g., 'colt'), value: list of rom files inside

    for root, _, files in os.walk(rom_folder_path):
        for file_name in files:
            if file_name.endswith('.zip'):
                zip_path = os.path.join(root, file_name)
                zip_name = os.path.splitext(file_name)[0]
                found_roms[zip_name] = []
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zf:
                        for entry in zf.infolist():
                            with zf.open(entry.filename) as f:
                                file_content = f.read()
                                hashes = calculate_hashes(file_content)
                                found_roms[zip_name].append({
                                    'name': entry.filename,
                                    'size': entry.file_size,
                                    'crc': hashes['crc'],
                                    'sha1': hashes['sha1']
                                    # You can add MD5, SHA256 here if needed
                                })
                except zipfile.BadZipFile:
                    print(f"Warning: Bad zip file found: {zip_path}")
                except Exception as e:  # pylint: disable=[W0718]
                    print(f"Error processing {zip_path}: {e}")
            elif file_name.endswith('.chd'):
                pass

    return found_roms
