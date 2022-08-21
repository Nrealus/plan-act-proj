import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

import time
import random
from unionfind import UnionFind2, UnionFind1

############################################

def compare_connected_component_building():

    uf1 = UnionFind1()
    uf2 = UnionFind2()

    u = set([i for i in range(100000)])
    v1 = random.sample(u,10000)
    v2 = random.sample(u - set(v1),10000)
    v3 = random.sample((u - set(v1)) - set(v2),10000)
    v4 = random.sample(((u - set(v1)) - set(v2)) - set(v3),10000)

    uf1.make_set(u)    
    uf2.make_set(u)
    
    print("--- uf1 ---")

    ts = time.perf_counter()
    for i in range(1,2500):
        uf1.union(v1[i-1],v1[i])
        uf1.union(v2[i-1],v2[i])
        uf1.union(v3[i-1],v3[i])
    es = time.perf_counter()
    print("unions time : {0}".format(es-ts))

    ts = time.perf_counter()
    for i in range(0,2500):
        uf1.find(v1[i])
        uf1.find(v2[i])
        uf1.find(v3[i])
    es = time.perf_counter()
    print("finds time : {0}".format(es-ts))

    ts = time.perf_counter()
    uf1.connected_component(v1[random.randint(0,2500)])
    uf1.connected_component(v2[random.randint(0,2500)])
    uf1.connected_component(v3[random.randint(0,2500)])
    es = time.perf_counter()
    print("connected components time : {0}".format(es-ts))

    ts = time.perf_counter()
    for i in range(0,2500):
        uf1.make_set([v1[i]])
        uf1.make_set([v2[i]])
        uf1.make_set([v3[i]])
    es = time.perf_counter()
    print("make set times {0}".format(es-ts))

    print("--- uf2 ---")

    ts = time.perf_counter()
    for i in range(1,2500):
        uf2.union(v1[i-1],v1[i])
        uf2.union(v2[i-1],v2[i])
        uf2.union(v3[i-1],v3[i])
    es = time.perf_counter()
    print("unions time : {0}".format(es-ts))

    ts = time.perf_counter()
    for i in range(0,2500):
        uf2.find(v1[i])
        uf2.find(v2[i])
        uf2.find(v3[i])
    es = time.perf_counter()
    print("finds time : {0}".format(es-ts))

    ts = time.perf_counter()
    uf2.connected_component(v1[random.randint(0,2500)])
    uf2.connected_component(v2[random.randint(0,2500)])
    uf2.connected_component(v3[random.randint(0,2500)])
    es = time.perf_counter()
    print("connected components time : {0}".format(es-ts))

    ts = time.perf_counter()
    uf2.contains(v1)
    uf2.contains(v2)
    uf2.contains(v3)
    es = time.perf_counter()
    print("contains : {0}".format(es-ts))

    ts = time.perf_counter()
    for i in range(0,2500):
        uf2.make_set([v1[i]])
        uf2.make_set([v2[i]])
        uf2.make_set([v3[i]])
    es = time.perf_counter()
    print("make set times {0}".format(es-ts))
