import sys
import subprocess
import math
import copy
import random
import matplotlib
import matplotlib.pyplot as plt

BRANCH_INC_CONST = "#define BRANCH_INC \"mov x2, 12 \\n\" \\\n"

FST_BR_LABEL =  "\"fst_br: \"                  \\\n"

NOP_INSTR =     "\"add  x10, x10, 4      \\n\" \\\n"
ADR_INSTR  =    "\"adr  x10, fst_br      \\n\" \\\n"
B_INSTR   =     "\"b    fst_br           \\n\" \\\n"
DSB_INSTR =     "\"dsb  sy               \\n\" \\\n"
ADJ_INSTR =     "\"add  x10, x10, 8      \\n\" \\\n"
MOV_INSTR =     "\"mov  x11, {x}         \\n\" \\\n"
MOVZ_INSTR =    "\"movz x11, {x}, lsl 16 \\n\" \\\n"
MOVK_INSTR  =    "\"movk x11, {x}         \\n\" \\\n"
SUB_INSTR =     "\"sub  x10, x10, x11    \\n\" \\\n"
ADD_INSTR =     "\"add  x10, x10, x11    \\n\" \\\n"
BRANCH_INSTR =  "\"br   x10              \\n\" \\\n"

LOOP_START = 0x19aa8
LOOP_END = 0x30000
EVICTION_SET = [0x1e098, 0x200a8, 0x24098]

i_file = open("branch_inc.h", "w")
i_file.write(BRANCH_INC_CONST)
i_file.close()

sets_visited = []
highest_misses = 0
optimal_set = []
for _ in range(math.factorial(len(EVICTION_SET))):
    while EVICTION_SET in sets_visited:
        random.shuffle(EVICTION_SET)
    sets_visited.append(copy.deepcopy(EVICTION_SET))

    first_addr = min(EVICTION_SET) - 52
    last_target = max(EVICTION_SET) + 4
    branch_targets = list()
    branch_inits = list()
    first_target = EVICTION_SET[0] - 44
    branch_inits.append(EVICTION_SET[0] - 12)
    for branch_addr in EVICTION_SET[1:]:
        branch_inits.append(branch_addr - 12)
        branch_targets.append(branch_addr - 44)
    branch_targets.append(last_target)

    instructions = list()
    curr_addr = LOOP_START
    while curr_addr < LOOP_END:
        if curr_addr == first_addr:
            instructions.append(ADR_INSTR)
            instructions.append(B_INSTR)
            curr_addr += 8
        elif curr_addr in branch_inits:
            set_index = branch_inits.index(curr_addr)
            curr_target = branch_targets[set_index]
            offset = abs(curr_target - curr_addr)
            if offset < 65535:
                instructions.append(MOV_INSTR.format(x=str(offset)))
                num_instrs = 4
            else:
                # One more mov instruction is needed
                del instructions[-1]
                curr_addr -= 4
                # Recompute offset
                offset = abs(curr_target - curr_addr)
                upper_bits = (offset & ~0xffff) >> 16
                lower_bits = offset & 0xffff
                instructions.append(MOVZ_INSTR.format(x=str(upper_bits)))
                instructions.append(MOVK_INSTR.format(x=str(lower_bits)))
                num_instrs = 5

            if curr_addr < curr_target:
                instructions.append(ADD_INSTR)
            else:
                instructions.append(SUB_INSTR)
            instructions.append(DSB_INSTR)
            instructions.append(BRANCH_INSTR)
            curr_addr += num_instrs * 4
        elif curr_addr == first_target:
            instructions.append(FST_BR_LABEL)
            instructions.append(DSB_INSTR)
            instructions.append(ADJ_INSTR)
            curr_addr += 8
        elif curr_addr in branch_targets:
            instructions.append(DSB_INSTR)
            instructions.append(ADJ_INSTR)
            curr_addr += 8
        else:
            instructions.append(NOP_INSTR)
            curr_addr += 4

    b_file = open("branches.h", "w")
    b_file.write("#define BRANCHES ")
    b_file.writelines(instructions)
    b_file.close()

    try:
        subprocess.run(f"clang -O0 btb_eviction_set.c -o btb_eviction_set", shell=True)
    except Exception as e:
        print("compilation of btb_eviction_set.c failed", str(e))

    num_misses = 0
    for _ in range(5000):
        try:
            result = subprocess.run("./btb_eviction_set", stdout=subprocess.PIPE).stdout.decode("utf-8")
        except Exception as e:
            print("running ./btb_eviction_set returned an error", str(e))
        num_misses += int(result)

    print("Number of misses for " + str([hex(x) for x in EVICTION_SET]) + ": " + str(num_misses))
    if num_misses > highest_misses:
        highest_misses = num_misses
        optimal_set = copy.deepcopy(EVICTION_SET)

print("Optimal set " + str([hex(x) for x in optimal_set]) + " with " + str(highest_misses) + " misses")
