#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
from typing import Optional, TypedDict


# Define TypedDicts for better type hinting
class RomData(TypedDict):
    """
    Represents the extracted data for a single ROM entry within a MAME game.

    Attributes:
        name (str): The name of the ROM file (e.g., "pacman.rom").
        size (int): The size of the ROM file in bytes.
        crc (Optional[str]): The CRC32 checksum of the ROM, if available.
        sha1 (Optional[str]): The SHA-1 hash of the ROM, if available.
        merge (Optional[str]): Indicates if this ROM is merged from another set.
        status (Optional[str]): The status of the ROM (e.g., "baddump", "nodump"), if specified.
    """
    name: str
    size: int
    crc: Optional[str]
    sha1: Optional[str]
    merge: Optional[str]
    status: Optional[str]


class GameData(TypedDict):
    """
    Represents the extracted data for a single game entry from a MAME DAT file.

    Attributes:
        description (str): A human-readable description of the game.
        year (Optional[str]): The year the game was released, if available.
        manufacturer (Optional[str]): The manufacturer of the game, if available.
        sourcefile (Optional[str]): The source file in the MAME project where the game's driver is defined.
        cloneof (Optional[str]): The name of the parent ROM set if this is a clone.
        romof (Optional[str]): The name of the parent ROM set if this is part of a larger family.
        roms (List[RomData]): A list of RomData objects, detailing each ROM associated with the game.
        samples (List[str]): A list of sample names used by the game, if any.
    """
    description: str
    year: Optional[str]
    manufacturer: Optional[str]
    sourcefile: Optional[str]
    cloneof: Optional[str]
    romof: Optional[str]
    roms: list[RomData]
    samples: list[str]


GamesDictionary = dict[str, GameData]
"""
A dictionary where keys are game ROM names (e.g., 'colt', 'pacman')
and values are GameData objects containing detailed information for each game.
"""


def parse_dat_file(dat_path: str) -> GamesDictionary:  # pylint: disable=[R0914,R0912]
    """
    Parses a Logiqx MAME DAT XML file and extracts game and ROM data.
    It expects a <datafile> as the root, with <header> and <game> or <machine> as its children.
    This function does not print anything to the console; it only returns the dictionary.

    Args:
        dat_path (str): The path of the .dat file.

    Returns:
        GamesDictionary: Dict with .dat data.
    """
    games_data: GamesDictionary = {}

    try:
        tree = ET.parse(dat_path)
        root = tree.getroot()

        # Check if the root tag is 'datafile'. If not, return an empty dictionary.
        # One could raise a custom Exception here or handle the error externally.
        if root.tag != 'datafile':
            return {}

        # Header information parsing is no longer printed, but the 'header_elem' can still be accessed
        # if you wanted to retrieve header data for other purposes.
        # header_elem = root.find('header')

        # First, try to find 'game' elements
        game_elements = root.findall('game')
        if not game_elements:
            # If no 'game' elements are found, try 'machine' elements (an older convention)
            game_elements = root.findall('machine')

        # If neither 'game' nor 'machine' elements are found, return an empty dictionary.
        if not game_elements:
            return {}

        # Iterate through each 'game' (or 'machine') element found
        for game_elem in game_elements:
            # Get the game's main name attribute
            game_name_attr = game_elem.get('name')
            if game_name_attr is None:
                continue  # Skip elements without a name attribute

            game_name: str = game_name_attr
            # Get the game's description, defaulting to the game name if not present
            description_elem = game_elem.find('description')
            if description_elem is not None and description_elem.text is not None:
                game_description = description_elem.text
            else:
                game_description = game_name

            # Extract additional game attributes, using Optional[str] for potentially missing fields
            year_elem = game_elem.find('year')
            year: Optional[str] = year_elem.text if year_elem is not None else None
            manufacturer_elem = game_elem.find('manufacturer')
            manufacturer: Optional[str] = manufacturer_elem.text if manufacturer_elem is not None else None
            sourcefile: Optional[str] = game_elem.get('sourcefile')
            cloneof: Optional[str] = game_elem.get('cloneof')
            romof: Optional[str] = game_elem.get('romof')

            # Initialize a list to hold ROM data for this game
            roms: list[RomData] = []
            for rom_elem in game_elem.findall('rom'):
                rom_name_attr = rom_elem.get('name')
                if rom_name_attr is None:
                    continue  # Skip ROMs without a name

                # Get ROM size, defaulting to '0' if attribute is missing, then convert to int
                rom_size_str = rom_elem.get('size', '0')

                roms.append(RomData(
                    name=rom_name_attr,
                    size=int(rom_size_str),
                    crc=rom_elem.get('crc'),       # CRC can be None
                    sha1=rom_elem.get('sha1'),     # SHA1 can be None
                    merge=rom_elem.get('merge'),   # Merge can be None
                    status=rom_elem.get('status')  # Status can be None
                ))

            # Initialize a list to hold sample names
            samples: list[str] = []
            for sample_elem in game_elem.findall('sample'):
                sample_name = sample_elem.get('name')
                if sample_name:  # Ensure the sample name exists
                    samples.append(sample_name)

            # Store all extracted data for the current game
            games_data[game_name] = GameData(
                description=game_description,
                year=year,
                manufacturer=manufacturer,
                sourcefile=sourcefile,
                cloneof=cloneof,
                romof=romof,
                roms=roms,
                samples=samples
            )

    except FileNotFoundError:
        return {}  # Return an empty dictionary if the file is not found
    except ET.ParseError:
        # Return an empty dictionary if there's an XML parsing error.
        # You might log the error 'e' here if debugging is needed.
        return {}

    return games_data
