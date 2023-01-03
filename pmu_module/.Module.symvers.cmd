cmd_/home/cendes/pmu_module/Module.symvers := sed 's/ko$$/o/' /home/cendes/pmu_module/modules.order | scripts/mod/modpost -m   -o /home/cendes/pmu_module/Module.symvers -e -i Module.symvers   -T -
