from typing import List

import psutil


def get_free_cpus(threshold: int = 10) -> List[int]:
    cpu_usages = psutil.cpu_percent(interval=1, percpu=True)
    free_cpus = [i for i, usage in enumerate(cpu_usages) if usage < threshold]
    if len(free_cpus) < 4:
        return [0, 1, 2, 3]
    else:
        return free_cpus


cpus_count = len(get_free_cpus())
