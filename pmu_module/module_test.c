#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>

int main (void) {
  int pmcr0_fd = open("/sys/kernel/pmc_regs/pmcr0", O_RDWR);
  if (pmcr0_fd < 0) {
    perror("failed to open PMCR0 sysfs file");
    return EXIT_FAILURE;
  }

  size_t pmcr0_val;
  if (read(pmcr0_fd, &pmcr0_val, sizeof(size_t)) < 0) {
    perror("failed to read pmcr0");
    return EXIT_FAILURE;
  }
  printf("Read 0x%lx from PMCR0\n", pmcr0_val);

  printf("Writing 0x3003400ff4ff into PMCR0\n");
  pmcr0_val = 0x3003400ff4ff;
  if (write(pmcr0_fd, &pmcr0_val, sizeof(size_t)) < 0) {
    perror("failed to write to PMCR0");
    return EXIT_FAILURE;
  }
  printf("Successfully wrote to PMCR0\n");

  if (read(pmcr0_fd, &pmcr0_val, sizeof(size_t)) < 0) {
    perror("failed to read pmcr0");
    return EXIT_FAILURE;
  }
  printf("Read 0x%lx from PMCR0\n", pmcr0_val);

  return 0;
}
