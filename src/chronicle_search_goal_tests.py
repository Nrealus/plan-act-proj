import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

from src.constraints.domain import Domain
from src.constraints.constraints import ConstraintNetwork, ConstraintType

from src.base import Assertion, AssertionType, Action, Method
from src.chronicle import Chronicle
from src.goal_node import GoalNode, GoalMode

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

main_chronicle = Chronicle()

def print_obj_details2(u:str, v:str):

    print("details on {0} and {1} : ".format(u,v))
    print("   {0} and {1} unified : {2}".format(u,v,main_chronicle.m_constraint_network.objvars_unified(u,v)))
    print("   {0} and {1} unifiable : {2}".format(u,v,main_chronicle.m_constraint_network.objvars_unifiable(u,v)))
    print("   {0} and {1} separable : {2}".format(u,v,main_chronicle.m_constraint_network.objvars_separable(u,v)))
    print("   {0} and {1} separated : {2}".format(u,v,main_chronicle.m_constraint_network.objvars_separated(u,v)))

def print_temporal_details1(u:str, v:str):

    print("details on {0} and {1} : ".format(u,v))
    print("   {2} <= '{1}' - '{0}' <= {3}".format(
        u,v,
        main_chronicle.m_constraint_network.m_stn.m_minimal_network[(u,v)],
        main_chronicle.m_constraint_network.m_stn.m_minimal_network[(v,u)]))

def init_situation1():
    main_chronicle.clear()
    main_chronicle.m_constraint_network.declare_and_init_objvars({
        "objvar_robots_grp1":Domain(p_initial_allowed_values=["robot1","robot2"]),
        "objvar_robots_grp2":Domain(p_initial_allowed_values=["robot2","robot3"]),
        "objvar_robots_grp3":Domain(p_initial_allowed_values=["robot5","robot5"]),
        "objvar_location_A":Domain(p_initial_allowed_values=["location1", "location2"]),
        "objvar_location_B":Domain(p_initial_allowed_values=["location2", "location3"]),
        "objvar_location_C":Domain(p_initial_allowed_values=["location4", "location5"]),
        "c_l01":Domain(p_initial_allowed_values=[-1]),
        "c_u01":Domain(p_initial_allowed_values=[5]),
        "c_l03":Domain(p_initial_allowed_values=[-4]),
        "c_u03":Domain(p_initial_allowed_values=[25]),
        "c_l12":Domain(p_initial_allowed_values=[0]),
        "c_u12":Domain(p_initial_allowed_values=[2]),
        "c_l23":Domain(p_initial_allowed_values=[-1]),
        "c_u23":Domain(p_initial_allowed_values=[5]),
    })
    main_chronicle.m_constraint_network.m_stn.m_controllability["t0"] = True
    main_chronicle.m_constraint_network.m_stn.m_controllability["t1"] = True
    main_chronicle.m_constraint_network.m_stn.m_controllability["t2"] = True
    main_chronicle.m_constraint_network.m_stn.m_controllability["t3"] = True

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
        p_sv_params_names=("param_robot",),
        p_sv_params_vars=("objvar_robots_grp1",),
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
        p_sv_params_names=("param_robot",),
        p_sv_params_vars=("objvar_robots_grp1",),
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
        for v in main_chronicle.m_constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, main_chronicle.m_constraint_network.objvar_domain(v).get_values()))

    main_chronicle.m_constraint_network.propagate_constraints(constrs)

    #main_chronicle.m_assertions[asrt1] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt1,GoalNode()).m_mode = GoalMode.SELECTED

    #main_chronicle.m_assertions[asrt2] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt2,GoalNode()).m_mode = GoalMode.SELECTED

    ts = time.perf_counter()
    res = asrt1.is_causally_supported_by(asrt2, main_chronicle.m_constraint_network)
    es = time.perf_counter()
    print("---")
    if verbose:
        print("is causally supported : {0}".format(res))
        print("minimal temporal network : {0}".format(main_chronicle.m_constraint_network.m_stn.m_minimal_network))
        print("time : {0}".format(es-ts))
    if not res:
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
        p_sv_params_names=("param_robot",),
        p_sv_params_vars=("objvar_robots_grp1",),
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
        p_sv_params_names=("param_robot",),
        p_sv_params_vars=("objvar_robots_grp1",),
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
        for v in main_chronicle.m_constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, main_chronicle.m_constraint_network.objvar_domain(v).get_values()))

    main_chronicle.m_constraint_network.propagate_constraints(constrs)

    #main_chronicle.m_assertions[asrt1] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt1,GoalNode()).m_mode = GoalMode.SELECTED

    #main_chronicle.m_assertions[asrt2] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt2,GoalNode()).m_mode = GoalMode.SELECTED

    ts = time.perf_counter()
    res = asrt2.is_causally_supported_by(asrt1, main_chronicle.m_constraint_network)
    es = time.perf_counter()
    print("---")
    if verbose:
        print("is causally supported : {0}".format(res))
        print("minimal temporal network : {0}".format(main_chronicle.m_constraint_network.m_stn.m_minimal_network))
        print("time : {0}".format(es-ts))
    if not res:
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
        p_sv_params_names=("param_robot",),
        p_sv_params_vars=("objvar_robots_grp1",),
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
        p_sv_params_names=("param_robot",),
        p_sv_params_vars=("objvar_robots_grp1",),
        p_sv_val="objvar_location_A",
        p_sv_val_sec=None,
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
        for v in main_chronicle.m_constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, main_chronicle.m_constraint_network.objvar_domain(v).get_values()))

    main_chronicle.m_constraint_network.propagate_constraints(constrs)

    #main_chronicle.m_assertions[asrt1] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt1,GoalNode()).m_mode = GoalMode.SELECTED

    #main_chronicle.m_assertions[asrt2] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt2,GoalNode()).m_mode = GoalMode.SELECTED

    ts = time.perf_counter()
    res = asrt2.is_causally_supported_by(asrt1, main_chronicle.m_constraint_network)
    es = time.perf_counter()
    print("---")
    if verbose:
        print("is causally supported : {0}".format(res))
        print("minimal temporal network : {0}".format(main_chronicle.m_constraint_network.m_stn.m_minimal_network))
        print("time : {0}".format(es-ts))
    if res:
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
        p_sv_params_names=("param_robot",),
        p_sv_params_vars=("objvar_robots_grp1",),
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
        p_sv_params_names=("param_robot",),
        p_sv_params_vars=("objvar_robots_grp2",),
        p_sv_val="objvar_location_B",
        p_sv_val_sec=None,
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
        for v in main_chronicle.m_constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, main_chronicle.m_constraint_network.objvar_domain(v).get_values()))

    main_chronicle.m_constraint_network.propagate_constraints(constrs)

    #main_chronicle.m_assertions[asrt1] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt1,GoalNode()).m_mode = GoalMode.SELECTED

    #main_chronicle.m_assertions[asrt2] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt2,GoalNode()).m_mode = GoalMode.SELECTED

    ts = time.perf_counter()
    res = asrt2.is_causally_supported_by(asrt1, main_chronicle.m_constraint_network)
    es = time.perf_counter()
    print("---")
    if verbose:
        print("is causally supported : {0}".format(res))
        print("minimal temporal network : {0}".format(main_chronicle.m_constraint_network.m_stn.m_minimal_network))
        print("time : {0}".format(es-ts))
    if not res:
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
        p_sv_params_names=("param_robot",),
        p_sv_params_vars=("objvar_robots_grp1",),
        p_sv_val="objvar_location_B",
        p_sv_val_sec="objvar_location_A",
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
        p_sv_params_names=("param_robot",),
        p_sv_params_vars=("objvar_robots_grp1",),
        p_sv_val="objvar_location_A",
        p_sv_val_sec=None,
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
        for v in main_chronicle.m_constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, main_chronicle.m_constraint_network.objvar_domain(v).get_values()))

    main_chronicle.m_constraint_network.propagate_constraints(constrs)

    #main_chronicle.m_assertions[asrt1] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt1,GoalNode()).m_mode = GoalMode.SELECTED

    #main_chronicle.m_assertions[asrt2] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt2,GoalNode()).m_mode = GoalMode.SELECTED

    ts = time.perf_counter()
    res = asrt2.is_causally_supported_by(asrt1, main_chronicle.m_constraint_network)
    es = time.perf_counter()
    print("---")
    if verbose:
        print("is causally supported : {0}".format(res))
        print("minimal temporal network : {0}".format(main_chronicle.m_constraint_network.m_stn.m_minimal_network))
        print("time : {0}".format(es-ts))
    if res:
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

    asrt1 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
        p_sv_params_names=("param_robot",),
        p_sv_params_vars=("objvar_robots_grp1",),
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
        p_sv_params_names=("param_robot",),
        p_sv_params_vars=("objvar_robots_grp1",),
        p_sv_val="objvar_location_A",
        p_sv_val_sec=None,
    )
    constrs.extend([
#        (ConstraintType.TEMPORAL,("t0", asrt2.time_start, 0, False)),
#        (ConstraintType.TEMPORAL,("t0", asrt2.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_start, "t0", 0, False)),
        (ConstraintType.TEMPORAL,("t0", asrt2.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_end, "t3", 0, False)),
        (ConstraintType.TEMPORAL,("t3", asrt2.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_start, asrt2.time_end, 0, asrt2.type == AssertionType.TRANSITION)),
    ])

    if verbose:
        for v in main_chronicle.m_constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, main_chronicle.m_constraint_network.objvar_domain(v).get_values()))

    main_chronicle.m_constraint_network.propagate_constraints(constrs)

    #main_chronicle.m_assertions[asrt1] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt1,GoalNode()).m_mode = GoalMode.SELECTED

    #main_chronicle.m_assertions[asrt2] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt2,GoalNode()).m_mode = GoalMode.SELECTED

    ts = time.perf_counter()
    res = asrt2.is_causally_supported_by(asrt1, main_chronicle.m_constraint_network)
    es = time.perf_counter()
    print("---")
    if verbose:
        print("is causally supported : {0}".format(res))
        print("time : {0}".format(es-ts))
    if not res:
        print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
    print("---")


def test10(verbose=False):

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
        m_type=AssertionType.PERSISTENCE,
        m_sv_name="sv_location",
        m_sv_params_names=("param_robot",),
        m_sv_params_vars=("objvar_robots_grp1",),
        m_time_start="t0",
        m_time_end="t1",
        m_sv_val="objvar_location_A",
        m_sv_val_sec=None,
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
        m_type=AssertionType.PERSISTENCE,
        m_sv_name="sv_location",
        m_sv_params_names=("param_robot",),
        m_sv_params_vars=("objvar_robots_grp1",),
        m_time_start="t2",
        m_time_end="t3",
        m_sv_val="objvar_location_B",
        m_sv_val_sec=None,
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

    main_chronicle.m_constraint_network.declare_and_init_objvars({
        "c_any":Domain(p_initial_allowed_values=[Domain._ANY_VALUE]),
        "my_robot":Domain(p_initial_allowed_values=["robot1"]),
        "my_destination":Domain(p_initial_allowed_values=["location3"]),
    })
    main_chronicle.m_constraint_network.m_stn.m_controllability["ts_action1"] = True
    main_chronicle.m_constraint_network.m_stn.m_controllability["te_action1"] = True

    action1 = Action(
        m_action_name="a_move",
        m_action_params_names=("param_robot", "param_destination_location"),
        m_action_params_vars=("my_robot","my_destination"),
        m_time_start="ts_action1",
        m_time_end="te_action1",
        m_assertions=set([
            Assertion(
                m_type=AssertionType.TRANSITION,
                m_sv_name="sv_location",
                m_sv_params_names=("param_robot",),
                m_sv_params_vars=("my_robot",),
                m_sv_val="c_any",
                m_sv_val_sec="my_destination",
                m_time_start="ts_action1",
                m_time_end="te_action1"
        )]),
        m_constraints=set([
            (ConstraintType.TEMPORAL,("t1","ts_action1",0,False)),
            (ConstraintType.TEMPORAL,("ts_action1","te_action1",-4,False)),
            (ConstraintType.TEMPORAL,("te_action1","ts_action1",8,False)),
            (ConstraintType.TEMPORAL,("te_action1","t2",0,False)),
        ])
    )

    if verbose:
        for v in main_chronicle.m_constraint_network.m_bcn.m_domains:
            print("{0} initial domain : {1}".format(v, main_chronicle.m_constraint_network.objvar_domain(v).get_values()))

    main_chronicle.m_constraint_network.propagate_constraints(constrs)

    #main_chronicle.m_assertions[asrt1] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt1,GoalNode()).m_mode = GoalMode.SELECTED

    #main_chronicle.m_assertions[asrt2] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt2,GoalNode()).m_mode = GoalMode.SELECTED

    ts = time.perf_counter()
    res = main_chronicle.is_action_or_method_applicable(action1, "t1")
    es = time.perf_counter()
    print("---")
    if verbose:
        print("(supportee, supporter) pairs : {0}".format(res))
        print("time : {0}".format(es-ts))
    if len(res) == 2:
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
