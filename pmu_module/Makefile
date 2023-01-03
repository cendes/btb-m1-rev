CONFIG_MODULE_SIG=n
KDIR = /lib/modules/5.19.0-2-arm64/build

kbuild:
	make -C $(KDIR) M=`pwd`
	sudo cp pmcr0_module.ko /lib/modules/`uname -r`
	sudo depmod
clean:
	make -C $(KDIR) M=`pwd` clean
