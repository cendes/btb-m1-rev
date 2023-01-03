#include <linux/module.h>
#define INCLUDE_VERMAGIC
#include <linux/build-salt.h>
#include <linux/elfnote-lto.h>
#include <linux/export-internal.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

BUILD_SALT;
BUILD_LTO_INFO;

MODULE_INFO(vermagic, VERMAGIC_STRING);
MODULE_INFO(name, KBUILD_MODNAME);

__visible struct module __this_module
__section(".gnu.linkonce.this_module") = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

#ifdef CONFIG_RETPOLINE
MODULE_INFO(retpoline, "Y");
#endif


static const struct modversion_info ____versions[]
__used __section("__versions") = {
	{ 0xcbd4898c, "fortify_panic" },
	{ 0x4829a47e, "memcpy" },
	{ 0x92997ed8, "_printk" },
	{ 0x88a7e7d, "kernel_kobj" },
	{ 0x8696f202, "kobject_create_and_add" },
	{ 0x95627384, "sysfs_create_file_ns" },
	{ 0x56ff7a84, "kobject_put" },
	{ 0x5ab1bd3e, "module_layout" },
};

MODULE_INFO(depends, "");

