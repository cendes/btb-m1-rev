import sys
import subprocess
import matplotlib
import matplotlib.pyplot as plt

BRANCH_EVEN = "\"add x10, x10, x2 \\n\" \\\n" \
              "\"br  x10          \\n\" \\\n"

BRANCH_ODD = "\"br  x11          \\n\" \\\n" \
             "\"add x11, x11, x2 \\n\" \\\n"

if sys.argv[1] == "-f":
    # For the fine-grained option: get the start and end number of branches
    start = int(sys.argv[2])
    curr_branches = start
    end = int(sys.argv[3])
else:
    # For the coarse-grained option, get the power of 2 of the largest number of branches
    start = 0
    curr_branches = 2
    end = int(sys.argv[1])


# Generate header files
e_file = open("branches_even.h", "w")
e_file.write("#define BRANCHES_EVEN ")
e_file.write(BRANCH_EVEN)
for _ in range(int((start - 1)/2)):
    e_file.write(BRANCH_EVEN)
e_file.close()

o_file = open("branches_odd.h", "w")
o_file.write("#define BRANCHES_ODD ")
o_file.write(BRANCH_ODD)
for _ in range(int((start - 1)/2)):
    o_file.write(BRANCH_ODD)
o_file.close()

branches_arr = list()
num_misses = list()

num_branches = 1
for i in range(start, end):
    try:
        subprocess.run(f"clang -O0 btb_size.c -o btb_size", shell=True)
    except Exception as e:
        print("compilation of btb_size.c failed", str(e))

    try:
        result = subprocess.run("./btb_size", stdout=subprocess.PIPE).stdout.decode("utf-8")
    except:
        print("running ./btb_size returned an error")

    print(str(curr_branches) + " branches: " + result)
    branches_arr.append(curr_branches)
    branches_arr.append(int(result))

    e_file = open("branches_even.h", "a")
    o_file = open("branches_odd.h", "a")
    for _ in range(num_branches):
        e_file.write(BRANCH_EVEN)
        o_file.write(BRANCH_ODD)
    e_file.close()
    o_file.close()

    if sys.argv[1] == "-f":
        curr_branches += 2
    else:
        curr_branches *= 2
        num_branches *= 2

plt.title("Number of indirect branch misses for a given number of indirect branches in a loop")
plt.xlabel("Number of indirect branch instructions")
plt.ylabel("Number of indirect branch misses")
plt.plot(branches_arr, num_misses)
plt.savefig("plots/size_even_odd.png")
