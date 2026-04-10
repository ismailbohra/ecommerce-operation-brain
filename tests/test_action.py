import pytest
import json
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from langchain_core.messages import SystemMessage, HumanMessage
from config import get_action_llm, get_callbacks
from graph.prompts import ACTION_PROMPT
from graph.actions import parse_actions
from tests.metrics import get_action_correctness_metric

ACTION_TEST_CASES = [
    {
        "input": "Fix the inventory issues",
        "synthesis": "3 products out of stock: Wireless Headphones (ID: 1), Yoga Mat (ID: 4), Protein Powder (ID: 11). Recommend restocking.",
        "expected_action_types": ["restock"],
        "expected_count_min": 1,
    },
    {
        "input": "Pause underperforming campaigns",
        "synthesis": "Social Media Push (ID: 2) has 0.8% CTR, well below 1% threshold. Wasting $100/day.",
        "expected_action_types": ["pause_campaign"],
        "expected_count_min": 1,
    },
    {
        "input": "Apply 10% discount to slow products",
        "synthesis": "Desk Lamp (ID: 8) has low sales but high stock. Consider discount to move inventory.",
        "expected_action_types": ["discount"],
        "expected_count_min": 1,
    },
    {
        "input": "Resolve the shipping tickets",
        "synthesis": "5 high priority shipping tickets: #101, #105, #109. All related to carrier delays.",
        "expected_action_types": ["resolve_ticket"],
        "expected_count_min": 1,
    },
    {
        "input": "What's the inventory status?",
        "synthesis": "Inventory is stable. 3 items out of stock but no immediate action needed.",
        "expected_action_types": [],
        "expected_count_min": 0,
    },
]


def run_action_planner(query: str, synthesis: str) -> str:
    llm = get_action_llm()
    callbacks = get_callbacks()

    context = f"""
## User Request
{query}

## Analysis Summary
{synthesis}
"""

    messages = [
        SystemMessage(content=ACTION_PROMPT),
        HumanMessage(content=context),
    ]

    response = llm.invoke(messages, config={"callbacks": callbacks})
    return response.content


@pytest.mark.parametrize("test_data", ACTION_TEST_CASES)
def test_action_correctness(test_data):
    output = run_action_planner(test_data["input"], test_data["synthesis"])

    test_case = LLMTestCase(
        input=test_data["input"],
        actual_output=output,
        context=[test_data["synthesis"]],
    )

    assert_test(test_case, [get_action_correctness_metric()])


@pytest.mark.parametrize("test_data", ACTION_TEST_CASES)
def test_action_returns_valid_json(test_data):
    output = run_action_planner(test_data["input"], test_data["synthesis"])
    actions = parse_actions(output)

    assert isinstance(actions, list), f"Actions should be a list, got: {type(actions)}"


@pytest.mark.parametrize("test_data", ACTION_TEST_CASES)
def test_action_count(test_data):
    output = run_action_planner(test_data["input"], test_data["synthesis"])
    actions = parse_actions(output)

    assert (
        len(actions) >= test_data["expected_count_min"]
    ), f"Expected at least {test_data['expected_count_min']} actions, got {len(actions)}"


@pytest.mark.parametrize("test_data", ACTION_TEST_CASES)
def test_action_types(test_data):
    if not test_data["expected_action_types"]:
        return  # Skip if no actions expected

    output = run_action_planner(test_data["input"], test_data["synthesis"])
    actions = parse_actions(output)

    action_types = [a.get("type") for a in actions]

    for expected_type in test_data["expected_action_types"]:
        assert (
            expected_type in action_types
        ), f"Expected action type '{expected_type}' not found in {action_types}"


@pytest.mark.parametrize("test_data", ACTION_TEST_CASES)
def test_action_has_required_fields(test_data):
    output = run_action_planner(test_data["input"], test_data["synthesis"])
    actions = parse_actions(output)

    required_fields = ["type", "params", "description", "reason"]

    for action in actions:
        for field in required_fields:
            assert field in action, f"Action missing required field '{field}': {action}"


def test_action_no_action_returns_empty():
    output = run_action_planner(
        "What's the weather?", "No business issues detected. All systems normal."
    )
    actions = parse_actions(output)

    assert (
        len(actions) == 0
    ), f"Expected empty actions for non-action query, got: {actions}"
