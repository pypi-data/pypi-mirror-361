"""Provides function to replace content between two tags in a file."""

import argparse
import sys
from pathlib import Path


def replace(file_path: Path, tag_start: str, tag_end: str, replace_file_path: Path):
    """Replaces text between two tags with the content from replace_file_path"""
    with file_path.open("r") as f:
        file_text = f.readlines()

    with replace_file_path.open("r") as f:
        text = f.readlines()

    replace_lines = False

    with file_path.open("w") as f:
        for line in file_text:
            if not replace_lines:
                # search for tag_start
                f.write(line)
                if line.startswith(tag_start):
                    replace_lines = True
                    f.writelines(text)
            elif line.startswith(tag_end):
                f.write(line)
                replace_lines = False
            else:
                pass


if __name__ == "__main__":
    ap = argparse.ArgumentParser(allow_abbrev=False)
    ap.add_argument("-s", "--start", type=str, required=True, help="start tag")
    ap.add_argument("-e", "--end", type=str, required=True, help="end tag")
    ap.add_argument("-f", "--file", type=str, required=True)
    ap.add_argument("-r", "--replace-file", type=str, required=True)

    args = ap.parse_args()
    print(args)

    fp = Path(args.file)
    replace_fp = Path(args.replace_file)

    if not fp.exists():
        print(f"--file is invalid - {args.file} doesn't exist", file=sys.stderr)
        sys.exit(1)

    if not replace_fp.exists():
        print(
            f"--replace-file is invalid - {args.replace_file} doesn't exist",
            file=sys.stderr,
        )
        sys.exit(1)

    replace(
        file_path=fp,
        tag_start=args.start,
        tag_end=args.end,
        replace_file_path=replace_fp,
    )
    sys.exit(0)
