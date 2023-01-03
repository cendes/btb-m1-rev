import sys
import subprocess
import matplotlib
import matplotlib.pyplot as plt

BRANCH_INC_CONST = "#define BRANCH_INC \"mov x2, 12 \\n\" \\\n"

NOP_INSTR =     "\"add x10, x10, 4  \\n\" \\\n"
BRANCH_INSTRS = "\"add x10, x10, x2 \\n\" \\\n" \
                "\"dsb sy           \\n\" \\\n" \
                "\"br  x10          \\n\" \\\n" \
                "\"dsb sy           \\n\" \\\n" \
                "\"add x10, x10, 8  \\n\" \\\n"

LOOP_START = 0x19aa8
LOOP_END = 0x25aa8
EVICTION_SET = [0x1a0a8, 0x1d048, 0x1e098]

i_file = open("branch_inc.h", "w")
i_file.write(BRANCH_INC_CONST)
i_file.close()


branch_inits = list()
for addr in EVICTION_SET:
    branch_inits.append(addr - 8)

b_file = open("branches.h", "w")
b_file.write("#define BRANCHES ")
curr_addr = LOOP_START
while curr_addr < LOOP_END:
    if curr_addr in branch_inits:
        b_file.write(BRANCH_INSTRS)
        curr_addr += 20
    else:
        b_file.write(NOP_INSTR)
        curr_addr += 4
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

print("Number of misses: " + str(num_misses))
