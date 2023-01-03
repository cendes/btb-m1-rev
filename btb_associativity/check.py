import sys
import subprocess
import numpy as np
import pickle

# THIS EXPERIMENT WAS NOT USED

BRANCH_INC_CONST = "#define BRANCH_INC \"mov x2, 12 \\n\" \\\n"

NOP_INSTR =    "\"nop              \\n\" \\\n"
ADR_INSTR =    "\"adr x10, .       \\n\" \\\n"
ADD_INSTR =    "\"add x10, x10, x2 \\n\" \\\n"
BRANCH_INSTR = "\"br  x10          \\n\" \\\n"

arr_file = open(sys.argv[1], "rb")
lines = pickle.load(arr_file)
arr_file.close()

instructions = np.empty(12289, dtype=object)
for i in range(len(instructions)):
    if i % 12 == 0 and (i/12) in lines:
        instructions[i - 2] = ADR_INSTR
        instructions[i - 1] = ADD_INSTR
        instructions[i] = BRANCH_INSTR
    else:
        instructions[i] = NOP_INSTR

i_file = open("branch_inc.h", "w")
i_file.write(BRANCH_INC_CONST)
i_file.close()

b_file = open("branches.h", "w")
b_file.write("#define BRANCHES ")
b_file.write(ADD_INSTR)
for i in range(len(instructions)):
    b_file.write(instructions[i])
b_file.close()

while True:
    try:
        subprocess.run(f"clang -O0 btb_size_nops.c -o btb_size_nops", shell=True)
    except Exception as e:
        print("compilation of btb_size_nops.c failed", str(e))

    try:
        result = subprocess.run("./btb_size_nops", stdout=subprocess.PIPE).stdout.decode("utf-8")
    except:
        print("running ./btb_size_nops returned an error")

    print("btb misses: " + result)
