from __future__ import annotations

import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

import typing
from enum import Enum
from src.utility.new_int_id import new_int_id
from src.constraints.constraints import ConstraintNetwork, ConstraintType
from src.assertion import Assertion

############################################


############################################

class ActionMethodTemplate(tuple):

    class Type(Enum):
        ACTION = 0
        METHOD = 1

    __slots__ = []
    def __new__(cls,
        p_type:Type,
        p_name:str,
        p_params:typing.Dict[str,str],
        p_assertions_func:typing.Callable[[str,str,typing.Dict[str,str]],typing.Set[Assertion]]=(lambda ts,te,params: set()),
        p_constraints_func:typing.Callable[[str,str,typing.Dict[str,str]],typing.Tuple[ConstraintType,typing.Any]]=(lambda ts,te,params: set()),
    ):
        return tuple.__new__(cls, (p_name, p_params.items(), p_assertions_func, p_constraints_func, p_type))

    @property
    def type(self) -> Type:
        return tuple.__getitem__(self, 4)

    @property
    def name(self) -> str:
        return tuple.__getitem__(self, 0)

    @property
    def params(self) -> typing.Dict[str,str]:
        return dict(tuple.__getitem__(self, 1))

    @property
    def assertions_func(self) -> typing.Callable[[str,str,typing.Dict[str,str]],typing.Set[Assertion]]:
        return tuple.__getitem__(self, 2)

    @property
    def constraints_func(self) -> typing.Callable[[str,str,typing.Dict[str,str]],typing.Set[typing.Tuple[ConstraintType,typing.Any]]]:
        return tuple.__getitem__(self, 3)

    def __getitem__(self, item):
        raise TypeError

class ActionMethod(tuple):

    __slots__ = []
    def __new__(cls,
        p_template:ActionMethodTemplate,
        p_args:typing.Dict[str,str],
        p_name:str="",
        p_time_start:str="",
        p_time_end:str="",
    ):

        k = new_int_id()
        if p_name == "":
            name = "{0}_{1}".format(p_template.name, str(k))
        else:
            name = p_name
        if p_time_start == "":
            ts = "__ts_act_{0}".format(str(k))
        else:
            ts = p_time_start
        if p_time_end == "":
            te = "__te_act_{0}".format(str(k))
        else:
            te = p_time_end

        return tuple.__new__(cls, (
            p_template,
            p_args.items(), 
            name,
            ts, te, 
            p_template.assertions_func(ts,te,p_args), 
            p_template.constraints_func(ts,te,p_args)))

    @property
    def type(self) -> ActionMethodTemplate.Type:
        return tuple.__getitem__(self, 0).type

    @property
    def template(self) -> ActionMethodTemplate:
        return tuple.__getitem__(self, 0)

    @property
    def name(self) -> str:
        return tuple.__getitem__(self, 2)

    @property
    def args(self) -> typing.Dict[str,str]:
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

    @property
    def constraints(self) -> typing.Set[typing.Tuple[ConstraintType,typing.Any]]:
        return tuple.__getitem__(self, 6)

    def __getitem__(self, item):
        raise TypeError

    def propagate_applicability(self,
        p_time:str,
        p_cn:ConstraintNetwork,
        p_assertions:typing.Iterable[Assertion],
        p_assertion_to_support:Assertion=None,
        p_backtrack=True,
    ) -> typing.Iterable[typing.Tuple[Assertion,Assertion]]:

        num_backtracks = 0
        res = []
        # the action/method's starting time must be "now" (p_time)
        if not p_cn.propagate_constraints(self.constraints):
            return []#([], 0)
        num_backtracks += 1
        if p_cn.tempvars_unified(self.time_start, p_time):
        #if (p_cn.propagate_constraints([
        #        (ConstraintType.TEMPORAL,(self.time_start, p_time, 0, False)),
        #        (ConstraintType.TEMPORAL,(p_time, self.time_start, 0, False))])
        #    and p_cn.tempvars_minimal_directed_distance(self.time_start, p_time) == 0
        #):
            num_backtracks += 1
            b1 = False
            b3 = (p_assertion_to_support == None)
            for i_act_or_meth_asrt in self.assertions:
                b2 = False
                for i_chronicle_asrt in p_assertions:
                    # just in case
                    if i_act_or_meth_asrt == i_chronicle_asrt:
                        break
                    # the chronicle must support all action/method's assertions which start at the same time as it
                    if not b2 and p_cn.tempvars_unified(i_act_or_meth_asrt.time_start,self.time_start):
                        cs = i_act_or_meth_asrt.propagate_causal_support_by(i_chronicle_asrt, p_cn, p_backtrack=False)
                        if cs[0]:
                            num_backtracks += cs[1]
                            res.append((i_chronicle_asrt, i_act_or_meth_asrt))
                            b2 = True
                            if b1:
                                break
                    # the action/method must have at least one assertion (any, not necessarily starting at the same as it)
                    # supporting an unsupported assertion already present in the chronicle
                    if not b1:
                        cs = i_chronicle_asrt.propagate_causal_support_by(i_act_or_meth_asrt, p_cn, p_backtrack=False)
                        if cs[0]:
                            num_backtracks += cs[1]
                            res.append((i_act_or_meth_asrt, i_chronicle_asrt))
                            b1 = True
                            if not b3 and i_chronicle_asrt == p_assertion_to_support:
                                b3 = True
                            if b2:
                                break
                if not b2:
                    for _ in range(num_backtracks):
                        p_cn.backtrack()
                    return []#([], 0)
            if not b1 or not b3:
                for _ in range(num_backtracks):
                    p_cn.backtrack()
                return []#([], 0)
        if p_backtrack:
            for _ in range(num_backtracks):
                p_cn.backtrack()
        return res#(res, num_backtracks)
