#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>
#include <fcntl.h>
#include <unistd.h>
#include "../m1.h"
#include "branch_inc.h"
#include "branches.h"
#include "../btb_sanitize.h"

int main(int argc, char* argv[]) {
  if (argc != 2) {
    printf("usage: ./btb_assoc instr_num \n");
    return EXIT_FAILURE;
  }
  size_t instr_num = atoi(argv[1]);
  
  int pmcr0_fd = open("/sys/kernel/pmc_regs/pmcr0", O_RDWR);
  if (pmcr0_fd < 0) {
    perror("failed to open PMCR0 sysfs file");
    return EXIT_FAILURE;
  }
  size_t pmcr0_val = 0x3003470ff4ff;
  if (write(pmcr0_fd, &pmcr0_val, sizeof(size_t)) < 0) {
    perror("failed to write to PMCR0");
    return EXIT_FAILURE;
  }

  // Configure the counter to trach branch mispredictions                                                                                                   
  // Enable PMC5                                                                                                                                            
  uint64_t pmcr1 = SREG_READ(PMCR1);
  pmcr1 |= EL0A64_ENABLE(5);
  SREG_WRITE(PMCR1, pmcr1);

  // Set PMC5 to count branch mispredictions                                                                                                                
  uint64_t pmesr0 = SREG_READ(PMESR0);
  pmesr0 = PMESR0_SET_EVENT(pmesr0, 5, BRANCH_INDIR_MISPRED_NONSPEC);
  SREG_WRITE(PMESR0, pmesr0);

  uint64_t btb_misses = 0;
  uint64_t addrs[NUM_BRANCHES];

  __asm__ volatile (
      BTB_SANITIZE
      BRANCH_SANITIZE_1024
      "       dsb  sy          \n"
      "       mov  x1,  20     \n" // Initialize the loop counter
      "       mov  x3,  %1     \n" // Initialize branch count
      BRANCH_INC                   // Constant branch address increment
      //"       adr  x12, init   \n" 
      "init:  adr  x10, start  \n"
      "       mov  x4,  0      \n"
      "       isb              \n"
      "       mrs  x5,  "PMC5" \n" // Load current PMC5 value
      "       isb              \n"
      "       dsb  sy          \n"
      "start:"
      BRANCHES
      "       dsb  sy          \n"
      "       subs x1,  x1, 1  \n"
      "       beq  end         \n"
      "       b    init        \n"
      "end:   isb              \n"
      "       mrs  x6,  "PMC5" \n" // Get current PMC5 value
      "       isb              \n"
      "       sub  %0,  x6, x5 \n" // Get number of BTB misses
      : "=r"(btb_misses)           // Output variables
      : "r"(instr_num)             // Input variables
      : "x1", "x2", "x3", "x4", "x5", "x6", "x10", "x12", "x15", "x16"   // Clobbered registers
  );

  printf("misses: %lu\n", btb_misses);
  printf("branch Addresses:\n");
  for (int i = 0; i < NUM_BRANCHES; i++) {
    printf("0x%lx\n", addrs[i]);
  }

  return 0;
}
