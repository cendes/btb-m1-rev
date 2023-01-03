import sys
import subprocess
import random
import matplotlib
import matplotlib.pyplot as plt

BRANCH_INC_CONST = "#define BRANCH_INC \"mov x2, 12 \\n\" \\\n"

FST_BR_LABEL =  "\"fst_br: \"              \\\n"

ADR_INSTR  =     "\"adr  x11, .        \\n\" \\\n"
MUL_INSTR  =     "\"mul  x10, x10, x11 \\n\" \\\n"
SDIV_INSTR =     "\"sdiv x10, x10, x3  \\n\" \\\n"
B_INSTR    =     "\"b    init          \\n\" \\\n"

TOTAL_SIZE = 5000
NUM_ITERATIONS = 2

instrs = [ADR_INSTR, MUL_INSTR, SDIV_INSTR]

labels_locs = list()
for _ in range(NUM_ITERATIONS-1):
    loc = random.randrange(TOTAL_SIZE)
    while loc in labels_locs:
        loc = random.randrange(TOTAL_SIZE)
    labels_locs.append(loc)

i_file = open("rand_body.h", "w")
i_file.write("#define RAND_BODY ")
i_file.write("\"rand" + str(NUM_ITERATIONS) + ": \"              \\\n")
curr_label = NUM_ITERATIONS-1
for loc in range(TOTAL_SIZE):
    if loc in labels_locs:
        i_file.write(B_INSTR)
        i_file.write("\"rand" + str(curr_label) + ": \"              \\\n")
        curr_label -= 1
    else:
        i_file.write(random.choice(instrs))
i_file.write(B_INSTR)
i_file.close()
