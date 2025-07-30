#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import os
import logging

log = logging.getLogger(__name__)

import importlib.metadata

__version__ = importlib.metadata.version(__package__)


def cond_hash(file: Path) -> tuple[str, str] | None:
    if file.is_dir() or file.stat().st_size == 0:
        log.debug(f"Skipping {file.name}")
        return
    hasher = hashlib.sha256()
    with file.open("rb") as f:
        while data := f.read(65536):
            hasher.update(data)

    checksum = hasher.hexdigest()
    log.debug(f"{checksum} {file}")
    return str(file), checksum


class ListDupes:
    def __init__(self):
        self._hashes = {}
        self._scanned = 0
        self.log = logging.getLogger(__name__ + ".ListDupes")

    @property
    def scanned(self) -> int:
        return self._scanned

    @property
    def found(self) -> int:
        return self._scanned - len(self._hashes)

    def find_duplicates(self, path: Path):
        log.debug(f"Scanning {path.absolute()}...")
        with ThreadPoolExecutor() as executor:
            for result in executor.map(cond_hash, path.rglob("*")):
                if result is None:
                    continue
                name, checksum = result
                self._scanned += 1
                if checksum in self._hashes:
                    yield (name, self._hashes[checksum])
                else:
                    self._hashes[checksum] = name


def main():
    import sys
    import argparse

    # fmt: off
    parser = argparse.ArgumentParser(description="Find duplicate files in a file tree, ignoring empty files.")
    parser.add_argument("path", type=Path, help="Where to look.")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Set verbosity level (0-3)")
    parser.add_argument("-s", "--summary", action="store_true", help="Only show number of scanned and found files")
    parser.add_argument("-o", "--dupes-only", action="store_true", help="print only names of duplicate files")
    parser.add_argument("-0", "--null", action="store_true", help="when -o is set, end lines with NUL instead of newline",)
    parser.add_argument("-c", "--count", action="store_true", help="print only the number of duplicates")
    parser.add_argument("--version", action="version", version=f"{__package__} v{__version__}")
    args = parser.parse_args()
    # fmt: on

    verbosity = max(logging.WARNING - (args.verbose * 10), logging.DEBUG)
    logging.basicConfig(level=verbosity)

    if args.null and not args.dupes_only:
        parser.error("-0 only makes sense with -o")

    scanner = ListDupes()

    try:
        for duplicate, original in scanner.find_duplicates(args.path):
            if args.dupes_only:
                print(duplicate, end="\0" if args.null else None)
            elif not (args.count or args.summary):
                print(f"{duplicate} -> {original}")
        if args.summary:
            print(f"scanned {scanner._scanned} files")
        if args.count or args.summary:
            if args.summary:
                ending = "" if scanner.found == 1 else "s"
                print(f"{scanner.found} duplicate{ending} found")
            else:
                print(scanner.found)

    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == "__main__":
    main()
