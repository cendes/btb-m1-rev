cmd_/home/cendes/pmu_module/modules.order := {   echo /home/cendes/pmu_module/pmcr0_module.ko; :; } | awk '!x[$$0]++' - > /home/cendes/pmu_module/modules.order
