import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

from src.constraints.domain import Domain
from src.constraints.constraints import ConstraintNetwork, ConstraintType

from src.base import Assertion, AssertionType
from src.chronicle import Chronicle

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
    constraint_network.m_stn.m_controllability["t0"] = True
    constraint_network.m_stn.m_controllability["t1"] = True
    constraint_network.m_stn.m_controllability["t2"] = True
    constraint_network.m_stn.m_controllability["t3"] = True

def test1(verbose=False):

    init_situation1()

    asrt1 = Assertion(
        m_type=AssertionType.PERSISTENCE,
        m_sv_name="sv_location",
        m_sv_params_names=("param_robot"),
        m_sv_params_vars=("objvar_robots_grp1"),
        m_time_start="t0",
        m_time_end="t1",
        m_sv_val="objvar_location_A",
        m_sv_val_sec=None,
    )

    asrt2 = Assertion(
        m_type=AssertionType.PERSISTENCE,
        m_sv_name="sv_location",
        m_sv_params_names=("param_robot"),
        m_sv_params_vars=("objvar_robots_grp1"),
        m_time_start="t0",
        m_time_end="t1",
        m_sv_val="objvar_location_B",
        m_sv_val_sec=None,
    )

    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    constrs = [
        (ConstraintType.TEMPORAL,("t0", "t1", "c_l01", False)),
        (ConstraintType.TEMPORAL,("t1", "t0", "c_u01", False)),
        (ConstraintType.TEMPORAL,("t0", "t3", "c_l03", False)),
        (ConstraintType.TEMPORAL,("t3", "t0", "c_u03", False)),
        (ConstraintType.TEMPORAL,("t1", "t2", "c_l12", False)),
        (ConstraintType.TEMPORAL,("t2", "t1", "c_u12", False)),
        (ConstraintType.TEMPORAL,("t2", "t3", "c_l23", False)),
        (ConstraintType.TEMPORAL,("t3", "t2", "c_u23", False)),
    ]
    constraint_network.propagate_constraints(constrs)

    chronicle.m_assertions[asrt1] = False
    ts = time.perf_counter()
    res = chronicle.get_induced_conflicts([asrt2], constraint_network)
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

    asrt1 = Assertion(
        m_type=AssertionType.PERSISTENCE,
        m_sv_name="sv_location",
        m_sv_params_names=("param_robot"),
        m_sv_params_vars=("objvar_robots_grp1"),
        m_time_start="t0",
        m_time_end="t1",
        m_sv_val="objvar_location_A",
        m_sv_val_sec=None,
    )

    asrt2 = Assertion(
        m_type=AssertionType.PERSISTENCE,
        m_sv_name="sv_location",
        m_sv_params_names=("param_robot"),
        m_sv_params_vars=("objvar_robots_grp1"),
        m_time_start="t2",
        m_time_end="t3",
        m_sv_val="objvar_location_B",
        m_sv_val_sec=None,
    )

    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    constrs = [
        (ConstraintType.TEMPORAL,("t0", "t1", "c_l01", False)),
        (ConstraintType.TEMPORAL,("t1", "t0", "c_u01", False)),
        (ConstraintType.TEMPORAL,("t0", "t3", "c_l03", False)),
        (ConstraintType.TEMPORAL,("t3", "t0", "c_u03", False)),
        (ConstraintType.TEMPORAL,("t1", "t2", "c_l12", False)),
        (ConstraintType.TEMPORAL,("t2", "t1", "c_u12", False)),
        (ConstraintType.TEMPORAL,("t2", "t3", "c_l23", False)),
        (ConstraintType.TEMPORAL,("t3", "t2", "c_u23", False)),
    ]
    constraint_network.propagate_constraints(constrs)
    #print(constraint_network.propagate_constraints_partial([(ConstraintType.TEMPORAL,("t3", "t0", 0, False))],True))
    #print(constraint_network.propagate_constraints_partial([(ConstraintType.TEMPORAL,("t2", "t1", 0, False))],True))

    chronicle.m_assertions[asrt1] = False        
    ts = time.perf_counter()
    res = chronicle.get_induced_conflicts([asrt2], constraint_network)
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

    asrt1 = Assertion(
        m_type=AssertionType.PERSISTENCE,
        m_sv_name="sv_location",
        m_sv_params_names=("param_robot"),
        m_sv_params_vars=("objvar_robots_grp1"),
        m_time_start="t0",
        m_time_end="t1",
        m_sv_val="objvar_location_A",
        m_sv_val_sec=None,
    )

    asrt2 = Assertion(
        m_type=AssertionType.PERSISTENCE,
        m_sv_name="sv_location",
        m_sv_params_names=("param_robot"),
        m_sv_params_vars=("objvar_robots_grp1"),
        m_time_start="t2",
        m_time_end="t3",
        m_sv_val="objvar_location_A",
        m_sv_val_sec=None,
    )

    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    constrs = [
        (ConstraintType.TEMPORAL,("t0", "t1", "c_l01", False)),
        (ConstraintType.TEMPORAL,("t1", "t0", "c_u01", False)),
        (ConstraintType.TEMPORAL,("t0", "t3", "c_l03", False)),
        (ConstraintType.TEMPORAL,("t3", "t0", "c_u03", False)),
        (ConstraintType.TEMPORAL,("t1", "t2", "c_l12", False)),
        (ConstraintType.TEMPORAL,("t2", "t1", "c_u12", False)),
        (ConstraintType.TEMPORAL,("t2", "t3", "c_l23", False)),
        (ConstraintType.TEMPORAL,("t3", "t2", "c_u23", False)),
    ]
    constraint_network.propagate_constraints(constrs)

    chronicle.m_assertions[asrt1] = False        
    ts = time.perf_counter()
    res = chronicle.get_induced_conflicts([asrt2], constraint_network)
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

    asrt1 = Assertion(
        m_type=AssertionType.PERSISTENCE,
        m_sv_name="sv_location",
        m_sv_params_names=("param_robot"),
        m_sv_params_vars=("objvar_robots_grp1"),
        m_time_start="t0",
        m_time_end="t1",
        m_sv_val="objvar_location_A",
        m_sv_val_sec=None,
    )

    asrt2 = Assertion(
        m_type=AssertionType.PERSISTENCE,
        m_sv_name="sv_location",
        m_sv_params_names=("param_robot"),
        m_sv_params_vars=("objvar_robots_grp1"),
        m_time_start="t2",
        m_time_end="t3",
        m_sv_val="objvar_location_C",
        m_sv_val_sec=None,
    )

    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    constrs = [
        (ConstraintType.TEMPORAL,("t0", "t1", "c_l01", False)),
        (ConstraintType.TEMPORAL,("t1", "t0", "c_u01", False)),
        (ConstraintType.TEMPORAL,("t0", "t3", "c_l03", False)),
        (ConstraintType.TEMPORAL,("t3", "t0", "c_u03", False)),
        (ConstraintType.TEMPORAL,("t1", "t2", "c_l12", False)),
        (ConstraintType.TEMPORAL,("t2", "t1", "c_u12", False)),
        (ConstraintType.TEMPORAL,("t2", "t3", "c_l23", False)),
        (ConstraintType.TEMPORAL,("t3", "t2", "c_u23", False)),
    ]
    constraint_network.propagate_constraints(constrs)

    chronicle.m_assertions[asrt1] = False        
    ts = time.perf_counter()
    res = chronicle.get_induced_conflicts([asrt2], constraint_network)
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

    asrt1 = Assertion(
        m_type=AssertionType.PERSISTENCE,
        m_sv_name="sv_location",
        m_sv_params_names=("param_robot"),
        m_sv_params_vars=("objvar_robots_grp1"),
        m_time_start="t0",
        m_time_end="t1",
        m_sv_val="objvar_location_A",
        m_sv_val_sec=None,
    )

    asrt2 = Assertion(
        m_type=AssertionType.TRANSITION,
        m_sv_name="sv_location",
        m_sv_params_names=("param_robot"),
        m_sv_params_vars=("objvar_robots_grp1"),
        m_time_start="t1",
        m_time_end="t2",
        m_sv_val="objvar_location_A",
        m_sv_val_sec="objvar_location_C",
    )

    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    constrs = [
        (ConstraintType.TEMPORAL,("t0", "t1", "c_l01", False)),
        (ConstraintType.TEMPORAL,("t1", "t0", "c_u01", False)),
        (ConstraintType.TEMPORAL,("t0", "t3", "c_l03", False)),
        (ConstraintType.TEMPORAL,("t3", "t0", "c_u03", False)),
        (ConstraintType.TEMPORAL,("t1", "t2", "c_l12", False)),
        (ConstraintType.TEMPORAL,("t2", "t1", "c_u12", False)),
        (ConstraintType.TEMPORAL,("t2", "t3", "c_l23", False)),
        (ConstraintType.TEMPORAL,("t3", "t2", "c_u23", False)),
    ]
    constraint_network.propagate_constraints(constrs)

    chronicle.m_assertions[asrt1] = False        
    ts = time.perf_counter()
    res = chronicle.get_induced_conflicts([asrt2], constraint_network)
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

    asrt1 = Assertion(
        m_type=AssertionType.PERSISTENCE,
        m_sv_name="sv_location",
        m_sv_params_names=("param_robot"),
        m_sv_params_vars=("objvar_robots_grp1"),
        m_time_start="t0",
        m_time_end="t1",
        m_sv_val="objvar_location_A",
        m_sv_val_sec=None,
    )

    asrt2 = Assertion(
        m_type=AssertionType.TRANSITION,
        m_sv_name="sv_location",
        m_sv_params_names=("param_robot"),
        m_sv_params_vars=("objvar_robots_grp1"),
        m_time_start="t2",
        m_time_end="t3",
        m_sv_val="objvar_location_A",
        m_sv_val_sec="objvar_location_C",
    )

    if verbose:
        for v in constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, constraint_network.objvar_domain(v).get_values()))

    constrs = [
        (ConstraintType.TEMPORAL,("t0", "t1", "c_l01", False)),
        (ConstraintType.TEMPORAL,("t1", "t0", "c_u01", False)),
        (ConstraintType.TEMPORAL,("t0", "t3", "c_l03", False)),
        (ConstraintType.TEMPORAL,("t3", "t0", "c_u03", False)),
        (ConstraintType.TEMPORAL,("t1", "t2", "c_l12", False)),
        (ConstraintType.TEMPORAL,("t2", "t1", "c_u12", False)),
        (ConstraintType.TEMPORAL,("t2", "t3", "c_l23", False)),
        (ConstraintType.TEMPORAL,("t3", "t2", "c_u23", False)),
    ]
    constraint_network.propagate_constraints(constrs)

    chronicle.m_assertions[asrt1] = False        
    ts = time.perf_counter()
    res = chronicle.get_induced_conflicts([asrt2], constraint_network)
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
