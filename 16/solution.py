import copy
import json

from collections import namedtuple

Sample = namedtuple('Sample', ['before_state', 'instruction', 'after_state'])
BinaryInstruction = namedtuple('BinaryInstruction', ['opcode', 'in1', 'in2', 'out'])


def addr(r, bi):
    r[bi.out] = r[bi.in1] + r[bi.in2]


def addi(r, bi):
    r[bi.out] = r[bi.in1] + bi.in2


def mulr(r, bi):
    r[bi.out] = r[bi.in1] * r[bi.in2]


def muli(r, bi):
    r[bi.out] = r[bi.in1] * bi.in2


def banr(r, bi):
    r[bi.out] = r[bi.in1] & r[bi.in2]


def bani(r, bi):
    r[bi.out] = r[bi.in1] & bi.in2


def borr(r, bi):
    r[bi.out] = r[bi.in1] | r[bi.in2]


def bori(r, bi):
    r[bi.out] = r[bi.in1] | bi.in2


def setr(r, bi):
    r[bi.out] = r[bi.in1]


def seti(r, bi):
    r[bi.out] = bi.in1


def gtir(r, bi):
    r[bi.out] = int(bi.in1 > r[bi.in2])


def gtri(r, bi):
    r[bi.out] = int(r[bi.in1] > bi.in2)


def gtrr(r, bi):
    r[bi.out] = int(r[bi.in1] > r[bi.in2])


def eqir(r, bi):
    r[bi.out] = int(bi.in1 == r[bi.in2])


def eqri(r, bi):
    r[bi.out] = int(r[bi.in1] == bi.in2)


def eqrr(r, bi):
    r[bi.out] = int(r[bi.in1] == r[bi.in2])


INSTRUCTION_SPECS = [
    addr, addi,
    mulr, muli,
    banr, bani,
    borr, bori,
    setr, seti,
    gtir, gtri, gtrr,
    eqir, eqri, eqrr
]


def read_input(filename):
    with open(filename) as f:
        contents = f.read()
    return _parse(contents)


def solution1(data):
    samples = data['samples']
    return sum(
        1 for sample in samples if len(
            _get_matching_instructions(INSTRUCTION_SPECS, sample, stop_after=3)
        ) >= 3
    )


def solution2(data):
    samples, test_program = data['samples'], data['test_program']
    matches = _find_all_matches(samples)
    identified_opcodes = {}
    identified_instructions = set()
    while len(identified_instructions) != len(INSTRUCTION_SPECS):
        matches = {opcode: instructions for opcode, instructions in matches.items() if opcode not in identified_opcodes}
        for opcode in sorted(matches, key=lambda opcode: len(matches[opcode])):
            instructions = [i for i in matches[opcode] if i not in identified_instructions]
            if len(instructions) == 1:
                instruction = instructions[0]
                identified_opcodes[opcode] = instruction
                identified_instructions.add(instruction)

    registries = [0 for _ in samples[0].before_state]
    for binary_instruction in test_program:
        instruction = identified_opcodes[binary_instruction.opcode]
        instruction(registries, binary_instruction)
    return registries[0]


def _parse(contents):
    part1, part2 = contents.split('\n\n\n')
    return {
        'samples': _parse_samples(part1.strip()),
        'test_program': [BinaryInstruction(*(int(v) for v in line.split())) for line in part2.strip().splitlines()]
    }


def _parse_samples(samples):
    groups = samples.split('\n\n')
    result = []
    for g in groups:
        state_before, instruction, state_after = g.split('\n')
        state_before = json.loads(state_before.split('Before: ')[1])
        instruction = BinaryInstruction(*(int(i) for i in instruction.split()))
        state_after = json.loads(state_after.split('After: ')[1])
        result.append(Sample(state_before, instruction, state_after))
    return result


def _get_matching_instructions(instructions, sample, stop_after=float('inf')):
    result = set()
    c = 0
    for instruction in instructions:
        registers = copy.copy(sample.before_state)
        instruction(registers, sample.instruction)
        if registers == sample.after_state:
            result.add(instruction)
            c += 1
            if c == stop_after:
                break
    return result


def _find_all_matches(samples):
    matches = {}
    for sample in samples:
        opcode = sample.instruction.opcode
        instructions = _get_matching_instructions(INSTRUCTION_SPECS, sample)
        if opcode not in matches:
            matches[opcode] = set(instructions)
        else:
            matches[opcode] = matches[opcode].intersection(instructions)
    return matches


def test_read_input():
    contents = """Before: [1, 1, 3, 3]
11 1 0 1
After:  [1, 1, 3, 3]

Before: [0, 1, 2, 2]
3 2 2 1
After:  [0, 2, 2, 2]



7 2 0 0
11 0 2 0
2 1 1 3
7 0 0 2"""
    data = _parse(contents)
    samples, test_program = data['samples'], data['test_program']
    assert [
        Sample(
            before_state=[1, 1, 3, 3],
            instruction=BinaryInstruction(11, 1, 0, 1),
            after_state=[1, 1, 3, 3]
        ),
        Sample(
            before_state=[0, 1, 2, 2],
            instruction=BinaryInstruction(3, 2, 2, 1),
            after_state=[0, 2, 2, 2]
        )
    ] == samples

    assert [
        BinaryInstruction(7, 2, 0, 0),
        BinaryInstruction(11, 0, 2, 0),
        BinaryInstruction(2, 1, 1, 3),
        BinaryInstruction(7, 0, 0, 2),
    ] == test_program


def test_solution1():
    sample = Sample(
        before_state=[3, 2, 1, 1],
        instruction=BinaryInstruction(opcode=9, in1=2, in2=1, out=2),
        after_state=[3, 2, 2, 1]
    )
    regs = copy.copy(sample.before_state)
    mulr(regs, sample.instruction)
    assert [3, 2, 2, 1] == regs

    regs = copy.copy(sample.before_state)
    addi(regs, sample.instruction)
    assert [3, 2, 2, 1] == regs

    regs = copy.copy(sample.before_state)
    seti(regs, sample.instruction)
    assert [3, 2, 2, 1] == regs

    assert 3 == len(_get_matching_instructions(INSTRUCTION_SPECS, sample, stop_after=3))
