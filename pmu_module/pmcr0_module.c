#include <linux/fs.h>
#include <linux/kobject.h>
#include <linux/module.h>
#include <linux/string.h>
#include <linux/sysfs.h>

#define PMCR0 "S3_1_c15_c0_0"

static struct kobject* pmcr0_module;

static size_t pmcr0;

static ssize_t pmcr0_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf) {
  __asm__ volatile (
      "    mrs %0, "PMCR0" \n"
      : "=r"(pmcr0)
  );

  pr_info("pmcr0_module: successfully read 0x%lx from PMCR0\n", pmcr0);

  memcpy(buf, (char* )&pmcr0, sizeof(size_t));
  return sizeof(size_t);
}

static ssize_t pmcr0_store (struct kobject *kobj, struct kobj_attribute *attr, char *buf, size_t count) {
  memcpy((char* )&pmcr0, buf, count);

  pr_info("pmcr0_module: writing 0x%lx to PMCR0\n", pmcr0);

  __asm__ volatile (
      "    msr "PMCR0", %0 \n"
      "    isb             \n "
      :
      : "r"(pmcr0)
  );

  pr_info("pmcr0_module: successfully wrote 0x%lx to PMCR0\n", pmcr0);

  return count;
}

static struct kobj_attribute pmcr0_attribute = __ATTR(pmcr0, 0660, pmcr0_show, (void *)pmcr0_store);

static int pmcr0_module_init(void) {
  pr_info("pmcr0_module: initializing module\n");
  
  pmcr0_module = kobject_create_and_add("pmc_regs", kernel_kobj);
  if (pmcr0_module == NULL) {
    pr_err("pmcr0_module: failed to create kobject\n");
    return -ENOMEM;
  }

  int ret = sysfs_create_file(pmcr0_module, &pmcr0_attribute.attr);
  if (ret != 0) {
    pr_err("pmcr0_module: failed to create sysfs file\n");
  }

  return ret;
}

static void pmcr0_module_exit(void) {
  pr_info("pmcr0_module: exited successfully\n");
  kobject_put(pmcr0_module);
}

module_init(pmcr0_module_init);
module_exit(pmcr0_module_exit);

MODULE_LICENSE("GPL");
