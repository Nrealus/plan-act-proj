from __future__ import annotations

import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

import typing
from enum import Enum
from src.base import Assertion, AssertionType, Action, Method
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
        
        self.m_plan: typing.Dict[Action|Method,Action|Method] = {} # quick n dirty tree as an adjacency list
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

    def is_action_or_method_applicable(self,
        p_act_or_meth:Action|Method,
        p_time:str,
        p_assertion_to_support:Assertion=None
    ) -> typing.Iterable[typing.Tuple[Assertion,Assertion]]:#,bool]]:
        """
        Determines whether a (specified) action/method is applicable to this chronicle at a specified time.
        Used for planning search purposes.
        Arguments:
            p_act_or_meth (Action|Method):
                The action/method whose applicability to check for 
            p_time (str):
                Time at which to test for the applicability of the specified action/method
            p_assertion_to_support (Assertion):
                Assertion that must be supported by the action in order to applicable.
                None by default.
        Returns:
            If the action/method is not applicable - an empty list []
            If it is applicable - a list of (supportee, supporter) pairs of Assertions which would be established in the chronicle when applying the action/method
            As such, all of the action's/method's assertions starting at the same time as it must be present in all pairs as the first element.
            And at least one of the action's/method's assertions present as a second element (with an already present supportee assertion from the chronicle as first element)
        Side effects:
            None
        """
        # NOTE: maybe p_time should rather be a direct float "time instance", rather than a timepoint/variable
        # idea : instead of true/false, return the (supportee (chronicle assertion), supporter (action assertion), order)
        # order : true if supportee is from chronicle, and supporter is from action/method
        # will facilitate action insertion, by directly providing the assertions to become supported, instead of performing a new search again
        res = []
        backtracks_num = 1
        # the action/method's starting time must be "now" (p_time)
        if not self.m_constraint_network.propagate_constraints(p_act_or_meth.constraints):
            return []
        if self.m_constraint_network.tempvars_unified(p_act_or_meth.time_start,p_time):
            b1 = False
            b3 = (p_assertion_to_support == None)
            for i_act_or_meth_asrt in p_act_or_meth.assertions:
                b2 = False
                for i_chronicle_asrt in self.m_assertions:
                    # just in case
                    if i_act_or_meth_asrt == i_chronicle_asrt:
                        break
                    # the chronicle must support all action/method's assertions which start at the same time as it
                    if (not b2 and i_act_or_meth_asrt.is_causally_supported_by(i_chronicle_asrt, self.m_constraint_network)
                        and self.m_constraint_network.tempvars_unified(i_act_or_meth_asrt.time_start,p_time)
                    ):
                        res.append((i_act_or_meth_asrt, i_chronicle_asrt))
                        b2 = True
                        #backtracks_num += 1
                        if b1:
                            break
                    # the action/method must have at least one assertion (any, not necessarily starting at the same as it)
                    # supporting an unsupported assertion already present in the chronicle
                    if not b1 and i_chronicle_asrt.is_causally_supported_by(i_act_or_meth_asrt, self.m_constraint_network):
                        res.append((i_chronicle_asrt, i_act_or_meth_asrt))
                        b1 = True
                        if not b3 and i_chronicle_asrt == p_assertion_to_support:
                            b3 = True
                        if b2:
                            break
                if not b2:
                    for _ in range(backtracks_num):
                        self.m_constraint_network.backtrack()
                    return []
            if not b1 or not b3:
                for _ in range(backtracks_num):
                    self.m_constraint_network.backtrack()
                return []
        for _ in range(backtracks_num):
            self.m_constraint_network.backtrack()
        return res

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