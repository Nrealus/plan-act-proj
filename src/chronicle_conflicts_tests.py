import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

from src.constraints.domain import Domain
from src.constraints.constraints import ConstraintNetwork, ConstraintType

from src.base import Assertion, AssertionType
from src.chronicle import Chronicle
from src.goal_node import GoalMode

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

chronicle = Chronicle()
constraint_network = ConstraintNetwork()

def reset():

    constraint_network.m_bcn.clear()
    constraint_network.m_stn.clear()
    chronicle.clear()

#def print_obj_details1():
#
#    print("details : ")
#    print("   var1 domain : {0}".format(constraint_network.objvar_domain("var1").get_values()))
#    print("   var2 domain : {0}".format(constraint_network.objvar_domain("var2").get_values()))
#    print("   var3 domain : {0}".format(constraint_network.objvar_domain("var3").get_values()))
#    print("   var4 domain : {0}".format(constraint_network.objvar_domain("var4").get_values()))
#    print("   var5 domain : {0}".format(constraint_network.objvar_domain("var5").get_values()))
#    print("   unionfind connected component - var1 : {0}".format(constraint_network.m_bcn.m_unifications.connected_component("var1")))
#    print("   unionfind connected component - var2 : {0}".format(constraint_network.m_bcn.m_unifications.connected_component("var2")))
#    print("   unionfind connected component - var3 : {0}".format(constraint_network.m_bcn.m_unifications.connected_component("var3")))
#    print("   unionfind connected component - var4 : {0}".format(constraint_network.m_bcn.m_unifications.connected_component("var4")))
#    print("   unionfind connected component - var5 : {0}".format(constraint_network.m_bcn.m_unifications.connected_component("var5")))

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
        constraint_network.tempvars_minimal_directed_distance(u,v),
        constraint_network.tempvars_minimal_directed_distance(v,u)))

def init_situation1():
    reset()
    constraint_network.declare_and_init_objvars({
        "objvar_robots_grp1":Domain(p_initial_allowed_values=["robot1","robot2"]),
        "objvar_robots_grp2":Domain(p_initial_allowed_values=["robot2","robot3"]),
        "objvar_robots_grp3":Domain(p_initial_allowed_values=["robot5","robot5"]),
        "objvar_location_A":Domain(p_initial_allowed_values=["location1", "location2"]),
        "objvar_location_B":Domain(p_initial_allowed_values=["location2", "location3"]),
        "objvar_location_C":Domain(p_initial_allowed_values=["location4", "location5"]),
        "c_l01":Domain(p_initial_allowed_values=[-1]),
        "c_u01":Domain(p_initial_allowed_values=[5]),
        "c_l03":Domain(p_initial_allowed_values=[1]),
        "c_u03":Domain(p_initial_allowed_values=[25]),
        "c_l12":Domain(p_initial_allowed_values=[3]),
        "c_u12":Domain(p_initial_allowed_values=[-1]),
        "c_l23":Domain(p_initial_allowed_values=[-3]),
        "c_u23":Domain(p_initial_allowed_values=[15]),
    })
    constraint_network.declare_and_init_tempvars({"t0":True,"t1":True,"t2":True,"t3":True})

def test1(verbose=False):

    init_situation1()
    constrs = []
    constrs.extend([
        (ConstraintType.TEMPORAL,("t0", "t1", "c_l01", False)),
        (ConstraintType.TEMPORAL,("t1", "t0", "c_u01", False)),
        (ConstraintType.TEMPORAL,("t0", "t3", "c_l03", False)),
        (ConstraintType.TEMPORAL,("t3", "t0", "c_u03", False)),
        (ConstraintType.TEMPORAL,("t1", "t2", "c_l12", False)),
        (ConstraintType.TEMPORAL,("t2", "t1", "c_u12", False)),
        (ConstraintType.TEMPORAL,("t2", "t3", "c_l23", False)),
        (ConstraintType.TEMPORAL,("t3", "t2", "c_u23", False)),
    ])

    asrt1 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
        p_sv_params_keys=("param_robot",),
        p_sv_params_values=("objvar_robots_grp1",),
        p_sv_val="objvar_location_A",
        p_sv_val_sec=None,
    )
    constrs.extend([
#        (ConstraintType.TEMPORAL,("t0", asrt1.time_start, 0, False)),
#        (ConstraintType.TEMPORAL,("t0", asrt1.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_start, "t0", 0, False)),
        (ConstraintType.TEMPORAL,("t0", asrt1.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_end, "t1", 0, False)),
        (ConstraintType.TEMPORAL,("t1", asrt1.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_start, asrt1.time_end, 0, asrt1.type == AssertionType.TRANSITION)),
    ])

    asrt2 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
        p_sv_params_keys=("param_robot",),
        p_sv_params_values=("objvar_robots_grp1",),
        p_sv_val="objvar_location_B",
        p_sv_val_sec=None,
    )
    constrs.extend([
#        (ConstraintType.TEMPORAL,("t0", asrt2.time_start, 0, False)),
#        (ConstraintType.TEMPORAL,("t0", asrt2.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_start, "t0", 0, False)),
        (ConstraintType.TEMPORAL,("t0", asrt2.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_end, "t1", 0, False)),
        (ConstraintType.TEMPORAL,("t1", asrt2.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_start, asrt2.time_end, 0, asrt2.type == AssertionType.TRANSITION)),
    ])

    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    ok = constraint_network.propagate_constraints(constrs)
    chronicle.m_constraint_network = constraint_network

    if verbose:
        print(chronicle.m_constraint_network.m_stn.m_minimal_network)

    if not ok:
        print("---")
        print("---")
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")
    else:            
        ts = time.perf_counter()
        chronicle.m_assertions[asrt1] = False
        res = chronicle.get_induced_conflicts([asrt2])
        es = time.perf_counter()
        print("---")
        if verbose:
            print("conflicts : {0}".format(res))
            print("time : {0}".format(es-ts))
        if res == set([(asrt1, asrt2)]):
            print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")

def test2(verbose=False):

    init_situation1()
    constrs = []
    constrs.extend([
        (ConstraintType.TEMPORAL,("t0", "t1", "c_l01", False)),
        (ConstraintType.TEMPORAL,("t1", "t0", "c_u01", False)),
        (ConstraintType.TEMPORAL,("t0", "t3", "c_l03", False)),
        (ConstraintType.TEMPORAL,("t3", "t0", "c_u03", False)),
        (ConstraintType.TEMPORAL,("t1", "t2", "c_l12", False)),
        (ConstraintType.TEMPORAL,("t2", "t1", "c_u12", False)),
        (ConstraintType.TEMPORAL,("t2", "t3", "c_l23", False)),
        (ConstraintType.TEMPORAL,("t3", "t2", "c_u23", False)),
    ])

    asrt1 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
        p_sv_params_keys=("param_robot",),
        p_sv_params_values=("objvar_robots_grp1",),
        p_sv_val="objvar_location_A",
        p_sv_val_sec=None,
    )
    constrs.extend([
#        (ConstraintType.TEMPORAL,("t0", asrt1.time_start, 0, False)),
#        (ConstraintType.TEMPORAL,("t0", asrt1.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_start, "t0", 0, False)),
        (ConstraintType.TEMPORAL,("t0", asrt1.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_end, "t1", 0, False)),
        (ConstraintType.TEMPORAL,("t1", asrt1.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_start, asrt1.time_end, 0, asrt1.type == AssertionType.TRANSITION)),
    ])

    asrt2 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
        p_sv_params_keys=("param_robot",),
        p_sv_params_values=("objvar_robots_grp1",),
        p_sv_val="objvar_location_B",
        p_sv_val_sec=None,
    )
    constrs.extend([
#        (ConstraintType.TEMPORAL,("t0", asrt2.time_start, 0, False)),
#        (ConstraintType.TEMPORAL,("t0", asrt2.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_start, "t2", 0, False)),
        (ConstraintType.TEMPORAL,("t2", asrt2.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_end, "t3", 0, False)),
        (ConstraintType.TEMPORAL,("t3", asrt2.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_start, asrt2.time_end, 0, asrt2.type == AssertionType.TRANSITION)),
    ])

    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    ok = constraint_network.propagate_constraints(constrs)
    chronicle.m_constraint_network = constraint_network

    if verbose:
        print(chronicle.m_constraint_network.m_stn.m_minimal_network)

    if not ok:
        print("---")
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")
    else:
        ts = time.perf_counter()
        chronicle.m_assertions[asrt1] = False
        res = chronicle.get_induced_conflicts([asrt2])
        es = time.perf_counter()
        print("---")
        if verbose:
            print("conflicts : {0}".format(res))
            print("time : {0}".format(es-ts))
        if res == set([(asrt1, asrt2)]):
            print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")

def test3(verbose=False):

    init_situation1()
    constrs = []
    constrs.extend([
        (ConstraintType.TEMPORAL,("t0", "t1", "c_l01", False)),
        (ConstraintType.TEMPORAL,("t1", "t0", "c_u01", False)),
        (ConstraintType.TEMPORAL,("t0", "t3", "c_l03", False)),
        (ConstraintType.TEMPORAL,("t3", "t0", "c_u03", False)),
        (ConstraintType.TEMPORAL,("t1", "t2", "c_l12", False)),
        (ConstraintType.TEMPORAL,("t2", "t1", "c_u12", False)),
        (ConstraintType.TEMPORAL,("t2", "t3", "c_l23", False)),
        (ConstraintType.TEMPORAL,("t3", "t2", "c_u23", False)),
    ])

    asrt1 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
        p_sv_params_keys=("param_robot",),
        p_sv_params_values=("objvar_robots_grp1",),
        p_sv_val="objvar_location_A",
        p_sv_val_sec=None,
    )
    constrs.extend([
#        (ConstraintType.TEMPORAL,("t0", asrt1.time_start, 0, False)),
#        (ConstraintType.TEMPORAL,("t0", asrt1.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_start, "t0", 0, False)),
        (ConstraintType.TEMPORAL,("t0", asrt1.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_end, "t1", 0, False)),
        (ConstraintType.TEMPORAL,("t1", asrt1.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_start, asrt1.time_end, 0, asrt1.type == AssertionType.TRANSITION)),
    ])

    asrt2 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
        p_sv_params_keys=("param_robot",),
        p_sv_params_values=("objvar_robots_grp1",),
        p_sv_val="objvar_location_A",
        p_sv_val_sec=None,
    )
    constrs.extend([
#        (ConstraintType.TEMPORAL,("t0", asrt2.time_start, 0, False)),
#        (ConstraintType.TEMPORAL,("t0", asrt2.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_start, "t2", 0, False)),
        (ConstraintType.TEMPORAL,("t2", asrt2.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_end, "t3", 0, False)),
        (ConstraintType.TEMPORAL,("t3", asrt2.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_start, asrt2.time_end, 0, asrt2.type == AssertionType.TRANSITION)),
    ])

    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    ok = constraint_network.propagate_constraints(constrs)
    chronicle.m_constraint_network = constraint_network

    if verbose:
        print(chronicle.m_constraint_network.m_stn.m_minimal_network)

    if not ok:
        print("---")
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")
    else:            
        ts = time.perf_counter()
        chronicle.m_assertions[asrt1] = False
        res = chronicle.get_induced_conflicts([asrt2])
        es = time.perf_counter()
        print("---")
        if verbose:
            print("conflicts : {0}".format(res))
            print("time : {0}".format(es-ts))
        if res == set():
            print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")

def test4(verbose=False):

    init_situation1()
    constrs = []
    constrs.extend([
        (ConstraintType.TEMPORAL,("t0", "t1", "c_l01", False)),
        (ConstraintType.TEMPORAL,("t1", "t0", "c_u01", False)),
        (ConstraintType.TEMPORAL,("t0", "t3", "c_l03", False)),
        (ConstraintType.TEMPORAL,("t3", "t0", "c_u03", False)),
        (ConstraintType.TEMPORAL,("t1", "t2", "c_l12", False)),
        (ConstraintType.TEMPORAL,("t2", "t1", "c_u12", False)),
        (ConstraintType.TEMPORAL,("t2", "t3", "c_l23", False)),
        (ConstraintType.TEMPORAL,("t3", "t2", "c_u23", False)),
    ])
    
    asrt1 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
        p_sv_params_keys=("param_robot",),
        p_sv_params_values=("objvar_robots_grp1",),
        p_sv_val="objvar_location_A",
        p_sv_val_sec=None,
    )
    constrs.extend([
#        (ConstraintType.TEMPORAL,("t0", asrt1.time_start, 0, False)),
#        (ConstraintType.TEMPORAL,("t0", asrt1.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_start, "t0", 0, False)),
        (ConstraintType.TEMPORAL,("t0", asrt1.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_end, "t1", 0, False)),
        (ConstraintType.TEMPORAL,("t1", asrt1.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_start, asrt1.time_end, 0, asrt1.type == AssertionType.TRANSITION)),
    ])

    asrt2 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
        p_sv_params_keys=("param_robot",),
        p_sv_params_values=("objvar_robots_grp1",),
        p_sv_val="objvar_location_C",
        p_sv_val_sec=None,
    )
    constrs.extend([
#        (ConstraintType.TEMPORAL,("t0", asrt2.time_start, 0, False)),
#        (ConstraintType.TEMPORAL,("t0", asrt2.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_start, "t2", 0, False)),
        (ConstraintType.TEMPORAL,("t2", asrt2.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_end, "t3", 0, False)),
        (ConstraintType.TEMPORAL,("t3", asrt2.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_start, asrt2.time_end, 0, asrt2.type == AssertionType.TRANSITION)),
    ])

    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    ok = constraint_network.propagate_constraints(constrs)
    chronicle.m_constraint_network = constraint_network

    if verbose:
        print(chronicle.m_constraint_network.m_stn.m_minimal_network)

    if not ok:
        print("---")
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")
    else:
        ts = time.perf_counter()
        chronicle.m_assertions[asrt1] = False        
        res = chronicle.get_induced_conflicts([asrt2])
        es = time.perf_counter()
        print("---")
        if verbose:
            print("conflicts : {0}".format(res))
            print("time : {0}".format(es-ts))
        if res == set([(asrt1, asrt2)]):
            print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")

def test5(verbose=False):

    init_situation1()
    constrs = []
    constrs.extend([
        (ConstraintType.TEMPORAL,("t0", "t1", "c_l01", False)),
        (ConstraintType.TEMPORAL,("t1", "t0", "c_u01", False)),
        (ConstraintType.TEMPORAL,("t0", "t3", "c_l03", False)),
        (ConstraintType.TEMPORAL,("t3", "t0", "c_u03", False)),
        (ConstraintType.TEMPORAL,("t1", "t2", "c_l12", False)),
        (ConstraintType.TEMPORAL,("t2", "t1", "c_u12", False)),
        (ConstraintType.TEMPORAL,("t2", "t3", "c_l23", False)),
        (ConstraintType.TEMPORAL,("t3", "t2", "c_u23", False)),
    ])
    
    asrt1 = Assertion(
        p_type=AssertionType.TRANSITION,
        p_sv_name="sv_location",
        p_sv_params_keys=("param_robot",),
        p_sv_params_values=("objvar_robots_grp1",),
        p_sv_val="objvar_location_A",
        p_sv_val_sec="objvar_location_B",
    )
    constrs.extend([
#        (ConstraintType.TEMPORAL,("t0", asrt1.time_start, 0, False)),
#        (ConstraintType.TEMPORAL,("t0", asrt1.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_start, "t0", 0, False)),
        (ConstraintType.TEMPORAL,("t0", asrt1.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_end, "t1", 0, False)),
        (ConstraintType.TEMPORAL,("t1", asrt1.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_start, asrt1.time_end, 0, asrt1.type == AssertionType.TRANSITION)),
    ])

    asrt2 = Assertion(
        p_type=AssertionType.TRANSITION,
        p_sv_name="sv_location",
        p_sv_params_keys=("param_robot",),
        p_sv_params_values=("objvar_robots_grp1",),
        p_sv_val="objvar_location_B",
        p_sv_val_sec="objvar_location_C",
    )
    constrs.extend([
#        (ConstraintType.TEMPORAL,("t0", asrt2.time_start, 0, False)),
#        (ConstraintType.TEMPORAL,("t0", asrt2.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_start, "t1", 0, False)),
        (ConstraintType.TEMPORAL,("t1", asrt2.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_end, "t3", 0, False)),
        (ConstraintType.TEMPORAL,("t3", asrt2.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_start, asrt2.time_end, 0, asrt2.type == AssertionType.TRANSITION)),
    ])

    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    ok = constraint_network.propagate_constraints(constrs)
    chronicle.m_constraint_network = constraint_network

    if verbose:
        print(chronicle.m_constraint_network.m_stn.m_minimal_network)

    if not ok:
        print("---")
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")
    else:
        ts = time.perf_counter()
        chronicle.m_assertions[asrt1] = False        
        res = chronicle.get_induced_conflicts([asrt2])
        es = time.perf_counter()
        print("---")
        if verbose:
            print("conflicts : {0}".format(res))
            print("time : {0}".format(es-ts))
        if res == set():
            print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")

def test6(verbose=False):

    init_situation1()
    constrs = []
    constrs.extend([
        (ConstraintType.TEMPORAL,("t0", "t1", "c_l01", False)),
        (ConstraintType.TEMPORAL,("t1", "t0", "c_u01", False)),
        (ConstraintType.TEMPORAL,("t0", "t3", "c_l03", False)),
        (ConstraintType.TEMPORAL,("t3", "t0", "c_u03", False)),
        (ConstraintType.TEMPORAL,("t1", "t2", "c_l12", False)),
        (ConstraintType.TEMPORAL,("t2", "t1", "c_u12", False)),
        (ConstraintType.TEMPORAL,("t2", "t3", "c_l23", False)),
        (ConstraintType.TEMPORAL,("t3", "t2", "c_u23", False)),
    ])
    #constrs.extend([
    #    (ConstraintType.TEMPORAL,("t1", "t2", 0, False)),
    #])
    asrt1 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
        p_sv_params_keys=("param_robot",),
        p_sv_params_values=("objvar_robots_grp1",),
        p_sv_val="objvar_location_A",
        p_sv_val_sec=None,
    )
    constrs.extend([
#        (ConstraintType.TEMPORAL,("t0", asrt1.time_start, 0, False)),
#        (ConstraintType.TEMPORAL,("t0", asrt1.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_start, "t0", 0, False)),
        (ConstraintType.TEMPORAL,("t0", asrt1.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_end, "t1", 0, False)),
        (ConstraintType.TEMPORAL,("t1", asrt1.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_start, asrt1.time_end, 0, asrt1.type == AssertionType.TRANSITION)),
    ])

    asrt2 = Assertion(
        p_type=AssertionType.TRANSITION,
        p_sv_name="sv_location",
        p_sv_params_keys=("param_robot",),
        p_sv_params_values=("objvar_robots_grp1",),
        p_sv_val="objvar_location_A",
        p_sv_val_sec="objvar_location_C",
    )
    constrs.extend([
#        (ConstraintType.TEMPORAL,("t0", asrt2.time_start, 0, False)),
#        (ConstraintType.TEMPORAL,("t0", asrt2.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_start, "t1", 0, False)),
        (ConstraintType.TEMPORAL,("t1", asrt2.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_end, "t2", 0, False)),
        (ConstraintType.TEMPORAL,("t2", asrt2.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_start, asrt2.time_end, 0, asrt2.type == AssertionType.TRANSITION)),
    ])

    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    ok = constraint_network.propagate_constraints(constrs)
    chronicle.m_constraint_network = constraint_network

    if verbose:
        print(chronicle.m_constraint_network.m_stn.m_minimal_network)

    if not ok:
        print("---")
        print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
        print("---")
    else:
        print("---")
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")

def test7(verbose=False):

    init_situation1()
    constrs = []
    constrs.extend([
        (ConstraintType.TEMPORAL,("t0", "t1", "c_l01", False)),
        (ConstraintType.TEMPORAL,("t1", "t0", "c_u01", False)),
        (ConstraintType.TEMPORAL,("t0", "t3", "c_l03", False)),
        (ConstraintType.TEMPORAL,("t3", "t0", "c_u03", False)),
        (ConstraintType.TEMPORAL,("t1", "t2", "c_l12", False)),
        (ConstraintType.TEMPORAL,("t2", "t1", "c_u12", False)),
        (ConstraintType.TEMPORAL,("t2", "t3", "c_l23", False)),
        (ConstraintType.TEMPORAL,("t3", "t2", "c_u23", False)),
    ])

    asrt1 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
        p_sv_params_keys=("param_robot",),
        p_sv_params_values=("objvar_robots_grp1",),
        p_sv_val="objvar_location_A",
        p_sv_val_sec=None,
    )
    constrs.extend([
#        (ConstraintType.TEMPORAL,("t0", asrt1.time_start, 0, False)),
#        (ConstraintType.TEMPORAL,("t0", asrt1.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_start, "t0", 0, False)),
        (ConstraintType.TEMPORAL,("t0", asrt1.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_end, "t1", 0, False)),
        (ConstraintType.TEMPORAL,("t1", asrt1.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_start, asrt1.time_end, 0, asrt1.type == AssertionType.TRANSITION)),
    ])

    asrt2 = Assertion(
        p_type=AssertionType.TRANSITION,
        p_sv_name="sv_location",
        p_sv_params_keys=("param_robot",),
        p_sv_params_values=("objvar_robots_grp1",),
        p_sv_val="objvar_location_A",
        p_sv_val_sec="objvar_location_C",
    )
    constrs.extend([
#        (ConstraintType.TEMPORAL,("t0", asrt2.time_start, 0, False)),
#        (ConstraintType.TEMPORAL,("t0", asrt2.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_start, "t2", 0, False)),
        (ConstraintType.TEMPORAL,("t2", asrt2.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_end, "t3", 0, False)),
        (ConstraintType.TEMPORAL,("t3", asrt2.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_start, asrt2.time_end, 0, asrt2.type == AssertionType.TRANSITION)),
    ])

    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    ok = constraint_network.propagate_constraints(constrs)
    chronicle.m_constraint_network = constraint_network

    if verbose:
        print(chronicle.m_constraint_network.m_stn.m_minimal_network)

    if not ok:
        print("---")
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")
    else:
        ts = time.perf_counter()
        chronicle.m_assertions[asrt1] = False
        res = chronicle.get_induced_conflicts([asrt2])
        es = time.perf_counter()
        print("---")
        if verbose:
            print("conflicts : {0}".format(res))
            print("time : {0}".format(es-ts))
        if res == set([(asrt1, asrt2)]):
            print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")


test1()
test2()
test3()
test4()
test5()
test6()
test7()