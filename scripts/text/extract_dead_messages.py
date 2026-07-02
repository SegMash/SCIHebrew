# coding=utf-8

"""
    extract_dead_messages.py

    Extract death messages from SCI script (.sc) files.

    Finds calls like (ProcedureName {message}) or multiline forms where the
    braced message appears on a later line:

        (EgoDeadNew
            {You were warned ogre and ogre again...}
        )

    The procedure name is configurable (default: EgoDead).
"""

import argparse
import os
import re
import sys
from pathlib import Path

DEFAULT_PROCEDURE = "EgoDead"
ENCODINGS = ("utf-8", "windows-1255", "windows-1252", "latin-1")


def read_file_text(filepath):
    last_error = None
    for encoding in ENCODINGS:
        try:
            with open(filepath, "r", encoding=encoding) as handle:
                return handle.read(), encoding
        except UnicodeDecodeError as exc:
            last_error = exc
    raise UnicodeDecodeError(
        last_error.encoding,
        last_error.object,
        last_error.start,
        last_error.end,
        f"Could not decode {filepath} with {ENCODINGS}",
    )


def find_balanced_close(text, open_pos):
    if open_pos >= len(text) or text[open_pos] != "(":
        return None

    depth = 1
    index = open_pos + 1
    while index < len(text):
        char = text[index]
        if char == "{":
            close = text.find("}", index + 1)
            if close == -1:
                return None
            index = close
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def extract_brace_strings(call_text):
    messages = []
    index = 0
    while index < len(call_text):
        if call_text[index] == "{":
            close = call_text.find("}", index + 1)
            if close == -1:
                break
            messages.append(call_text[index + 1 : close])
            index = close
        index += 1
    return messages


def is_procedure_definition(text, open_pos):
    prefix = text[max(0, open_pos - 12) : open_pos]
    return prefix.rstrip().endswith("(procedure")


def find_dead_messages(text, procedure_name):
    pattern = re.compile(r"\(" + re.escape(procedure_name) + r"(?=[\s\r\n{)])")
    results = []

    for match in pattern.finditer(text):
        open_pos = match.start()
        if is_procedure_definition(text, open_pos):
            continue

        close_pos = find_balanced_close(text, open_pos)
        if close_pos is None:
            continue

        call_text = text[open_pos : close_pos + 1]
        messages = extract_brace_strings(call_text)
        if not messages:
            continue

        line_number = text.count("\n", 0, open_pos) + 1
        results.append(
            {
                "line": line_number,
                "messages": messages,
                "call_text": call_text,
            }
        )

    return results


def scan_directory(source_dir, procedure_name):
    source_path = Path(source_dir)
    sc_files = sorted(source_path.rglob("*.sc"))

    if not sc_files:
        print(f"No .sc files found in '{source_dir}'.")
        return []

    all_results = []
    for sc_file in sc_files:
        try:
            content, encoding = read_file_text(sc_file)
        except UnicodeDecodeError as exc:
            print(f"Error reading '{sc_file}': {exc}")
            continue

        matches = find_dead_messages(content, procedure_name)
        for match in matches:
            for message in match["messages"]:
                all_results.append(
                    {
                        "file": str(sc_file),
                        "line": match["line"],
                        "message": message,
                        "encoding": encoding,
                    }
                )

    return all_results


def write_output(results, output_path, include_source):
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as handle:
        if include_source:
            handle.write("file,line,message\n")
            for item in results:
                message = item["message"].replace("\r", "").replace("\n", "\\n")
                handle.write(f"{item['file']},{item['line']},\"{message}\"\n")
        else:
            seen = set()
            for item in results:
                message = item["message"]
                if message in seen:
                    continue
                seen.add(message)
                handle.write(message + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Extract braced death messages from SCI .sc script files."
    )
    parser.add_argument(
        "source_dir",
        help="Directory containing .sc files (searched recursively)",
    )
    parser.add_argument(
        "-p",
        "--procedure",
        default=DEFAULT_PROCEDURE,
        help=f"Procedure name to search for (default: {DEFAULT_PROCEDURE})",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (default: <source_dir>/dead_messages.csv)",
    )
    parser.add_argument(
        "--include-source",
        action="store_true",
        help="Write CSV output with source file and line number for each message",
    )
    parser.add_argument(
        "--unique",
        action="store_true",
        help="When writing plain text output, write each message only once",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.source_dir):
        print(f"Error: Directory '{args.source_dir}' not found.")
        sys.exit(1)

    output_path = args.output or os.path.join(args.source_dir, "dead_messages.csv")
    results = scan_directory(args.source_dir, args.procedure)

    if args.include_source:
        write_output(results, output_path, include_source=True)
    else:
        if args.unique:
            write_output(results, output_path, include_source=False)
        else:
            with open(output_path, "w", encoding="utf-8") as handle:
                for item in results:
                    handle.write(item["message"] + "\n")

    unique_messages = len({item["message"] for item in results})
    print(
        f"Extracted {len(results)} message(s) "
        f"({unique_messages} unique) using procedure '{args.procedure}'."
    )
    print(f"Output written to '{output_path}'.")


if __name__ == "__main__":
    main()
