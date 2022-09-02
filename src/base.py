from __future__ import annotations

import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

import typing
from enum import Enum
from src.utility.new_int_id import new_int_id
from src.constraints.constraints import ConstraintNetwork, ConstraintType

############################################

# NOTE: Base, 29 / 08 / 2022

# Lots of basic building blocks / primitives are implemented / defined here.

# Specifically Assertions, Actions and Methods (which are practically the same in terms of structure).

# "Temporal assertions" (Assertions for short) are the main building block of the approach to temporal planning used in the project.
# They can be described as temporally qualified fluents on state variables.
# There are usually two types of Assertions - Persistence and Transition (sometimes called Change) - but sometimes a third type is also considered (Assignment)
# Persistence assertions express the fact that a state variable is equal to a certain value for the whole duration of a temporal interval
# Transition assertions express the fact that a state variable has a certain value at the beginning of a temporal interval,
# and then at some point acquires (or transitions to) another value, which it holds until the interval's end.
# Assertions are used to describe temporal knowledge.
# They are composed of a head (state variable name and parameter names, as well as parameter values (i.e. variables)) and a temporal interval, i.e. a start and end time point variable

# Actions

# Methods

############################################

class AssertionType(Enum):
    PERSISTENCE=0
    TRANSITION=1

class Assertion(tuple):

    __slots__ = []
    def __new__(cls,
        p_type:AssertionType,
        p_sv_name:str,
        p_sv_params_keys:typing.Tuple[str,...],
        p_sv_params_values:typing.Tuple[str,...],
        p_sv_val:object,
        p_sv_val_sec:object=None,
        p_time_start:str="",
        p_time_end:str="",
    ):
        # create (supposed to be) unique timepoint variable names corresponding to the start and end of this assertion
        k = new_int_id()
        if p_time_start == "":
            ts = "_ts_asrt_{0}".format(str(k))
        else:
            ts = p_time_start
        if p_time_end == "":
            te = "_te_asrt_{0}".format(str(k))
        else:
            te = p_time_end
        return tuple.__new__(cls, (p_type, p_sv_name, p_sv_params_keys, p_sv_params_values, ts, te, p_sv_val, p_sv_val_sec))

    @property
    def type(self) -> AssertionType:
        return tuple.__getitem__(self, 0)

    @property
    def sv_name(self) -> str:
        return tuple.__getitem__(self, 1)

    @property
    def sv_params_names(self) -> typing.Tuple[str,...]:
        return tuple.__getitem__(self, 2)

    @property
    def sv_params_values(self) -> typing.Tuple[str,...]:
        return tuple.__getitem__(self, 3)

    @property
    def time_start(self) -> str:
        return tuple.__getitem__(self, 4)

    @property
    def time_end(self) -> str:
        return tuple.__getitem__(self, 5)

    @property
    def sv_val(self) -> object:
        return tuple.__getitem__(self, 6)

    @property
    def sv_val_sec(self) -> object:
        return tuple.__getitem__(self, 7)

    def __getitem__(self, item):
        raise TypeError

    def is_causally_supported_by(self, p_other_assertion:Assertion, p_cn:ConstraintNetwork) -> bool:
        """
        Determines whether this assertion is causally supported by another (specified) assertion, based on the specified constraint network
        Used to determine if an action or method is applicable in a chronicle (at a certain time).
        Arguments:
            p_other_assertion:
                Assertion to check as possible supporter of this one 
            p_cn:
                Constraint network to test against
        Returns:
            True if this assertion is causally supported by the specified input assertion,
            False otherwise
        Side effects:
            None
        """
        # check if the head of this assertion and the specified one is different
        if (self.sv_name == p_other_assertion.sv_name and self.sv_params_names == p_other_assertion.sv_params_names):
            for i in range(len(self.sv_params_values)):
                if p_cn.objvars_separable(self.sv_params_values[i],p_other_assertion.sv_params_values[i]):
                    return False
        else:
            return False
        # check if the start timepoint of this assertion and end timepoint of the input assertion are the same
        if (self.time_start == p_other_assertion.time_end
            or (p_cn.tempvars_minimal_directed_distance(self.time_start, p_other_assertion.time_end) == 0
                and p_cn.tempvars_minimal_directed_distance(p_other_assertion.time_end, self.time_start) == 0)
        ):
            # check if the values at the end of the specified assertion and at the start of this assertion are the same
            if ((p_other_assertion.type == AssertionType.PERSISTENCE and p_cn.objvars_unified(p_other_assertion.sv_val, self.sv_val))
                or (p_other_assertion.type == AssertionType.TRANSITION and p_cn.objvars_unified(p_other_assertion.sv_val_sec, self.sv_val))
            ):
                return True
        return False

    def check_conflict(self, p_asrt2:Assertion, p_cn:ConstraintNetwork):
        """
        Determines whether this assertion is conflicting with the specified input assertion, based on the specified constraint network
        Used to determine (potential) conflicts in a chronicle (for search purposes)
        Arguments:
            p_asrt2
                Assertion to test against
            p_cn:
                Constraint network to test against
        Returns:
            True if this assertion is possibly conflitcing with the specified assertion (based on the specified constraint network)
            False otherwise
        Side effects:
            None
        """
        # an assertion can't be conflicting with itself
        if self == p_asrt2:
            return False
        # check if the head of this assertion and the specified one is different
        elif self.sv_name == p_asrt2.sv_name and self.sv_params_names == p_asrt2.sv_params_names:
            b = True
            for i in range(len(self.sv_params_values)):
                if not p_cn.objvars_unifiable(self.sv_params_values[i],p_asrt2.sv_params_values[i]):
                    return False
        #else:
        #    warnings.warn("shouldn't happen...!!!!")

        if self.type == AssertionType.PERSISTENCE and p_asrt2.type == AssertionType.PERSISTENCE:

            if b and p_cn.objvars_separable(self.sv_val, p_asrt2.sv_val):
                # if the assertions' temporal windows possibly intersect
                if (p_cn.tempvars_minimal_directed_distance(self.time_start,p_asrt2.time_end)
                    * p_cn.tempvars_minimal_directed_distance(p_asrt2.time_start,self.time_end) >= 0
                ):
                    return True
            return False

        elif self.type == AssertionType.TRANSITION and p_asrt2.type == AssertionType.TRANSITION:

            if b:
                # if the assertions' temporal windows possibly intersect
                if (p_cn.tempvars_minimal_directed_distance(self.time_start,p_asrt2.time_end)
                    * p_cn.tempvars_minimal_directed_distance(p_asrt2.time_start,self.time_end) >= 0
                ):
                    # if the transition statements have the same (unified) values and same start and end timepoints
                    # or have the same (unified) values and are connected by the end of one another
                    # then there's no conflict
                    if ((p_cn.objvars_unified(self.sv_val, p_asrt2.sv_val) and p_cn.objvars_unified(self.sv_val_sec, p_asrt2.sv_val_sec)
                        and p_cn.tempvars_minimal_directed_distance(self.time_start,p_asrt2.time_start) == 0
                        and p_cn.tempvars_minimal_directed_distance(p_asrt2.time_start,self.time_start) == 0
                        and p_cn.tempvars_minimal_directed_distance(self.time_end,p_asrt2.time_end) == 0
                        and p_cn.tempvars_minimal_directed_distance(p_asrt2.time_end,self.time_end) == 0)
                    or (p_cn.objvars_unified(self.sv_val, p_asrt2.sv_val_sec)
                        and p_cn.tempvars_minimal_directed_distance(self.time_start,p_asrt2.time_end) == 0
                        and p_cn.tempvars_minimal_directed_distance(p_asrt2.time_end,self.time_start) == 0)
                    or (p_cn.objvars_unified(p_asrt2.sv_val, self.sv_val_sec)
                        and p_cn.tempvars_minimal_directed_distance(p_asrt2.time_start,self.time_end) == 0
                        and p_cn.tempvars_minimal_directed_distance(self.time_end,p_asrt2.time_start) == 0)
                    ):
                        return False
                    else:
                        return True
            return False

        else:

            if self.type == AssertionType.PERSISTENCE:
                asrt_pers = self
                asrt_trans = p_asrt2
            else:
                asrt_pers = p_asrt2
                asrt_trans = self

            if b:
                # if the assertions' temporal windows possibly intersect
                if (p_cn.tempvars_minimal_directed_distance(asrt_pers.time_start,asrt_trans.time_end)
                    * p_cn.tempvars_minimal_directed_distance(asrt_trans.time_start,asrt_pers.time_end) >= 0
                ):
                    # if have the same (unified) values and are connected by the end of one another
                    # then there's no conflict
                    if ((p_cn.objvars_unified(asrt_trans.sv_val_sec, asrt_pers.sv_val)
                        and p_cn.tempvars_minimal_directed_distance(asrt_pers.time_start,asrt_trans.time_end) == 0
                        and p_cn.tempvars_minimal_directed_distance(asrt_trans.time_end,asrt_pers.time_start) == 0)
                    or (p_cn.objvars_unified(asrt_pers.sv_val, asrt_trans.sv_val)
                        and p_cn.tempvars_minimal_directed_distance(asrt_trans.time_start,asrt_pers.time_end) == 0
                        and p_cn.tempvars_minimal_directed_distance(asrt_pers.time_end,asrt_trans.time_start) == 0)
                    ):
                        return False
                    else:
                        return True
            return False

#class Timeline():
#    m_sv_name:str
#    m_assertions:typing.List[Assertion]

class ActionAndMethodTemplate(tuple):

    __slots__ = []
    def __new__(cls,
        p_name:str,
        p_params_names:typing.Tuple[str,...],
        p_assertions:typing.Callable[[str,str,typing.Dict[str,str]],typing.Set[Assertion]]=(lambda ts,te,params: set()),
        p_constraints:typing.Callable[[str,str,typing.Dict[str,str]],typing.Tuple[ConstraintType,typing.Any]]=(lambda ts,te,params: set()),
    ):
        return tuple.__new__(cls, (p_name, p_params_names, p_assertions, p_constraints))

    @property
    def name(self) -> str:
        return tuple.__getitem__(self, 0)

    @property
    def params_names(self) -> typing.Tuple[str,...]:
        return tuple.__getitem__(self, 1)

    @property
    def assertions_function(self) -> typing.Callable[[str,str,typing.Dict[str,str]],typing.Set[Assertion]]:
        return tuple.__getitem__(self, 2)

    @property
    def constraints_function(self) -> typing.Callable[[str,str,typing.Dict[str,str]],typing.Tuple[ConstraintType,typing.Any]]:
        return tuple.__getitem__(self, 3)

    def __getitem__(self, item):
        raise TypeError

class Action(tuple):

    __slots__ = []
    def __new__(cls,
        p_action_template:ActionAndMethodTemplate,
        p_action_params:typing.Dict[str,str],
        p_action_name:str="",
        p_time_start:str="",
        p_time_end:str="",
    ):

        k = new_int_id()
        if p_action_name == "":
            name = "{0}_{1}".format(p_action_template.name, str(k))
        else:
            name = p_action_name
        if p_time_start == "":
            ts = "_ts_act_{0}".format(str(k))
        else:
            ts = p_time_start
        if p_time_end == "":
            te = "_te_act_{0}".format(str(k))
        else:
            te = p_time_end
        return tuple.__new__(cls, (
            p_action_template,
            p_action_params.items(), 
            name,
            ts, te, 
            p_action_template.assertions_function(ts,te,p_action_params), 
            p_action_template.constraints_function(ts,te,p_action_params)))

    @property
    def action_name(self) -> str:
        return tuple.__getitem__(self, 2)

    @property
    def action_params(self) -> typing.Dict[str,str]:
        return dict(tuple.__getitem__(self, 1))

    @property
    def time_start(self) -> str:
        return tuple.__getitem__(self, 3)

    @property
    def time_end(self) -> str:
        return tuple.__getitem__(self, 4)

    @property
    def assertions(self) -> typing.Set[Assertion]:
        return tuple.__getitem__(self, 5)
    # (unsupported assertions) (Nau 2020 : "no supported assertions = if you insert an action into a chronicle, you need to figure out how to support it")
    # reminds of HGN(?) ActorSim(?) and Bit-Monnot 2020 (hierarchronicles - "method chronicles with subtasks and no effects" and "action chronicles with effects and no subtasks")

    @property
    def constraints(self) -> typing.Set[typing.Tuple[ConstraintType,typing.Any]]:
        return tuple.__getitem__(self, 6)

    def __getitem__(self, item):
        raise TypeError

class Method(tuple):

    __slots__ = []
    def __new__(cls,
        p_method_template:ActionAndMethodTemplate,
        p_method_params:typing.Dict[str,str],
        p_method_name:str="",
        p_time_start:str="",
        p_time_end:str="",
    ):

        k = new_int_id()
        if p_method_name == "":
            name = "{0}_{1}".format(p_method_template.name, str(k))
        else:
            name = p_method_name
        if p_time_start == "":
            ts = "_ts_act_{0}".format(str(k))
        else:
            ts = p_time_start
        if p_time_end == "":
            te = "_te_act_{0}".format(str(k))
        else:
            te = p_time_end
        return tuple.__new__(cls, (
            p_method_template,
            p_method_params.items(), 
            name,
            ts, te, 
            p_method_template.assertions_function(ts,te,p_method_params), 
            p_method_template.constraints_function(ts,te,p_method_params)))

    @property
    def method_name(self) -> str:
        return tuple.__getitem__(self, 2)

    @property
    def method_params(self) -> typing.Dict[str,str]:
        return dict(tuple.__getitem__(self, 1))

    @property
    def time_start(self) -> str:
        return tuple.__getitem__(self, 3)

    @property
    def time_end(self) -> str:
        return tuple.__getitem__(self, 4)

    @property
    def assertions(self) -> typing.Set[Assertion]:
        return tuple.__getitem__(self, 5)
    # actually subgoals ; Nau 2020: "can't make a change happen, can only create subgoals"

    @property
    def constraints(self) -> typing.Set[typing.Tuple[ConstraintType,typing.Any]]:
        return tuple.__getitem__(self, 6)


