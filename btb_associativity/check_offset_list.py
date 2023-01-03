import sys
import subprocess
import random
import matplotlib
import matplotlib.pyplot as plt

BRANCH_INC_CONST = "#define BRANCH_INC \"mov x2, 12 \\n\" \\\n"

FST_BR_LABEL =  "\"fst_br: \"              \\\n"

NOP_INSTR =     "\"add x10, x10, 4   \\n\" \\\n"
ADR_INSTR  =    "\"adr x10, fst_br   \\n\" \\\n"
B_INSTR   =     "\"b   fst_br        \\n\" \\\n"
DSB_INSTR =     "\"dsb sy            \\n\" \\\n"
ADJ_INSTR =     "\"add x10, x10, 8   \\n\" \\\n"
LIST_INSTRS =   "\"ldr x11, [x3]     \\n\" \\\n" \
                "\"add x10, x10, x11 \\n\" \\\n" \
                "\"ldr x12, [x3, #8] \\n\" \\\n" \
                "\"dc  civac, x3     \\n\" \\\n" \
                "\"add x3,  x3, x12  \\n\" \\\n"
BRANCH_INSTR =  "\"br  x10           \\n\" \\\n"

LOOP_START = 0x19b98
LOOP_END = 0x30000
EVICTION_SET = [0x1d048, 0x23048, 0x1a018, 0x24008]

i_file = open("branch_inc.h", "w")
i_file.write(BRANCH_INC_CONST)
i_file.close()

first_addr = min(EVICTION_SET) - 52
last_target = max(EVICTION_SET) + 4
branch_targets = list()
branch_inits = list()
#random.shuffle(EVICTION_SET)
first_target = EVICTION_SET[0] - 44
branch_inits.append(EVICTION_SET[0] - 24)
for branch_addr in EVICTION_SET[1:]:
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
o_file.write("#define NUM_BRANCHES " + str(len(target_offsets)) + "\n")
o_file.close()

for addr in EVICTION_SET:
    print(hex(addr))

b_file = open("branches.h", "w")
b_file.write("#define BRANCHES ")
curr_addr = LOOP_START
while curr_addr < LOOP_END:
    if curr_addr == first_addr:
        b_file.write(ADR_INSTR)
        b_file.write(B_INSTR)
        curr_addr += 8
    elif curr_addr in branch_inits:
        b_file.write(LIST_INSTRS)
        b_file.write(DSB_INSTR)
        b_file.write(BRANCH_INSTR)
        curr_addr += 28
    elif curr_addr == first_target:
        b_file.write(FST_BR_LABEL)
        b_file.write(DSB_INSTR)
        b_file.write(ADJ_INSTR)
        curr_addr += 8
    elif curr_addr in branch_targets:
        b_file.write(DSB_INSTR)
        b_file.write(ADJ_INSTR)
        curr_addr += 8
    else:
        b_file.write(NOP_INSTR)
        curr_addr += 4
b_file.close()

try:
    subprocess.run(f"clang -O0 btb_list_set.c -o btb_list_set", shell=True)
except Exception as e:
    print("compilation of btb_list_set.c failed", str(e))

num_misses = 0
for _ in range(5000):
    try:
        result = subprocess.run("./btb_list_set", stdout=subprocess.PIPE).stdout.decode("utf-8")
    except Exception as e:
        print("running ./btb_list_set returned an error", str(e))
    num_misses += int(result)

print("Number of misses: " + str(num_misses))
