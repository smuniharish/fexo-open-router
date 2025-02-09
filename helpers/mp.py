from multiprocessing import Pool
from helpers.get_free_cpus import get_free_cpus

def create_pool():
    freecpusLength = len(get_free_cpus())
    print("free cpus",freecpusLength)
    free_cpus = freecpusLength
    p = Pool(free_cpus)
    return p

def create_process_in_pool(process_func,args):
    p = create_pool()
    results = p.map(process_func,args)
    return results
def create_process_in_async_pool(process_func,args):
    p = create_pool()
    results = p.map_async(process_func,args)
    return results.get()
def create_process_in_starmap_async_pool(process_func,args):
    p = create_pool()
    results = p.starmap_async(process_func,args)
    return results
def create_process_in_starmap_pool(process_func,args):
    p = create_pool()
    results = p.starmap(process_func,args)
    return results
