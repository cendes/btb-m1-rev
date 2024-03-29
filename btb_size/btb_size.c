#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>
#include <fcntl.h>
#include <unistd.h>
#include "../m1.h"
#include "branches_even.h"
#include "branches_odd.h"

int main() {
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

  __asm__ volatile (
      BRANCH_SANITIZE_1024
      "       mov  x1,  10     \n" // Initialize the loop counter
      "       mov  x2,  8      \n" // Constant branch address increment
      "       adr  x12, init   \n" 
      "init:  adr  x11, start  \n"
      "       add  x11, x11, 4 \n"
      "       adr  x10, half   \n"
      "       isb              \n"
      "       mrs  x5,  "PMC5" \n" // Load current PMC5 value
      "       isb              \n"
      "start:"
      BRANCHES_ODD
      "half:"
      BRANCHES_EVEN
      "       dsb  sy          \n"
      "       subs x1,  x1, 1  \n"
      "       beq  end         \n"
      "       br   x12         \n"
      "end:   isb              \n"
      "       mrs  x6,  "PMC5" \n" // Get current PMC5 value
      "       isb              \n"
      "       sub  %0,  x6, x5 \n" // Get number of BTB misses
      : "=r"(btb_misses)                       // Output variables
      :                                        // Input variables
      : "x1", "x2", "x5", "x6", "x10", "x11", "x12"   // Clobbered registers
  );

  printf("%lu\n", btb_misses);

  return 0;
}
