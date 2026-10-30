from thesis_routing.tools.academic_rules import should_escalate_to_human
from thesis_routing.tools.prerequisite_checker import can_take

def test_escalate_type_a() -> None:
    assert should_escalate_to_human('A') is True
    assert should_escalate_to_human('N') is False

def test_can_take() -> None:
    graph = {'C2': {'prereq': ['C1']}}
    assert can_take({'passed_courses': ['C1']}, 'C2', graph) is True
