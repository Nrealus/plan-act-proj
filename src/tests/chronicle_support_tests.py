import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

from src.constraints.domain import Domain
from src.constraints.constraints import ConstraintNetwork, ConstraintType

from src.assertion import Assertion, AssertionType
from src.actionmethod import ActionMethodTemplate, ActionMethod
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

def init_situation1():
    main_chronicle.clear()
    main_chronicle.m_constraint_network.init_objvars({
        "objvar_robots_all":Domain(p_initial_allowed_values=["robot1","robot2","robot3","robot4","robot5"]),
        "objvar_robots_grp1":Domain(p_initial_allowed_values=["robot1","robot2"]),
        "objvar_robots_grp2":Domain(p_initial_allowed_values=["robot2","robot3"]),
        "objvar_robots_grp3":Domain(p_initial_allowed_values=["robot4","robot5"]),
        "objvar_locations_all":Domain(p_initial_allowed_values=["location1","location2","location3","location4","location5"]),
        "objvar_location_A":Domain(p_initial_allowed_values=["location1", "location2"]),
        "objvar_location_B":Domain(p_initial_allowed_values=["location2", "location3"]),
        "objvar_location_C":Domain(p_initial_allowed_values=["location4", "location5"]),
        "c_l01":Domain(p_initial_allowed_values=[-1]),
        "c_u01":Domain(p_initial_allowed_values=[5]),
        "c_l03":Domain(p_initial_allowed_values=[-4]),
        "c_u03":Domain(p_initial_allowed_values=[25]),
        "c_l12":Domain(p_initial_allowed_values=[-5]),
        "c_u12":Domain(p_initial_allowed_values=[10]),
        "c_l23":Domain(p_initial_allowed_values=[-1]),
        "c_u23":Domain(p_initial_allowed_values=[5]),
    })
    main_chronicle.m_constraint_network.init_tempvars({"t0":True,"t1":True,"t2":True,"t3":True})

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
        p_sv_params=(("param_robot","objvar_robots_grp1"),),
        p_sv_val="objvar_location_A",
        p_sv_val_sec=None,
        p_time_start="t0",
        p_time_end="t1",
    )

    asrt2 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
        p_sv_params=(("param_robot","objvar_robots_grp1"),),
        p_sv_val="objvar_location_A",
        p_sv_val_sec=None,
        p_time_start="t2",
        p_time_end="t3"
    )

    if verbose:
        for v in main_chronicle.m_constraint_network.m_bcn.domains:
            print("{0} initial domain : {1}".format(v, main_chronicle.m_constraint_network.objvar_domain(v).get_values()))

    ok = main_chronicle.m_constraint_network.propagate_constraints(constrs)

    if verbose:
        print("minimal temporal network : {0}".format(main_chronicle.m_constraint_network.m_stn.minimal_network))

    if not ok:
        print("---")
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")
    else:
        ts = time.perf_counter()
        res = asrt1.propagate_causal_support_by(asrt2, main_chronicle.m_constraint_network)
        es = time.perf_counter()
        print("---")
        if verbose:
            print("is causally supported : {0}".format(res[0]))
            print("time : {0}".format(es-ts))
        if not res[0]:
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
        p_sv_params=(("param_robot","objvar_robots_grp1"),),
        p_sv_val="objvar_location_A",
        p_sv_val_sec=None,
        p_time_start="t0",
        p_time_end="t1",
    )

    asrt2 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
        p_sv_params=(("param_robot","objvar_robots_grp1"),),
        p_sv_val="objvar_location_A",
        p_sv_val_sec=None,
        p_time_start="t2",
        p_time_end="t3"
    )

    if verbose:
        for v in main_chronicle.m_constraint_network.m_bcn.domains:
            print("{0} initial domain : {1}".format(v, main_chronicle.m_constraint_network.objvar_domain(v).get_values()))

    ok = main_chronicle.m_constraint_network.propagate_constraints(constrs)

    if verbose:
        print("minimal temporal network : {0}".format(main_chronicle.m_constraint_network.m_stn.minimal_network))

    if not ok:
        print("---")
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")
    else:
        ts = time.perf_counter()
        res = asrt2.propagate_causal_support_by(asrt1, main_chronicle.m_constraint_network)
        es = time.perf_counter()
        print("---")
        if verbose:
            print("is causally supported : {0}".format(res[0]))
            print("time : {0}".format(es-ts))
        if not res[0]:
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
        p_sv_params=(("param_robot","objvar_robots_grp1"),),
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
        p_sv_params=(("param_robot","objvar_robots_grp1"),),
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
        for v in main_chronicle.m_constraint_network.m_bcn.domains:
            print("{0} initial domain : {1}".format(v, main_chronicle.m_constraint_network.objvar_domain(v).get_values()))

    ok = main_chronicle.m_constraint_network.propagate_constraints(constrs)

    if verbose:
        print("minimal temporal network : {0}".format(main_chronicle.m_constraint_network.m_stn.minimal_network))

    if not ok:
        print("---")
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")
    else:
        ts = time.perf_counter()
        res = asrt2.propagate_causal_support_by(asrt1, main_chronicle.m_constraint_network)
        es = time.perf_counter()
        print("---")
        if verbose:
            print("is causally supported : {0}".format(res[0]))
            print("time : {0}".format(es-ts))
        if res[0]:
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
        p_sv_params=(("param_robot","objvar_robots_grp1"),),
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
        p_sv_params=(("param_robot","objvar_robots_grp2"),),
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
        for v in main_chronicle.m_constraint_network.m_bcn.domains:
            print("{0} initial domain : {1}".format(v, main_chronicle.m_constraint_network.objvar_domain(v).get_values()))

    ok = main_chronicle.m_constraint_network.propagate_constraints(constrs)

    if verbose:
        print("minimal temporal network : {0}".format(main_chronicle.m_constraint_network.m_stn.minimal_network))

    if not ok:
        print("---")
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")
    else:
        ts = time.perf_counter()
        res = asrt2.propagate_causal_support_by(asrt1, main_chronicle.m_constraint_network)
        es = time.perf_counter()
        print("---")
        if verbose:
            print("is causally supported : {0}".format(res[0]))
            print("time : {0}".format(es-ts))
        if res[0]:
            print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")

def test4_1(verbose=False):

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
        p_sv_params=(("param_robot","objvar_robots_grp1"),),
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
        p_sv_params=(("param_robot","objvar_robots_grp3"),),
        p_sv_val="objvar_location_C",
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
        for v in main_chronicle.m_constraint_network.m_bcn.domains:
            print("{0} initial domain : {1}".format(v, main_chronicle.m_constraint_network.objvar_domain(v).get_values()))

    ok = main_chronicle.m_constraint_network.propagate_constraints(constrs)

    if verbose:
        print("minimal temporal network : {0}".format(main_chronicle.m_constraint_network.m_stn.minimal_network))

    if not ok:
        print("---")
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")
    else:
        ts = time.perf_counter()
        res = asrt2.propagate_causal_support_by(asrt1, main_chronicle.m_constraint_network)
        es = time.perf_counter()
        print("---")
        if verbose:
            print("is causally supported : {0}".format(res[0]))
            print("time : {0}".format(es-ts))
        if not res[0]:
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
        p_sv_params=(("param_robot","objvar_robots_grp1"),),
        p_sv_val="objvar_location_B",
        p_sv_val_sec="objvar_location_A",
    )
    constrs.extend([
        (ConstraintType.TEMPORAL,(asrt1.time_start, "t0", 0, False)),
        (ConstraintType.TEMPORAL,("t0", asrt1.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_end, "t1", 0, False)),
        (ConstraintType.TEMPORAL,("t1", asrt1.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_start, asrt1.time_end, 0, asrt1.type == AssertionType.TRANSITION)),
    ])
    
    asrt2 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
        p_sv_params=(("param_robot","objvar_robots_grp1"),),
        p_sv_val="objvar_location_A",
        p_sv_val_sec=None,
    )
    constrs.extend([
        (ConstraintType.TEMPORAL,(asrt2.time_start, "t1", 0, False)),
        (ConstraintType.TEMPORAL,("t1", asrt2.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_end, "t3", 0, False)),
        (ConstraintType.TEMPORAL,("t3", asrt2.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_start, asrt2.time_end, 0, asrt2.type == AssertionType.TRANSITION)),
    ])
        
    if verbose:
        for v in main_chronicle.m_constraint_network.m_bcn.domains:
            print("{0} initial domain : {1}".format(v, main_chronicle.m_constraint_network.objvar_domain(v).get_values()))

    ok = main_chronicle.m_constraint_network.propagate_constraints(constrs)

    if verbose:
        print("minimal temporal network : {0}".format(main_chronicle.m_constraint_network.m_stn.minimal_network))

    if not ok:
        print("---")
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")
    else:
        ts = time.perf_counter()
        res = asrt2.propagate_causal_support_by(asrt1, main_chronicle.m_constraint_network)
        es = time.perf_counter()
        print("---")
        if verbose:
            print("is causally supported : {0}".format(res[0]))
            print("time : {0}".format(es-ts))
        if res[0]:
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
        p_sv_params=(("param_robot","objvar_robots_grp1"),),
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
        p_sv_params=(("param_robot","objvar_robots_grp1"),),
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
        for v in main_chronicle.m_constraint_network.m_bcn.domains:
            print("{0} initial domain : {1}".format(v, main_chronicle.m_constraint_network.objvar_domain(v).get_values()))

    ok = main_chronicle.m_constraint_network.propagate_constraints(constrs)

    if verbose:
        print("minimal temporal network : {0}".format(main_chronicle.m_constraint_network.m_stn.minimal_network))

    if not ok:
        print("---")
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")
    else:
        ts = time.perf_counter()
        res = asrt2.propagate_causal_support_by(asrt1, main_chronicle.m_constraint_network)
        es = time.perf_counter()
        print("---")
        if verbose:
            print("is causally supported : {0}".format(res[0]))
            print("time : {0}".format(es-ts))
        if not res[0]:
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
    
    main_chronicle.m_constraint_network.init_objvars({
        "my_robot":Domain(p_initial_allowed_values=["robot1","robot2","robot3"]),
        "my_destination":Domain(p_initial_allowed_values=["location1", "location2", "location3"])
    })

    action_template = ActionMethodTemplate(
        p_type=ActionMethodTemplate.Type.ACTION,
        p_name="action_move",
        p_param_domain_vars=(
            ("p_robot","objvar_robots_all"),
            ("p_dest_location","objvar_locations_all"),
        ),
        p_assertions_func=lambda ts,te,param_args: set([
            Assertion(
                p_type=AssertionType.TRANSITION,
                p_sv_name="sv_location",
                p_sv_params=(("p_robot",param_args["p_robot"]),),
                p_sv_val=Domain._ANY_VALUE_VAR,
                p_sv_val_sec=param_args["p_dest_location"],
                p_time_start=ts,
                p_time_end=te,
        )]),
        p_constraints_func=lambda ts,te,params: set([
            (ConstraintType.TEMPORAL,(ts,te,-6,False)),
            (ConstraintType.TEMPORAL,(te,ts,6,False)),
        ])
    )

    action1 = ActionMethod(
        p_template=action_template,
        p_param_arg_vars=(("p_robot", "my_robot"), ("p_dest_location","my_destination")),
        p_name="",
        p_time_start="t1",
        p_time_end="t2"
    )
    #constrs.extend([
    #    (ConstraintType.UNIFICATION,(action1.args["p_robot"],"objvar_robots_grp1")),
    #    (ConstraintType.UNIFICATION,(action1.args["p_dest_location"],"objvar_location_B")),
    #])
    
    asrt1 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
            p_sv_params=(("p_robot","objvar_robots_grp1"),),
        p_sv_val="objvar_location_A",
        p_sv_val_sec=None,
        p_time_start="t0",
        p_time_end="t1",
    )
    
    asrt2 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
            p_sv_params=(("p_robot","objvar_robots_grp1"),),
        p_sv_val="objvar_location_B",
        p_sv_val_sec=None,
        p_time_start="t2",
        p_time_end="t3",
    )
    
    if verbose:
        for v in main_chronicle.m_constraint_network.m_bcn.domains:
            print("{0} initial domain : {1}".format(v, main_chronicle.m_constraint_network.objvar_domain(v).get_values()))

    main_chronicle.m_assertions[asrt1] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt1,GoalNode()).m_mode = GoalMode.SELECTED
    main_chronicle.m_assertions[asrt2] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt2,GoalNode()).m_mode = GoalMode.SELECTED

    ok = main_chronicle.m_constraint_network.propagate_constraints(constrs)

    if verbose:
        print("minimal temporal network : {0}".format(main_chronicle.m_constraint_network.m_stn.minimal_network))

    if not ok:
        print("---")
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")
    else:
        ts = time.perf_counter()
        res = action1.propagate_applicability(
            p_time="t1",
            p_cn=main_chronicle.m_constraint_network,
            p_assertions=main_chronicle.m_assertions
        )
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

def test11(verbose=False):

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
    
    main_chronicle.m_constraint_network.init_objvars({
        "my_robot":Domain(p_initial_allowed_values=["robot1","robot2","robot3"]),
        "my_destination":Domain(p_initial_allowed_values=["location1", "location2", "location3"])
    })

    action_template = ActionMethodTemplate(
        p_type=ActionMethodTemplate.Type.ACTION,
        p_name="action_move",
        p_param_domain_vars=(
            ("p_robot","objvar_robots_all"),
            ("p_dest_location","objvar_locations_all"),
        ),
        p_assertions_func=lambda ts,te,param_args: set([
            Assertion(
                p_type=AssertionType.TRANSITION,
                p_sv_name="sv_location",
                p_sv_params=(("p_robot",param_args["p_robot"]),),
                p_sv_val=Domain._ANY_VALUE_VAR,
                p_sv_val_sec=param_args["p_dest_location"],
                p_time_start=ts,
                p_time_end=te,
        )]),
        p_constraints_func=lambda ts,te,params: set([
            (ConstraintType.TEMPORAL,(ts,te,-6,False)),
            (ConstraintType.TEMPORAL,(te,ts,6,False)),
        ])
    )

    action1 = ActionMethod(
        p_template=action_template,
        p_param_arg_vars=(("p_robot", "my_robot"), ("p_dest_location","my_destination")),
        p_name="",
        p_time_start="t1",
        p_time_end="t2"
    )
    constrs.extend([
        (ConstraintType.UNIFICATION,(action1.param_arg_vars[0][1],"objvar_robots_grp1")),
        (ConstraintType.UNIFICATION,(action1.param_arg_vars[1][1],"objvar_location_B")),
    ])
    
    asrt1 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
            p_sv_params=(("p_robot","objvar_robots_grp1"),),
        p_sv_val="objvar_location_A",
        p_sv_val_sec=None,
        p_time_start="t0",
        p_time_end="t1",
    )
    
    asrt2 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
            p_sv_params=(("p_robot","objvar_robots_grp1"),),
        p_sv_val="objvar_location_B",
        p_sv_val_sec=None,
        p_time_start="t2",
        p_time_end="t3",
    )
    
    if verbose:
        for v in main_chronicle.m_constraint_network.m_bcn.domains:
            print("{0} initial domain : {1}".format(v, main_chronicle.m_constraint_network.objvar_domain(v).get_values()))

    main_chronicle.m_assertions[asrt1] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt1,GoalNode()).m_mode = GoalMode.SELECTED
    main_chronicle.m_assertions[asrt2] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt2,GoalNode()).m_mode = GoalMode.SELECTED

    ok = main_chronicle.m_constraint_network.propagate_constraints(constrs)

    if verbose:
        print("minimal temporal network : {0}".format(main_chronicle.m_constraint_network.m_stn.minimal_network))

    if not ok:
        print("---")
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")
    else:
        ts = time.perf_counter()
        res = action1.propagate_applicability(
            p_time="t2",
            p_cn=main_chronicle.m_constraint_network,
            p_assertions=main_chronicle.m_assertions
        )
        es = time.perf_counter()
        print("---")
        if verbose:
            print("(supportee, supporter) pairs : {0}".format(res))
            print("time : {0}".format(es-ts))
        if res == []:
            print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")

def test12(verbose=False):

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
    
    main_chronicle.m_constraint_network.init_objvars({
        "my_robot":Domain(p_initial_allowed_values=["robot1","robot2","robot3"]),
        "my_destination":Domain(p_initial_allowed_values=["location1", "location2", "location3"])
    })

    action_template = ActionMethodTemplate(
        p_type=ActionMethodTemplate.Type.ACTION,
        p_name="action_move",
        p_param_domain_vars=(
            ("p_robot","objvar_robots_all"),
            ("p_dest_location","objvar_locations_all"),
        ),
        p_assertions_func=lambda ts,te,param_args: set([
            Assertion(
                p_type=AssertionType.TRANSITION,
                p_sv_name="sv_location",
                p_sv_params=(("p_robot",param_args["p_robot"]),),
                p_sv_val=Domain._ANY_VALUE_VAR,
                p_sv_val_sec=param_args["p_dest_location"],
                p_time_start=ts,
                p_time_end=te,
        )]),
        p_constraints_func=lambda ts,te,params: set([
            (ConstraintType.TEMPORAL,(ts,te,-6,False)),
            (ConstraintType.TEMPORAL,(te,ts,6,False)),
        ])
    )

    action1 = ActionMethod(
        p_template=action_template,
        p_param_arg_vars=(("p_robot", "my_robot"), ("p_dest_location","my_destination")),
        p_name="",
        p_time_start="",
        p_time_end=""
    )
    constrs.extend([
        (ConstraintType.UNIFICATION,(action1.param_arg_vars[0][1],"objvar_robots_grp1")),
        (ConstraintType.UNIFICATION,(action1.param_arg_vars[1][1],"objvar_location_B")),
        (ConstraintType.TEMPORAL,(action1.time_start, "t1", 0, False)),
        (ConstraintType.TEMPORAL,("t1", action1.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(action1.time_end, "t2", 0, False)),
        (ConstraintType.TEMPORAL,("t2", action1.time_end, 0, False)),
    ])
    
    asrt1 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
            p_sv_params=(("p_robot","objvar_robots_grp1"),),
        p_sv_val="objvar_location_A",
        p_sv_val_sec=None,
    )
    constrs.extend([
        (ConstraintType.TEMPORAL,(asrt1.time_start, "t0", 0, False)),
        (ConstraintType.TEMPORAL,("t0", asrt1.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_end, "t1", 0, False)),
        (ConstraintType.TEMPORAL,("t1", asrt1.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_start, asrt1.time_end, 0, asrt1.type == AssertionType.TRANSITION)),
    ])
    
    asrt2 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
            p_sv_params=(("p_robot","objvar_robots_grp1"),),
        p_sv_val="objvar_location_B",
        p_sv_val_sec=None,
    )
    constrs.extend([
        (ConstraintType.TEMPORAL,(asrt2.time_start, "t2", 0, False)),
        (ConstraintType.TEMPORAL,("t2", asrt2.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_end, "t3", 0, False)),
        (ConstraintType.TEMPORAL,("t3", asrt2.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_start, asrt2.time_end, 0, asrt2.type == AssertionType.TRANSITION)),
    ])
    
    if verbose:
        for v in main_chronicle.m_constraint_network.m_bcn.domains:
            print("{0} initial domain : {1}".format(v, main_chronicle.m_constraint_network.objvar_domain(v).get_values()))

    main_chronicle.m_assertions[asrt1] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt1,GoalNode()).m_mode = GoalMode.SELECTED
    main_chronicle.m_assertions[asrt2] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt2,GoalNode()).m_mode = GoalMode.SELECTED

    ok = main_chronicle.m_constraint_network.propagate_constraints(constrs)

    if verbose:
        print("minimal temporal network : {0}".format(main_chronicle.m_constraint_network.m_stn.minimal_network))

    if not ok:
        print("---")
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")
    else:
        ts = time.perf_counter()
        res = action1.propagate_applicability(
            p_time="t1",
            p_cn=main_chronicle.m_constraint_network,
            p_assertions=main_chronicle.m_assertions)
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

def test13(verbose=False):

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
    
    main_chronicle.m_constraint_network.init_objvars({
        "my_robot":Domain(p_initial_allowed_values=["robot1","robot2","robot3"]),
        "my_destination":Domain(p_initial_allowed_values=["location1", "location2", "location3"])
    })

    action_template = ActionMethodTemplate(
        p_type=ActionMethodTemplate.Type.ACTION,
        p_name="action_move",
        p_param_domain_vars=(
            ("p_robot","objvar_robots_all"),
            ("p_dest_location","objvar_locations_all"),
        ),
        p_assertions_func=lambda ts,te,param_args: set([
            Assertion(
                p_type=AssertionType.TRANSITION,
                p_sv_name="sv_location",
                p_sv_params=(("p_robot",param_args["p_robot"]),),
                p_sv_val=Domain._ANY_VALUE_VAR,
                p_sv_val_sec=param_args["p_dest_location"],
                p_time_start=ts,
                p_time_end=te,
        )]),
        p_constraints_func=lambda ts,te,params: set([
            (ConstraintType.TEMPORAL,(ts,te,-1,False)),
            (ConstraintType.TEMPORAL,(te,ts,4,False)),
        ])
    )

    action1 = ActionMethod(
        p_template=action_template,
        p_param_arg_vars=(("p_robot", "my_robot"), ("p_dest_location","my_destination")),
        p_name="",
        p_time_start="t1",
        p_time_end="t2"
    )

    constrs.extend([
        (ConstraintType.UNIFICATION,(action1.param_arg_vars[0][1],"objvar_robots_grp1")),
        (ConstraintType.UNIFICATION,(action1.param_arg_vars[1][1],"objvar_location_B")),
    ])

    asrt1 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
            p_sv_params=(("p_robot","objvar_robots_grp1"),),
        p_sv_val="objvar_location_A",
        p_sv_val_sec=None,
    )
    constrs.extend([
        (ConstraintType.TEMPORAL,(asrt1.time_start, "t0", 0, False)),
        (ConstraintType.TEMPORAL,("t0", asrt1.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_end, "t1", 0, False)),
        (ConstraintType.TEMPORAL,("t1", asrt1.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_start, asrt1.time_end, 0, asrt1.type == AssertionType.TRANSITION)),
    ])
    
    asrt2 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
            p_sv_params=(("p_robot","objvar_robots_grp1"),),
        p_sv_val="objvar_location_B",
        p_sv_val_sec=None,
    )
    constrs.extend([
        (ConstraintType.TEMPORAL,(asrt2.time_start, "t2", 0, False)),
        (ConstraintType.TEMPORAL,("t2", asrt2.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_end, "t3", 0, False)),
        (ConstraintType.TEMPORAL,("t3", asrt2.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_start, asrt2.time_end, 0, asrt2.type == AssertionType.TRANSITION)),
    ])
    
    if verbose:
        for v in main_chronicle.m_constraint_network.m_bcn.domains:
            print("{0} initial domain : {1}".format(v, main_chronicle.m_constraint_network.objvar_domain(v).get_values()))

    main_chronicle.m_assertions[asrt1] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt1,GoalNode()).m_mode = GoalMode.SELECTED
    main_chronicle.m_assertions[asrt2] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt2,GoalNode()).m_mode = GoalMode.SELECTED

    ok = main_chronicle.m_constraint_network.propagate_constraints(constrs)

    if verbose:
        print("minimal temporal network : {0}".format(main_chronicle.m_constraint_network.m_stn.minimal_network))

    if not ok:
        print("---")
        print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
        print("---")
    else:
        ts = time.perf_counter()
        res = action1.propagate_applicability(
            p_time="t1",
            p_cn=main_chronicle.m_constraint_network,
            p_assertions=main_chronicle.m_assertions)
        es = time.perf_counter()
        print("---")
        if verbose:
            print("(supportee, supporter) pairs : {0}".format(res))
            print("time : {0}".format(es-ts))
        if res == []:
            print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")

def test14(verbose=False):

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
    
    main_chronicle.m_constraint_network.init_objvars({
        "my_robot":Domain(p_initial_allowed_values=["robot1","robot2","robot3"]),
        "my_destination":Domain(p_initial_allowed_values=["location1", "location2", "location3"])
    })

    action_template = ActionMethodTemplate(
        p_type=ActionMethodTemplate.Type.ACTION,
        p_name="action_move",
        p_param_domain_vars=(
            ("p_robot","objvar_robots_all"),
            ("p_dest_location","objvar_locations_all"),
        ),
        p_assertions_func=lambda ts,te,param_args: set([
            Assertion(
                p_type=AssertionType.TRANSITION,
                p_sv_name="sv_location",
                p_sv_params=(("p_robot",param_args["p_robot"]),),
                p_sv_val=Domain._ANY_VALUE_VAR,
                p_sv_val_sec=param_args["p_dest_location"],
                p_time_start=ts,
                p_time_end=te,
        )]),
        p_constraints_func=lambda ts,te,params: set([
            (ConstraintType.TEMPORAL,(ts,te,-1,False)),
            (ConstraintType.TEMPORAL,(te,ts,4,False)),
        ])
    )

    action1 = ActionMethod(
        p_template=action_template,
        p_param_arg_vars=(("p_robot", "my_robot"), ("p_dest_location","my_destination")),
        p_name="",
        p_time_start="",
        p_time_end=""
    )
    constrs.extend([
        (ConstraintType.TEMPORAL,("t1",action1.time_start,0,False)),
        (ConstraintType.TEMPORAL,(action1.time_start,"t1",0,False)),
        (ConstraintType.TEMPORAL,("t2",action1.time_end,0,False)),
        (ConstraintType.TEMPORAL,(action1.time_end,"t2",0,False)),
        (ConstraintType.TEMPORAL,(action1.time_start,action1.time_end,-1,False)),
        (ConstraintType.TEMPORAL,(action1.time_end,action1.time_start,4,False)),
    ])

    asrt1 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
            p_sv_params=(("p_robot","objvar_robots_grp1"),),
        p_sv_val="objvar_location_A",
        p_sv_val_sec=None,
    )
    constrs.extend([
        (ConstraintType.TEMPORAL,(asrt1.time_start, "t0", 0, False)),
        (ConstraintType.TEMPORAL,("t0", asrt1.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_end, "t1", 0, False)),
        (ConstraintType.TEMPORAL,("t1", asrt1.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt1.time_start, asrt1.time_end, 0, asrt1.type == AssertionType.TRANSITION)),
    ])
    
    asrt2 = Assertion(
        p_type=AssertionType.PERSISTENCE,
        p_sv_name="sv_location",
            p_sv_params=(("p_robot","objvar_robots_grp1"),),
        p_sv_val="objvar_location_B",
        p_sv_val_sec=None,
    )
    constrs.extend([
        (ConstraintType.TEMPORAL,(asrt2.time_start, "t2", 0, False)),
        (ConstraintType.TEMPORAL,("t2", asrt2.time_start, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_end, "t3", 0, False)),
        (ConstraintType.TEMPORAL,("t3", asrt2.time_end, 0, False)),
        (ConstraintType.TEMPORAL,(asrt2.time_start, asrt2.time_end, 0, asrt2.type == AssertionType.TRANSITION)),
    ])
    
    if verbose:
        for v in main_chronicle.m_constraint_network.m_bcn.domains:
            print("{0} initial domain : {1}".format(v, main_chronicle.m_constraint_network.objvar_domain(v).get_values()))

    main_chronicle.m_assertions[asrt1] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt1,GoalNode()).m_mode = GoalMode.SELECTED
    main_chronicle.m_assertions[asrt2] = False
    #main_chronicle.m_goal_nodes.setdefault(asrt2,GoalNode()).m_mode = GoalMode.SELECTED

    ok = main_chronicle.m_constraint_network.propagate_constraints(constrs)

    if verbose:
        print("minimal temporal network : {0}".format(main_chronicle.m_constraint_network.m_stn.minimal_network))

    if not ok:
        print("---")
        print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
        print("---")
    else:
        ts = time.perf_counter()
        res = action1.propagate_applicability(
            p_time="t1",
            p_cn=main_chronicle.m_constraint_network,
            p_assertions=main_chronicle.m_assertions)
        es = time.perf_counter()
        print("---")
        if verbose:
            print("(supportee, supporter) pairs : {0}".format(res))
            print("time : {0}".format(es-ts))
        if res == []:
            print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")

test1()
test2()
test3()
test4()
test4_1()
test5()
test6()
test10()
test11()
test12()
test13()
test14()

