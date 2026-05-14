# TODO remove ugly {'val': 'DText', 'id': 'string_1'} selectors

# TODO other generations:
# said/synonym
# .hep

# https://wiki.scummvm.org/index.php?title=SCI/Specifications/SCI_virtual_machine/Introduction#Script_resources

# -g SCI0 C:\Zvika\ScummVM-dev\HebrewAdventure\sq1vga\PATCHES\103.scr
# -g SCI0 C:\Zvika\Games\Space_Quest_I_-_The_Sarien_Encounter_VGA_1991.dev\SQ1VGA.patches\103.scr
# "C:\Zvika\Games\heroquest1vga\qfg1vga-gog.Z\PATCHES\999.scr"
# -g SCI2 "C:\Zvika\Games\GK Hebrew\Gabriel Knight [GOG].patches\64962.scr"
# "C:\Zvika\ScummVM-dev\HebrewAdventure\sq3\PATCHES\script.001"

import argparse
import os

import asm_lib.opcodes as opcodes_mod
from asm_lib.opcodes import SciOpcodes, instruction_length
from asm_lib.instruction import Instruction
from asm_lib.misc import *
from asm_lib.sci_section import SciSection, SectionKind


def get_pointers(objects):
    pointers_l = [o.pointers for o in objects if o.kind == SectionKind.RELOCATION]
    if pointers_l:
        assert len(pointers_l) == 1  # guessing, if it fails - adapt following code
        pointers = pointers_l[0]
        return pointers
    else:
        return []


def configure_lofsa_relative(script_file):
    suffix = Path(script_file).suffix.lower()
    # SCI0 resources are commonly named script.000/script.001/... and use relative LOFSA/LOFSS.
    value = suffix.startswith('.') and suffix[1:].isdigit()
    global CONFIG_LOFSA_RELATIVE
    CONFIG_LOFSA_RELATIVE = value
    opcodes_mod.CONFIG_LOFSA_RELATIVE = value


def load_vocab_groups(script_file):
    vocab_candidates = [
        Path(script_file).parent / 'vocab.900',
        Path(script_file).parent / 'vocab.000',
    ]

    vocab_path = next((p for p in vocab_candidates if p.exists()), None)
    if vocab_path is None:
        return {}

    data = vocab_path.read_bytes()
    if not data.startswith(SIERRA_VOCAB_HEADER):
        return {}
    data = data[2:]

    pointer_bytes = 255 * 2 if vocab_path.suffix.lower() == '.900' else 26 * 2
    if len(data) < pointer_bytes:
        return {}

    idx = pointer_bytes
    current_word = ""
    groups = {}
    while idx < len(data):
        same_letters = data[idx]
        idx += 1
        current_word = current_word[:same_letters]

        word_bytes = []
        if vocab_path.suffix.lower() == '.900':
            while idx < len(data) and data[idx] != 0:
                word_bytes.append(data[idx])
                idx += 1
            if idx >= len(data):
                break
            idx += 1
        else:
            found_end = False
            while idx < len(data):
                val = data[idx]
                idx += 1
                if val >= 0x80:
                    word_bytes.append(val - 0x80)
                    found_end = True
                    break
                if val < 0x20:
                    continue
                word_bytes.append(val)
            if not found_end:
                break

        try:
            current_word += bytes(word_bytes).decode(ENCODING_OUTPUT)
        except UnicodeDecodeError:
            current_word += bytes(word_bytes).decode('latin1')

        if idx + 2 >= len(data):
            break

        byte1 = data[idx]
        byte2 = data[idx + 1]
        byte3 = data[idx + 2]
        idx += 3

        group = ((byte2 & 0b1111) << 8) + byte3
        groups.setdefault(group, [])
        if current_word not in groups[group]:
            groups[group].append(current_word)

    return groups


def format_vocab_group(group, vocab_groups):
    words = vocab_groups.get(group, [])
    if words:
        return f'0x{group:04x}:{"|".join(words[:2])}'
    return f'0x{group:04x}'


############################################################################################################
#################################         FIRST   PASS         #############################################
############################################################################################################

def strings_first(obj):
    strings = bytes(obj.data).split(b'\0')
    offset = obj.obj_offset
    obj.strings = []
    for s in strings:
        str = escape_string(s.decode(ENCODING_OUTPUT))
        obj.strings.append({'offset': offset, 'str': str, 'id': strings_first.id, 'usages': [],
                            'special': False})
        offset += len(s) + 1
        strings_first.id += 1


def code_first(obj):
    code = obj.data
    obj.instructions = []
    idx = 0
    while idx < len(code):
        opcode = SciOpcodes(code[idx] >> 1)
        num_of_operands = instruction_length(code[idx]) - 1
        operands = code[idx + 1:idx + 1 + num_of_operands]
        obj.instructions.append(Instruction(opcode, operands, obj.obj_offset + idx, kernels=kernels))
        idx += instruction_length(code[idx])


def exports_first(obj):
    obj.exports = []
    idx = 0
    num_of_exports = read_le(obj.data, idx)
    idx += 2
    for i in range(num_of_exports):
        length = 4 if CONFIG_WIDE_EXPORTS else 2
        obj.exports.append(int.from_bytes(obj.data[idx:idx + length], byteorder='little', signed=False))
        idx += length


def object_first(obj):
    idx = 0
    assert read_le(obj.data, idx) == SCRIPT_OBJECT_MAGIC_NUMBER
    idx += 2
    # I'm not 100% sure about "local variable offset" being always 0; if it turns out to be wrong - needs further investigation
    assert read_le(obj.data, idx) == 0
    idx += 2
    obj.func_selector_offset = read_le(obj.data, idx)  # not important, mainly for testing stability
    idx += 2

    num_of_var_selectors = read_le(obj.data, idx)
    idx += 2
    obj.var_selector_vals = []
    for i in range(num_of_var_selectors):
        obj.var_selector_vals.append(read_le(obj.data, idx))
        idx += 2

    obj.species = obj.var_selector_vals[0]
    obj.superClass = obj.var_selector_vals[1]
    obj.name = obj.var_selector_vals[3]

    if obj.kind == SectionKind.CLASS:
        # TODO translate selector IDs to names, from vocab.997
        obj.var_selector_ids = []
        for i in range(num_of_var_selectors):
            obj.var_selector_ids.append(read_le(obj.data, idx))
            idx += 2

        obj.var_selectors = {}
        for i in range(num_of_var_selectors):
            obj.var_selectors[obj.var_selector_ids[i]] = obj.var_selector_vals[i]

    assert obj.func_selector_offset + 6 == idx
    obj.num_of_func_selectors = read_le(obj.data, idx)
    idx += 2

    func_selectors_ids = []
    for i in range(obj.num_of_func_selectors):
        func_selectors_ids.append(read_le(obj.data, idx))
        idx += 2

    assert read_le(obj.data, idx) == 0
    idx += 2

    func_selectors_pointers = []
    for i in range(obj.num_of_func_selectors):
        func_selectors_pointers.append(read_le(obj.data, idx))
        idx += 2

    obj.func_selectors = []
    for i in range(obj.num_of_func_selectors):
        obj.func_selectors.append({'id': func_selectors_ids[i], 'pointer': func_selectors_pointers[i]})

    assert idx == len(obj.data)


def relocation_first(obj):
    idx = 0
    num_of_pointers = read_le(obj.data, idx)
    idx += 2
    
    # Check if there are padding zeros (SCI1+ format) or not (SCI0 format)
    # SCI1+ has two extra zero bytes here, SCI0 doesn't
    if idx + 2 <= len(obj.data) and read_le(obj.data, idx) == 0:
        idx += 2  # Skip padding zeros (SCI1+ format)
    
    obj.pointers = {}
    for i in range(num_of_pointers):
        obj.pointers[(read_le(obj.data, idx))] = False
        idx += 2
    assert idx == len(obj.data)


def preload_first(obj):
    # this object is just a flag - contains no data; only its existence is of significance - but not for our needs
    assert obj.data == b''


def local_vars_first(obj):
    obj.local_vars = []
    idx = 0
    while True:
        try:
            obj.local_vars.append(read_le(obj.data, idx))
        except IndexError:
            break
        idx += 2


def said_first(obj, vocab_groups):
    op_names = {
        0xF0: 'F0',
        0xF1: 'F1',
        0xF2: 'F2',
        0xF3: 'F3',
        0xF4: 'F4',
        0xF5: 'F5',
        0xF6: 'F6',
        0xF7: 'F7',
        0xF8: 'F8',
        0xF9: 'F9',
    }
    standalone_ops = {0xF5, 0xF6, 0xF7}
    ops_with_group = {0xF0, 0xF1, 0xF2, 0xF3, 0xF4, 0xF8}

    obj.said_entries = {}
    idx = 0
    entry_id = 0
    while idx < len(obj.data):
        start_idx = idx
        start_offset = obj.obj_offset + idx
        parts = []

        while idx < len(obj.data):
            token = obj.data[idx]
            if token == 0xFF:
                idx += 1
                break

            if token >= 0xF0:
                name = op_names.get(token, f'F{token:02X}')
                if token in standalone_ops:
                    parts.append(name)
                    idx += 1
                elif token in ops_with_group and idx + 2 < len(obj.data):
                    group = (obj.data[idx + 1] << 8) + obj.data[idx + 2]
                    parts.append(f'{name}({format_vocab_group(group, vocab_groups)})')
                    idx += 3
                else:
                    parts.append(name)
                    idx += 1
            elif idx + 1 < len(obj.data):
                group = (obj.data[idx] << 8) + obj.data[idx + 1]
                parts.append(format_vocab_group(group, vocab_groups))
                idx += 2
            else:
                parts.append(f'0x{obj.data[idx]:02x}')
                idx += 1

        if parts:
            text = ' '.join(parts)
            obj.said_entries[start_offset] = {
                'id': f'said_{entry_id}',
                'text': text,
                'offset': start_offset,
                'local_offset': start_idx,
            }
            entry_id += 1


############################################################################################################
#################################         SECOND/THIRD  PASS         #######################################
############################################################################################################


# used also for third pass
def object_second(obj, objects, third_pass):
    # TODO work will all files, have all classes, and then match selectors to ids. now it's very partial and therefore pointless
    pointers = get_pointers(objects)
    strings = sum([o.strings for o in objects if o.kind == SectionKind.STRINGS], [])
    for i, selector in enumerate(obj.var_selector_vals):
        matches = [s for s in strings if s['offset'] == selector]
        pointer = obj.obj_offset + MAGIC_8 + i * 2
        if pointer in pointers and not pointers[pointer]:
            if matches:
                assert len(matches) == 1
                matches[0]['usages'].append({'obj': obj, 'selector_i': i})
                if i <= 3:
                    matches[0]['special'] = True
                obj.var_selector_vals[i] = {'val': matches[0]['str'], 'id': get_string_id(matches[0])}
                pointers[pointer] = {'obj': obj, 'selector_i': i, 'val': obj.var_selector_vals[i]}
            elif isinstance(selector, int) and third_pass:
                new_string = string_match_not_on_start(objects, strings, pointers, selector, pointer,
                                                       {'obj': obj, 'selector_i': i})
                if new_string:
                    if i <= 3:
                        new_string['special'] = True
                    obj.var_selector_vals[i] = {'val': new_string['str'], 'id': get_string_id(new_string)}
                    pointers[pointer] = {'obj': obj, 'selector_i': i, 'val': obj.var_selector_vals[i]}

    # update strings
    obj.species = obj.var_selector_vals[0]
    obj.superClass = obj.var_selector_vals[1]
    try:
        obj.name = obj.var_selector_vals[3]['val']
    except TypeError:
        if third_pass:
            obj.name = f"class_{obj.name}"
            print(f"Warning: unnamed object ({obj})")
    if third_pass:
        if obj.unique_extension:
            obj.name += obj.unique_extension

    if third_pass:
        instructions = sum([o.instructions for o in objects if o.kind == SectionKind.CODE], [])
        for selector in obj.func_selectors:
            # TODO replace selector['id'] with name from selector table (vocab.997)
            matches = [i for i in instructions if i.offset == selector['pointer']]
            # maybe the assertion is not accurate (in case there's a 'jmp' or 'bnt', etc. for the start of function)
            # however, it passed fine through all of SQ1VGA
            assert len(matches) == 1

            uniqify_name(obj, objects)
            assert matches[0].label is None
            matches[0].label = f'{obj.sanitize(str(obj.name))}::{selector["id"]}'
            selector['label'] = matches[0].label


def string_match_not_on_start(objects, strings, pointers, str_offset, pointer, usage_dict):
    if strings[0]['offset'] <= str_offset <= strings[-1]['offset']:
        match = [s for s in strings if s['offset'] <= str_offset][-1]
        assert str_offset >= match['offset']
        assert str_offset <= match['offset'] + len(match['str'])
        delta = str_offset - match['offset']
        strings_obj = [o for o in objects if o.kind == SectionKind.STRINGS][0]
        new_string = {'offset': str_offset,
                      'str': match['str'][delta:],
                      'id': f"{match['id']}_offset_{delta}",
                      'usages': [usage_dict],  # {'obj': obj, 'instr': instr}
                      'special': False,
                      }
        strings_obj.strings.append(new_string)
        strings_obj.strings = sorted(strings_obj.strings, key=lambda s: s['offset'])
        pointers[pointer] = usage_dict
        return new_string
    else:
        return None


def uniqify_name(instance, objects):
    matches = [o for o in objects if
               o.kind in [SectionKind.OBJECT, SectionKind.CLASS] and o.name == instance.name]
    assert matches
    if len(matches) > 1:
        instance.unique_extension += "_u"
        instance.name = f"{instance.name}_u"


def code_third(obj, objects):
    pointers = get_pointers(objects)
    strings = sum([o.strings for o in objects if o.kind == SectionKind.STRINGS], [])
    said_entries = {}
    for said_obj in [o for o in objects if o.kind == SectionKind.SAID]:
        for offset, entry in getattr(said_obj, 'said_entries', {}).items():
            said_entries[offset] = entry
    all_instructions = sum([o.instructions for o in objects if o.kind == SectionKind.CODE], [])

    for i, instr in enumerate(obj.instructions):
        if instr.opcode.is_relative():
            try:
                offset = instr.operands[0]
            except TypeError:
                offset = instr.operands
            matches = [ins for ins in all_instructions if ins.offset == offset]
            if matches:
                assert len(matches) == 1
                matches[0].set_label()
                if type(instr.operands) is list:
                    instr.operands[0] = matches[0].label
                else:
                    instr.operands = matches[0].label

    for i, instr in enumerate(obj.instructions):
        if instr.offset + 1 in pointers:
            matches = [s for s in strings if s['offset'] == instr.operands]
            if matches:
                assert len(matches) == 1
                pointers[instr.offset + 1] = {'obj': obj, 'instr': instr}
                matches[0]['usages'].append({'obj': obj, 'instr': instr})
                instr.operands = get_string_id(matches[0])
                instr.str = matches[0]['str']
            else:
                new_string = string_match_not_on_start(objects, strings, pointers, instr.operands, instr.offset + 1,
                                                       {'obj': obj, 'instr': instr})
                if new_string is not None:
                    instr.operands = get_string_id(new_string)
                    instr.str = new_string['str']

    for i, instr in enumerate(obj.instructions):
        matches = [o for o in objects if
                   o.kind in [SectionKind.OBJECT, SectionKind.CLASS] and instr.operands == o.obj_offset + MAGIC_8]
        if matches:
            assert len(matches) == 1
            uniqify_name(matches[0], objects)
            if instr.offset + 1 in pointers:
                pointers[instr.offset + 1] = {'obj': obj, 'instr': instr}
                matches[0].usages.append({'obj': obj, 'instr': instr})
                instr.operands = matches[0].get_id()
                instr.obj = matches[0]

    for instr in obj.instructions:
        if instr.opcode in [SciOpcodes.op_lofsa, SciOpcodes.op_lofss] and isinstance(instr.operands, int):
            if instr.operands in said_entries:
                said = said_entries[instr.operands]
                instr.operands = said['id']
                instr.str = said['text']

    for i in range(1, len(obj.instructions)):
        instr = obj.instructions[i]
        prev_instr = obj.instructions[i - 1]
        if instr.opcode == SciOpcodes.op_callk and isinstance(instr.operands, str) and instr.operands.startswith('Said,'):
            if prev_instr.opcode in [SciOpcodes.op_lofsa, SciOpcodes.op_lofss] and prev_instr.str:
                instr.str = prev_instr.str


def local_vars_third(obj, objects):
    pointers = get_pointers(objects)
    strings = sum([o.strings for o in objects if o.kind == SectionKind.STRINGS], [])
    for i, var in enumerate(obj.local_vars):
        pointer = obj.obj_offset + i * 2
        if pointer in pointers:
            matches = [s for s in strings if s['offset'] == var]
            if matches:
                assert len(matches) == 1
                matches[0]['usages'].append({'obj': obj, 'var': var, 'i': i})
                obj.local_vars[i] = {'val': matches[0]['str'], 'id': get_string_id(matches[0])}
                pointers[pointer] = {'obj': obj, 'index': i, 'var': obj.local_vars[i]}
            # TODO do we need inaccuate string match for local vars?
            # else:
            #     new_string = string_match_not_on_start(objects, strings, pointers, instr.operands, instr.offset + 1,
            #                                            {'obj': obj, 'instr': instr})
            #     if new_string is not None:
            #         instr.operands = get_string_id(new_string)
            #         instr.str = new_string['str']

    # TODO do we need object matches for local vars?
    # for i, instr in enumerate(obj.instructions):
    #     matches = [o for o in objects if
    #                o.kind in [ObjectKind.OBJECT, ObjectKind.CLASS] and instr.operands == o.obj_offset + MAGIC_8]
    #     if matches:
    #         assert len(matches) == 1
    #         if instr.offset + 1 in pointers:
    #             pointers[instr.offset + 1] = True
    #             matches[0].usages.append({'obj': obj, 'instr': instr})
    #             instr.operands = matches[0].get_id()
    #             instr.obj = matches[0]


############################################################################################################
#################################         FOURTH PASS           ############################################
############################################################################################################

def strings_fourth(obj, objects):
    for s in obj.strings:
        if len(s['usages']) == 0 and s['str'] and \
                len([str(s1['id']) for s1 in obj.strings if str(s1['id']).startswith(str(s['id']) + "_offset_")]) == 0:
            print('Warning, unused string: ', end='')
            print(s)


def exports_fourth(obj, objects):
    for i, exp in enumerate(obj.exports):
        if exp != 0:
            instructions = sum([o.instructions for o in objects if o.kind == SectionKind.CODE], [])
            matches = [inst for inst in instructions if inst.offset == exp]
            if matches:
                if len(matches) >= 1:
                    matches[0].exported = True
                    matches[0].set_label()
                    obj.exports[i] = matches[0]
                    if len(matches) > 1:
                        print(f"Warning: export {hex(exp)} has {len(matches)} instruction matches")
            else:
                matches = [o for o in objects if
                           o.kind in [SectionKind.OBJECT, SectionKind.CLASS] and exp == o.obj_offset + MAGIC_8]
                if len(matches) >= 1:
                    matches[0].exported = True
                    obj.exports[i] = matches[0]
                    if len(matches) > 1:
                        print(f"Warning: export {hex(exp)} has {len(matches)} object matches")
                else:
                    print(f"Warning: export {hex(exp)} not found in instructions or objects")


def relocation_fourth(obj, objects):
    unused = 0
    for p, used in obj.pointers.items():
        try:
            if not used:
                unused += 1
        except TypeError:
            # 'used' might be a dict or False, handle both
            if used is False:
                unused += 1
    if unused > 0:
        print(f"Warning: {unused} unused pointers out of {len(obj.pointers)}")


def code_fourth(obj, objects):
    for i, instr in enumerate(obj.instructions):
        if instr.opcode in [SciOpcodes.op_lofsa, SciOpcodes.op_lofss]:
            if not isinstance(instr.operands, str):
                print(f"Error: illegal param at: {instr.str_dump()}")
                instr.legal = False


############################################################################################################
#################################         GENERAL              #############################################
############################################################################################################


def split_objects(orig_script_file):
    in_script = Path(orig_script_file).read_bytes()
    assert in_script[:2] == SIERRA_SCRIPT_HEADER
    in_script = in_script[2:]

    # divide script file to objects
    objects = []
    idx = 0
    while True:
        obj_type = read_le(in_script, idx)
        if obj_type == 0:
            break
        obj_length = read_le(in_script, idx + 2)
        assert obj_length > 0
        assert obj_length % 2 == 0
        obj_data = in_script[idx + 4:idx + obj_length]
        objects.append(SciSection(obj_type, idx + 4, obj_length, obj_data))
        idx += obj_length

    if False:  # start of work on SCI2
        heap_file = os.path.splitext(orig_script_file)[0] + '.hep'
        heap = Path(heap_file).read_bytes()
        assert heap[:2] == SIERRA_HEAP_HEADER
        heap = heap[2:]

        in_script += heap

        endOfStringOffset = read_le(heap, 0)
        objectStartOffset = read_le(heap, 2) * 2 + 4

        assert endOfStringOffset <= len(heap)
        assert objectStartOffset <= len(heap)

        # divide script file to objects
        objects = []
        hep_idx = objectStartOffset
        scr_idx = 0
        while True:
            obj_type = read_le(heap, hep_idx)
            hep_idx += 2
            print("obj_type", hex(obj_type))
            if obj_type != SCRIPT_OBJECT_MAGIC_NUMBER:
                break
            offset = scr_idx - in_script[scr_idx] - 2  # TODO not good
            num_properties = read_le(heap, hep_idx)
            hep_idx += 2

            script_num = read_le(heap, hep_idx + 6)
            print(offset, num_properties, script_num)

            # obj_length = read_le(in_script, idx + 2)
            # assert obj_length > 0
            # obj_data = in_script[idx + 4:idx + obj_length]
            # obj = [obj_type, idx + 4, obj_length, obj_data]
            # objects.append(obj)
            # idx += obj_length

        print('heap', heap)

    return objects


def get_configs():
    return f""".CONFIG
WIDE_EXPORTS = {CONFIG_WIDE_EXPORTS}
LOFSA_RELATIVE = {CONFIG_LOFSA_RELATIVE}

"""


def disasm(orig_script_file):
    configure_lofsa_relative(orig_script_file)
    vocab_groups = load_vocab_groups(orig_script_file)
    objects = split_objects(orig_script_file)
    strings_first.id = 0

    # first pass
    new_objects = []
    for obj in objects:
        if obj.kind in [SectionKind.OBJECT, SectionKind.CLASS]:
            object_first(obj)
        elif obj.kind == SectionKind.CODE:
            code_first(obj)
        elif obj.kind == SectionKind.STRINGS:
            strings_first(obj)
        elif obj.kind == SectionKind.EXPORTS:
            exports_first(obj)
        elif obj.kind == SectionKind.RELOCATION:
            relocation_first(obj)
        elif obj.kind == SectionKind.PRELOAD_TEXT:
            preload_first(obj)
        elif obj.kind == SectionKind.LOCAL_VARS:
            local_vars_first(obj)
        elif obj.kind == SectionKind.SAID:
            said_first(obj, vocab_groups)
        elif obj.kind == SectionKind.SYNONYMS:
            # SYNONYMS not implemented yet
            pass
        else:
            raise NotImplementedError(f"Section kind {obj.kind} not implemented")
        new_objects.append(obj)
    objects = new_objects

    # second pass
    for obj in objects:
        if obj.kind in [SectionKind.OBJECT, SectionKind.CLASS]:
            object_second(obj, objects, third_pass=False)

    # third pass (calling again some second pass functions)
    for obj in objects:
        if obj.kind in [SectionKind.OBJECT, SectionKind.CLASS]:
            object_second(obj, objects, third_pass=True)
        elif obj.kind == SectionKind.CODE:
            code_third(obj, objects)
        elif obj.kind == SectionKind.LOCAL_VARS:
            local_vars_third(obj, objects)

    # fourth pass
    for obj in objects:
        if obj.kind == SectionKind.STRINGS:
            strings_fourth(obj, objects)
        elif obj.kind == SectionKind.EXPORTS:
            exports_fourth(obj, objects)
        elif obj.kind == SectionKind.RELOCATION:
            relocation_fourth(obj, objects)
        elif obj.kind == SectionKind.CODE:
            code_fourth(obj, objects)

    return get_configs() + '\n\n'.join([obj.str_dump() for obj in objects]) + '\n'


def disasm_all(srcdir, asmdir):
    srcpath = Path(srcdir)
    asm_path = Path(asmdir)
    asm_path.mkdir(exist_ok=True, parents=True)
    
    # Handle both individual files and directories
    if srcpath.is_file():
        # Single file mode
        script_files = [srcpath]
        kernels_dir = srcpath.parent
    else:
        # Directory mode - look for .scr files and script.* files
        scr_files = list(srcpath.glob('*.scr'))
        script_files_glob = list(srcpath.glob('script.*'))
        script_files = scr_files + [f for f in script_files_glob if f.suffix.lstrip('.').isdigit() or f.suffix == '.scr']
        kernels_dir = srcpath
    
    global kernels
    kernels = Kernels(kernels_dir, asm_path, mode='disasm')
    
    for scr in script_files:
        if scr.name.lower() != 'install.scr':
            sca = asm_path / f'{scr.stem}.sca'
            print("--------")
            print(f"Disassembling {scr} to {sca}")
            try:
                result = disasm(scr)
                sca.write_text(result)
                print(f"Successfully disassembled to {sca}")
            except Exception as e:
                print(f"ERROR disassembling {scr}: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description=f"Sierra 'SCRIPT' disassembler - WIP", )
    parser.add_argument("srcdir", help="source file or directory containing the scripts (.scr, .000, .001, etc files)")
    parser.add_argument("asmdir", help="directory to write the assembly (.sca) files")
    args = parser.parse_args()

    disasm_all(args.srcdir, args.asmdir)
