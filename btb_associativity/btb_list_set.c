#include <stdlib.h>
#include <stdio.h>
#include <pthread.h>
#include <fcntl.h>
#include <unistd.h>
#include "../m1.h"
#include "branch_inc.h"
#include "branches.h"
#include "../btb_sanitize.h"
#include "offsets.h"
#include "rand_body.h"

struct b_offset_node {
  int64_t b_offset;
  int64_t next_offset;
};

static int64_t offsets[NUM_BRANCHES] = OFFSET_ARRAY;

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

  // Allocate the list of branch offsets
  struct b_offset_node* offset_list = malloc(sizeof(struct b_offset_node));
  struct b_offset_node* curr_node = offset_list;
  curr_node->b_offset = offsets[0];
  for (int i = 1; i < NUM_BRANCHES; i++) {
    struct b_offset_node* next_node = malloc(sizeof(struct b_offset_node));
    next_node->b_offset = offsets[i];
    // Get the difference between the address of the current node and the next node
    curr_node->next_offset = (int64_t)next_node - (int64_t)curr_node;
    curr_node = next_node;
  }
  curr_node->next_offset = (int64_t)offset_list - (int64_t)curr_node;

  uint64_t btb_misses = 0;
  // uint64_t addr = 0;

  __asm__ volatile (
      BTB_SANITIZE
      BRANCH_SANITIZE_1024
      "       dsb  sy          \n"
      "       mov  x1,  3      \n" // Initialize the loop counter
      BRANCH_INC                   // Constant branch address increment
      //"       adr  x12, init   \n"
      "       mov  x3,  %1     \n" // Get the address of the offset list
      "       tst  x1,  3      \n" // Clear the flags
      "init:  adr  x10, start  \n"
      "       isb              \n"
      "       mrs  x5,  "PMC5" \n" // Load current PMC5 value
      "       isb              \n"
      "       dsb  sy          \n"
      "start:"
      BRANCHES
      "       dsb  sy          \n"
      "       subs x1,  x1, 1  \n"
      "       beq  end         \n"
      "       cmp  x1,  2      \n"
      "       beq  rand1       \n"
      "       bne  rand2       \n"
      "       b    init        \n"
      RAND_BODY
      "end:   isb              \n"
      "       mrs  x6,  "PMC5" \n" // Get current PMC5 value
      "       isb              \n"
      "       sub  %0,  x6, x5 \n" // Get number of BTB misses
      // "       adr  %1, ."
      : "=r"(btb_misses) /*,  "=r"(addr) */           // Output variables
      : "r"(offset_list)                              // Input variables
      : "x1", "x2", "x3", "x5", "x6", "x10", "x11", "x12"   // Clobbered registers
  );

  printf("%lu\n", btb_misses);
  //printf("%lx\n", addr);

  return 0;
}
