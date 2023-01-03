import sys
import subprocess
import matplotlib
import matplotlib.pyplot as plt

BRANCH_INC_CONST = "#define BRANCH_INC \"mov x2, {inc} \\n\" \\\n"

ADD_INSTR =    "\"add x10, x10, x2 \\n\" \\\n"
NOP_INSTR =    "\"nop              \\n\" \\\n"
BRANCH_INSTR = "\"br  x10          \\n\" \\\n"

num_nops = int(sys.argv[1])

if sys.argv[2] == "-f":
    start = int(sys.argv[3])
    end = int(sys.argv[4])
else:
    start = 0
    end = int(sys.argv[2])

i_file = open("branch_inc.h", "w")
i_file.write(BRANCH_INC_CONST.format(inc=str((num_nops + 2) * 4)))
i_file.close()

b_file = open("branches.h", "w")
b_file.write("#define BRANCHES ")
b_file.write(ADD_INSTR)
for _ in range(num_nops):
    b_file.write(NOP_INSTR)
b_file.write(BRANCH_INSTR)
b_file.close()

num_branches = 1
for i in range(start, end):
    try:
        subprocess.run(f"clang -O0 btb_size_nops.c -o btb_size_nops", shell=True)
    except Exception as e:
        print("compilation of btb_size_nops.c failed", str(e))

    try:
        result = subprocess.run("./btb_size_nops", stdout=subprocess.PIPE).stdout.decode("utf-8")
    except:
        print("running ./btb_size_nops returned an error")

    print(str(num_branches) + " branches: " + result)

    b_file = open("branches.h", "a")
    for _ in range(num_branches):
        b_file.write(ADD_INSTR)
        for _ in range(num_nops):
            b_file.write(NOP_INSTR)
        b_file.write(BRANCH_INSTR)
    b_file.close()

    if sys.argv[2] == "-f":
        num_branches += 1
    else:
        num_branches *= 2
