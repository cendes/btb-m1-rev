import sys
import subprocess
import math
import copy
import random
import matplotlib
import matplotlib.pyplot as plt

BRANCH_INC_CONST = "#define BRANCH_INC \"mov x2, 12 \\n\" \\\n"

FST_BR_LABEL =  "\"fst_br: \"         \\\n"

NOP_INSTR =     "\"add  x10, x10, 4   \\n\" \\\n"
ADR_INSTR  =    "\"adr  x10, fst_br   \\n\" \\\n"
B_INSTR   =     "\"b    fst_br        \\n\" \\\n"
DSB_INSTR =     "\"dsb  sy            \\n\" \\\n"
ADJ_INSTR =     "\"add  x10, x10, 8   \\n\" \\\n"
ADJ2_INSTR =    "\"add  x10, x10, 12  \\n\" \\\n"
LIST_INSTRS =   "\"ldr x11, [x3]      \\n\" \\\n" \
                "\"add x10, x10, x11  \\n\" \\\n" \
                "\"ldr x12, [x3, #8]  \\n\" \\\n" \
                "\"dc  civac, x3      \\n\" \\\n" \
                "\"add x3,  x3, x12   \\n\" \\\n"
ADD_INSTR =     "\"add  x10, x10, x11 \\n\" \\\n"
BRANCH_INSTR =  "\"br   x10           \\n\" \\\n"

LOOP_START = 0x19d28
LOOP_END = 0x30000

BRANCH_LEN = 44

i_file = open("branch_inc.h", "w")
i_file.write(BRANCH_INC_CONST)
i_file.close()

l_file = open("branch_len.h", "w")
l_file.write("#define BRANCH_LEN " + str(BRANCH_LEN) + "\n")
l_file.close()

high_flips = list()

for i in range(6, 31, 1):
    for j in range(6, 31, 1):
        if i == j:
            continue

        branches = list()
        test_branch_addr = random.randrange(LOOP_START + 50, LOOP_END) & ~0x3
        branches.append(test_branch_addr)
        curr_branch = test_branch_addr | (0x1 << 32)
        branches.append(curr_branch)
        last_target = test_branch_addr + 4
        flipped_branch = (test_branch_addr ^ (0x1 << i) ^ (0x1 << j)) | (0x1 << 32)
        branches.append(flipped_branch)

        a_file = open("branch_addr.h", "w")
        a_file.write("#define BRANCH_ADDRS {" + ", ".join([hex(x - 44) for x in branches[1:]]) + "}\n")
        a_file.close()

        first_addr = min(branches) - 52
        branch_targets = list()
        branch_inits = list()
        first_target = branches[0] - 44
        branch_inits.append(branches[0] - 24)
        for branch_addr in branches[1:]:
            branch_inits.append(branch_addr - 24)
            branch_targets.append(branch_addr - 44)
        branch_targets.append(last_target)

        target_offsets = list()
        for init_addr in branch_inits:
            set_index = branch_inits.index(init_addr)
            curr_target = branch_targets[set_index]
            target_offsets.append(curr_target - init_addr)
        o_file = open("offsets.h", "w")
        o_file.write("#define OFFSET_ARRAY {" + ", ".join([str(x) for x in target_offsets]) + "}\n")
        o_file.write("#define NUM_BRANCHES " + str(len(branches)) + "\n")
        o_file.write("#define NUM_RANDS " + str(len(branches) - 1) + "\n")
        o_file.close()

        instructions = list()
        curr_addr = LOOP_START
        while curr_addr < LOOP_END:
            # if curr_addr == first_addr:
            #     instructions.append(ADR_INSTR)
            #     instructions.append(B_INSTR)
            #     curr_addr += 8
            if curr_addr in branch_inits:
                instructions.append(LIST_INSTRS)
                instructions.append(DSB_INSTR)
                instructions.append(BRANCH_INSTR)
                curr_addr += 28
            # elif curr_addr == first_target:
            #     instructions.append(FST_BR_LABEL)
            #     instructions.append(DSB_INSTR)
            #     instructions.append(ADJ_INSTR)
            #     curr_addr += 8
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

        map_b_instr = list()
        map_b_instr.append(DSB_INSTR)
        map_b_instr.append(ADJ2_INSTR)
        for _ in range(2):
            map_b_instr.append(NOP_INSTR)
        map_b_instr.append(LIST_INSTRS)
        map_b_instr.append(DSB_INSTR)
        map_b_instr.append(BRANCH_INSTR)

        m_file = open("map_b_instrs.h", "w")
        m_file.write("#define MAP_B_INSTRS ")
        m_file.writelines(map_b_instr)
        m_file.close()

        try:
            subprocess.run(f"clang -O0 btb_upper_set.c -o btb_upper_set", shell=True)
        except Exception as e:
            print("compilation of btb_upper_set.c failed", str(e))

        num_misses = 0
        for _ in range(5000):
            try:
                result = subprocess.run("./btb_upper_set", stdout=subprocess.PIPE).stdout.decode("utf-8")
            except Exception as e:
                print("running ./btb_upper_set returned an error", str(e))
            if result == "":
                continue
            num_misses += int(result)

        print("Number for flips at bits " + str(i) + " and " + str(j) + "(" + str([hex(x) for x in branches]) + "): " + str(num_misses))
        if num_misses >= 4000:
            high_flips.append((i, j))

# Remove inconsistencies
for (i, j) in copy.deepcopy(high_flips):
    if not (j, i) in high_flips:
        high_flips.remove((i, j))

# Remove repeats
for (i, j) in copy.deepcopy(high_flips):
    if (j, i) in high_flips:
        high_flips.remove((j, i))

print("Bit flips with high number of misses: " + str(high_flips))
