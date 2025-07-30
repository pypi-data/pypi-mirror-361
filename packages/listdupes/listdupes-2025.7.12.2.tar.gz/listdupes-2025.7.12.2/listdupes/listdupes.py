#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import os

import importlib.metadata
__version__ = importlib.metadata.version(__package__ or __name__)

def cond_hash(file: Path) -> tuple[str, str] | None:
    if file.is_dir() or file.stat().st_size == 0:
        return
    hasher = hashlib.sha256()
    with file.open("rb") as f:
        while data := f.read(65536):
            hasher.update(data)
    return str(file), hasher.hexdigest()

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Find duplicate files in a file tree, ignoring empty files.")
    parser.add_argument("path", type=Path, help="Where to look.")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="print more file info")
    parser.add_argument("-o", "--dupes-only", action="store_true", help="print only names of duplicate files")
    parser.add_argument("-0", "--null", action="store_true", help="when -o is set, end lines with NUL instead of newline",)
    parser.add_argument("-c", "--count", action="store_true", help="print only the number of duplicates")
    parser.add_argument("--version", action="version", version=f"dupes v{__version__}")
    args = parser.parse_args()

    if args.null and not args.dupes_only:
        parser.error("-0 only makes sense with -o")

    hashes = {}
    scanned = 0
    if args.verbose >= 2:
        print(f"starting at {args.path.absolute()}...")
    with ThreadPoolExecutor() as executor:
        for result in executor.map(cond_hash, args.path.glob("**")):
            if result is None:
                continue
            name, checksum = result
            if args.verbose >= 2:
                print(checksum, name)
            scanned += 1
            if checksum in hashes:
                if args.dupes_only:
                    print(name, end="\0" if args.null else None)
                elif not args.count or args.verbose:
                    print(f"{name} -> {hashes[checksum]}")
            else:
                hashes[checksum] = name

    if args.verbose:
        print(f"scanned {scanned} files")
    if args.count or args.verbose:
        dupes = scanned - len(hashes)
        if args.verbose:
            ending = "" if dupes == 1 else "s"
            print(f"{dupes} duplicate{ending} found")
        else:
            print(dupes)


if __name__ == "__main__":
    main()
