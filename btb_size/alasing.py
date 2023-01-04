import subprocess
import matplotlib
import matplotlib.pyplot as plt

FIRST_SET_INSTRUCTION = "\"adr x{regnum}, start \\n\" \\\n"
SET_INSTRUCTION = "\"add x{regnum}, x{prevreg}, 4 \\n\" \\\n"
BRANCH_INSTRUCTION = "\"br x{regnum} \\n\" \\\n"
FIRST_REGNUM = 10

s_file = open("regsets.h", "w")
s_file.write("#define REGSETS ")
s_file.write(FIRST_SET_INSTRUCTION.format(regnum=str(FIRST_REGNUM)))
s_file.close()

b_file = open("branches.h", "w")
b_file.write("#define BRANCHES ")
b_file.close()

c_file = open("cloblst.h", "w")
c_file.write("#define CLOBLST ")
c_file.write("\"x" + str(FIRST_REGNUM) + "\"")
c_file.close()

curr_regnum = FIRST_REGNUM
num_branches = 1
for num_branches in range(17):
    try:
        subprocess.run(f"clang -O0 btb_aliasing.c -o btb_aliasing", shell=True)
    except Exception as e:
        print("compilation of btb_size.c failed", str(e))

    try:
        result = subprocess.run("./btb_aliasing", stdout=subprocess.PIPE).stdout.decode("utf-8")
    except:
        print("running ./btb_aliasing returned an error")

    print(str(num_branches) + " branches: " + result)

    curr_regnum += 1

    s_file = open("regsets.h", "a")
    s_file.write(SET_INSTRUCTION.format(regnum=curr_regnum, prevreg=curr_regnum - 1))
    s_file.close()

    b_file = open("branches.h", "a")
    b_file.write(BRANCH_INSTRUCTION.format(regnum=curr_regnum))
    b_file.close()

    c_file = open("cloblst.h", "a")
    c_file.write(", \"x" + str(curr_regnum) + "\"")
    c_file.close()
