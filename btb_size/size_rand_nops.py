import sys
import subprocess
import random
import matplotlib
import matplotlib.pyplot as plt

BRANCH_INC_CONST = "#define BRANCH_INC \"mov x2, 8 \\n\" \\\n"

ADD_INSTR =    "\"add  x10, x10, x2 \\n\" \\\n"
ADDI_INSTR =   "\"add  x10, x10, 4  \\n\" \\\n"
BRANCH_INSTR = "\"br   x10          \\n\" \\\n"

random.seed()

power = int(sys.argv[1])

i_file = open("branch_inc.h", "w")
i_file.write(BRANCH_INC_CONST)
i_file.close()

b_file = open("branches.h", "w")
b_file.write("#define BRANCHES ")
b_file.write(ADD_INSTR)
b_file.write(BRANCH_INSTR)
b_file.close()

num_branches = 1
for i in range(power):
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
        for _ in range(random.randrange(16)):
            b_file.write(ADDI_INSTR)
        b_file.write(ADD_INSTR)
        b_file.write(BRANCH_INSTR)
    b_file.close()

    if sys.argv[1] == "-f":
        num_branches += 1
    else:
        num_branches *= 2
