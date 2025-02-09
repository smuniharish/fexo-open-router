import psutil
def get_free_cpus(threshold=10):
    cpu_usages = psutil.cpu_percent(interval=1, percpu=True)
    free_cpus = [i for i, usage in enumerate(cpu_usages) if usage < threshold]
    if len(free_cpus)>0:
        return free_cpus
    else:
        return [0,1,2,3]
    # return [0, 1, 2, 3,4,5]
if __name__ == '__main__':
    free_cpu = len(get_free_cpus())