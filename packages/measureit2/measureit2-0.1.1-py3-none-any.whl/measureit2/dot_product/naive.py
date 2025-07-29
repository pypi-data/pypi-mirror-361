import time
from itertools import starmap
from operator import mul

def dp0(list1: list, list2: list) -> tuple:
    start = time.time()
    ret = 0
    if len(list1) != len(list2):
        raise ValueError("Both lists must have the same length.")
    for i in range(len(list1)):
        ret += list1[i]*list2[i]
    return ret, time.time() - start 

def dp1(list1: list, list2: list) -> tuple:
    start = time.time()
    if len(list1) != len(list2):
        raise ValueError("Both lists must have the same length.")
    return sum(x * y for x, y in zip(list1, list2)), time.time() - start

def dp2(list1: list, list2: list) -> tuple:
    start = time.time()
    if len(list1) != len(list2):
        raise ValueError("Both lists must have the same length.")
    return sum(map(mul,list1,list2)), time.time() - start

def dp3(list1: list, list2: list) -> tuple:
    start = time.time()
    if len(list1) != len(list2):
        raise ValueError("Both lists must have the same length.")
    return sum(starmap(mul,zip(list1,list2))), time.time() - start