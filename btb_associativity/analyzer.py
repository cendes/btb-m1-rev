import subprocess
import numpy as np
import random
import pickle
import matplotlib
import matplotlib.pyplot as plt

# THIS EXPERIMENT WAS NOT USED

BRANCH_INC_CONST = "#define BRANCH_INC \"mov x2, 12 \\n\" \\\n"

NOP_INSTR =    "\"nop              \\n\" \\\n"
ADR_INSTR =    "\"adr x10, .       \\n\" \\\n"
ADD_INSTR =    "\"add x10, x10, x2 \\n\" \\\n"
BRANCH_INSTR = "\"br  x10          \\n\" \\\n"

instructions = np.empty(12289, dtype=object)
instructions[0] = BRANCH_INSTR
for i in range(1, len(instructions)):
    instructions[i] = NOP_INSTR

lines = [0]

i_file = open("branch_inc.h", "w")
i_file.write(BRANCH_INC_CONST)
i_file.close()

b_file = open("branches.h", "w")
b_file.write("#define BRANCHES ")
b_file.write(ADD_INSTR)
for i in range(len(instructions)):
    b_file.write(instructions[i])
b_file.close()

random.seed(0)
curr_instr = 0
num_branches = 1
for i in range(1024):
    try:
        subprocess.run(f"clang -O0 btb_size_nops.c -o btb_size_nops", shell=True)
    except Exception as e:
        print("compilation of btb_size_nops.c failed", str(e))

    try:
        result = subprocess.run("./btb_size_nops", stdout=subprocess.PIPE).stdout.decode("utf-8")
    except:
        print("running ./btb_size_nops returned an error")

    print("run " + str(i) + " instr at " + str(curr_instr) + ": " + result)

    instr_found = False
    while not instr_found:
        curr_instr = random.randrange(1025)
        if curr_instr not in lines:
            lines.append(curr_instr)
            instr_found = True

    curr_line = curr_instr * 12
    instructions[curr_line - 2] = ADR_INSTR
    instructions[curr_line - 1] = ADD_INSTR
    instructions[curr_line] = BRANCH_INSTR

    b_file = open("branches.h", "w")
    b_file.write("#define BRANCHES ")
    b_file.write(ADD_INSTR)
    for j in range(len(instructions)):
        b_file.write(instructions[j])
    b_file.close()

    arr_file = open("run" + str(i), "wb")
    pickle.dump(lines, arr_file)
    arr_file.close()
