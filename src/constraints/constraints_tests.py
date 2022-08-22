import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

from domain import Domain
from constraints import ConstraintNetwork, ConstraintType

import time

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

############################################

constraint_network = ConstraintNetwork()

def reset_constraint_network():

    constraint_network.m_bcn.clear()
    constraint_network.m_stn.clear()

def print_obj_details1():

    print("details : ")
    print("   var1 domain : {0}".format(constraint_network.objvar_domain("var1").get_values()))
    print("   var2 domain : {0}".format(constraint_network.objvar_domain("var2").get_values()))
    print("   var3 domain : {0}".format(constraint_network.objvar_domain("var3").get_values()))
    print("   var4 domain : {0}".format(constraint_network.objvar_domain("var4").get_values()))
    print("   var5 domain : {0}".format(constraint_network.objvar_domain("var5").get_values()))
    print("   unionfind connected component - var1 : {0}".format(constraint_network.m_bcn.m_unifications.connected_component("var1")))
    print("   unionfind connected component - var2 : {0}".format(constraint_network.m_bcn.m_unifications.connected_component("var2")))
    print("   unionfind connected component - var3 : {0}".format(constraint_network.m_bcn.m_unifications.connected_component("var3")))
    print("   unionfind connected component - var4 : {0}".format(constraint_network.m_bcn.m_unifications.connected_component("var4")))
    print("   unionfind connected component - var5 : {0}".format(constraint_network.m_bcn.m_unifications.connected_component("var5")))

def print_obj_details2(u:str, v:str):

    print("details on {0} and {1} : ".format(u,v))
    print("   {0} and {1} unified : {2}".format(u,v,constraint_network.objvars_unified(u,v)))
    print("   {0} and {1} unifiable : {2}".format(u,v,constraint_network.objvars_unifiable(u,v)))
    print("   {0} and {1} separable : {2}".format(u,v,constraint_network.objvars_separable(u,v)))
    print("   {0} and {1} separated : {2}".format(u,v,constraint_network.objvars_separated(u,v)))

def print_temporal_details1(u:str, v:str):

    print("details on {0} and {1} : ".format(u,v))
    print("   {2} <= '{1}' - '{0}' <= {3}".format(
        u,v,
        constraint_network.m_stn.m_minimal_network[(u,v)],
        constraint_network.m_stn.m_minimal_network[(v,u)]))

def test1(verbose=False):

    reset_constraint_network()
    constraint_network.declare_and_init_objvars({
        "var1":Domain(initial_allowed_values=[1,2,3,4,5]),
        "var1":Domain(initial_allowed_values=[1,2,3,4,5]),
        "var2":Domain(initial_allowed_values=[0,1,2,3,4]),
        "var3":Domain(initial_allowed_values=[1,2,3]),
        "var4":Domain(initial_allowed_values=[3,4,5]),
        "var5":Domain(initial_allowed_values=[6,7]),
    })
    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    constrs = [
        (ConstraintType.UNIFICATION,("var1", "var2")),
    ]
    ts = time.perf_counter()
    res = constraint_network.propagate_constraints_partial(constrs)
    es = time.perf_counter()
    print("---")
    if verbose:
        print("input constraints : {0}".format(constrs))
        print("(arc-consistent) propagation successful ? : {0}".format(res))
        print("time : {0}".format(es-ts))
        print_obj_details1()
        print_obj_details2("var1","var2")
    if res == True:
        print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
    print("---")

def test2(verbose=False):
    
    reset_constraint_network()
    constraint_network.declare_and_init_objvars({
        "var1":Domain(initial_allowed_values=[1,2,3,4,5]),
        "var1":Domain(initial_allowed_values=[1,2,3,4,5]),
        "var2":Domain(initial_allowed_values=[0,1,2,3,4]),
        "var3":Domain(initial_allowed_values=[1,2,3]),
        "var4":Domain(initial_allowed_values=[3,4,5]),
        "var5":Domain(initial_allowed_values=[6,7]),
    })
    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    constrs = [
        (ConstraintType.UNIFICATION,("var1", "var4")),
        (ConstraintType.UNIFICATION,("var3", "var1")),
    ]
    ts = time.perf_counter()
    res = constraint_network.propagate_constraints_partial(constrs)
    es = time.perf_counter()
    print("---")
    if verbose:
        print("input constraints : {0}".format(constrs))
        print("(arc-consistent) propagation successful ? : {0}".format(res))
        print("time : {0}".format(es-ts))
        print_obj_details1()
        print_obj_details2("var1","var2")
    if res == True:
        print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
    print("---")

def test3(verbose=False):
    
    reset_constraint_network()
    constraint_network.declare_and_init_objvars({
        "var1":Domain(initial_allowed_values=[1,2,3,4,5]),
        "var1":Domain(initial_allowed_values=[1,2,3,4,5]),
        "var2":Domain(initial_allowed_values=[0,1,2,3,4]),
        "var3":Domain(initial_allowed_values=[1,2,3]),
        "var4":Domain(initial_allowed_values=[3,4,5]),
        "var5":Domain(initial_allowed_values=[6,7]),
    })
    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    constrs = [
        (ConstraintType.UNIFICATION,("var1", "var5")),
    ]
    ts = time.perf_counter()
    res = constraint_network.propagate_constraints_partial(constrs)
    es = time.perf_counter()
    print("---")
    if verbose:
        print("input constraints : {0}".format(constrs))
        print("(arc-consistent) propagation successful ? : {0}".format(res))
        print("time : {0}".format(es-ts))
        print_obj_details1()
        print_obj_details2("var1","var5")
    if res == False:
        print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
    print("---")

def test4(verbose=False):
    
    reset_constraint_network()
    constraint_network.declare_and_init_objvars({
        "var1":Domain(initial_allowed_values=[1,2,3,4,5]),
        "var1":Domain(initial_allowed_values=[1,2,3,4,5]),
        "var2":Domain(initial_allowed_values=[0,1,2,3,4]),
        "var3":Domain(initial_allowed_values=[1,2,3]),
        "var4":Domain(initial_allowed_values=[3,4,5]),
        "var5":Domain(initial_allowed_values=[6,7]),
    })
    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    constrs = [
        (ConstraintType.SEPARATION,("var2", "var1")),
    ]
    ts = time.perf_counter()
    res = constraint_network.propagate_constraints_partial(constrs)
    es = time.perf_counter()
    print("---")
    if verbose:
        print("input constraints : {0}".format(constrs))
        print("(arc-consistent) propagation successful ? : {0}".format(res))
        print("time : {0}".format(es-ts))
        print_obj_details1()
        print_obj_details2("var1","var2")
    if res == True:
        print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
    print("---")

def test5(verbose=False):
    
    reset_constraint_network()
    constraint_network.declare_and_init_objvars({
        "var1":Domain(initial_allowed_values=[1,2,3,4,5]),
        "var1":Domain(initial_allowed_values=[1,2,3,4,5]),
        "var2":Domain(initial_allowed_values=[0,1,2,3,4]),
        "var3":Domain(initial_allowed_values=[1,2,3]),
        "var4":Domain(initial_allowed_values=[3,4,5]),
        "var5":Domain(initial_allowed_values=[6,7]),
    })
    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    constrs = [
        (ConstraintType.SEPARATION,("var2", "var1")),
        (ConstraintType.DISJ_UNIFICATION,("var1", ["var2","var3","var5"])),
    ]
    ts = time.perf_counter()
    res = constraint_network.propagate_constraints_partial(constrs)
    es = time.perf_counter()
    print("---")
    if verbose:
        print("input constraints : {0}".format(constrs))
        print("(arc-consistent) propagation successful ? : {0}".format(res))
        print("time : {0}".format(es-ts))
        print_obj_details1()
        print_obj_details2("var1","var2")
    if res == True:
        print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
    print("---")

def test6(verbose=False):
    
    reset_constraint_network()
    constraint_network.declare_and_init_objvars({
        "var1":Domain(initial_allowed_values=[1,2,3,4,5]),
        "var1":Domain(initial_allowed_values=[1,2,3,4,5]),
        "var2":Domain(initial_allowed_values=[0,1,2,3,4]),
        "var3":Domain(initial_allowed_values=[1,2,3]),
        "var4":Domain(initial_allowed_values=[3,4,5]),
        "var5":Domain(initial_allowed_values=[6,7]),
    })
    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    constrs = [
        (ConstraintType.SEPARATION,("var1", "var2")),
        (ConstraintType.GENERAL_RELATION,("relation", (("var2","var3"),[(1,1),(2,2)]))),
    ]
    ts = time.perf_counter()
    res = constraint_network.propagate_constraints_partial(constrs)
    es = time.perf_counter()
    print("---")
    if verbose:
        print("input constraints : {0}".format(constrs))
        print("(arc-consistent) propagation successful ? : {0}".format(res))
        print("time : {0}".format(es-ts))
        print_obj_details1()
        print_obj_details2("var1","var2")
    if res == True:
        print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
    print("---")

def test7(verbose=False):
    
    reset_constraint_network()
    constraint_network.declare_and_init_objvars({
        "var1":Domain(initial_allowed_values=[1,2,3,4,5]),
        "var1":Domain(initial_allowed_values=[1,2,3,4,5]),
        "var2":Domain(initial_allowed_values=[0,1,2,3,4]),
        "var3":Domain(initial_allowed_values=[1,2,3]),
        "var4":Domain(initial_allowed_values=[3,4,5]),
        "var5":Domain(initial_allowed_values=[6,7]),
    })
    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    constrs = [
        (ConstraintType.UNIFICATION,("var1", "var2")),
        (ConstraintType.UNIFICATION,("var1", "var3")),
        (ConstraintType.SEPARATION,("var3", "var2")),
    ]
    ts = time.perf_counter()
    res = constraint_network.propagate_constraints_partial(constrs)
    es = time.perf_counter()
    print("---")
    if verbose:
        print("input constraints : {0}".format(constrs))
        print("(arc-consistent) propagation successful ? : {0}".format(res))
        print("time : {0}".format(es-ts))
        print_obj_details1()
        print_obj_details2("var1","var2")
    if res == False:
        print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
    print("---")

def test8(verbose=False):
    
    reset_constraint_network()
    constraint_network.declare_and_init_objvars({
        "var1":Domain(initial_allowed_values=[1,2,3,4,5]),
        "var1":Domain(initial_allowed_values=[1,2,3,4,5]),
        "var2":Domain(initial_allowed_values=[0,1,2,3,4]),
        "var3":Domain(initial_allowed_values=[1,2,3]),
        "var4":Domain(initial_allowed_values=[3,4,5]),
        "var5":Domain(initial_allowed_values=[6,7]),
    })
    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    constrs = [
        (ConstraintType.DISJ_UNIFICATION,("var1", ["var2","var4"])),
        (ConstraintType.GENERAL_RELATION,("relation", (("var2","var3"),[(0,1),(1,1),(0,3),(1,3)]))),
    ]
    ts = time.perf_counter()
    res = constraint_network.propagate_constraints_partial(constrs)
    es = time.perf_counter()
    print("---")
    if verbose:
        print("input constraints : {0}".format(constrs))
        print("(arc-consistent) propagation successful ? : {0}".format(res))
        print("time : {0}".format(es-ts))
        print_obj_details1()
        print_obj_details2("var1","var2")
    if res == True:
        print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
    print("---")

def test9(verbose=False):
    
    reset_constraint_network()
    constraint_network.declare_and_init_objvars({
        "var1":Domain(initial_allowed_values=[1,2,3,4,5]),
        "var1":Domain(initial_allowed_values=[1,2,3,4,5]),
        "var2":Domain(initial_allowed_values=[0,1,2,3,4]),
        "var3":Domain(initial_allowed_values=[1,2,3]),
        "var4":Domain(initial_allowed_values=[3,4,5]),
        "var5":Domain(initial_allowed_values=[6,7]),
    })
    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    constrs = [
        (ConstraintType.SEPARATION,("var1", "var5")),
    ]
    ts = time.perf_counter()
    res = constraint_network.propagate_constraints_partial(constrs)
    es = time.perf_counter()
    print("---")
    if verbose:
        print("input constraints : {0}".format(constrs))
        print("(arc-consistent) propagation successful ? : {0}".format(res))
        print("time : {0}".format(es-ts))
        print_obj_details1()
        print_obj_details2("var1","var5")
    if res == True:
        print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
    print("---")

def test10(verbose=False):
    
    reset_constraint_network()
    constraint_network.m_stn.m_controllability["t1"] = True
    constraint_network.m_stn.m_controllability["t2"] = True
    constraint_network.m_stn.m_controllability["t3"] = True
    constraint_network.m_stn.m_controllability["t4"] = True
    constraint_network.declare_and_init_objvars({
        "c_l01":Domain(initial_allowed_values=[-10]),
        "c_u01":Domain(initial_allowed_values=[15]),
    })

    constrs = [
        (ConstraintType.TEMPORAL,("t1","origin","c_u01")),
        (ConstraintType.TEMPORAL,("origin","t1","c_l01")),
    ]
    ts = time.perf_counter()
    res = constraint_network.propagate_constraints_partial(constrs)
    es = time.perf_counter()
    print("---")
    if verbose:
        print("propagation successful ? : {0}".format(res))
        print("time : {0}".format(es-ts))
        print(constraint_network.m_stn.m_minimal_network)
    if res == True:
        print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
    print("---")

def test11(verbose=False):
    
    reset_constraint_network()
    constraint_network.m_stn.m_controllability["t1"] = True
    constraint_network.m_stn.m_controllability["t2"] = True
    constraint_network.m_stn.m_controllability["t3"] = True
    constraint_network.m_stn.m_controllability["t4"] = True
    constraint_network.declare_and_init_objvars({
        "c_l01":Domain(initial_allowed_values=[-10]),
        "c_u01":Domain(initial_allowed_values=[15]),
        "c_l02":Domain(initial_allowed_values=[-6]),
        "c_u02":Domain(initial_allowed_values=[8]),
        "c_l21":Domain(initial_allowed_values=[-10]),
        "c_u21":Domain(initial_allowed_values=[12]),
    })

    constrs = [
        (ConstraintType.TEMPORAL,("origin","t1","c_l01")),
        (ConstraintType.TEMPORAL,("t1","origin","c_u01")),
        (ConstraintType.TEMPORAL,("origin","t2","c_l02")),
        (ConstraintType.TEMPORAL,("t2","origin","c_u02")),
        (ConstraintType.TEMPORAL,("t2","t1","c_l21")),
        (ConstraintType.TEMPORAL,("t1","t2","c_u21")),
    ]
    ts = time.perf_counter()
    res = constraint_network.propagate_constraints_partial(constrs)
    es = time.perf_counter()
    print("---")
    if verbose:
        print("propagation successful ? : {0}".format(res))
        print("time : {0}".format(es-ts))
        print(constraint_network.m_stn.m_minimal_network)
    if res == False:
        print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
    print("---")

def test12(verbose=False):
    
    reset_constraint_network()
    constraint_network.m_stn.m_controllability["t1"] = True
    constraint_network.m_stn.m_controllability["t2"] = True
    constraint_network.m_stn.m_controllability["t3"] = True
    constraint_network.m_stn.m_controllability["t4"] = True
    constraint_network.declare_and_init_objvars({
        "c_l01":Domain(initial_allowed_values=[-10]),
        "c_u01":Domain(initial_allowed_values=[15]),
        "c_l12":Domain(initial_allowed_values=[-10]),
        "c_u12":Domain(initial_allowed_values=[15]),
        "c_l03":Domain(initial_allowed_values=[0]),
        "c_u03":Domain(initial_allowed_values=[3]),
        "c_l34":Domain(initial_allowed_values=[-8]),
        "c_u34":Domain(initial_allowed_values=[12]),
        "c_l41":Domain(initial_allowed_values=[0]),
        "c_u41":Domain(initial_allowed_values=[2]),
    })

    constrs = [
        (ConstraintType.TEMPORAL,("origin","t1","c_l01")),
        (ConstraintType.TEMPORAL,("t1","origin","c_u01")),
        (ConstraintType.TEMPORAL,("t1","t2","c_l12")),
        (ConstraintType.TEMPORAL,("t2","t1","c_u12")),
        (ConstraintType.TEMPORAL,("origin","t3","c_l03")),
        (ConstraintType.TEMPORAL,("t3","origin","c_u03")),
        (ConstraintType.TEMPORAL,("t3","t4","c_l34")),
        (ConstraintType.TEMPORAL,("t4","t3","c_u34")),
        (ConstraintType.TEMPORAL,("t4","t1","c_l41")),
        (ConstraintType.TEMPORAL,("t1","t4","c_u41")),
    ]
    ts = time.perf_counter()
    res = constraint_network.propagate_constraints_partial(constrs)
    es = time.perf_counter()
    print("---")
    if verbose:
        print("propagation successful ? : {0}".format(res))
        print("time : {0}".format(es-ts))
        print(constraint_network.m_stn.m_minimal_network)
    if res == True:
        print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
    print("---")

def test13(verbose=False):
    
    reset_constraint_network()
    constraint_network.m_stn.m_controllability["t1"] = True
    constraint_network.m_stn.m_controllability["t2"] = True
    constraint_network.m_stn.m_controllability["t3"] = True
    constraint_network.m_stn.m_controllability["t4"] = True
    constraint_network.declare_and_init_objvars({
        "c_l01":Domain(initial_allowed_values=[-6,-5,-4,-3,-2,-1]),
        "c_u01":Domain(initial_allowed_values=[5,6,7,8,9,10])
    })

    constrs = [
        (ConstraintType.TEMPORAL,("origin","t1","c_l01")),
        (ConstraintType.TEMPORAL,("t1","origin","c_u01")),
    ]
    ts = time.perf_counter()
    res = constraint_network.propagate_constraints_partial(constrs)
    es = time.perf_counter()
    print("---")
    if verbose:
        print("propagation successful ? : {0}".format(res))
        print("time : {0}".format(es-ts))
        print(constraint_network.m_stn.m_minimal_network)
    if res == True:
        print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
    print("---")

