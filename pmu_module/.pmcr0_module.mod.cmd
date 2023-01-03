cmd_/home/cendes/pmu_module/pmcr0_module.mod := printf '%s\n'   pmcr0_module.o | awk '!x[$$0]++ { print("/home/cendes/pmu_module/"$$0) }' > /home/cendes/pmu_module/pmcr0_module.mod
