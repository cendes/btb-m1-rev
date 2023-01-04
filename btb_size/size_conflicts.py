import sys
import subprocess
import matplotlib
import matplotlib.pyplot as plt

BRANCH_INC_CONST = "#define BRANCH_INC \"mov x2, {inc} \\n\" \\\n"

ADD_INSTR =    "\"add x10, x10, x2 \\n\" \\\n"
NOP_INSTR =    "\"nop              \\n\" \\\n"
BRANCH_INSTR = "\"br  x10          \\n\" \\\n"

num_branches = int(sys.argv[1])
max_nops = int(sys.argv[2])
num_nops = 0

i_file = open("branch_inc.h", "w")
i_file.write(BRANCH_INC_CONST.format(inc=str((num_nops + 2) * 4)))
i_file.close()

b_file = open("branches.h", "w")
b_file.write("#define BRANCHES ")
for _ in range(num_branches):
    b_file.write(ADD_INSTR)
    for _ in range(num_nops):
        b_file.write(NOP_INSTR)
    b_file.write(BRANCH_INSTR)
b_file.close()

result_set = list()

for i in range(max_nops):
    try:
        subprocess.run(f"clang -O0 btb_size_nops.c -o btb_size_nops", shell=True)
    except Exception as e:
        print("compilation of btb_size_nops.c failed", str(e))

    try:
        result = subprocess.run("./btb_size_nops", stdout=subprocess.PIPE).stdout.decode("utf-8")
    except:
        print("running ./btb_size_nops returned an error")

    print(str(num_nops) + " nops: " + result)
    result_set.append(int(result))

    num_nops += 1

    i_file = open("branch_inc.h", "w")
    i_file.write(BRANCH_INC_CONST.format(inc=str((num_nops + 2) * 4)))
    i_file.close()

    b_file = open("branches.h", "w")
    b_file.write("#define BRANCHES ")
    for _ in range(num_branches):
        b_file.write(ADD_INSTR)
        for _ in range(num_nops):
            b_file.write(NOP_INSTR)
        b_file.write(BRANCH_INSTR)
    b_file.close()

plt.plot(range(4, max_nops * 4 + 1, 4), result_set)
plt.xticks(range(44, max_nops * 4 + 1, 44))
plt.title("Number of misses with " + sys.argv[1] + " indirect branches separated by each respective number of bytes", wrap=True)
plt.xlabel("Number of bytes between each indirect branch")
plt.ylabel("Number of indirect branch misses")
plt.savefig("plots/size_conflicts_" + sys.argv[1] + ".png")
