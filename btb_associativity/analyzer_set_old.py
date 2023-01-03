import sys
import subprocess
import matplotlib
import matplotlib.pyplot as plt

BRANCH_INC_CONST = "#define BRANCH_INC \"mov x2, 48 \\n\" \\\n"

CHECK_CNTRS =  "\"subs x1, x1,  1    \\n\" \\\n" \
               "\"beq  end           \\n\" \\\n" \

SER_INSTR =    "\"dsb  sy            \\n\" \\\n"
ADD_INSTR =    "\"add x10, x10, x2   \\n\" \\\n"
NOP_INSTR =    "\"nop                \\n\" \\\n"
BRANCH_INSTR = "\"br  x10            \\n\" \\\n"

i_file = open("branch_inc.h", "w")
i_file.write(BRANCH_INC_CONST)
i_file.close()

b_file = open("branches.h", "w")
b_file.write("#define BRANCHES ")
for i in range(1024):
    b_file.write(SER_INSTR)
    b_file.write(ADD_INSTR)
    if i == int(sys.argv[1]) + 1:
        b_file.write(CHECK_CNTRS)
        for _ in range(7):
            b_file.write(NOP_INSTR)
    else:
        for _ in range(9):
            b_file.write(NOP_INSTR)
    b_file.write(BRANCH_INSTR)
b_file.close()

num_branches = 1
for i in range(1024):
    try:
        subprocess.run(f"clang -O0 btb_evict_set.c -o btb_evict_set", shell=True)
    except Exception as e:
        print("compilation of btb_assoc.c failed", str(e))

    try:
        result = subprocess.run("./btb_evict_set", stdout=subprocess.PIPE).stdout.decode("utf-8")
    except Exception as e:
        print("running ./btb_assoc returned an error", str(e))

    print("branch " + str(i) + ": " + result)
