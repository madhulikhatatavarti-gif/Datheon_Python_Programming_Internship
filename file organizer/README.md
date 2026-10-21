# File Organizer

A desktop automation script that cleans up a cluttered folder (such as Downloads) by sorting files into category subfolders based on their extension. Written in Python 3 using only the standard library (`os`, `shutil`, `pathlib`, `logging`, `argparse`).

## Features

- Reads every file in the chosen folder with `os.scandir()` and checks its extension.
- Creates the category folders automatically when needed: `Documents`, `Images`, `Videos`, `Archives`, `Code`.
- Moves files with `shutil.move()`.
- **Name collisions:** if a file with the same name already exists in the target folder, the new file is renamed (`report (1).pdf`, `report (2).pdf`, ...) so nothing is ever overwritten.
- **Error handling:** `PermissionError`, `FileExistsError` and other `OSError`s are caught, logged, and the script carries on with the next file.
- Leaves unrecognised file types, subfolders, hidden files and the script itself untouched.
- Prints a formatted execution summary (files moved per category, skipped, errors).
- Writes a timestamped log to `organizer.log`.
- `--dry-run` previews what would happen without moving anything.

## Category mapping

| Folder    | Extensions |
|-----------|------------|
| Documents | .pdf .doc .docx .txt .rtf .odt .xls .xlsx .csv .ppt .pptx .md |
| Images    | .jpg .jpeg .png .gif .bmp .webp .svg .tiff .ico |
| Videos    | .mp4 .mkv .avi .mov .wmv .flv .webm |
| Archives  | .zip .rar .7z .tar .gz .bz2 |
| Code      | .py .js .html .css .java .c .cpp .h .json .xml .sql .sh .ts |

Extensions are matched case-insensitively, and the mapping is a dictionary at the top of `organizer.py` that is easy to extend.

## How to run

1. Install Python 3 from https://www.python.org/downloads/
2. Open a terminal in the `organizer` folder.
3. Preview first (nothing is moved):

```
python organizer.py "C:\Users\YourName\Downloads" --dry-run
```

4. Run for real (it asks for confirmation first):

```
python organizer.py "C:\Users\YourName\Downloads"
```

If you run `python organizer.py` with no folder, it asks which folder to organize and suggests your Downloads folder.

Add `--yes` to skip the confirmation question.

## Options

| Option      | What it does |
|-------------|--------------|
| `folder`    | Folder to organize (optional - the script asks if omitted) |
| `--dry-run` | Show what would be moved without changing anything |
| `--yes`     | Do not ask for confirmation |

## Note

Only the files directly inside the chosen folder are organized. Existing subfolders are not opened or changed.
