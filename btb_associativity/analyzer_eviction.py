import sys
import subprocess
import matplotlib
import matplotlib.pyplot as plt

# Get Number of evictions right after each branch

BRANCH_INC_CONST = "#define BRANCH_INC \"mov x2, 48 \\n\" \\\n"

CHECK_CNTRS =  "\"dsb sy            \\n\" \\\n" \
               "\"eor x15, x1,  1   \\n\" \\\n" \
               "\"eor x16, x4,  x3  \\n\" \\\n" \
               "\"orr x16, x16, x15 \\n\" \\\n" \
               "\"cbz x16, end      \\n\" \\\n" \
               "\"add x4,  x4,  1   \\n\" \\\n"

DSB_INSTR =    "\"dsb sy            \\n\" \\\n"
ADD_INSTR =    "\"add x10, x10, x2  \\n\" \\\n"
NOP_INSTR =    "\"nop               \\n\" \\\n"
BRANCH_INSTR = "\"br  x10           \\n\" \\\n"

if len(sys.argv) > 1:
    eviction_set = eval(sys.argv[1])
else:
    eviction_set = []

i_file = open("branch_inc.h", "w")
i_file.write(BRANCH_INC_CONST)
i_file.close()

b_file = open("branches.h", "w")
b_file.write("#define BRANCHES ")
for i in range(1024):
    b_file.write(DSB_INSTR)
    b_file.write(ADD_INSTR)
    for _ in range(2):
        b_file.write(NOP_INSTR)
    b_file.write(CHECK_CNTRS)
    b_file.write(DSB_INSTR)
    if i in eviction_set:
        b_file.write(NOP_INSTR)
    else:
        b_file.write(BRANCH_INSTR)
b_file.close()

num_branches = 1
for i in range(1024):
    try:
        subprocess.run(f"clang -O0 btb_assoc.c -o btb_assoc", shell=True)
    except Exception as e:
        print("compilation of btb_assoc.c failed", str(e))

    try:
        result = subprocess.run(["./btb_assoc", str(i)], stdout=subprocess.PIPE).stdout.decode("utf-8")
    except Exception as e:
        print("running ./btb_assoc returned an error", str(e))

    print("branch " + str(i) + ": " + result)
