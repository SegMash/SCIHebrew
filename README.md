# SCI Hebrew Project

Tools and assets for creating Hebrew patches for Sierra SCI adventure games (KQ4, KQ5, KQ6, KQ7, QFG1).

> See [README_OLD.md](README_OLD.md) for the original development guide.

---

## Quick Start

| Game | Assets dir | Hebrew messages | Build script |
|------|-----------|-----------------|--------------|
| KQ4  | `games_assets/kq4` | `output_kq4/*_messages_hebrew.txt` | `scripts/translate_kq4.cmd` |
| KQ5  | `games_assets/kq5` | `output_kq5/*_hebrew.txt` | `scripts/translate_kq5.cmd` |
| KQ6  | `games_assets/kq6` | `output_kq6/*_messages_hebrew.txt` | `scripts/translate_kq6.cmd` |
| KQ7  | `games_assets/kq7` | `output_kq7/*_messages_hebrew.txt` | `scripts/translate_kq7.cmd` |
| QFG1 | `games_assets/qfg1` | `output_qfg1/*_messages_hebrew.txt` | `scripts/translate_qfg1.cmd` |

---

## Top-Level Build Scripts

### `scripts/translate_kq4.cmd`
Builds the KQ4 Hebrew patch. Creates mapping files from single/multi/format message files, translates SCI text resources, imports the vocabulary, and runs NSIS to produce the patch installer.

```cmd
scripts\translate_kq4.cmd
```

### `scripts/translate_kq5.cmd`
Builds the KQ5 Hebrew patch. Extracts English subtitles from TSV files, applies Hebrew translations, converts back to SCI TEX format, and copies fonts/scripts to the work directory.

```cmd
scripts\translate_kq5.cmd
```

### `scripts/translate_kq6.cmd`
Builds the KQ6 Hebrew patch. Applies JSON translations, parses SCI 1.1 MSG files, creates mapping files, replaces text in CSV files, creates binary MSG files, copies assets, and runs NSIS + zips for Android install.

```cmd
scripts\translate_kq6.cmd
```

### `scripts/translate_kq6_spec.cmd`
Specialized build for a single KQ6 module (916). Same pipeline as `translate_kq6.cmd` but restricted to one message file.

```cmd
scripts\translate_kq6_spec.cmd
```

### `scripts/translate_kq7.cmd`
Builds the KQ7 Hebrew patch. Same pipeline as KQ6 (JSON → parse → map → replace → create MSG), then copies MSG files to the KQ7 work PATCHES directory.

```cmd
scripts\translate_kq7.cmd
```

### `scripts/translate_qfg1.cmd`
Builds the QFG1 Hebrew patch. Same pipeline as KQ4 (map → translate texts → import vocab), then copies binary resources to the work directory.

```cmd
scripts\translate_qfg1.cmd
```

### `scripts/recreate_kq6_movie.cmd`
Recreates the KQ6 opening movie (`TOON.AVI`) with Hebrew subtitles. Generates subtitle frames, encodes them to a silent AVI, then merges with the original audio track using ffmpeg.

```cmd
scripts\recreate_kq6_movie.cmd
```

---

## `scripts/scripts/` — SCI Script Tools

### `copy_scripts.py`
Copies compiled `script.XXX` files from a source folder to a target folder based on a `scripts.list` file.

```
python scripts/scripts/copy_scripts.py <scripts.list> <source_dir> <target_dir>
```

### `extract_strings.py`
Scans all `.sc` source files in a folder and extracts hardcoded English strings enclosed in `{...}` or `"..."` delimiters. Output is a plain text file with one string per line.

```
python scripts/scripts/extract_strings.py <src_dir> <output_file>
python scripts/scripts/extract_strings.py --delimiter quotes <src_dir> <output_file>
```

### `replace_strings.py`
Reads a mapping file (`english === hebrew`) and replaces hardcoded strings inside `.sc` script source files. Writes translated files to a new output folder.

```
python scripts/scripts/replace_strings.py <src_dir> <src_heb_dir> <mapping_file>
```

### `scr_insert_byte_patcher.py`
Low-level binary patcher for compiled SCI script/heap files. Inserts or patches bytes at specific offsets using the SCI assembly opcode table, used for targeted fixes that cannot be done through SCICompanion.

```
python scripts/scripts/scr_insert_byte_patcher.py <script_file> <heap_file> [options]
```

---

## `scripts/text/` — Text & Message Tools

### `extract_texts.py`
Extracts all messages from SCI `text.*` resource files into plain text files, separated into single-line, multi-line, and format-string categories.

```
python scripts/text/extract_texts.py <game_dir> <output_single> <output_multi> <output_format>
```

### `extract_english.py`
Reads a TSV file (used by KQ5-style subtitle resources) and extracts the English text column to a plain text file.

```
python scripts/text/extract_english.py <tsv_file> <output_file>
```

### `map_files.py`
Maps corresponding lines from an English source file and a Hebrew translation file, producing a `english === hebrew` mapping file. Supports `--multiline` mode and `--append` to merge multiple mappings.

```
python scripts/text/map_files.py <english.txt> <hebrew.txt> <mapping.txt>
python scripts/text/map_files.py --multiline <english.txt> <hebrew.txt> <mapping.txt> --append
```

### `translate_texts.py`
Applies a mapping file to SCI `text.*` binary resources. Reads with windows-1252 encoding, writes with windows-1255 (Hebrew) encoding.

```
python scripts/text/translate_texts.py <resources_dir> <output_dir> <mapping_file>
```

### `tex2tsv.py`
Reads a SCI TEX binary resource and converts it to a TSV file for editing.

```
python scripts/text/tex2tsv.py <tex_file> <output_dir>
```

### `tsv2tex.py`
Converts a TSV file back into a SCI TEX binary resource.

```
python scripts/text/tsv2tex.py <tsv_file> <output_dir> [--no-selector]
```

### `parse_msg.py`
Parses a Sierra SCI 1.1 binary `.msg` file and exports all messages to a CSV file.

```
python scripts/text/parse_msg.py <file.msg> [--debug]
```

### `parse_sci1.1_messages.py`
Batch runner: scans a directory for `*.msg` files, runs `parse_msg.py` on each, then runs `process_messages.py` to generate split English/format/multi message lists.

```
python scripts/text/parse_sci1.1_messages.py <resources_dir> <output_dir> [module_number]
```

### `process_messages.py`
Reads a CSV of parsed messages and generates cleaned plain-text output files (single-line, multi-line, format strings) suitable for mapping and AI translation.

```
python scripts/text/process_messages.py <messages.csv> <output_dir>
```

### `create_msg.py`
Converts a translated CSV file (originally produced by `parse_msg.py`) back to a binary SCI 1.1 `.msg` file.

```
python scripts/text/create_msg.py <messages.csv> <output.msg>
```

### `replace_in_csv.py`
Reads a CSV file of parsed messages and replaces English text with Hebrew translations from a mapping file.

```
python scripts/text/replace_in_csv.py <messages.csv> <mapping_file> <output_dir>
```

### `replace_in_tsv.py`
Reads a TSV file and replaces the English text column with Hebrew translations from a mapping file.

```
python scripts/text/replace_in_tsv.py <file.tsv> <mapping_file> <output_dir>
```

### `mapping_to_json.py`
Converts a `english === hebrew` mapping file to a `messages.json` format used for AI-assisted translation workflows.

```
python scripts/text/mapping_to_json.py <mapping_file> <output.json>
```

### `json_to_hebrew.py`
Compares an old and new `messages.json` and updates Hebrew translation text files with any changed translations (matched by message number).

```
python scripts/text/json_to_hebrew.py <old.json> <new.json> <hebrew.txt>
```

### `json_to_hebrew_kq5.py`
Reads a `messages.json` file and writes translations back to KQ5-style `*_hebrew.txt` files.

```
python scripts/text/json_to_hebrew_kq5.py <messages.json> <output_dir>
```

### `json_to_hebrew_kq6.py`
Same as `json_to_hebrew_kq5.py` but for KQ6/KQ7-style message files.

```
python scripts/text/json_to_hebrew_kq6.py <messages.json> <output_dir>
```

### `merge_files.py`
Merges split Hebrew text files (produced by `split_file.py`, named `*_part<N>_hebrew.txt`) back into a single output file, in numeric order.

```
python scripts/text/merge_files.py <parts_dir> <output_file>
```

### `split_file.py`
Splits a large text file into smaller files with a specified number of lines per file (default: 250). Useful for feeding to AI translation in chunks.

```
python scripts/text/split_file.py <input_file> [--lines 250] [output_dir]
```

### `find_hebrew_in_scripts.py`
Scans `.sc` source files for lines containing Hebrew characters (windows-1255, ASCII 224–250). Used to audit scripts for already-translated strings.

```
python scripts/text/find_hebrew_in_scripts.py <src_dir>
```

### `find_nikud.py`
Scans a file (typically `messages.json`) for lines containing Hebrew nikud (vowel marks, U+05B0–U+05C7) which should generally not appear in translated strings.

```
python scripts/text/find_nikud.py <messages.json> [--show-text]
```

### `fix_kq6_165_messages.py`
One-off patch for KQ6 module 165: adds a missing message row to the translated CSV file.

```
python scripts/text/fix_kq6_165_messages.py <165_messages.csv>
```

---

## `scripts/fonts/` — Font Tools

### `parse_font.py`
Parses a SCI binary font file and exports each character as a PNG image. Useful for inspecting or editing a font.

```
python scripts/fonts/parse_font.py <font_file> <output_dir>
```

### `build_font.py`
Builds a SCI binary font file from a directory of PNG character images. This is the reverse of `parse_font.py`.

```
python scripts/fonts/build_font.py <images_dir> <output_font_file>
```

### `generate_hebrew_font.py`
Generates PNG bitmap images for the 27 Hebrew characters (code points 128–154) from the embedded `fontData_ExtendedHebrew` array. Used to bootstrap Hebrew character images for `build_font.py`.

```
python scripts/fonts/generate_hebrew_font.py <output_dir>
```

---

## `scripts/images/` — Image Manipulation Tools

### `copy_region.py`
Copies a rectangular region from one image and pastes it into another image (in-place).

```
python scripts/images/copy_region.py source.png target.png x1 y1 x2 y2
```

### `filter_palette_indexes.py`
Replaces specified palette index values with index 0 in an 8-bit indexed PNG. Optionally restricts filtering to one or more rectangular areas.

```
python scripts/images/filter_palette_indexes.py image.png 5 12 37
python scripts/images/filter_palette_indexes.py image.png 5 12 37 --area 60,110,420,140
```

### `merge_images.py`
Merges multiple 8-bit indexed PNG images by taking the maximum palette index at each pixel. Optionally restricted to a rectangular area. Used to composite subtitle frames onto background frames.

```
python scripts/images/merge_images.py a.png b.png c.png [-o merged.png] [--area x1,y1,x2,y2]
```

### `generate_subtitle_frames.py`
High-level script that generates Hebrew subtitle frames for the KQ6 opening movie. Calls `generate_text_frame.py` per subtitle and composites onto extracted base frames.

```
python scripts/images/generate_subtitle_frames.py
```

### `generate_text_frame.py`
Generates a single 8-bit indexed PNG frame with text rendered inside specified margins. Supports RTL (Hebrew) text via the `python-bidi` library.

```
python scripts/images/generate_text_frame.py --width 640 --height 480 --font arial.ttf \
  --font-size 20 --font-color white --background black --text "Your text" --output out.png
```

### `write_text.py`
Writes text directly onto an existing 8-bit indexed PNG using a specified palette color index. Supports RTL text with `--rtl`.

```
python scripts/images/write_text.py base.png "שלום" --font david.ttf --font-size 20 \
  --color-index 5 --x 400 --y 50 --rtl
```

### `print_palette.py`
Prints the 256-color palette of an 8-bit indexed PNG file. Optional flags: `--used` (skip empty entries), `--hex` (show hex values).

```
python scripts/images/print_palette.py image.png [--used] [--hex]
```

---

## `scripts/pictures/` — SCI Picture (P56) Tools

### `extract_p56_layer.py`
Extracts a bitmap layer from a Sierra SCI2 picture patch (`.p56`) file and saves it as an 8-bit indexed PNG.

```
python scripts/pictures/extract_p56_layer.py <file.p56> --layer <N> [-o <out.png>]
```

### `import_p56_layer.py`
Injects a modified PNG image back into a layer of a `.p56` file. The PNG must be in indexed mode (`P`) and match the original layer dimensions.

```
python scripts/pictures/import_p56_layer.py <file.p56> <image.png> --layer <N> [--in-place | -o <out.p56>]
```

### `extract_png_palette.py`
Extracts the palette embedded in a `.p56` file and saves it in one of several formats: `txt`, `json`, `gpl` (GIMP), or `bin`.

```
python scripts/pictures/extract_png_palette.py <file.p56> [-o <output>] [--format txt|json|gpl|bin]
```

### `apply_png_palette.py`
Applies an external palette file to a PNG, producing a new 8-bit indexed PNG with the new color mapping. Supports `txt`, `json`, `gpl`, and `bin` palette formats.

```
python scripts/pictures/apply_png_palette.py <image.png> <palette_file> [-o <out.png>]
```

---

## `scripts/views/` — SCI View (V56) Tools

### `extract_v56.py`
Extracts all loops/cells from a Sierra SCI VGA view (`.v56`) file as 8-bit indexed PNGs with embedded palette and transparency.

```
python scripts/views/extract_v56.py <file.v56> [-o <output_dir>] [--palette <file.pal>]
```

### `import_v56.py`
Imports modified PNG images back into a `.v56` file. Matches images by name (`<view>_<loop>_<cell>.png`), compresses using Sierra RLE, and writes a new `.v56`.

```
python scripts/views/import_v56.py <file.v56> <images_dir> [-o <output.v56>]
```

---

## `scripts/robot/` — Sierra Robot (RBT) Video Tools

### `encode_rbt.py`
Encodes a folder of numbered frame images (PNG/BMP, 8-bit or RGB) and an optional WAV audio file into a Sierra Robot v5/v6 `.rbt` video file playable in ScummVM.

```
python scripts/robot/encode_rbt.py <frames_dir> <output.rbt> [--fps 15] [--audio file.wav] \
  [--lzs] [--v6] [--palette file.png]
```

### `parse_rbt.py`
Parses a Sierra Robot (`.rbt`) video file (v5 or v6) and extracts frames and metadata to an output directory.

```
python scripts/robot/parse_rbt.py <file.rbt> [-o <output_dir>]
```

### `play_rbt.py`
Plays a Sierra Robot (`.rbt`) video file, decoding palettised frames and Sierra SOL DPCM-16 audio via pygame.

```
python scripts/robot/play_rbt.py <file.rbt> [--scale 2] [--no-audio]
```

### `inject_subtitles.py`
Dry-runs a subtitle injection timeline: for each frame in an `.rbt` file, prints which Hebrew subtitle text would be injected based on a subtitle marker file.

```
python scripts/robot/inject_subtitles.py <file.rbt> <subtitles_file> --font <font_file>
```

---

## `scripts/avi/` — AVI Video Tools

### `encode_avi_raw.py`
Encodes a folder of 8-bit indexed PNG frames into an uncompressed palette AVI file. No codec required — pure RIFF/AVI format.

```
python scripts/avi/encode_avi_raw.py <frames_dir> <output.avi> [fps]
```

---

## `scripts/vocab/` — Vocabulary / Parser Tools

### `vocab_export.py`
Exports the game vocabulary (`vocab.000` or `vocab.900`) to a CSV file for editing. Converts Sierra vocab formats to readable text for translation workflows.

```
python scripts/vocab/vocab_export.py <vocab_file> <output_dir>
```

### `vocab_import.py`
Imports a translated vocabulary CSV back into a `vocab.000` binary file. Validates for duplicates and multi-word entries before writing.

```
python scripts/vocab/vocab_import.py <output_dir> <work_dir> <resources_dir>
```

### `vocab_migrate_sci_to_sci.py`
Migrates Hebrew translations from one SCI game's vocab.csv to another SCI game's vocab.csv. For each English word in the target vocab, looks it up in the source vocab and copies the Hebrew translation if found.

```
python scripts/vocab/vocab_migrate_sci_to_sci.py <source_vocab.csv> <target_vocab.csv> <output_vocab.csv> [--debug]
```

**Usage:**
- `<source_vocab.csv>`: Source SCI vocab with existing Hebrew translations
- `<target_vocab.csv>`: Target SCI vocab to be enhanced
- `<output_vocab.csv>`: Output file with merged translations
- `--debug`: Show detailed matching information for each word

**Notes:**
- Skips rows that already have Hebrew translations (contains pipe character)
- Most reliable when source and target are from similar games in the same series
- More reliable than AGI-to-SCI migration due to matching word format

---

## `scripts/asm_lib/` — Assembly Library (Shared)

Internal library used by `scr_insert_byte_patcher.py`. Provides SCI bytecode lexer, parser, opcode definitions, and section/heap utilities. Not intended to be called directly.

| Module | Purpose |
|--------|---------|
| `asm_lexer.py` | Tokenizes SCI assembly text |
| `asm_parser.py` | Parses tokenized SCI assembly |
| `opcodes.py` | SCI opcode table and instruction lengths |
| `instruction.py` | Instruction data model |
| `sci_section.py` | Script/heap section reader |
| `misc.py` | Shared constants (magic numbers, headers) |
