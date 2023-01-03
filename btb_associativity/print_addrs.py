import sys
import subprocess
import matplotlib
import matplotlib.pyplot as plt

BRANCH_INC_CONST = "#define BRANCH_INC \"mov x2, 48 \\n\" \\\n"

BRANCH_LIST = ", \"=r\" (addrs[{n}])"

ADD_INSTR =    "\"add x10, x10, x2 \\n\" \\\n"
NOP_INSTR =    "\"nop              \\n\" \\\n"
ADR_INSTRS =   "\"adr %{n}, .      \\n\" \\\n" \
               "\"add %{n}, %{n}, 8 \\n\" \\\n"
BRANCH_INSTR = "\"br  x10          \\n\" \\\n"

EVICTION_SET = [25, 281, 282, 793, 794, 878]

i_file = open("branch_inc.h", "w")
i_file.write(BRANCH_INC_CONST)
i_file.close()

l_file = open("branch_list.h", "w")
l_file.write("#define NUM_BRANCHES " + str(len(EVICTION_SET)) + "\n")
l_file.write("#define BRANCH_LIST ")
for i in range(len(EVICTION_SET)):
    l_file.write(BRANCH_LIST.format(n=str(i)))
l_file.close()

curr_var = 1
b_file = open("branches.h", "w")
b_file.write("#define BRANCHES ")
for i in range(1024):
    b_file.write(ADD_INSTR)
    for _ in range(8):
        b_file.write(NOP_INSTR)
    if i in EVICTION_SET:
        b_file.write(ADR_INSTRS.format(n=str(curr_var)))
        b_file.write(BRANCH_INSTR)
        curr_var += 1
    else:
        for _ in range(3):
            b_file.write(NOP_INSTR)
b_file.close()

try:
    subprocess.run(f"clang -O0 btb_branch_addrs.c -o btb_branch_addrs", shell=True)
except Exception as e:
    print("compilation of btb_eviction_set.c failed", str(e))

print("Compilation done. run ./btb_branch_addrs")
