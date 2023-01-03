import random
import sys
import subprocess
import copy
import time
import matplotlib
import matplotlib.pyplot as plt

BRANCH_INC_CONST = "#define BRANCH_INC \"mov x2, 48 \\n\" \\\n"

CHECK_CNTRS =  ["\"dsb sy            \\n\" \\\n",
                "\"eor x15, x1,  1   \\n\" \\\n",
                "\"eor x16, x4,  x3  \\n\" \\\n",
                "\"orr x16, x16, x15 \\n\" \\\n",
                "\"cbz x16, end      \\n\" \\\n",
                "\"add x4,  x4,  1   \\n\" \\\n"]

DSB_INSTR =    "\"dsb sy             \\n\" \\\n"
ADD_INSTR =    "\"add x10, x10, x2   \\n\" \\\n"
NOP_INSTR =    "\"nop                \\n\" \\\n"
BRANCH_INSTR = "\"br  x10            \\n\" \\\n"

INITIAL_ELEMENTS = [25]

i_file = open("branch_inc.h", "w")
i_file.write(BRANCH_INC_CONST)
i_file.close()

# Get initial eviction set
instructions = list()
evict_set = copy.deepcopy(INITIAL_ELEMENTS)
for _ in range(1024):
    instructions.append(DSB_INSTR)
    instructions.append(ADD_INSTR)
    for _ in range(2):
        instructions.append(NOP_INSTR)
    for check_instr in CHECK_CNTRS:
        instructions.append(check_instr)
    instructions.append(DSB_INSTR)
    instructions.append(BRANCH_INSTR)

# Get initial eviction set
branches_removed = list()
for _ in range(1024 - len(INITIAL_ELEMENTS)):
    i = random.randrange(1024)
    while i in evict_set or i in branches_removed:
        i = random.randrange(1024)

    instructions[(i+1)*12 - 1] = NOP_INSTR
    b_file = open("branches.h", "w")
    b_file.write("#define BRANCHES ")
    b_file.writelines(instructions)
    b_file.close()

    try:
        subprocess.run(f"clang -O0 btb_assoc.c -o btb_assoc", shell=True)
    except Exception as e:
        print("compilation of btb_assoc.c failed", str(e))

    num_evictions = -1
    curr_run = 0
    while curr_run < 5:
        try:
            result = subprocess.run(["./btb_assoc", sys.argv[1]], stdout=subprocess.PIPE).stdout.decode("utf-8")
        except Exception as e:
            print("running ./btb_assoc returned an error", str(e))

        print("Removed branch " + str(i) + ": " + result)
        if num_evictions == -1:
            num_evictions = int(result)
        elif num_evictions != int(result):
            print("Different result obtained, restarting")
            num_evictions = -1
            curr_run = 0
        else:
            curr_run += 1

    if round(num_evictions) == 0:
        print("Putting back branch " + str(i))
        instructions[(i+1)*12 - 1] = BRANCH_INSTR
        evict_set.append(i)
    else:
        branches_removed.append(i)

print("Eviction set: " + str(evict_set))

# Trim down eviction set
print("Next run")
while len(evict_set) > 6:
    index = random.randrange(len(evict_set))
    while evict_set[index] in INITIAL_ELEMENTS:
        index = random.randrange(len(evict_set))

    i = evict_set.pop(index)
    instructions[(i + 1) * 12 - 1] = NOP_INSTR
    b_file = open("branches.h", "w")
    b_file.write("#define BRANCHES ")
    b_file.writelines(instructions)
    b_file.close()

    try:
        subprocess.run(f"clang -O0 btb_assoc.c -o btb_assoc", shell=True)
    except Exception as e:
        print("compilation of btb_assoc.c failed", str(e))

    num_evictions = -1
    curr_run = 0
    while curr_run < 5:
        try:
            result = subprocess.run(["./btb_assoc", sys.argv[1]], stdout=subprocess.PIPE).stdout.decode("utf-8")
        except Exception as e:
            print("running ./btb_assoc returned an error", str(e))

        print("Removed branch " + str(i) + ": " + result)
        if num_evictions == -1:
            num_evictions = int(result)
        elif num_evictions != int(result):
            print("Different result obtained, restarting")
            num_evictions = -1
            curr_run = 0
        else:
            curr_run += 1

    if round(num_evictions) == 0:
        print("Putting back branch " + str(i))
        instructions[(i + 1) * 12 - 1] = BRANCH_INSTR
        evict_set.append(i)

    print("Eviction set: " + str(evict_set))

