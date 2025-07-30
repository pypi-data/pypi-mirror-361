#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os

from mameguard.libaudit import AuditReport, audit_roms
from mameguard.libdat import GamesDictionary, parse_dat_file
from mameguard.libroms import scan_rom_folder
from mameguard.version import __version__


def format_text_report(audit_results: AuditReport, dat_data: GamesDictionary, show_status: str) -> str:  # pylint: disable=[R0912]
    """
    Formats the audit results into a human-readable text report.

    This function generates a multi-line string containing a summary of the
    audit and a detailed breakdown of game statuses, optionally filtered
    by the 'show_status' parameter.

    Args:
        audit_results (AuditReport): A dictionary containing the audit results
                                     for all scanned games.
        dat_data (GamesDictionary): A dictionary containing the parsed data
                                    from the MAME DAT file, used for game descriptions.
        show_status (str): A string indicating which game statuses to display
                           in the detailed report. Valid values are "all",
                           "complete", "partial", "missing", or "mismatched".

    Returns:
        str: A multi-line string representing the formatted audit report.
    """
    report_lines = []

    complete_count = sum(1 for r in audit_results.values() if r['status'] == 'Complete')
    partial_count = sum(1 for r in audit_results.values() if r['status'] == 'Partial')
    missing_count = sum(1 for r in audit_results.values() if r['status'] == 'Missing')

    report_lines.append("\n--- Audit Summary ---")
    report_lines.append(f"Total Games in DAT: {len(dat_data)}")
    report_lines.append(f"Complete Sets: {complete_count}")
    report_lines.append(f"Partial Sets: {partial_count}")
    report_lines.append(f"Missing Sets: {missing_count}")
    report_lines.append("-" * 25)

    # --- Detailed Game Status ---
    report_lines.append("\n--- Detailed Game Status ---")

    filtered_games = []
    if show_status == "all":
        # If 'all' is requested, simply add all games from audit_results
        filtered_games = list(audit_results.items())
    else:
        # Otherwise, apply specific filters
        for game_name, result in audit_results.items():
            if result['status'].lower() == show_status:
                filtered_games.append((game_name, result))
            elif show_status == "mismatched" and result['mismatched_roms']:
                # The 'mismatched' filter should include games that have mismatched ROMs,
                # regardless of their overall 'Complete', 'Partial', 'Missing' status.
                filtered_games.append((game_name, result))

    if not filtered_games:
        report_lines.append("No games found matching the selected status filter.")
    else:
        # Sort games alphabetically for consistent output
        filtered_games.sort(key=lambda x: x[0])

        for game_name, result in filtered_games:
            # Get the full description from dat_data, falling back to game_name if not found
            game_data_entry = dat_data.get(game_name)
            if game_data_entry is not None:
                game_description = game_data_entry.get('description', game_name)
            else:
                game_description = game_name

            report_lines.append(f"\nGame: {game_name} ({game_description})")
            report_lines.append(f"  Status: {result['status']}")

            if result['missing_roms']:
                report_lines.append(f"  Missing ROMs ({len(result['missing_roms'])}):")
                for rom in result['missing_roms']:
                    report_lines.append(f"    - {rom['name']} (Size: {rom['size']}, CRC: {rom['expected_crc']}, SHA1: {rom['expected_sha1']})")

            if result['mismatched_roms']:
                report_lines.append(f"  Mismatched ROMs ({len(result['mismatched_roms'])}):")
                for rom in result['mismatched_roms']:
                    report_lines.append(f"    - {rom['name']}")
                    report_lines.append(f"      Expected: Size={rom['size']}, CRC={rom['expected_crc']}, SHA1={rom['expected_sha1']}")
                    report_lines.append(f"      Found:    Size={rom['found_size']}, CRC={rom['found_crc']}, SHA1={rom['found_sha1']}")

            # Optionally, you could also list found_roms if desired, but for brevity,
            # we usually focus on problems (missing/mismatched).
            # if result['found_roms'] and show_status == "all":
            #     report_lines.append(f"  Correct ROMs found: {len(result['found_roms'])}")

    return "\n".join(report_lines)


def main() -> None:  # pylint: disable=[R0912,R0915]
    """
    Main function for the mameguard CLI tool.
    Handles command-line arguments and orchestrates DAT parsing, ROM scanning, and auditing.
    """
    parser = argparse.ArgumentParser(
        description="A CLI Tool for Auditing MAME ROM Collections.",
        formatter_class=argparse.RawTextHelpFormatter,  # For better formatting of help text
        epilog='For command-specific help: mameguard <command> --help'
    )

    parser.add_argument(
        "-V", "--version",
        action='version',
        version=f'%(prog)s {__version__}',
        help='Show program\'s version number and exit'
    )

    # Define subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Available commands"
    )

    # --- 'audit' command ---
    audit_parser = subparsers.add_parser(
        "audit",
        help="Perform a full audit of your ROMs against a DAT file."
    )
    audit_parser.add_argument(
        "dat_path",
        help="Path to the MAME DAT file (e.g., MAME 0.277.dat)."
    )
    audit_parser.add_argument(
        "roms_path",
        help="Path to your MAME ROMs folder (e.g., /home/user/mame_roms/)."
    )
    audit_parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format for the audit report (default: text).\n"
             "  'text': Human-readable summary in console.\n"
             "  'json': Detailed JSON output to console or --output-file."
    )
    audit_parser.add_argument(
        "--output-file",
        help="Path to save the report (e.g., audit_report.json, audit_report.txt).\n"
             "If not specified, output goes to console."
    )
    audit_parser.add_argument(
        "--show-status",
        choices=["all", "complete", "partial", "missing", "mismatched"],
        default="all",
        help="Filter games by audit status (default: all).\n"
             "  'all': Show all games.\n"
             "  'complete': Show only complete sets.\n"
             "  'partial': Show only partial sets.\n"
             "  'missing': Show only missing sets.\n"
             "  'mismatched': Show only sets with mismatched ROMs."
    )
    audit_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show verbose output during scanning and auditing."
    )

    # --- 'scan' command (optional, for just scanning ROMs) ---
    scan_parser = subparsers.add_parser(
        "scan",
        help="Scan a ROM folder and output found ROMs (useful for debugging)."
    )
    scan_parser.add_argument(
        "roms_path",
        help="Path to your MAME ROMs folder."
    )
    scan_parser.add_argument(
        "--output-json",
        help="Path to save the scanned ROMs as a JSON file."
    )
    scan_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show verbose output during scanning."
    )

    args = parser.parse_args()

    # --- Command Execution Logic ---
    if args.command == "audit":
        if not os.path.exists(args.dat_path):
            print(f"Error: DAT file not found at '{args.dat_path}'")
            return
        if not os.path.isdir(args.roms_path):
            print(f"Error: ROMs folder not found or is not a directory at '{args.roms_path}'")
            return

        if args.verbose:
            print(f"Parsing DAT file: '{args.dat_path}'...")
        dat_data = parse_dat_file(args.dat_path)
        if not dat_data:
            print(f"Error: Could not parse DAT file or it contains no games. Check '{args.dat_path}'.")
            return
        if args.verbose:
            print(f"DAT file parsed. Found {len(dat_data)} games.")

        if args.verbose:
            print(f"Scanning ROM folder: '{args.roms_path}'...")
        scanned_roms = scan_rom_folder(args.roms_path)
        if args.verbose:
            print(f"ROM folder scanned. Found {len(scanned_roms)} ZIP files.")

        if args.verbose:
            print("Auditing ROMs...")
        audit_results = audit_roms(dat_data, scanned_roms)
        if args.verbose:
            print("Audit complete.")

        # --- Output Generation ---
        if args.output_format == "json":
            output_content = json.dumps(audit_results, indent=2)
        else:  # text format
            output_content = format_text_report(audit_results, dat_data, args.show_status)

        if args.output_file:
            try:
                with open(args.output_file, 'w', encoding='utf-8') as f:
                    f.write(output_content)
                print(f"Audit report saved to '{args.output_file}' (format: {args.output_format}).")
            except IOError as e:
                print(f"Error: Could not write to output file '{args.output_file}': {e}")
        else:
            print(output_content)

    elif args.command == "scan":
        if not os.path.isdir(args.roms_path):
            print(f"Error: ROMs folder not found or is not a directory at '{args.roms_path}'")
            return

        if args.verbose:
            print(f"Scanning ROM folder: '{args.roms_path}'...")
        scanned_roms = scan_rom_folder(args.roms_path)
        if args.verbose:
            print(f"ROM folder scanned. Found {len(scanned_roms)} ZIP files.")

        if args.output_json:
            try:
                with open(args.output_json, 'w', encoding='utf-8') as f:
                    json.dump(scanned_roms, f, indent=2)
                print(f"Scanned ROMs saved to '{args.output_json}'.")
            except IOError as e:
                print(f"Error: Could not write to output JSON file '{args.output_json}': {e}")
        else:
            print(json.dumps(scanned_roms, indent=2))  # Default to printing JSON to console


if __name__ == "__main__":
    main()
