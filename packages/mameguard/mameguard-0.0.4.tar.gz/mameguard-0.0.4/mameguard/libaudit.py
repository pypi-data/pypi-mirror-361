#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional, TypedDict

# Import functions and TypedDicts from your custom libraries
from mameguard.libdat import GamesDictionary
from mameguard.libroms import ScannedRomsDictionary


class MissingRom(TypedDict):
    """Represents a ROM that is expected by the DAT but not found or matched."""
    name: str
    size: int
    expected_crc: Optional[str]
    expected_sha1: Optional[str]


class FoundRom(TypedDict):
    """Represents a ROM that is found and matched correctly."""
    name: str
    size: int
    crc: str
    sha1: str


class MismatchedRom(TypedDict):
    """Represents a ROM found, but its hashes/size do not match the DAT."""
    name: str
    size: int
    expected_crc: Optional[str]
    expected_sha1: Optional[str]
    found_size: int
    found_crc: str
    found_sha1: str


class AuditResult(TypedDict):
    """
    Detailed audit result for a single game.
    """
    status: str  # "Complete", "Partial", "Missing"
    missing_roms: list[MissingRom]
    found_roms: list[FoundRom]  # Correctly matched ROMs
    mismatched_roms: list[MismatchedRom]


AuditReport = dict[str, AuditResult]


def audit_roms(dat_data: GamesDictionary, scanned_roms: ScannedRomsDictionary) -> AuditReport:  # pylint: disable=[R0914]
    """
    Compares the DAT file data with the scanned ROMs to generate an audit report.

    Args:
        dat_data (libdat.GamesDictionary): Data parsed from the MAME DAT file.
        scanned_roms (libroms.ScannedRomsDictionary): Data from scanning the ROM folder.

    Returns:
        AuditReport: A dictionary detailing the audit results for each game.
    """
    audit_report: AuditReport = {}

    for game_name, dat_game_info in dat_data.items():
        expected_roms = dat_game_info['roms']
        actual_roms_in_zip = scanned_roms.get(game_name, [])  # Get ROMs for this game, or empty list if zip not found

        game_missing_roms: list[MissingRom] = []
        game_found_roms: list[FoundRom] = []
        game_mismatched_roms: list[MismatchedRom] = []

        # Convert actual_roms_in_zip into a dict for faster lookup by name and hash
        # Use a list of dicts to handle cases where multiple ROMs might have the same hash/size
        # but different names, though usually names are unique within a zip.
        actual_roms_map = {}
        for r_entry in actual_roms_in_zip:
            # Create a unique key for lookup. name is usually enough for MAME ROMs.
            actual_roms_map[r_entry['name']] = r_entry

        all_expected_roms_found = True
        num_matched_roms = 0

        for expected_rom in expected_roms:
            expected_rom_name = expected_rom['name']
            expected_size = expected_rom['size']
            expected_crc = expected_rom['crc']
            expected_sha1 = expected_rom['sha1']

            matched = False

            # Check if this expected ROM is in the actual_roms_map
            if expected_rom_name in actual_roms_map:
                found_rom = actual_roms_map[expected_rom_name]

                # Compare size, CRC, and SHA1
                if (found_rom['size'] == expected_size and found_rom['crc'] == expected_crc and found_rom['sha1'] == expected_sha1):
                    game_found_roms.append(FoundRom(
                        name=found_rom['name'],
                        size=found_rom['size'],
                        crc=found_rom['crc'],
                        sha1=found_rom['sha1']
                    ))
                    num_matched_roms += 1
                    matched = True
                else:
                    # Mismatch found
                    game_mismatched_roms.append(MismatchedRom(
                        name=expected_rom_name,
                        size=expected_size,
                        expected_crc=expected_crc,
                        expected_sha1=expected_sha1,
                        found_size=found_rom['size'],
                        found_crc=found_rom['crc'],
                        found_sha1=found_rom['sha1']
                    ))
                    all_expected_roms_found = False  # Even if present, it's a mismatch
                    matched = True  # It was found, just not correctly

            if not matched:
                game_missing_roms.append(MissingRom(
                    name=expected_rom_name,
                    size=expected_size,
                    expected_crc=expected_crc,
                    expected_sha1=expected_sha1
                ))
                all_expected_roms_found = False

        # Determine game status
        status = "Missing"
        if len(actual_roms_in_zip) > 0:  # If the ZIP exists
            if all_expected_roms_found and num_matched_roms == len(expected_roms):
                status = "Complete"
            elif num_matched_roms > 0:  # Some ROMs matched, but not all or some were mismatched
                status = "Partial"

        audit_report[game_name] = AuditResult(
            status=status,
            missing_roms=game_missing_roms,
            found_roms=game_found_roms,
            mismatched_roms=game_mismatched_roms
        )

    return audit_report
