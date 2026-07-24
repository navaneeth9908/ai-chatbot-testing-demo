import pytest

from ai_chatbot_qa_demo.python_trace_examples import negative_index_position, safe_slice_demo, trigger_name_error


def test_negative_index_rule_is_len_plus_index():
    values = ["a", "b", "c", "d"]

    assert negative_index_position(values, -1) == 3
    assert negative_index_position(values, -4) == 0
    assert values[-1] == "d"
    assert values[-4] == "a"


def test_slice_demo_matches_python_rules():
    values = [10, 20, 30, 40, 50]

    assert safe_slice_demo(values, 1, 4) == [20, 30, 40]
    assert safe_slice_demo(values, None, -1) == [10, 20, 30, 40]


def test_name_error_example_is_real_runtime_error_not_compiler_confusion():
    with pytest.raises(NameError):
        trigger_name_error()
