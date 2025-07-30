# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.6] - 2025-07-12
### Added
- **Missing version.py in Release:** Corrected an oversight where the version.py file was not included in the previous release build. This file, crucial for proper version management, is now correctly added and will be part of all future releases.

## [0.0.5] - 2025-07-12

### Fixed
- **Bug Fix:** Corrected image path in README.md to use the GitHub raw content URL, ensuring the `mameguard` logo is now correctly displayed on PyPI.

## [0.0.4] - 2025-07-12

### Fixed
- **Bug Fix:** Corrected image path in README.md to use absolute URL, ensuring logo visibility on PyPI.

## [0.0.3] - 2025-07-12

### Added
- **Visual Update:** The `mameguard` logo has been added to the README.md, enhancing the project's visual identity and recognition.

## [0.0.2] - 2025-07-12

### Added
- **New Feature:** Implemented `--version` command-line argument, allowing users to easily check the current application version.

## [0.0.1] - 2025-07-11

### Added
- Initial release of mameguard, a MAME ROM auditing CLI tool.
- Core functionality to parse MAME DAT (XML) files.
- Ability to scan specified ROM folders and calculate CRC32 and SHA1 hashes for ROMs within ZIP archives.
- Implementation of the `audit` command to compare DAT file data with scanned ROMs, providing detailed reports on game set status (Complete, Partial, Missing).
- Support for filtering audit reports by status (`--show-status` option).
- Option to output audit reports in human-readable text or machine-readable JSON format (`--output-format` option).
- Functionality to save reports to a specified file (`--output-file` option).
- Implementation of the `scan` command for standalone ROM folder scanning.
- Verbose output mode (`-v/--verbose`) for progress messages.
- Basic project structure, including `libdat.py`, `libroms.py`, `libaudit.py`, and `cli.py` modules.