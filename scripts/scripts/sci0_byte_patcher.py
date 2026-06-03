#!/usr/bin/env python3
"""
SCI0 script byte patcher.

Insert N null bytes (action=insert) or remove N bytes (action=remove) at
a given offset in a SCI0 ``script.NNN`` file (e.g. ``script.000``,
``script.137``), and fix everything that depends on offsets:

  * containing section's length field
  * relocation table -- each entry's location AND the absolute pointer
    stored at the location it points to
  * EXPORTS values
  * OBJECT/CLASS ``func_selector_offset`` (only if the modification
    falls inside the object's pre-``num_methods`` header area)
  * relative branches in CODE: ``bt``, ``bnt``, ``jmp``, ``call``
  * relative ``lofsa`` / ``lofss`` in CODE (SCI0 default)

Usage::

    python sci0_byte_patcher.py SCRIPT OFFSET COUNT [--action insert|remove]
                                [--payload-offset] [--out OUT] [--backup]

Example::

    python sci0_byte_patcher.py game/script.137 0x1A6 4 --action insert --backup
    python sci0_byte_patcher.py game/script.000 0x252 2 --action remove

By default OFFSET is interpreted as a **raw file offset** (i.e., as it
appears in a hex editor of the script.NNN file). When the file starts
with the 2-byte ``0x82 0x00`` Sierra prefix, those 2 bytes are
automatically subtracted to land on the right payload position.

Pass ``--payload-offset`` if your offset is already in payload
coordinates (i.e., relative to the script content with the 2-byte prefix
already excluded).
"""

import argparse
import sys
from pathlib import Path

# Allow running from this folder (asm_lib lives next to it).
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from asm_lib.opcodes import instruction_length  # noqa: E402

SIERRA_SCRIPT_HEADER = b'\x82\x00'
SCRIPT_OBJECT_MAGIC_NUMBER = 0x1234

# ------------------------- SCI0 section types -------------------------
SEC_OBJECT = 1
SEC_CODE = 2
SEC_SYNONYMS = 3
SEC_SAID = 4
SEC_STRINGS = 5
SEC_CLASS = 6
SEC_EXPORTS = 7
SEC_RELOCATION = 8
SEC_PRELOAD_TEXT = 9
SEC_LOCAL_VARS = 10

# Opcode VALUES (= byte >> 1) for instructions whose operand is a relative
# signed offset that we must repatch when the script grows or shrinks.
# In SCI0, lofsa / lofss are relative (see script_disasm.configure_lofsa_relative).
OP_BT = 0x17
OP_BNT = 0x18
OP_JMP = 0x19
OP_CALL = 0x20
OP_LOFSA = 0x39
OP_LOFSS = 0x3a
RELATIVE_OPS = {OP_BT, OP_BNT, OP_JMP, OP_CALL, OP_LOFSA, OP_LOFSS}


# ------------------------- low-level helpers -------------------------

def read_u16(buf, off):
    return int.from_bytes(buf[off:off + 2], 'little', signed=False)


def read_s_int(buf, off, size):
    return int.from_bytes(buf[off:off + size], 'little', signed=True)


def write_u16(buf, off, value):
    buf[off:off + 2] = (value & 0xFFFF).to_bytes(2, 'little', signed=False)


def write_s_int(buf, off, size, value):
    lo = -(1 << (size * 8 - 1))
    hi = (1 << (size * 8 - 1)) - 1
    if not (lo <= value <= hi):
        raise ValueError(
            f"signed value {value} doesn't fit in {size} bytes at offset 0x{off:04x}"
        )
    buf[off:off + size] = value.to_bytes(size, 'little', signed=True)


def shift(value, ins_off, delta):
    """Shift offset ``value`` past the modification at ``ins_off`` by ``delta``.

    delta > 0 (insert): values >= ins_off shift by +delta.
    delta < 0 (remove): values >= ins_off + |delta| shift by delta;
                        values inside [ins_off, ins_off + |delta|) are an error.
    """
    if value < ins_off:
        return value
    if delta < 0 and ins_off <= value < ins_off + (-delta):
        raise ValueError(
            f"offset 0x{value:04x} falls inside removed range "
            f"[0x{ins_off:04x}, 0x{ins_off + (-delta):04x})"
        )
    return value + delta


# ------------------------- section parsing -------------------------

def parse_sections(payload):
    """Return (sections, terminator_off).

    Each section is a dict with: type, start, length (incl. 4-byte header),
    data_start, data_end, data_length. ``terminator_off`` is the offset of
    the trailing ``0x00 0x00`` marker.
    """
    sections = []
    idx = 0
    while idx + 2 <= len(payload):
        sec_type = read_u16(payload, idx)
        if sec_type == 0:
            return sections, idx
        if idx + 4 > len(payload):
            raise ValueError(f"truncated section header at 0x{idx:04x}")
        sec_length = read_u16(payload, idx + 2)
        if sec_length < 4:
            raise ValueError(
                f"impossibly small section length {sec_length} at 0x{idx:04x}"
            )
        if idx + sec_length > len(payload):
            raise ValueError(
                f"section at 0x{idx:04x} (length {sec_length}) overruns payload"
            )
        sections.append({
            'type': sec_type,
            'start': idx,
            'length': sec_length,
            'data_start': idx + 4,
            'data_end': idx + sec_length,
            'data_length': sec_length - 4,
        })
        idx += sec_length
    raise ValueError("script ended without terminator (type=0)")


def find_containing_section(sections, offset):
    """Return the section whose data area [data_start, data_end] contains
    ``offset``. End-of-data is allowed (means "append at end of section").
    Offsets that fall inside a section's 4-byte header raise ValueError.
    Returns None if past the last section's data.
    """
    for s in sections:
        if s['data_start'] <= offset <= s['data_end']:
            return s
        if s['start'] <= offset < s['data_start']:
            raise ValueError(
                f"offset 0x{offset:04x} is inside the 4-byte header of section "
                f"at 0x{s['start']:04x} (type={s['type']}). Pick an offset within "
                f"[0x{s['data_start']:04x}, 0x{s['data_end']:04x}]."
            )
    return None


# ------------------ gatherers (use OLD coordinates) ------------------

def gather_relative_branches(payload, sections):
    out = []
    for s in sections:
        if s['type'] != SEC_CODE:
            continue
        idx = s['data_start']
        end = s['data_end']
        while idx < end:
            op_byte = payload[idx]
            ins_len = instruction_length(op_byte)
            if idx + ins_len > end:
                raise ValueError(
                    f"truncated instruction in CODE section at 0x{idx:04x}"
                )
            op_val = op_byte >> 1
            if op_val in RELATIVE_OPS:
                if op_val == OP_CALL:
                    rel_size = ins_len - 2  # last byte is the frame size
                else:
                    rel_size = ins_len - 1
                rel_loc = idx + 1
                rel_val = read_s_int(payload, rel_loc, rel_size)
                target = idx + ins_len + rel_val
                out.append({
                    'src': idx,
                    'ins_len': ins_len,
                    'rel_loc': rel_loc,
                    'rel_size': rel_size,
                    'target': target,
                })
            idx += ins_len
    return out


def gather_relocation(payload, sections):
    """For each relocation entry: (entry_loc, ptr_loc, ptr_val).

    SCI0 layout: 2 bytes count, then count*2 bytes of pointer-locations.
    Some SCI1+ scripts add a 2-byte zero pad after the count -- we
    auto-detect by comparing the section data length against the two
    possible expected sizes.
    """
    out = []
    for s in sections:
        if s['type'] != SEC_RELOCATION:
            continue
        ds = s['data_start']
        num = read_u16(payload, ds)
        expected_no_pad = 2 + num * 2
        expected_pad = 4 + num * 2
        if s['data_length'] == expected_no_pad:
            idx = ds + 2  # SCI0
        elif s['data_length'] == expected_pad:
            idx = ds + 4  # SCI1+
        else:
            raise ValueError(
                f"relocation section at 0x{s['start']:04x} has unexpected size: "
                f"data_length={s['data_length']} but expected {expected_no_pad} "
                f"(SCI0) or {expected_pad} (SCI1+) for {num} pointers"
            )
        for i in range(num):
            entry_loc = idx
            ptr_loc = read_u16(payload, entry_loc)
            if ptr_loc + 2 > len(payload):
                raise ValueError(
                    f"relocation entry #{i} at 0x{entry_loc:04x} -> 0x{ptr_loc:04x} "
                    f"is out of bounds"
                )
            ptr_val = read_u16(payload, ptr_loc)
            out.append({
                'entry_loc': entry_loc,
                'ptr_loc': ptr_loc,
                'ptr_val': ptr_val,
            })
            idx += 2
    return out


def gather_exports(payload, sections):
    out = []
    for s in sections:
        if s['type'] != SEC_EXPORTS:
            continue
        ds = s['data_start']
        num = read_u16(payload, ds)
        idx = ds + 2
        for _ in range(num):
            entry_loc = idx
            val = read_u16(payload, entry_loc)
            out.append({'entry_loc': entry_loc, 'value': val})
            idx += 2
    return out


def gather_object_func_offsets(payload, sections):
    """Each OBJECT/CLASS section starts (in its data area) with::

        [0..2)  SCRIPT_OBJECT_MAGIC_NUMBER (0x1234)
        [2..4)  zero
        [4..6)  func_selector_offset (call it F)
        ...
        [F+6..) the "num of methods" word and the method table

    F is the gap (in bytes) between the func_selector_offset field itself
    and the num_methods word. So num_methods lives at data_start + F + 6.
    F changes only if bytes are added/removed *between* data_start and the
    num_methods position.
    """
    out = []
    for s in sections:
        if s['type'] not in (SEC_OBJECT, SEC_CLASS):
            continue
        ds = s['data_start']
        if ds + 6 > len(payload):
            continue
        if read_u16(payload, ds) != SCRIPT_OBJECT_MAGIC_NUMBER:
            continue
        fso_loc = ds + 4
        fso_val = read_u16(payload, fso_loc)
        num_methods_loc = ds + fso_val + 6
        out.append({
            'section': s,
            'fso_loc': fso_loc,
            'fso_val': fso_val,
            'num_methods_loc': num_methods_loc,
        })
    return out


# ------------------------- main patching -------------------------

def apply_patch(payload_in, action, offset, count):
    if action not in ('insert', 'remove'):
        raise ValueError(f"unknown action: {action!r}")
    if count <= 0:
        raise ValueError(f"count must be positive, got {count}")

    payload = bytes(payload_in)
    delta = count if action == 'insert' else -count

    if action == 'insert':
        if not (0 <= offset <= len(payload)):
            raise ValueError(
                f"insert offset 0x{offset:04x} out of range "
                f"(payload size 0x{len(payload):04x})"
            )
    else:
        if offset < 0 or offset + count > len(payload):
            raise ValueError(
                f"remove range [0x{offset:04x}, 0x{offset + count:04x}) "
                f"out of range (payload size 0x{len(payload):04x})"
            )

    sections, terminator_off = parse_sections(payload)
    target_section = find_containing_section(sections, offset)
    if target_section is None:
        raise ValueError(
            f"offset 0x{offset:04x} is not inside any section's data area "
            f"(sections end at 0x{terminator_off:04x})"
        )

    rel_branches = gather_relative_branches(payload, sections)
    relocs = gather_relocation(payload, sections)
    exports = gather_exports(payload, sections)
    obj_funcs = gather_object_func_offsets(payload, sections)

    if action == 'insert':
        new_payload = bytearray(
            payload[:offset] + b'\x00' * count + payload[offset:]
        )
    else:
        new_payload = bytearray(payload[:offset] + payload[offset + count:])

    # 1) Section length field (only the containing section grows/shrinks).
    new_length = target_section['length'] + delta
    if new_length < 4:
        raise ValueError(
            f"resulting section length {new_length} would be < 4 (corrupting the section)"
        )
    if new_length % 2 != 0:
        print(
            f"WARNING: section at 0x{target_section['start']:04x} (type {target_section['type']}) "
            f"has odd length {new_length} after patching; SCI0 conventions expect even lengths.",
            file=sys.stderr,
        )
    # The length field is at section.start + 2. Insertion is INSIDE this
    # section's data, so section.start (and thus the length field's location)
    # is before the modification and stays put.
    write_u16(new_payload, target_section['start'] + 2, new_length)

    # 2) Relocation entries.
    for r in relocs:
        new_entry_loc = shift(r['entry_loc'], offset, delta)
        new_ptr_loc = shift(r['ptr_loc'], offset, delta)
        new_ptr_val = shift(r['ptr_val'], offset, delta)
        write_u16(new_payload, new_entry_loc, new_ptr_loc)
        write_u16(new_payload, new_ptr_loc, new_ptr_val)

    # 3) Exports (skip null entries; they're "no export").
    for e in exports:
        new_entry_loc = shift(e['entry_loc'], offset, delta)
        new_val = e['value']
        if new_val != 0:
            new_val = shift(new_val, offset, delta)
        write_u16(new_payload, new_entry_loc, new_val)

    # 4) OBJECT/CLASS func_selector_offset (only when the modification falls
    #    inside the object's "header area" before num_methods).
    for o in obj_funcs:
        sec = o['section']
        if not (sec['data_start'] <= offset <= sec['data_end']):
            continue
        new_fso_loc = shift(o['fso_loc'], offset, delta)
        if offset < o['num_methods_loc']:
            new_fso_val = o['fso_val'] + delta
            if new_fso_val < 0 or new_fso_val > 0xFFFF:
                raise ValueError(
                    f"func_selector_offset overflow at section 0x{sec['start']:04x}"
                )
            write_u16(new_payload, new_fso_loc, new_fso_val)
        # else: modification is after the func_selectors, fso doesn't change

    # 5) Relative branches & lofsa / lofss in CODE.
    for p in rel_branches:
        new_src = shift(p['src'], offset, delta)
        new_target = shift(p['target'], offset, delta)
        new_rel_loc = new_src + 1
        new_rel = new_target - (new_src + p['ins_len'])
        write_s_int(new_payload, new_rel_loc, p['rel_size'], new_rel)

    stats = {
        'sections': len(sections),
        'relative_branches_patched': len(rel_branches),
        'relocation_entries_patched': len(relocs),
        'export_entries_patched': len(exports),
        'object_sections_scanned': len(obj_funcs),
        'target_section_type': target_section['type'],
        'target_section_start': target_section['start'],
        'old_payload_size': len(payload),
        'new_payload_size': len(new_payload),
    }
    return bytes(new_payload), stats


# ------------------------- CLI -------------------------

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=(
            "SCI0 script byte patcher: insert/remove bytes in a script.NNN "
            "file and fix all jumps, relocations, exports and section lengths."
        ),
    )
    parser.add_argument('script', help='path to script.NNN file (SCI0)')
    parser.add_argument(
        'offset',
        help=(
            'offset to patch at (decimal or 0x...). '
            'Interpreted as a RAW FILE offset by default (the 2-byte 0x82 0x00 '
            'prefix, if present, is subtracted automatically). '
            'Use --payload-offset to pass an already-prefix-stripped offset.'
        ),
    )
    parser.add_argument(
        'count', type=lambda x: int(x, 0),
        help='number of bytes to insert (action=insert) or remove (action=remove)',
    )
    parser.add_argument(
        '--action', choices=['insert', 'remove'], default='insert',
        help='action to perform',
    )
    parser.add_argument(
        '--payload-offset', action='store_true',
        help=(
            'treat OFFSET as a payload offset (already excludes the leading '
            '2-byte 0x82 0x00 prefix). Default is to treat OFFSET as a raw file offset.'
        ),
    )
    parser.add_argument('--out', help='output path (default: overwrite the input file)')
    parser.add_argument(
        '--backup', action='store_true',
        help='create a .bak (or .bak1, .bak2, ...) before overwriting',
    )
    args = parser.parse_args()

    script_path = Path(args.script)
    raw = script_path.read_bytes()

    has_header = raw[:2] == SIERRA_SCRIPT_HEADER
    payload = raw[2:] if has_header else raw

    offset = int(args.offset, 0)
    if not args.payload_offset and has_header:
        # Default: OFFSET is a raw file offset; subtract the 2-byte 0x82 0x00 prefix
        # to land on the equivalent payload offset.
        offset -= 2
    if offset < 0:
        raise SystemExit(
            "offset resolves to a negative payload position "
            "(did you mean to pass --payload-offset?)"
        )

    new_payload, stats = apply_patch(payload, args.action, offset, args.count)

    out_bytes = (SIERRA_SCRIPT_HEADER if has_header else b'') + new_payload
    out_path = Path(args.out) if args.out else script_path

    backup_path = None
    if args.backup and out_path.exists():
        backup_path = out_path.with_suffix(out_path.suffix + '.bak')
        i = 1
        while backup_path.exists():
            backup_path = out_path.with_suffix(out_path.suffix + f'.bak{i}')
            i += 1
        backup_path.write_bytes(out_path.read_bytes())

    out_path.write_bytes(out_bytes)

    if backup_path is not None:
        print(f'Backup: {backup_path}')
    print(f'Wrote:  {out_path}')
    print(
        f"{'Inserted' if args.action == 'insert' else 'Removed'} "
        f"{args.count} byte(s) at payload offset 0x{offset:04x}"
    )
    print('Stats:', stats)


if __name__ == '__main__':
    main()
