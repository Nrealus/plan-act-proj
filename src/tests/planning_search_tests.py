import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

from src.constraints.domain import Domain
from src.constraints.constraints import ConstraintNetwork, ConstraintType

from src.assertion import Assertion, AssertionType
from src.actionmethod import ActionMethodTemplate, ActionMethod
from src.chronicle import Chronicle
from src.planning_search import SearchNode, SearchNodeType
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

def init_situation1(chronicle:Chronicle):
    chronicle.clear()
    chronicle.m_constraint_network.init_objvars({
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
    chronicle.m_constraint_network.init_tempvars({"t0":True,"t1":True,"t2":True,"t3":True})
    chronicle.m_constraint_network.propagate_constraints([
        (ConstraintType.TEMPORAL,("t0", "t1", "c_l01", False)),
        (ConstraintType.TEMPORAL,("t1", "t0", "c_u01", False)),
        (ConstraintType.TEMPORAL,("t0", "t3", "c_l03", False)),
        (ConstraintType.TEMPORAL,("t3", "t0", "c_u03", False)),
        (ConstraintType.TEMPORAL,("t1", "t2", "c_l12", False)),
        (ConstraintType.TEMPORAL,("t2", "t1", "c_u12", False)),
        (ConstraintType.TEMPORAL,("t2", "t3", "c_l23", False)),
        (ConstraintType.TEMPORAL,("t3", "t2", "c_u23", False)),
    ])


def test1(verbose=False):

    ####

    action_template = ActionMethodTemplate(
        p_type=ActionMethodTemplate.Type.ACTION,
        p_name="action_move",
        p_params=(
            ("p_robot","objvar_robots_all"),
            ("p_destination_location","objvar_locations_all"),
        ),
        p_assertions_func=lambda ts,te,params: set([
            Assertion(
                p_type=AssertionType.TRANSITION,
                p_sv_name="sv_location",
                p_sv_params_keys=("p_robot", "p_dest_location"),
                p_sv_params_values=(params["p_robot"],),
                p_sv_val=Domain._ANY_VALUE_VAR,
                p_sv_val_sec=params["p_dest_location"],
                p_time_start=ts,
                p_time_end=te,
        )]),
        p_constraints_func=lambda ts,te,_: set([
            (ConstraintType.TEMPORAL,(ts,te,-6,False)),
            (ConstraintType.TEMPORAL,(te,ts,11,False)),
        ])
    )

    ####

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

    constrs = []

    root_chronicle = Chronicle()
    init_situation1(root_chronicle)

    ok = root_chronicle.m_constraint_network.propagate_constraints(constrs)

    root_chronicle.m_assertions[asrt1] = True
    root_chronicle.m_goal_nodes.setdefault(asrt1, GoalNode()).m_mode = GoalMode.COMMITTED
    root_chronicle.m_causal_network[asrt1] = None

    root_chronicle.m_assertions[asrt2] = False
    root_chronicle.m_goal_nodes.setdefault(asrt2, GoalNode()).m_mode = GoalMode.SELECTED

    print(root_chronicle.m_assertions)

    root_search_node = SearchNode(
        p_node_type=SearchNodeType.FLAW,
        p_parent=None,
        p_time=1,
        p_state=None,
        p_chronicle=root_chronicle,
        p_action_method_templates_library=set(action_template),
    )
    
    if not ok:
        print("---")
        print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")
    else:
        ts = time.perf_counter()
        res = root_search_node.build_children()
        es = time.perf_counter()
        print("---")
        if verbose:
            _i = 0
            nodes = [root_search_node]
            while len(nodes) > 0:
                print("---{0}---".format(_i))
                _i += 1
                cur_node = nodes.pop(0)
                print(cur_node)
                cur_node.build_children()
                print(cur_node.m_children)
                nodes.extend(cur_node.m_children)
            print("time : {0}".format(es-ts))
        #if len(res) == 2:
        #    print(f"{bcolors.OKGREEN}SUCCESS !{bcolors.ENDC}")
        #else:
        #    print(f"{bcolors.FAIL}FAILURE !{bcolors.ENDC}")
        print("---")

test1(1)