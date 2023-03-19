# WARNING

The code in this repository has not been thoroughly tested. This code has been laying in my PC for months without me having time to work on it. I figured that it would be better to publish it as it is rather than leaving it hidden in the filesystem. If you find any problem, please open an issue.

## What's This?

This is a small python library to extract and rebuild files used by Project Zero for PS2. For now it supports extracting and rebuilding the IMG_BD.BIN file and the game OBJ text files (IG_MSG, M0_EVENT, M1_EVENT, M2_EVENT, M3_EVENT, M4_EVENT).

Extraction can be performed directly from and to the ISO file, or using the files by themselves (e.g., extract the English text from IG_MSG_E.OBJ into a JSON file and rebuild the IG_MSG_E.OBJ file from the JSON).

Ideally this tool could be used to produce a full localization to a language other than the 5 present in the PAL version, by extracting and editing both TM2 images for the graphical localization and all text OBJ files for the in-game text.

## Usage

The main entry point is the `ztools.py` file (or if installed with pip, it is also available as the `zerotools` command). There are three main commands available:
* `imgbd` - to extract and rebuild the main IMG_BD.BIN file
* `text` - to extract and rebuild text files (OBJs)
* `elf` - to extract filenames (useful if you want to work with files rather than using the ISO, in which case the named are automatically extracted from the main ELF in the ISO when needed).

Each command has its own subcommands:

```
imgbd
  ├─ extract-iso    - Extract IMG_BD files from ISO.
  ├─ rebuild-iso    - Rebuild IMG_BD from files and inject it back into ISO.
  ├─ extract-fs     - Extract IMG_BD files from files.
  └─ rebuild-fs     - Rebuild IMG_BD from files and save it into folder.
text
  ├─ extract-iso    - Extract and parse in-game text files from ISO.
  ├─ rebuild-iso    - Rebuild in-game text and inject it back into ISO.
  ├─ extract-file   - Extract and parse in-game text files from OBJ.
  └─ rebuild-file   - Rebuild in-game text and save it as OBJ file.
elf
  ├─ parse-iso      - Extract various file names from ISO.
  └─ parse-file     - Extract various file names from ELF file.
```

please, refer to each subcommand help for specific usage.

Most notably, the text can be extracted into three different formats:
* JSON
* XML
* TXT Files

A command line example to extract all English text would be:

```
python3 ztools.py text extract-iso /path/to/SLES_508.21.ProjectZero.iso /path/to/output/folder/ -f JSON -l EN
```
which will produce the following files in the specified folder:
```
IG_MSG_E.json
M0_EVENT_E.json
M1_EVENT_E.json
M2_EVENT_E.json
M3_EVENT_E.json
M4_EVENT_E.json
```
Each file (for example the `IG_MSG_E.json`) can then be edited and inserted back into the ISO with the following command:
```
python3 ztools.py text rebuild-iso /path/to/output/folder/IG_MSG_E.json /path/to/SLES_508.21.ProjectZero.iso -f JSON -l EN -t IG_MSG
```

## Documentation

Additionally, in the `docs` folder, you can find some documentation about file formats, specifically the IMG_BD.BIN and the OBJ language files.