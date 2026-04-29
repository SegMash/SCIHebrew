import argparse
from pathlib import Path

from asm_lib.misc import SIERRA_SCRIPT_HEADER, SIERRA_HEAP_HEADER, SCRIPT_OBJECT_MAGIC_NUMBER
from asm_lib.opcodes import SciOpcodes, instruction_length


def read_u16(buf: bytearray, off: int) -> int:
    return int.from_bytes(buf[off:off + 2], byteorder='little', signed=False)


def write_u16(buf: bytearray, off: int, value: int) -> None:
    buf[off:off + 2] = int(value & 0xFFFF).to_bytes(2, byteorder='little', signed=False)


def read_sint(buf: bytearray, off: int, size: int) -> int:
    return int.from_bytes(buf[off:off + size], byteorder='little', signed=True)


def write_sint(buf: bytearray, off: int, size: int, value: int) -> None:
    min_v = -(1 << (size * 8 - 1))
    max_v = (1 << (size * 8 - 1)) - 1
    if not (min_v <= value <= max_v):
        raise ValueError(f"relative offset {value} does not fit in {size} bytes")
    buf[off:off + size] = int(value).to_bytes(size, byteorder='little', signed=True)


def strip_prefix(data: bytes, expected: bytes) -> bytes:
    if data[:2] == expected:
        return data[2:]
    return data


def shift_offset(old_off: int, insert_off: int) -> int:
    return old_off + 1 if old_off >= insert_off else old_off


def parse_sci2_objects(hep: bytearray):
    fixups_offset = read_u16(hep, 0)
    n_vars = read_u16(hep, 2)
    true_start = 6 + n_vars * 2
    legacy_start = n_vars * 2 + 4

    if true_start + 2 <= len(hep) and read_u16(hep, true_start) == SCRIPT_OBJECT_MAGIC_NUMBER:
        obj_pos = true_start
    elif legacy_start + 2 <= len(hep) and read_u16(hep, legacy_start) == SCRIPT_OBJECT_MAGIC_NUMBER:
        obj_pos = legacy_start
    else:
        # No recognizable object list start.
        return []

    objects = []
    while obj_pos + 8 <= fixups_offset and read_u16(hep, obj_pos) == SCRIPT_OBJECT_MAGIC_NUMBER:
        words = read_u16(hep, obj_pos + 2)
        if words == 0:
            break
        size = words * 2
        method_offset = read_u16(hep, obj_pos + 6)
        objects.append({
            'start': obj_pos,
            'size': size,
            'method_offset': method_offset,
        })
        obj_pos += size
    return objects


def gather_method_pointer_locations(scr: bytearray, objects):
    locs = []
    pointers = []
    for obj in objects:
        moff = obj['method_offset']
        if moff == 0 or moff + 2 > len(scr):
            continue
        num_methods = read_u16(scr, moff)
        table_end = moff + 2 + num_methods * 4
        if table_end > len(scr):
            continue
        for i in range(num_methods):
            ptr_loc = moff + 2 + i * 4 + 2
            locs.append(ptr_loc)
            pointers.append(read_u16(scr, ptr_loc))
    return locs, pointers


def gather_dispatch_locations(scr: bytearray):
    count = read_u16(scr, 6)
    locs = []
    vals = []
    for i in range(count):
        loc = 8 + i * 2
        if loc + 2 > len(scr):
            break
        locs.append(loc)
        vals.append(read_u16(scr, loc))
    return locs, vals


def gather_relative_patches(scr: bytearray, code_start: int, code_end: int):
    patches = []
    off = code_start
    while off < code_end:
        op_byte = scr[off]
        try:
            opcode = SciOpcodes(op_byte >> 1)
        except ValueError as e:
            raise ValueError(f"unknown opcode at 0x{off:04x}: 0x{op_byte:02x}") from e

        ins_len = instruction_length(op_byte)
        if off + ins_len > code_end:
            raise ValueError(f"truncated instruction at 0x{off:04x}")

        if opcode in [SciOpcodes.op_bt, SciOpcodes.op_bnt, SciOpcodes.op_jmp]:
            rel_size = ins_len - 1
            rel_loc = off + 1
            rel_val = read_sint(scr, rel_loc, rel_size)
            target = off + ins_len + rel_val
            patches.append((off, ins_len, rel_loc, rel_size, target))
        elif opcode == SciOpcodes.op_call:
            rel_size = ins_len - 2
            rel_loc = off + 1
            rel_val = read_sint(scr, rel_loc, rel_size)
            target = off + ins_len + rel_val
            patches.append((off, ins_len, rel_loc, rel_size, target))

        off += ins_len

    return patches


def patch_scr_payload(scr: bytes, hep: bytes, insert_off: int, insert_byte: int):
    old = bytearray(scr)
    if not (0 <= insert_off <= len(old)):
        raise ValueError(f"insert offset out of range: {insert_off} (len={len(old)})")

    old_fixups_off = read_u16(old, 0)
    if old_fixups_off + 2 > len(old):
        raise ValueError("invalid SCR fixups offset")

    objects = parse_sci2_objects(bytearray(hep))
    method_ptr_locs, method_ptr_vals = gather_method_pointer_locations(old, objects)
    if not method_ptr_vals:
        raise ValueError("could not locate method pointers from HEP/SCR")

    code_start = min(v for v in method_ptr_vals if v != 0)
    code_end = old_fixups_off
    if not (0 <= code_start <= code_end <= len(old)):
        raise ValueError("invalid code range derived from SCR")

    dispatch_locs, dispatch_vals = gather_dispatch_locations(old)

    rel_patches = gather_relative_patches(old, code_start, code_end)

    new = bytearray(old[:insert_off] + bytes([insert_byte]) + old[insert_off:])

    # Header fixups offset shifts if insertion was before table.
    new_fixups_off = old_fixups_off + (1 if insert_off <= old_fixups_off else 0)
    write_u16(new, 0, new_fixups_off)

    # Method table code pointers are absolute SCR payload offsets.
    for loc, old_val in zip(method_ptr_locs, method_ptr_vals):
        new_loc = shift_offset(loc, insert_off)
        new_val = old_val + (1 if old_val >= insert_off else 0)
        write_u16(new, new_loc, new_val)

    # Dispatch entries may be code pointers; patch only entries in old code range.
    for loc, old_val in zip(dispatch_locs, dispatch_vals):
        if code_start <= old_val < old_fixups_off:
            new_loc = shift_offset(loc, insert_off)
            new_val = old_val + (1 if old_val >= insert_off else 0)
            write_u16(new, new_loc, new_val)

    # SCR fixup entries point to locations in SCR that contain relocatable pointers.
    fix_count = read_u16(old, old_fixups_off)
    for i in range(fix_count):
        old_entry_loc = old_fixups_off + 2 + i * 2
        old_site = read_u16(old, old_entry_loc)
        new_entry_loc = new_fixups_off + 2 + i * 2
        new_site = old_site + (1 if old_site >= insert_off else 0)
        write_u16(new, new_entry_loc, new_site)

    # Relative branch/call operands are re-based from shifted source/target offsets.
    for old_off, ins_len, rel_loc, rel_size, old_target in rel_patches:
        new_off = shift_offset(old_off, insert_off)
        new_rel_loc = new_off + 1
        new_target = old_target + (1 if old_target >= insert_off else 0)
        new_rel = new_target - (new_off + ins_len)
        write_sint(new, new_rel_loc, rel_size, new_rel)

    return bytes(new), {
        'code_start': code_start,
        'code_end': code_end,
        'method_ptrs': len(method_ptr_locs),
        'dispatch_entries': len(dispatch_locs),
        'relative_ops': len(rel_patches),
        'scr_fixups': fix_count,
        'old_fixups_off': old_fixups_off,
        'new_fixups_off': new_fixups_off,
    }


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Insert one byte into SCI2 SCR payload and patch pointers/relative offsets.',
    )
    parser.add_argument('scr', help='path to .scr file')
    parser.add_argument('hep', help='path to matching .hep file')
    parser.add_argument('offset', help='payload offset to insert at (decimal or 0x...)')
    parser.add_argument('--byte', default='0x00', help='byte value to insert (decimal or 0x...)')
    parser.add_argument('--raw-file-offset', action='store_true',
                        help='treat offset as file offset including 2-byte 0x82 00 prefix')
    parser.add_argument('--in-place', action='store_true',
                        help='deprecated: kept for compatibility; patcher now writes in-place by default')
    parser.add_argument('--out', help='output SCR path (default: overwrite input SCR)')
    parser.add_argument('--backup', action='store_true',
                        help='create a backup of the destination file before writing (.bak, .bak1, ...)')
    args = parser.parse_args()

    scr_path = Path(args.scr)
    hep_path = Path(args.hep)

    scr_raw = scr_path.read_bytes()
    hep_raw = hep_path.read_bytes()
    scr_payload = strip_prefix(scr_raw, SIERRA_SCRIPT_HEADER)
    hep_payload = strip_prefix(hep_raw, SIERRA_HEAP_HEADER)

    offset = int(args.offset, 0)
    if args.raw_file_offset:
        offset -= 2
    if offset < 0:
        raise ValueError('offset resolves to negative payload position')

    insert_byte = int(args.byte, 0)
    if not (0 <= insert_byte <= 0xFF):
        raise ValueError('--byte must be in range 0..255')

    patched_payload, stats = patch_scr_payload(scr_payload, hep_payload, offset, insert_byte)

    if scr_raw[:2] == SIERRA_SCRIPT_HEADER:
        out_bytes = SIERRA_SCRIPT_HEADER + patched_payload
    else:
        out_bytes = patched_payload

    if args.out:
        out_path = Path(args.out)
    else:
        out_path = scr_path

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
    print(f'Wrote: {out_path}')
    print(f"Inserted byte 0x{insert_byte:02x} at payload offset 0x{offset:04x}")
    print('Stats:', stats)


if __name__ == '__main__':
    main()
