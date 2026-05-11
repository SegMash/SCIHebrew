# Sierra's SCI vocab format has "old" version (used by vocab.000) - with 7 bits ascii
# and 8th bit used for string end
# while "new" version (used by vocab.900) has 8 bits ascii
#
# reference: http://sci.sierrahelp.com/Documentation/SCISpecifications/27-TheParser.html#AEN5794
# for Hebrew translation, we need the vocab to be in the newer version

# this exports vocab file to a csv
# see also vocab_import.py
import argparse
import glob
import os
import pathlib
import csv
import re

import config

SIERRA_VOCAB_HEADER = b'\x86\0'
VOCAB_FILE = "vocab.000"
VOCAB_ENCODING = 'windows-1255'

classes = {
    0x004: 'CONJUNCTION',
    0x008: 'ASSOCIATION',
    0x010: 'PREPOSITION',
    0x020: 'ARTICLE',
    0x040: 'ADJECTIVE',
    0x080: 'PRONOUN',
    0x100: 'NOUN',
    0x200: 'INDICATIVE_VERB',
    0x400: 'ADVERB',
    0x800: 'IMPERATIVE_VERB'
}

# TODO del?
def get_room_number(script):
    room = re.search(r'\(script#\s*(.+)\)', script).group(1)
    if room.isdigit():
        return room.zfill(3)
    else:
        print("strings_import: get_room_number need to add support to define: ", room)
        return room


def get_classes(i):
    result = []
    for k in classes.keys():
        if i & k != 0:
            result.append(classes[k])
    return result


def detect_vocab_kind(vocab_path):
    if vocab_path.suffix.lower() == '.900':
        return 'new'
    return 'old'


def decode_vocab_bytes(word_bytes):
    try:
        return bytes(word_bytes).decode(VOCAB_ENCODING)
    except UnicodeDecodeError:
        return bytes(word_bytes).decode('latin1')


def parse_vocab_entries(in_vocab, kind):
    pointer_bytes = 255 * 2 if kind == 'new' else 26 * 2
    if len(in_vocab) < pointer_bytes:
        raise ValueError(f"Input vocab is too short for {kind} format pointer table")

    entries = []
    idx = pointer_bytes
    current_word = ""
    while idx < len(in_vocab):
        same_letters = in_vocab[idx]
        idx += 1
        current_word = current_word[:same_letters]

        word_bytes = []
        if kind == 'new':
            while idx < len(in_vocab) and in_vocab[idx] != 0:
                word_bytes.append(in_vocab[idx])
                idx += 1
            if idx >= len(in_vocab):
                break
            idx += 1  # zero terminator
        else:
            found_end = False
            while idx < len(in_vocab):
                val = in_vocab[idx]
                idx += 1
                if val >= 0x80:
                    word_bytes.append(val - 0x80)
                    found_end = True
                    break
                if val < 0x20:
                    print(f"Warning: strange char with ascii value {val}. Ignoring")
                    continue
                word_bytes.append(val)
            if not found_end:
                break

        current_word += decode_vocab_bytes(word_bytes)

        if idx + 2 >= len(in_vocab):
            break

        byte1 = in_vocab[idx]
        byte2 = in_vocab[idx + 1]
        byte3 = in_vocab[idx + 2]
        idx += 3

        cls = (byte1 << 4) + (byte2 >> 4)
        group = ((byte2 & 0b1111) << 8) + byte3
        entries.append({'word': current_word, 'class': get_classes(cls), 'group': group})

    return entries


def get_said_per_room(gamedir):
    result = {}
    srcdir = os.path.join(gamedir, 'src')
    for filename in glob.iglob(os.path.join(srcdir, '*.sc')):
        with open(filename) as f:
            text = f.read()
            text_dense = text.replace('\n', '').replace('\t','')
            room = get_room_number(text)
            saids = re.findall(r"\(Said\s'(.*?)'", text_dense)
            words_in_room = set([w for l in [re.split(r'\W+', said) for said in saids] for w in l if w])
            for word in words_in_room:
                cur = result.get(word, [])
                cur.append((room, [said for said in saids if word in said]))
                result[word] = cur
    return result


def vocab_export(vocab_file, csvdir):
    vocab_path = pathlib.Path(vocab_file)
    gamedir = str(vocab_path.parent)

    in_vocab = list(vocab_path.read_bytes())
    assert bytes(in_vocab[:2]) == SIERRA_VOCAB_HEADER
    in_vocab = in_vocab[2:]

    said_per_room = get_said_per_room(gamedir)
    kind = detect_vocab_kind(vocab_path)
    vocab = parse_vocab_entries(in_vocab, kind)
    vocab_by_group = {}
    for entry in vocab:
        group = entry['group']
        if group in vocab_by_group:
            vocab_by_group[group]['words'].append(entry['word'])
            if sorted(vocab_by_group[group]['class']) != sorted(entry['class']):
                vocab_by_group[group]['class'].extend(entry['class'])
                vocab_by_group[group]['class'] = sorted(set(vocab_by_group[group]['class']))
                print("Warning: class mismatch: ", vocab_by_group[group])
        else:
            vocab_by_group[group] = {
                'words': [entry['word']],
                'class': entry['class']
            }
    sorted_vocab = []
    for k in sorted(vocab_by_group.keys()):
        entry = vocab_by_group[k]

        rooms = []
        for word in entry['words']:
            if word in said_per_room:
                said = said_per_room[word]
                rooms.extend([s[0].zfill(3) for s in said])
                rooms = list(set(rooms))
                rooms.sort(key=int)

        entry['group'] = k
        entry['words'] = " | ".join(entry['words'])
        entry['class'] = " | ".join(entry['class'])
        if rooms:
            # added 'in ' to force Excel treat it as text, and thus keeping the leading zeroes,
            # which will help in easy sort by room
            entry['rooms'] = "in " + ", ".join(rooms)
        else:
            entry['rooms'] = ''
        entry['comments'] = ''

        sorted_vocab.append(entry)
    sorted_vocab = sorted(sorted_vocab, key=lambda k: (k['rooms'] == "", k['rooms']))
    write_csv(csvdir, sorted_vocab, config.vocab_csv_filename)


def write_csv(csvdir, vocab, vocab_csv_filename):
    with open(os.path.join(csvdir, vocab_csv_filename), 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, vocab[0].keys(), quoting=csv.QUOTE_ALL)
        dict_writer.writeheader()
        dict_writer.writerows(vocab)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='Exports dictionary words from SCI vocab files (vocab.000 / vocab.900) to CSV',)
    parser.add_argument("vocab_file", help=f"path to vocab file (for example: <game_dir>/{VOCAB_FILE})")
    parser.add_argument("csvdir", help=f"directory to write {config.vocab_csv_filename}")
    args = parser.parse_args()

    vocab_export(args.vocab_file, args.csvdir)
