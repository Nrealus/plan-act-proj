from __future__ import annotations

import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

import typing
from enum import Enum
from src.assertion import Assertion
from src.actionmethod import ActionMethod
from src.constraints.constraints import ConstraintNetwork, ConstraintType
from src.goal_node import GoalMode, GoalNode

############################################

# NOTE: Chronicle, 29 / 08 / 2022

# The chronicle is implemented here. It is one of the main building blocks of the planning system.

# A chronicle is a collection of temporal assertions and constraints on the variables appearing in them.
# Often, temporal assertions on a particular state variable and constraints on them are called timeline.
# We do not represent them explicitly, as we can do just fine representing temporal assertions and constraints directly,
# however an explicit representation of timelines to group assertions by state variables could be beneficial if 
# it proves to be more efficient algorithmically.

# A chronicle expresses temporal knowledge and temporal evolution of multiple state variables

class Chronicle():

    def __init__(self):
        # in bit-monnot 2022 there are also subtasks. adapting to subgoals seems weird, as subgoals can (are) already specified in unsupported assertions

        self.m_goal_nodes: typing.Dict[Assertion, GoalNode] = {}
        # also could instead create "extended assertions" extended with the goal node constructs (mode etc) - unifying "assertions" with "goals"

        self.m_assertions: typing.Dict[Assertion, bool] = {} # bool value : supported or not
        
        self.m_plan: typing.Dict[ActionMethod,ActionMethod] = {} # quick n dirty tree as an adjacency list
        # actions (or their operational model) in the plan will be triggered / executed and will transition the goal nodes for
        # their assertions to "dispatched" mode.

        # in the case of assertions that are spawned from an action, store that action
        # when this action will be triggered during acting (for example in a bt) during its execution, it will have to make sure 
        # that the current state is indeed conformant to those assertions
        # in other words, this action (in BT, for example) will make sure to execute the commands to follow these assertions
        # and monitor the correctness of their execution (- basically monitoring)
        # in the case of assertions that do not spawn from actions directly (like persistence assertions introduced as direct supporters)
        # create a simple action which only corresponds to monitoring the state of the assertion (i.e. only monitoring,
        # not actuating, as that would be done by "real" actions (like in the first case) having transitions/assignment assertions)
        # the concrete instantiation of such actions (for the second case) could even be defered to the last moment before dispatching...?

        #self.m_supporter_origin_commitment: typing.Dict[Assertion, Method] = {} # commitment on the origin of the supporter to choose for an unsupported assertion (<-> "supporting task commitments" FAPE 2020)
        # NOTE: not necessary, as this information can already be found in the committed expansion of the goal node
        # if in resolver info the resolver type is appropriate and the method/action instance is not None, then we know the origin
        # of the supporter (even if it is decided later, which is possible in case of methods, not actions)

        self.m_causal_network: typing.Dict[Assertion, Assertion] = {} # value : supporter assertion. if a priori supported : None
        
        self.m_conflicts: typing.Set[typing.Tuple[Assertion,Assertion]] = set()

        # efficient way of accessing constraints involving variables from a specified assertion ?
        self.m_constraint_network: ConstraintNetwork = ConstraintNetwork()
        #self.m_actions = [] - in GNT 2016 (book) - "a set A of temporally qualified primitives and tasks"...

    def clear(self):
        
        self.m_goal_nodes = {}
        self.m_assertions = {}
        self.m_plan = {}
        #self.m_supporter_origin_commitment = {}
        self.m_causal_network = {}
        #self.m_constraints = []        
        self.m_constraint_network = ConstraintNetwork()
        #self.m_constraint_network.m_bcn.clear()
        #self.m_constraint_network.m_stn.clear()

    def get_induced_conflicts(self, p_new_assertions:typing.Iterable[Assertion]) -> typing.Set[typing.Tuple[Assertion,Assertion]]:
        """
        Determines the conflicting assertions which would appear in this chronicle if the specified input assertions were introduced to the chronicle.
        Used for planning search purposes in an incremental way.
        Arguments:
            p_new_assertions (Iterable[Assertion]):
                The input assertions to test
        Returns:
            Returns pairs of conflicting assertions which would get introduced if the specified input assertions were added to the chronicle
        Side effects:
            None
        """
        res:typing.Set[typing.Tuple[Assertion,Assertion]] = set()
        # naive brute force implementation
        # can use heuristics, info accumulated during search etc for inference (causal chains etc) to restrict the search / candidate flaws
        for new_asrt in p_new_assertions:
            for asrt in self.m_assertions:
                #FIXME: don't forget about this goal mode thing
                #if (self.m_goal_nodes.setdefault(asrt,GoalNode()).m_mode != GoalMode.FORMULATED
                #    and asrt.check_conflict(new_asrt, self.m_constraint_network)
                #):# and not (new_asrt, asrt) in res:
                if asrt.check_conflict(new_asrt, self.m_constraint_network):
                    res.add((asrt,new_asrt))
        return res