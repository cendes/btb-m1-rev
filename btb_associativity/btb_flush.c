#include "btb_sanitize.h"

int main() {
  __asm__ volatile (
      BTB_SANITIZE
      :
      :
      : "x1", "x2", "x10"
  );

  return 0;
}
