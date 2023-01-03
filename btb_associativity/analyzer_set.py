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

if len(sys.argv) > 2:
    remove_set = eval(sys.argv[2])
else:
    remove_set = []

i_file = open("branch_inc.h", "w")
i_file.write(BRANCH_INC_CONST)
i_file.close()

# Get initial eviction set
instructions = list()
evict_set = list()
for i in range(1024):
    instructions.append(DSB_INSTR)
    instructions.append(ADD_INSTR)
    for _ in range(2):
        instructions.append(NOP_INSTR)
    for check_instr in CHECK_CNTRS:
        instructions.append(check_instr)
    instructions.append(DSB_INSTR)
    if i in remove_set:
        instructions.append(NOP_INSTR)
    else:
        instructions.append(BRANCH_INSTR)

for i in range(1024):
    if i in remove_set:
        continue

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

print("Eviction set: " + str(evict_set))

# Trim down eviction set
print("Next run")
for _ in range(50):
    for i in copy.deepcopy(evict_set):
        evict_set.remove(i)
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

# Recompile binary so we can do objdmp
b_file = open("branches.h", "w")
b_file.write("#define BRANCHES ")
b_file.writelines(instructions)
b_file.close()

try:
    subprocess.run(f"clang -O0 btb_assoc.c -o btb_assoc", shell=True)
except Exception as e:
    print("compilation of btb_assoc.c failed", str(e))
