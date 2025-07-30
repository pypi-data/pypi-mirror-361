# Dupes

A tool to find duplicate files in a directory.

## Installation

    $ uv tool install listdupes


## Usage

```
usage: listdupes [-h] [-v] [-o] [-0] [-c] [--version] path

Find duplicate files in a file tree, ignoring empty files.

positional arguments:
  path              Where to look.

options:
  -h, --help        show this help message and exit
  -v, --verbose     print more file info
  -o, --dupes-only  print only names of duplicate files
  -0, --null        when -o is set, end lines with NUL instead of newline
  -c, --count       print only the number of duplicates
  --version         show program's version number and exit
```
