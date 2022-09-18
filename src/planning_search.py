from __future__ import annotations
from dataclasses import dataclass
from poplib import POP3_SSL

import sys

sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

import typing
from enum import Enum
from copy import deepcopy
from src.utility.new_int_id import new_int_id
from src.utility.powerset import powerset
from src.constraints.domain import Domain
from src.constraints.constraints import ConstraintNetwork, ConstraintType
from src.assertion import Assertion, AssertionType
from src.actionmethod import ActionMethodTemplate, ActionMethod
from src.chronicle import Chronicle
from src.goal_node import GoalMode, GoalNode

class SearchNodeType(Enum):
    FLAW = 0
    RESOLVER = 1
    CHARLIE = 2
    EVE = 3

class ResolverType(Enum):
    CONFLICT_SEPARATION=0
    EXISTING_DIRECT_PERSISTENCE_SUPPORT_NOW=1
    NEW_DIRECT_PERSISTENCE_SUPPORT_NOW=2
    METHOD_INSERTION_NOW=3
    ACTION_INSERTION_NOW=4

class FlawNodeInfo():
    def __init__(self,
        p_assertion1:Assertion,
        p_assertion2:Assertion
    ):
        self.m_assertion1:Assertion=p_assertion1
        self.m_assertion2:Assertion=p_assertion2
        # if assertion2 is None, then the flaw is an unsupportd assertion / open goal flaw
        # if not, then the flaw is a (possibly) conflicting assertions flaw

class ResolverNodeInfo():
    def __init__(self,
        p_type:ResolverType,
        p_direct_support_assertion:Assertion,
        p_direct_support_assertion_supporter:Assertion,
        p_new_constraint_network:ConstraintNetwork,
        p_new_constraints:typing.Set[typing.Tuple[ConstraintType,typing.Any]],
        p_action_or_method_instance:ActionMethod,
        p_action_or_method_assertion_support_info:typing.Set[typing.Tuple[Assertion,Assertion]],
    ):
        self.m_type:ResolverType=p_type
        self.m_direct_support_assertion:Assertion=p_direct_support_assertion
        self.m_direct_support_assertion_supporter:Assertion=p_direct_support_assertion_supporter
        self.m_new_constraint_network:ConstraintNetwork=p_new_constraint_network
        self.m_new_constraints:typing.Set[typing.Tuple[ConstraintType,typing.Any]]=p_new_constraints
        self.m_action_or_method_instance:ActionMethod=p_action_or_method_instance
        self.m_action_or_method_assertion_support_info:typing.Set[typing.Tuple[Assertion,Assertion]]=p_action_or_method_assertion_support_info

class CharlieMoveInfo():
    def __init__(self,
        p_selected_controllable_timepoints:typing.List[str],
        p_wait_time:None|str,
    ):
        self.m_selected_controllable_timepoints:typing.List[str]=p_selected_controllable_timepoints
        self.m_time:None|str=p_wait_time # here float could make sense...! i.e. wait until a certain "real" time, not necessarily towards a variable / time point. in that case - "str"
        # if it's <= 0 it means we have a "play" move. if not - "wait" move

class EveMoveInfo():
    def __init__(self,
        p_selected_uncontrollable_timepoints:typing.List[str]
    ):
        self.m_selected_uncontrollable_timepoints:typing.List[str]=p_selected_uncontrollable_timepoints

class SearchNode():

    monitor_action_template = ActionMethodTemplate(
        p_type=ActionMethodTemplate.Type.ACTION,
        p_name="action_monitor_assertion",
        p_params=(("p_assertion","all_assertions_objvar"),), # obviously, need to find a way to represent non explicit domains
        p_constraints_func=lambda ts,te,_:[
            (ConstraintType.TEMPORAL, (ts,te,0,False))
        ]
    )

    def __init__(self,
        p_node_type:SearchNodeType,
        p_parent:SearchNode,
        p_time:str,
        p_observation:object,
        p_chronicle:Chronicle,
        p_action_method_templates_library:typing.Set[ActionMethodTemplate]=set(),
        p_flaw_node_info:FlawNodeInfo=None,
        p_resolver_node_info:ResolverNodeInfo=None,
        p_charlie_move_info:CharlieMoveInfo=None,
        p_eve_move_info:EveMoveInfo=None,
    ):
        self.m_node_type:SearchNodeType = p_node_type
        self.m_parent:SearchNode = p_parent
        self.m_children:typing.List[SearchNode] = []

        self.m_time:str = p_time
        self.m_observation:object = p_observation
        self.m_chronicle:Chronicle = p_chronicle
        #self.scheduled_time_points ?
        #other variables than time points ? maybe already accounted for in constr net ?

        self.m_action_method_templates_library:typing.Set[ActionMethodTemplate] = p_action_method_templates_library

        # V these actually correspond to the edge coming from the parent V
        # in other words, it contains the details of the _parent_'s choice for this node 
        self.m_flaw_node_info:FlawNodeInfo = p_flaw_node_info
        self.m_resolver_node_info:ResolverNodeInfo = p_resolver_node_info
        self.m_charlie_move_info:CharlieMoveInfo = p_charlie_move_info
        self.m_eve_move_info:EveMoveInfo = p_eve_move_info
        # as such, we have the following:
        # flaw type node : has non-empty resolver_info or eve_move_info (depending on previous node), nothing if root
        # resolver type node : has non-empty flaw_info
        # charlie type node : same as flaw type node (depending on parent node, non-empty resolver_info or eve_move_info)
        # eve node type : has non-empty charlie_move_info
        
        # so, if we want to know the search choices made at this node, we need to go through its children and look at their "info" fields
        # or, if we want to know our choices "directly", store them in lists, "parallel" to the children list
        # e.g. flaws[], resolvers[], charlie_moves[], eve_moves[] (indices corresponding to children list)

    def build_children(self):

        if self.m_node_type == SearchNodeType.FLAW:

            # resolvable at time now !!
            flaws = self.select_flaws() # order/priority can depend on search strategy
            for fi in flaws:
                self.m_children.append(SearchNode(
                    p_node_type=SearchNodeType.RESOLVER,
                    p_parent=self,
                    p_time=self.m_time,
                    p_observation=deepcopy(self.m_observation),
                    p_chronicle=self.m_chronicle.copy_chronicle(),
                    p_action_method_templates_library=self.m_action_method_templates_library,
                    p_flaw_node_info=fi))

        if self.m_node_type == SearchNodeType.RESOLVER:

            # usable at time now !!
            old_chronicle = self.m_chronicle.copy_chronicle()
            
            resolvers = self.select_resolvers() # order/priority can depend on search strategy
            for ri in resolvers:
                
                # The chronicle of the child search node that is being created 
                transformed_chronicle = old_chronicle.copy_chronicle()
            
                if ri.m_type == ResolverType.CONFLICT_SEPARATION:

                    # Apply constraints resolving the flaw to the chronicle of the child search node currently being built
                    #transformed_chronicle.m_constraint_network.propagate_constraints(ri.m_new_constraints)
                    transformed_chronicle.m_constraint_network = ri.m_new_constraint_network
                    # Remove the adressed conflict from the collection of current conflicts in the chronicle of the child search node currently being built
                    transformed_chronicle.m_conflicts.remove((self.m_flaw_node_info.m_assertion1,self.m_flaw_node_info.m_assertion2))

                elif ri.m_type == ResolverType.EXISTING_DIRECT_PERSISTENCE_SUPPORT_NOW or ri.m_type == ResolverType.NEW_DIRECT_PERSISTENCE_SUPPORT_NOW:

                    # A "dummy action" considered to be the expansion of the goal corresponding to the addressed unsupported assertion
                    # Indeed, in accordance with the goal lifecycle, before a goal can be set to the "dispatched" mode,
                    # it needs to be in the "committed" mode, which represents the fact that a means to 
                    # achieve this goal (plan : action, method...) was found and committed to.
                    # Direct support of a previously unsupported assertion is a way to achieve (or guarantee/promise the achievement of) the
                    # goal corresponding to that assertion. To represent that in the *plan* (i.e. course of *action*, not just chronicle) we 
                    # make use of actions which are supposed to achieve / maintain the "promise" made in the chronicle.
                    # Which actually corresponds to the monitoring function of planning and acting.
                    # In conclusion - this action will have to monitor whether the newly directly supported assertion is indeed respected during execution
                    # It is this action that will be triggered when the goal/assertion will be dispatched
                    new_action = ActionMethod(
                        p_template=SearchNode.monitor_action_template,
                        p_args=(
                            ("p_assertion",self.m_flaw_node_info.m_assertion1),
                        ),
                        p_time_start=self.m_flaw_node_info.m_assertion1.time_start,
                        p_time_end=self.m_flaw_node_info.m_assertion1.time_end,
                    )
                    # Finding this new action's hierarchical place in the plan (parent (method) following the plan decomposition) 
                    parent = None
                    if not transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_parent is None:
                        if not transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_parent.m_committed_expansion is None:
                            parent = transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_parent.m_committed_expansion
                    # Adding the action to the plan in the chronicle of the child search node currently being built
                    # Notice that the line above can still give a None parent
                    transformed_chronicle.m_plan[new_action] = parent
                    
                    # Transitioning the goal corresponding to the flawed assertion in this search node's chronicle to "expanded" mode
                    # with this action as a possible expansion
                    self.m_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_mode = GoalMode.EXPANDED
                    self.m_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_possible_expansions.append(new_action)

                    # Setting the assertion from unsupported to supported and adding its supporter to the causal network
                    # in the chronicle of the child search node currently being built
                    transformed_chronicle.m_assertions[self.m_flaw_node_info.m_assertion1] = True
                    transformed_chronicle.m_causal_network[self.m_flaw_node_info.m_assertion1] = ri.m_direct_support_assertion
                    
                    # Transitioning the goal corresponding to the flawed assertion to "committed" mode with the action introduced above as its committed expansion
                    # in the chronicle of the child search node currently being built
                    transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_mode = GoalMode.COMMITTED
                    transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_possible_expansions = [new_action]
                    transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_committed_expansion = new_action
                    
                    # The following code deals with the case where the direct supporter used was not already present in the chronicle
                    # and was created specifically to resolve the flaw. This newly created direct supporter must be, in turn, directly supported
                    # itself by a persistence assertion already present in the chronicle (ri.m_direct_support_assertion_supporter).
                    # As such, if it is None, direct_support_assertion must have necessarily been already present in the chronicle.
                    # And if it isn't, it needs to be managed (support from ri.m_direct_support_assertion_supporter, status of the corresponding goal)
                    if ri.m_direct_support_assertion_supporter is not None:

                        # Same as above, but addresses the supporter of the introduced direct supporter of the flawed unsupported assertion.
                        new_action2 = ActionMethod(
                            p_template=SearchNode.monitor_action_template,
                            p_args=(("p_assertion",ri.m_direct_support_assertion),),
                            p_time_start=ri.m_direct_support_assertion.time_start,
                            p_time_end=ri.m_direct_support_assertion.time_end,
                        )
                        # Same parent as for the direct supporter - the idea is that both these actions stem from the same decision
                        transformed_chronicle.m_plan[new_action2] = parent

                        # Not adressing ri.m_direct_support_assertion_supporter in this search node's chronicle,
                        # as in this case the ri.m_direct_support_assertion was newly created and not present in this search node's chronicle,
                        # which means that the goal corresponding to it simply doesn't exist yet.
                        # It exists in the chronicle of the child search node currently being built,
                        # where it is introduced in directly "committed" mode (see below)

                        # Same as in the above part
                        transformed_chronicle.m_assertions[ri.m_direct_support_assertion] = True
                        transformed_chronicle.m_causal_network[ri.m_direct_support_assertion] = ri.m_direct_support_assertion_supporter

                        # Same as in the above part
                        transformed_chronicle.m_goal_nodes[ri.m_direct_support_assertion] = GoalNode()
                        transformed_chronicle.m_goal_nodes[ri.m_direct_support_assertion].m_mode = GoalMode.COMMITTED
                        transformed_chronicle.m_goal_nodes[ri.m_direct_support_assertion].m_parent = transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1]
                        transformed_chronicle.m_goal_nodes[ri.m_direct_support_assertion].m_possible_expansions = [new_action2]
                        transformed_chronicle.m_goal_nodes[ri.m_direct_support_assertion].m_committed_expansion = new_action2

                    # Apply the constraints introduced to allow the suggested direct supporter to be one
                    transformed_chronicle.m_constraint_network.propagate_constraints(ri.m_new_constraints)
                    # Update the collection of current conflicts in the chronicle of the child search node currently being built
                    # with all the conflicts which may have appeared after the application of these constraints and possilby new direct supporter assertion
                    transformed_chronicle.m_conflicts.update(transformed_chronicle.get_induced_conflicts([ri.m_direct_support_assertion]))

                elif ri.m_type == ResolverType.METHOD_INSERTION_NOW or ri.m_type == ResolverType.ACTION_INSERTION_NOW:
                    
                    # Finding the hierarchical place in the plan (parent (method) following the plan decomposition)
                    # of the action/method suggested by this resolver
                    parent = None
                    if not transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_parent is None:
                        if not transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_parent.m_committed_expansion is None:
                            parent = transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_parent.m_committed_expansion
                    # Adding the action/method to the plan in the chronicle of the child search node currently being built
                    # Notice that the line above can still give a None parent
                    transformed_chronicle.m_plan[ri.m_action_or_method_instance] = parent

                    # Transitioning the goal corresponding to the flawed assertion in this search node's chronicle to "expanded" mode
                    # with action/method suggested in the resolver as a possible expansion
                    self.m_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_mode = GoalMode.EXPANDED
                    self.m_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_possible_expansions.append(ri.m_action_or_method_instance)

                    # Transitioning the goal corresponding to the flawed assertion to "committed" mode with the action introduced above as its committed expansion
                    # in the chronicle of the child search node currently being built is done at the end of the 2nd next loop,
                    # as the flawed unsupported assertion must be one of the assertions supported by the action/method.

                    # Update the chronicle of the child search node currently being built by adding the assertions of the action/method chosen in the resolver to it
                    for i_asrt in ri.m_action_or_method_instance.assertions:
                        
                        transformed_chronicle.m_assertions[i_asrt] = False

                        transformed_chronicle.m_goal_nodes[i_asrt] = GoalNode()
                        transformed_chronicle.m_goal_nodes[i_asrt].m_mode = GoalMode.SELECTED
                        transformed_chronicle.m_goal_nodes[i_asrt].m_parent = transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1]

                    # Manage the assertion supports which made the action/method applicable in the first place
                    # (i.e. set the supported assertions from unsupported to supported and add their supporter in the causal network)
                    for (i_asrt_supporter, i_asrt_supportee) in ri.m_action_or_method_assertion_support_info:

                        # All of the assertions of the action/method, starting at the same time as it, have to be supported by the chronicle
                        # But those that do not start at the same time as it (and as such don't have to be supported by the chronicle)
                        # still need to be introduced, which is done in the loop above. 
                        
                        transformed_chronicle.m_assertions[i_asrt_supportee] = True
                        transformed_chronicle.m_causal_network[i_asrt_supportee] = i_asrt_supporter

                        # Also, at least one of the chronicle's assertions must be supported by an assertion from the action/method
                        # (The flawed unsupported assertion is (must) be one of them)
                        # These assertions and the corresponding goals are managed below
                        if i_asrt_supportee in ri.m_action_or_method_instance.assertions:
                            asrt = i_asrt_supportee
                        else:
                            asrt = i_asrt_supporter
                        if asrt != self.m_flaw_node_info.m_assertion1:
                            transformed_chronicle.m_goal_nodes[asrt].m_mode = GoalMode.COMMITTED
                            transformed_chronicle.m_goal_nodes[asrt].m_parent = transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1]
                            transformed_chronicle.m_goal_nodes[asrt].m_possible_expansions = [ri.m_action_or_method_instance]
                            transformed_chronicle.m_goal_nodes[asrt].m_committed_expansion = ri.m_action_or_method_instance

                    # Apply the constraints introduced of the action/method and also any other constraints that may be in the resolver
                    transformed_chronicle.m_constraint_network = ri.m_new_constraint_network
                    #transformed_chronicle.m_constraint_network.init_objvars(ri.m_objvars_domains)
                    #transformed_chronicle.m_constraint_network.propagate_constraints(ri.m_action_or_method_instance.constraints)
                    #transformed_chronicle.m_constraint_network.propagate_constraints(ri.m_constraints)
                    ## Propagating the instantiation variable for the action/method
                    ## Done here and not earlier (e.g. when adding the action/method to the plan)
                    ## as other constraints should be propagated first (in order to use the correct )
                    ## NOTE: this is very basic / crude / inefficient, but good enough for now.
                    #_name = ri.m_action_or_method_instance.name
                    #_args = ri.m_action_or_method_instance.args
                    #_args_values  = _args.values()
                    #_n = len(_args.keys())
                    #_rows = []
                    #def _recursion(_i, _row:typing.List):
                    #    _rowcopy = _row.copy()
                    #    for _v in self.m_chronicle.m_constraint_network.objvar_domain(_args_values[_i]).get_values():
                    #        _row.append(_v)
                    #    if _i <= _n-2:
                    #        _recursion(_i+1,_row)
                    #    else:
                    #        _rows.append(_row.copy())
                    #    _row = _rowcopy
                    #    if _i > 0:
                    #        _recursion(0,[])
                    #    else:
                    #        return
                    #_recursion(0,[])
                    ##_id_objvar = "__actmethinst_{0}{1}_id".format(_name, _args)
                    ##if transformed_chronicle.m_constraint_network.objvar_domain(_id_objvar) is None:
                    ##    transformed_chronicle.m_constraint_network.declare_and_init_objvars({_id_objvar:Domain()})
                    #rows_final = _rows#[]
                    ##for _row in _rows:
                    ##    _id = new_int_id()
                    ##    transformed_chronicle.m_constraint_network.objvar_domain(_id_objvar).add_discrete_value(_id)
                    ##    rows_final = tuple(_row + [_id])
                    #transformed_chronicle.m_constraint_network.propagate_constraints([
                    #    (ConstraintType.GENERAL_RELATION,
                    #        ("__actmethinst_{0}{1}_rel{2}".format(_name, _args, new_int_id()),
                    #        tuple([_p for _p in _args_values]),# + [_id_objvar]),
                    #        rows_final)
                    #    )
                    #])
                    ## !! TODO !!: the above approach to general relations assumes an explicit discrete domains representation...
                    ## As we cannot really represent all of the possible values for such variables/table columns explicitly,
                    ## we will *NEED* better variable domain representations for that very soon.
                    ## It is also quite inefficient and unelegant

                    # Update the collection of current conflicts in the chronicle of the child search node currently being built
                    # with all the conflicts which may have appeared after the application of the action/method
                    transformed_chronicle.m_conflicts.update(transformed_chronicle.get_induced_conflicts(ri.m_action_or_method_instance.assertions))

                # decision could be made using search control on whether to follow with a flaw or charlie child (or both)
                # until then / by default - both 

                self.m_children.append(SearchNode(p_node_type=SearchNodeType.FLAW,
                    p_parent=self,
                    p_time=self.m_time,
                    p_observation=deepcopy(self.m_observation),
                    p_chronicle=transformed_chronicle,
                    p_action_method_templates_library=self.m_action_method_templates_library,
                    p_resolver_node_info=ri))

                #self.m_children.append(SearchNode(p_node_type=SearchNodeType.CHARLIE,
                #    p_parent=self,
                #    p_time=self.m_time,
                #    p_state=deepcopy(self.m_state),
                #    p_chronicle=transformed_chronicle,
                #    p_action_method_templates_library=self.m_action_method_templates_library,
                #    p_resolver_node_info=ri))

        if self.m_node_type == SearchNodeType.CHARLIE:
            
            old_chronicle = self.m_chronicle.copy_chronicle()

            charlie_moves = self.select_charlie_moves()
            for ci in charlie_moves:

                transformed_chronicle = deepcopy(old_chronicle)

                # "play" move
                if ci.m_time is None:
                # should the wait time be a float "offset" ? or should it be a time point that comes next ?
                #FIXME: probably. change this tomorrow

                    for ctr_tp in ci.m_selected_controllable_timepoints:

                        #transformed_chronicle.m_constraint_network.propagate_constraints([
                        #    (ConstraintType.TEMPORAL, (ctr_tp, "ref_tp", self.m_time, False)),
                        #    (ConstraintType.TEMPORAL, ("ref_tp", ctr_tp, self.m_time, False)),
                        #])

                        transformed_chronicle.m_constraint_network.propagate_constraints([
                            (ConstraintType.TEMPORAL, (ctr_tp, self.m_time, 0, False)),
                            (ConstraintType.TEMPORAL, (self.m_time, ctr_tp, 0, False)),
                        ])

                        asrts_starting_at_ctr_tp = []
                        for _asrt in transformed_chronicle.m_assertions:
                            if transformed_chronicle.m_constraint_network.tempvars_unified(ctr_tp, _asrt.time_start):
                                asrts_starting_at_ctr_tp.append(_asrt)
                        
                        for asrt in asrts_starting_at_ctr_tp:
                            if transformed_chronicle.m_goal_nodes[asrt].m_mode == GoalMode.COMMITTED:
                                transformed_chronicle.m_goal_nodes[asrt].m_mode = GoalMode.DISPATCHED
                                #NOTE: action dispatching ?..
                                # "preparation for execution -> execution_state state variable with inactive/running/completed values, then outcomes(successful,failed,unknown(?))"
                        # goal mode : dispatch (for start) for assertions whose starting time point is selected here
 
                    self.m_children.append(SearchNode(p_node_type=SearchNodeType.EVE,
                        p_parent=self,
                        p_time=self.m_time,
                        p_observation=self.m_observation,
                        p_chronicle=transformed_chronicle,
                        p_action_method_templates_library=self.m_action_method_templates_library,
                        p_charlie_move_info=ci))

                # "wait" move
                else:

                    # ci.m_time is basically any (both controllable and uncontrollable) timepoint that can come next.
                    # like "next" in nau temporal (...?) 

                    self.m_children.append(SearchNode(p_node_type=SearchNodeType.EVE,
                        p_parent=self,
                        p_time=ci.m_time,
                        p_observation=deepcopy(self.m_observation),
                        p_chronicle=transformed_chronicle,
                        p_action_method_templates_library=self.m_action_method_templates_library,
                        p_charlie_move_info=ci))
            
        if self.m_node_type == SearchNodeType.EVE:
            pass
            # for ...
            #     self.m_children.append(SearchNode(p_node_type=SearchNodeType.CHARLIE,
            #         p_parent=self,
            #         p_time=self.m_time,
            #         p_state=deepcopy(self.m_state),
            #         p_chronicle=transformed_chronicle,
            #         p_action_method_templates_library=self.m_action_method_templates_library,
            #         p_eve_move_info=ei))
            # for ...
            #     self.m_children.append(SearchNode(p_node_type=SearchNodeType.FLAW,
            #         p_parent=self,
            #         p_time=self.m_time,
            #         p_state=deepcopy(self.m_state),
            #         p_chronicle=transformed_chronicle,
            #         p_action_method_templates_library=self.m_action_method_templates_library,
            #         p_eve_move_info=ei))

    def select_flaws(self) -> typing.List[FlawNodeInfo]:
        # use non null self.m_resolver_node_info or self.m_eve_move_info
        res = []
        # in general : "priority queue" (or just priority order in list) according to search strategy
        # for example : flaws with only one possible resolver first... (FAPE 2020 p.40)
        # maybe if mcts is used, not all children at the same time ? maybe come back to this node later and "complete" its children ?--
        for asrt in self.m_chronicle.m_assertions:
            if not self.m_chronicle.m_assertions[asrt] and self.m_chronicle.m_goal_nodes[asrt].m_mode != GoalMode.FORMULATED:
                res.append(FlawNodeInfo(p_assertion1=asrt,p_assertion2=None))

        for (asrt1, asrt2) in self.m_chronicle.m_conflicts:
                res.append(FlawNodeInfo(p_assertion1=asrt1,p_assertion2=asrt2))
        
        return res

    def select_resolvers(self) -> typing.List[ResolverNodeInfo]:
        res = []

        # Case of an unsupported assertion flaw

        if self.m_flaw_node_info.m_assertion2 is None:

            # NOTE:
            # there can only be unsupported assertions starting at time now or later (not before, that would just mean failed acting)
            # so we assume that self.m_flaw_node_info.m_assertion1's start time is later than (or at the same time as) self.time
            # (would it be beneficial to enforce it by an explicit constraint ? (easier conflict/inconsistency detection from that ?))

            # direct support resolvers

            for i_asrt in self.m_chronicle.m_assertions:

                if (i_asrt.type == AssertionType.PERSISTENCE
                    and i_asrt.has_same_head(self.m_flaw_node_info.m_assertion1)
                    and i_asrt != self.m_flaw_node_info.m_assertion1
                ):
                    if (self.m_chronicle.m_constraint_network.propagate_constraints([
                            (ConstraintType.TEMPORAL, (i_asrt.time_end, self.m_flaw_node_info.m_assertion1.time_start, 0, False)),
                            (ConstraintType.TEMPORAL, (self.m_flaw_node_info.m_assertion1.time_start, i_asrt.time_end, 0, False)),
                            (ConstraintType.UNIFICATION, (i_asrt.sv_val, self.m_flaw_node_info.m_assertion1.sv_val))
                        ], p_backtrack=False)
                    ):
                        if self.m_chronicle.m_constraint_network.tempvars_unified(i_asrt.time_end, self.m_time):#self.m_flaw_node_info.m_assertion1.time_start):

                            res.append(ResolverNodeInfo(
                                p_type = ResolverType.EXISTING_DIRECT_PERSISTENCE_SUPPORT_NOW,
                                p_direct_support_assertion = i_asrt,
                                p_direct_support_assertion_supporter = None,
                                p_new_constraint_network = None,
                                p_new_constraints = [
                                    (ConstraintType.TEMPORAL, (i_asrt.time_end, self.m_flaw_node_info.m_assertion1.time_start, 0, False)),
                                    (ConstraintType.TEMPORAL, (self.m_flaw_node_info.m_assertion1.time_start, i_asrt.time_end, 0, False)),
                                    # here i_asrt.time_end is already (see if statement above) unified/equal to self.m_time (i.e. time "now")
                                    (ConstraintType.UNIFICATION, (i_asrt.sv_val, self.m_flaw_node_info.m_assertion1.sv_val)),
                                ],
                                p_action_or_method_instance = None,
                                p_action_or_method_assertion_support_info = None,
                            ))
                    
                        self.m_chronicle.m_constraint_network.backtrack()

                    if (self.m_chronicle.m_constraint_network.propagate_constraints([
                            (ConstraintType.TEMPORAL,(i_asrt.time_end, self.m_flaw_node_info.m_assertion1.time_start, 0, True)),
                            (ConstraintType.UNIFICATION, (i_asrt.sv_val, self.m_flaw_node_info.m_assertion1.sv_val)),
                        ], p_backtrack=False)
                    ):
                        # !!!NOTE!!! possible latest assertions on the considered state variable, before the flawed one
                        # (no reason to take ones where we're sure that there is one between it and the flawed one)
                        # will be easier if we group assertions by head (-> explicit timelines ?)
                        # OR (NOTE) MAYBE no point in this ? as if we don't take the "latest" assertion from which to support,
                        # applying the resolver will cause a potential conflict flaw (between the introduced supporter and "later" assertions)
                        # but that is not necessarily a problem or something to avoid - this conflict could get resolved sucessfully.
                        if (self.m_chronicle.m_constraint_network.tempvars_unified(i_asrt.time_end, self.m_time)
                            and self.m_chronicle.m_constraint_network.tempvars_minimal_directed_distance(
                                i_asrt.time_end, self.m_flaw_node_info.m_assertion1.time_start) > 0
                        ):
                            dsa = Assertion(
                                p_type=AssertionType.PERSISTENCE,
                                p_sv_name=self.m_flaw_node_info.m_assertion1.sv_name,
                                p_sv_params=self.m_flaw_node_info.m_assertion1.sv_params,
                                p_sv_val=i_asrt.sv_val,
                                p_sv_val_sec=None,
                                p_time_start=self.m_time, # i_asrt.time_end ? NOTE: Either this or constraint below
                                p_time_end=self.m_flaw_node_info.m_assertion1.time_start
                            )

                            constrs = set([
                                (ConstraintType.TEMPORAL, (dsa.time_end, self.m_flaw_node_info.m_assertion1.time_start, 0, False)),
                                (ConstraintType.TEMPORAL, (self.m_flaw_node_info.m_assertion1.time_start, dsa.time_end, 0, False)),
                                # here i_asrt.time_end is already (see if statement above) unified/equal to self.m_time (i.e. time "now")
                                (ConstraintType.UNIFICATION, (dsa.sv_val, self.m_flaw_node_info.m_assertion1.sv_val)),
                                (ConstraintType.TEMPORAL, (i_asrt.time_end, dsa.time_start, 0, False)),
                                (ConstraintType.TEMPORAL, (dsa.time_start, i_asrt.time_end, 0, False)),
                                # here i_asrt.time_end is already (see if statement above) unified/equal to self.m_time (i.e. time "now")
                                (ConstraintType.UNIFICATION, (i_asrt.sv_val, dsa.sv_val))
                            ])

                            res.append(ResolverNodeInfo(
                                p_type = ResolverType.NEW_DIRECT_PERSISTENCE_SUPPORT_NOW,
                                p_direct_support_assertion = dsa,
                                p_direct_support_assertion_supporter = i_asrt,
                                p_new_constraint_network = None,
                                p_new_constraints = constrs,
                                p_action_or_method_instance = None,
                                p_action_or_method_assertion_support_info = None,
                            ))
                    
                        self.m_chronicle.m_constraint_network.backtrack()
                        
            # action/method insertion resolvers
            # lots of heuristics (both lifted and grounded ?) will need to be used and search space reduction techniques (reachability analysis etc)

            for i_act_or_meth_template in self.m_action_method_templates_library:

                # Only consider action templates which have an assertion with the same header as the flawed unsupported one
                # Indeed, it must be supported by one of the assertions of the chosen action/method
                # !!!NOTE!!! we assume that the head of the assertions (sv_name and sv_params first elements) do not depend on assertion parameters
                _b = False
                same_sv_as_flaw_asrt:Assertion = None
                i_act_or_meth_template_asrts = i_act_or_meth_template.assertions_func(
                    self.m_time, self.m_flaw_node_info.m_assertion1.time_start, { pair[0]:pair[1] for pair in i_act_or_meth_template.params })
                for i_asrt in i_act_or_meth_template_asrts:
                    if i_asrt.has_same_head(self.m_flaw_node_info.m_assertion1):
                        same_sv_as_flaw_asrt = i_asrt
                        _b = True
                        break
                if not _b:
                    continue
    
                _n = len(i_act_or_meth_template.params)
                rows = []
                def _recursion(_i, _row:typing.List[str]):
                    if _i < _n:
                        for _v in self.m_chronicle.m_constraint_network.objvar_domain(i_act_or_meth_template.params[_i][1]).get_values():
                            _newrow = _row.copy()
                            _newrow[_i] = _v
                            _recursion(_i+1,_newrow)
                    else:
                        rows.append(tuple(_row))
                _recursion(0, [""]*_n)
                
                if same_sv_as_flaw_asrt.type == AssertionType.TRANSITION:
                    unif_constr = (ConstraintType.UNIFICATION, 
                        (same_sv_as_flaw_asrt.sv_val_sec, self.m_flaw_node_info.m_assertion1.sv_val))
                else:
                    unif_constr = (ConstraintType.UNIFICATION, 
                        (same_sv_as_flaw_asrt.sv_val, self.m_flaw_node_info.m_assertion1.sv_val)),

                #propagated = self.m_chronicle.m_constraint_network.propagate_constraints(
                #    i_act_or_meth_template.constraints_func(
                #        self.m_time, self.m_flaw_node_info.m_assertion1.time_start, i_act_or_meth_template.params)
                #    .union([
                #        unif_constr,
                #        (ConstraintType.GENERAL_RELATION,
                #            ("__actmethtempl_{0}{1}_rel".format(i_act_or_meth_template.name, i_act_or_meth_template.params),
                #            tuple(i_act_or_meth_template.params.values()),
                #            rows))
                #    ])
                #)
                
                if ("__actmethtempl_{0}{1}_rel".format(i_act_or_meth_template.name, i_act_or_meth_template.params)
                    in self.m_chronicle.m_constraint_network.m_bcn.m_general_relations
                ):
                    propagated = True
                else:
                    propagated = self.m_chronicle.m_constraint_network.propagate_constraints([
                        (ConstraintType.GENERAL_RELATION,
                            ("__actmethtempl_{0}{1}_rel".format(i_act_or_meth_template.name, i_act_or_meth_template.params),
                                (tuple([pair[1] for pair in i_act_or_meth_template.params]),
                                rows)))
                    ])
                
                if propagated:

                    new_constraint_network = deepcopy(self.m_chronicle.m_constraint_network)
                    propagated = new_constraint_network.propagate_constraints(
                        i_act_or_meth_template.constraints_func(
                            self.m_time, self.m_flaw_node_info.m_assertion1.time_start, { pair[0] for pair in i_act_or_meth_template.params })
                        .union([unif_constr])
                    )
                
                    if propagated:
        
                        args = ()
                        objvars_domains = {}
                        _n = new_int_id()
                        for param in i_act_or_meth_template.params:
                            arg_objvar_name = "__actmethinst{0}_{1}{2}_arg_{3}".format(
                                _n, i_act_or_meth_template.name, i_act_or_meth_template.params, param[0])
                            #objvars_domains[arg_objvar_name] = deepcopy(new_constraint_network.objvar_domain(param[1]))
                            objvars_domains[arg_objvar_name] = Domain(p_initial_allowed_values=new_constraint_network.objvar_domain(param[1]).get_values())
                            args += ((param[0],arg_objvar_name),)
                        new_constraint_network.init_objvars(objvars_domains)
                        
                        act_or_meth_instance = ActionMethod(
                            p_template=i_act_or_meth_template,
                            p_time_start=self.m_time,
                            #p_time_end=self.m_flaw_node_info.m_assertion1.time_start,
                            #NOTE, FIXME !!! the action/method's end time doesn't necessarily have to be the start of the flawed unsupported assertion !!!
                            # as a matter of fact, the assertion inside the action/method supporting isn't necessarily ending at the same time as the whole action !!!!
                            # how to deal with this ? just keep it lifted ? (its own variable name) to do that just don't specify the argument
                            p_args=args
                        )
                        act_or_meth_assertion_support_info = act_or_meth_instance.propagate_applicability(
                            p_time=self.m_time,
                            p_cn=new_constraint_network,
                            p_assertions=self.m_chronicle.m_assertions,
                            p_assertion_to_support=self.m_flaw_node_info.m_assertion1,
                            p_backtrack=False,
                        )

                        if len(act_or_meth_assertion_support_info) > 0:
                            
                            if act_or_meth_instance.template.type == ActionMethodTemplate.Type.ACTION:
                                _t = ResolverType.ACTION_INSERTION_NOW
                            else:
                                _t = ResolverType.METHOD_INSERTION_NOW

                            res.append(ResolverNodeInfo(
                                p_type = _t,
                                p_direct_support_assertion=None,
                                p_direct_support_assertion_supporter=None,
                                p_new_constraints=None,
                                p_new_constraint_network=new_constraint_network,
                                p_action_or_method_instance=act_or_meth_instance,
                                p_action_or_method_assertion_support_info=act_or_meth_assertion_support_info
                            ))
    
                if not propagated:
                    continue

        # Case of a conflict flaw

        else:
                                
            # temporal separation resolver

            if (self.m_chronicle.m_constraint_network.tempvars_minimal_directed_distance(
                self.m_time, self.m_flaw_node_info.m_assertion1.time_start) > 0
            ):
                if (self.m_chronicle.m_constraint_network.propagate_constraints([
                    (ConstraintType.TEMPORAL, (self.m_flaw_node_info.m_assertion2.time_end, self.m_flaw_node_info.m_assertion1.time_start, 0, True))
                    ])
                ):
                    new_constraint_network = deepcopy(self.m_chronicle.m_constraint_network)
                    self.m_chronicle.m_constraint_network.backtrack()

                    res.append(ResolverNodeInfo(
                        p_type=ResolverType.CONFLICT_SEPARATION,
                        p_direct_support_assertion = None,
                        p_direct_support_assertion_supporter = None,
                        p_new_constraint_network = new_constraint_network,
                        p_new_constraints = None,
                        p_action_or_method_instance = None,
                        p_action_or_method_assertion_support_info = None,
                    ))

            if (self.m_chronicle.m_constraint_network.tempvars_minimal_directed_distance(
                self.m_time, self.m_flaw_node_info.m_assertion2.time_start) > 0
            ):
                if (self.m_chronicle.m_constraint_network.propagate_constraints([
                    (ConstraintType.TEMPORAL, (self.m_flaw_node_info.m_assertion1.time_end, self.m_flaw_node_info.m_assertion2.time_start, 0, True))
                    ])
                ):
                    new_constraint_network = deepcopy(self.m_chronicle.m_constraint_network)
                    self.m_chronicle.m_constraint_network.backtrack()

                    res.append(ResolverNodeInfo(
                        p_type = ResolverType.CONFLICT_SEPARATION,
                        p_direct_support_assertion = None,
                        p_direct_support_assertion_supporter = None,
                        p_new_constraint_network = new_constraint_network,
                        p_new_constraints = None,
                        p_action_or_method_instance = None,
                        p_action_or_method_assertion_support_info = None,
                    ))

            # value unification resolver for two persistences

            if (self.m_flaw_node_info.m_assertion1.type == AssertionType.PERSISTENCE
                and self.m_flaw_node_info.m_assertion2.type == AssertionType.PERSISTENCE
            ):
                if (self.m_chronicle.m_constraint_network.propagate_constraints([
                    (ConstraintType.UNIFICATION, (self.m_flaw_node_info.m_assertion1.sv_val, self.m_flaw_node_info.m_assertion2.sv_val))
                    ])
                ):
                    new_constraint_network = deepcopy(self.m_chronicle.m_constraint_network)
                    self.m_chronicle.m_constraint_network.backtrack()

                    res.append(ResolverNodeInfo(
                        p_type = ResolverType.CONFLICT_SEPARATION,
                        p_direct_support_assertion = None,
                        p_direct_support_assertion_supporter = None,
                        p_new_constraint_network = new_constraint_network,
                        p_new_constraints = None,
                        p_action_or_method_instance = None,
                        p_action_or_method_assertion_support_info = None,
                    ))

            # value unification resolver for two transitions (involves temporal constraints as well)

            elif (self.m_flaw_node_info.m_assertion1.type == AssertionType.TRANSITION
                and self.m_flaw_node_info.m_assertion2.type == AssertionType.TRANSITION
            ):
                if (self.m_chronicle.m_constraint_network.tempvars_minimal_directed_distance(
                    self.m_time, self.m_flaw_node_info.m_assertion1.time_start) > 0
                ):
                    if (self.m_chronicle.m_constraint_network.propagate_constraints([
                        (ConstraintType.UNIFICATION, (self.m_flaw_node_info.m_assertion1.sv_val, self.m_flaw_node_info.m_assertion2.sv_val_sec)),
                        (ConstraintType.TEMPORAL, (self.m_flaw_node_info.m_assertion2.time_end, self.m_flaw_node_info.m_assertion1.time_start, 0, False)), 
                        (ConstraintType.TEMPORAL, (self.m_flaw_node_info.m_assertion1.time_start, self.m_flaw_node_info.m_assertion2.time_end, 0, False)),
                        ])
                    ):
                        new_constraint_network = deepcopy(self.m_chronicle.m_constraint_network)
                        self.m_chronicle.m_constraint_network.backtrack()

                        res.append(ResolverNodeInfo(
                            p_type = ResolverType.CONFLICT_SEPARATION,
                            p_direct_support_assertion = None,
                            p_direct_support_assertion_supporter = None,
                            p_new_constraint_network = new_constraint_network,
                            p_new_constraints = None,
                            p_action_or_method_instance = None,
                            p_action_or_method_assertion_support_info = None,
                        ))

                if (self.m_chronicle.m_constraint_network.tempvars_minimal_directed_distance(
                    self.m_time, self.m_flaw_node_info.m_assertion2.time_start) > 0
                ):
                    if (self.m_chronicle.m_constraint_network.propagate_constraints([
                        (ConstraintType.UNIFICATION, (self.m_flaw_node_info.m_assertion2.sv_val, self.m_flaw_node_info.m_assertion1.sv_val_sec)),
                        (ConstraintType.TEMPORAL, (self.m_flaw_node_info.m_assertion1.time_end, self.m_flaw_node_info.m_assertion2.time_start, 0, False)), 
                        (ConstraintType.TEMPORAL, (self.m_flaw_node_info.m_assertion2.time_start, self.m_flaw_node_info.m_assertion1.time_end, 0, False)),
                        ])
                    ):
                        new_constraint_network = deepcopy(self.m_chronicle.m_constraint_network)
                        self.m_chronicle.m_constraint_network.backtrack()

                        res.append(ResolverNodeInfo(
                            p_type = ResolverType.CONFLICT_SEPARATION,
                            p_direct_support_assertion = None,
                            p_direct_support_assertion_supporter = None,
                            p_new_constraint_network = new_constraint_network,
                            p_new_constraints = None,
                            p_action_or_method_instance = None,
                            p_action_or_method_assertion_support_info = None,
                        ))

            # value unification resolver for a persistence and a transition

            else:

                if self.m_flaw_node_info.m_assertion1.type == AssertionType.PERSISTENCE:
                    _pers_asrt = self.m_flaw_node_info.m_assertion1
                    _trans_asrt = self.m_flaw_node_info.m_assertion2
                else:
                    _pers_asrt = self.m_flaw_node_info.m_assertion2
                    _trans_asrt = self.m_flaw_node_info.m_assertion1

                if (self.m_chronicle.m_constraint_network.tempvars_minimal_directed_distance(
                    self.m_time, _pers_asrt.time_start) > 0
                ):
                    if (self.m_chronicle.m_constraint_network.propagate_constraints([
                        (ConstraintType.UNIFICATION, (_pers_asrt.sv_val, _trans_asrt.sv_val_sec)),
                        (ConstraintType.TEMPORAL, (_trans_asrt.time_end, _pers_asrt.time_start, 0, False)), 
                        (ConstraintType.TEMPORAL, (_pers_asrt.time_start, _trans_asrt.time_end, 0, False)),
                        ])
                    ):
                        new_constraint_network = deepcopy(self.m_chronicle.m_constraint_network)
                        self.m_chronicle.m_constraint_network.backtrack()

                        res.append(ResolverNodeInfo(
                            p_type = ResolverType.CONFLICT_SEPARATION,
                            p_direct_support_assertion = None,
                            p_direct_support_assertion_supporter = None,
                            p_new_constraint_network = new_constraint_network,
                            p_new_constraints = None,
                            p_action_or_method_instance = None,
                            p_action_or_method_assertion_support_info = None,
                        ))

                if (self.m_chronicle.m_constraint_network.tempvars_minimal_directed_distance(
                    self.m_time, _trans_asrt.time_start) > 0
                ):
                    if (self.m_chronicle.m_constraint_network.propagate_constraints([
                        (ConstraintType.UNIFICATION, (_trans_asrt.sv_val, _pers_asrt)),
                        (ConstraintType.TEMPORAL, (_pers_asrt.time_end, _trans_asrt.time_start, 0, False)), 
                        (ConstraintType.TEMPORAL, (_trans_asrt.time_start, _pers_asrt.time_end, 0, False)),
                        ])
                    ):
                        new_constraint_network = deepcopy(self.m_chronicle.m_constraint_network)
                        self.m_chronicle.m_constraint_network.backtrack()

                        res.append(ResolverNodeInfo(
                            p_type = ResolverType.CONFLICT_SEPARATION,
                            p_direct_support_assertion = None,
                            p_direct_support_assertion_supporter = None,
                            p_new_constraint_network = new_constraint_network,
                            p_new_constraints = None,
                            p_action_or_method_instance = None,
                            p_action_or_method_assertion_support_info = None,
                        ))
                        
            # sv (assertion parameters) separation resolver

            # NOTE: consider the impact of time "now" :
            # - inapplicable if both assertions have already started (before time now)
            # - applicable otherwise (special case if one has already started ?
            #                         or maybe not ? - indeed, if an assertion has already started, 
            #                         the state variables corresponding to its parameters (their values)
            #                         are already fixed... or are they ? - indeed, their domain is not necessarily reduced to a singleton
            #                         in that case, should the lifted representation still be used or should we instantiate all ground variants of the assertions ?
            # NOTE: Same remarks apply to the value unification resolvers above as well...!

            _i_separable = []
            for _i in range(len(self.m_flaw_node_info.m_assertion1.sv_params)):
                if (self.m_chronicle.m_constraint_network.objvars_separable(
                    self.m_flaw_node_info.m_assertion1.sv_params[_i][1], self.m_flaw_node_info.m_assertion2.sv_params[_i][1])
                ):
                    _i_separable.append(_i)
            _i_separable_ps = powerset(_i_separable, include_empty=False)
            
            for _tpl in _i_separable_ps:
                if (self.m_chronicle.m_constraint_network.propagate_constraints(
                    [(ConstraintType.SEPARATION, (self.m_flaw_node_info.m_assertion1.sv_params[_i][1], self.m_flaw_node_info.m_assertion2.sv_params[_i][1]))
                    for _i in _tpl])
                ):
                    new_constraint_network = deepcopy(self.m_chronicle.m_constraint_network)
                    self.m_chronicle.m_constraint_network.backtrack()

                    res.append(ResolverNodeInfo(
                        p_type = ResolverType.CONFLICT_SEPARATION,
                        p_direct_support_assertion = None,
                        p_direct_support_assertion_supporter = None,
                        p_new_constraint_network = new_constraint_network,
                        p_new_constraints = None,
                        p_action_or_method_instance = None,
                        p_action_or_method_assertion_support_info = None,
                    ))

        return res

    # NOTE: TWO POSSIBLE APPROACHES : 
    # EITHER USE FLOAT CURRENT SEARCH NODE TIME (SELF.M_TIME) OR STR
    #
    # IF FLOAT : TEST WHETHER << min_network["candidate_tp","ref_tp"] <= self.m_time <= min_network["ref_tp", "candidate_tp"] >>
    # TO DETERMINE IF "candidate_tp" CAN BE SET/DISPATCHED AT TIME self.m_time. (THEN : POWER SET OF THESE CANDIDATES (FOR "PLAY" MOVES))
    # PROBLEM : HOW TO CHOOSE TIMES FOR "WAIT" MOVES (FLOAT TOO?) ? SAMPLING / "INTUITION" ? (K.Osanlou?)
    #
    # IF STR : USE THE FOLLOWING LOOP TO DETERMINE POSSIBLE NEXT TIMEPOINTS:
    #    next_ctrl_tps = []
    #    for _tp1 in self.m_chronicle.m_constraint_network.m_stn.m_controllability:
    #        # if tp1 is necessarily after self.m_time (i.e its earliest occurence is after self.m_time)
    #        if (self.m_chronicle.m_constraint_network.tempvars_unified(_tp1, self.m_time)
    #            and self.m_chronicle.m_constraint_network.m_stn.m_controllability[_tp1] == True
    #            and self.m_chronicle.m_constraint_network.m_stn.m_minimal_network[_tp1, self.m_time] < 0
    #        ):
    #            _b = True
    #            for _tp2 in self.m_chronicle.m_constraint_network.m_stn.m_controllability: 
    #                # if not (tp1 is necessarily after tp2 and tp2 is necessarily after self.m_time)
    #                if (self.m_chronicle.m_constraint_network.m_stn.m_controllability[_tp2] == True
    #                    and not self.m_chronicle.m_constraint_network.tempvars_unified(_tp1, _tp2)
    #                    and not self.m_chronicle.m_constraint_network.tempvars_unified(_tp2, self.m_time)
    #                    and self.m_chronicle.m_constraint_network.m_stn.m_minimal_network[_tp1, _tp2] < 0
    #                    and self.m_chronicle.m_constraint_network.m_stn.m_minimal_network[ _tp2, self.m_time] < 0
    #                ):
    #                    _b = False
    #                    break
    #        if _b:
    #                next_ctrl_tps.append(_tp1)
    # THEN, POWER SET OF THESE CANDIDATES (FOR "PLAY" MOVES)
    # PROBLEM : HOW TO CHOOSE TIMES FOR "WAIT" MOVES (STR TOO ?) ? ONE OF THE VERY SAME "NEXT" CANDIDATES ?

    def select_charlie_moves(self) -> typing.List[CharlieMoveInfo]:
        res = []
        # use non null self.m_resolver_node_info or self.m_eve_move_info
        return res

    def select_eve_moves(self) -> typing.List[EveMoveInfo]:
        res = []
        # use non null self.m_charlie_move_info
        return res
