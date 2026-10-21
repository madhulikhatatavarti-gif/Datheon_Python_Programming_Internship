#!/usr/bin/env python3
"""File organizer: sorts the files in a cluttered folder (e.g. Downloads)
into category subfolders based on each file's extension.

Categories: Documents, Images, Videos, Archives, Code.
Files with other extensions are left where they are.

Usage:
    python organizer.py                      # asks which folder to organize
    python organizer.py "C:\\Users\\me\\Downloads"
    python organizer.py "C:\\Users\\me\\Downloads" --dry-run   # preview only
    python organizer.py "C:\\Users\\me\\Downloads" --yes       # skip the confirmation

Every action is also written to organizer.log (next to this script).
"""

import argparse
import logging
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

# ------------------------------------------------------------------ categories
CATEGORIES = {
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx",
                  ".csv", ".ppt", ".pptx", ".md"],
    "Images":    [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".tiff", ".ico"],
    "Videos":    [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
    "Archives":  [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Code":      [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".h", ".json",
                  ".xml", ".sql", ".sh", ".ts"],
}

# Reverse lookup: extension -> category folder, e.g. {".pdf": "Documents", ...}
EXTENSION_MAP = {ext: folder for folder, exts in CATEGORIES.items() for ext in exts}

SCRIPT_DIR = Path(__file__).resolve().parent
LOG_FILE = SCRIPT_DIR / "organizer.log"

log = logging.getLogger("organizer")


def setup_logging():
    """Log to the console (short) and to organizer.log (with timestamps)."""
    log.setLevel(logging.INFO)
    log.handlers.clear()

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(console)

    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-7s %(message)s"))
        log.addHandler(file_handler)
    except OSError:
        print(f"Note: could not create the log file {LOG_FILE}; logging to console only.")


# --------------------------------------------------------------------- helpers
def unique_destination(path: Path) -> Path:
    """If `path` already exists, return 'name (1).ext', 'name (2).ext', ... instead."""
    if not path.exists():
        return path
    counter = 1
    while True:
        candidate = path.with_name(f"{path.stem} ({counter}){path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def scan_files(folder: Path):
    """Return the files directly inside `folder` that should be organized."""
    files = []
    with os.scandir(folder) as entries:
        for entry in entries:
            if entry.name.startswith("."):          # hidden files
                continue
            if not entry.is_file(follow_symlinks=False):   # folders and symlinks
                continue
            if Path(entry.path).resolve() == Path(__file__).resolve():  # this script
                continue
            files.append(Path(entry.path))
    return sorted(files)


def organize(folder: Path, dry_run: bool):
    """Move every recognised file into its category folder. Returns the results."""
    moved = Counter()      # category -> number of files moved
    skipped = []           # files with no matching category
    errors = []            # (file, reason)

    for file in scan_files(folder):
        category = EXTENSION_MAP.get(file.suffix.lower())
        if category is None:
            skipped.append(file)
            log.info(f"  SKIP   {file.name}  (no category for '{file.suffix or 'no extension'}')")
            continue

        target_dir = folder / category
        destination = unique_destination(target_dir / file.name)
        renamed = destination.name != file.name

        if dry_run:
            note = f"  (renamed to {destination.name})" if renamed else ""
            log.info(f"  WOULD MOVE  {file.name}  ->  {category}/{note}")
            moved[category] += 1
            continue

        try:
            target_dir.mkdir(exist_ok=True)           # create the category folder if needed
            shutil.move(str(file), str(destination))
            note = f"  (renamed to {destination.name})" if renamed else ""
            log.info(f"  MOVED  {file.name}  ->  {category}/{note}")
            moved[category] += 1
        except PermissionError:
            errors.append((file, "permission denied (file in use or protected)"))
            log.error(f"  ERROR  {file.name}: permission denied (file in use or protected)")
        except FileExistsError:
            errors.append((file, "a file with that name already exists"))
            log.error(f"  ERROR  {file.name}: a file with that name already exists")
        except OSError as exc:
            errors.append((file, str(exc)))
            log.error(f"  ERROR  {file.name}: {exc}")

    return moved, skipped, errors


def print_summary(folder: Path, moved, skipped, errors, dry_run):
    total = sum(moved.values())
    verb = "would be moved" if dry_run else "moved"
    log.info("")
    log.info("=" * 50)
    log.info("  EXECUTION SUMMARY" + ("  (DRY RUN - nothing changed)" if dry_run else ""))
    log.info("=" * 50)
    log.info(f"  Folder:           {folder}")
    for category in CATEGORIES:
        if moved[category]:
            log.info(f"  {category + ':':<17} {moved[category]} file(s) {verb}")
    log.info("  " + "-" * 46)
    log.info(f"  Total {verb}:".ljust(20) + f" {total}")
    log.info(f"  Skipped:          {len(skipped)} (unrecognised type)")
    log.info(f"  Errors:           {len(errors)}")
    log.info("=" * 50)
    if not dry_run:
        log.info(f"  Full log saved to {LOG_FILE}")


# ------------------------------------------------------------------------ main
def parse_args():
    parser = argparse.ArgumentParser(description="Organize a folder by file type.")
    parser.add_argument("folder", nargs="?", help="folder to organize (default: ask)")
    parser.add_argument("--dry-run", action="store_true", help="preview without moving anything")
    parser.add_argument("--yes", action="store_true", help="skip the confirmation question")
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging()

    raw = args.folder or input(
        f"Folder to organize [{Path.home() / 'Downloads'}]: "
    ).strip().strip('"')
    folder = Path(raw).expanduser() if raw else Path.home() / "Downloads"

    if not folder.is_dir():
        log.error(f"'{folder}' is not a folder. Check the path and try again.")
        return 1

    try:
        files = scan_files(folder)
    except PermissionError:
        log.error(f"Permission denied: cannot read '{folder}'.")
        return 1

    log.info(f"\nOrganizing: {folder}  ({len(files)} file(s) found)")
    if not files:
        log.info("Nothing to organize.")
        return 0

    if not args.dry_run and not args.yes:
        answer = input("Move these files into category folders now? (y/n): ").strip().lower()
        if answer not in ("y", "yes"):
            log.info("Cancelled. No files were moved.")
            return 0

    log.info("")
    moved, skipped, errors = organize(folder, args.dry_run)
    print_summary(folder, moved, skipped, errors, args.dry_run)
    return 1 if errors else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        print("\n\nInterrupted. Goodbye!\n")
