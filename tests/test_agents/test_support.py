import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from graph.agents import SupportAgent
from tests.metrics import (
    get_relevancy_metric,
    get_tool_usage_metric,
    get_data_accuracy_metric,
)

agent = SupportAgent()

SUPPORT_TEST_CASES = [
    {
        "input": "How many open tickets do we have?",
        "context": ["Open ticket count and priority breakdown"],
        "expected_keywords": ["tickets", "open", "high", "medium", "low"],
    },
    {
        "input": "Show me high priority tickets",
        "context": ["High priority ticket list"],
        "expected_keywords": ["high", "priority", "ID"],
    },
    {
        "input": "What are the main support issues?",
        "context": ["Ticket summary by category"],
        "expected_keywords": ["shipping", "order", "refund", "technical"],
    },
    {
        "input": "Are there any shipping complaints?",
        "context": ["Shipping category tickets"],
        "expected_keywords": ["shipping", "ticket", "ID"],
    },
    {
        "input": "What's the ticket trend this week?",
        "context": ["Ticket creation trends"],
        "expected_keywords": ["tickets", "day", "trend"],
    },
]


def run_support_agent(query: str) -> str:
    return agent.run(query)


@pytest.mark.parametrize("test_data", SUPPORT_TEST_CASES)
def test_support_agent_relevancy(test_data):
    output = run_support_agent(test_data["input"])

    test_case = LLMTestCase(
        input=test_data["input"],
        actual_output=output,
        context=test_data["context"],
    )

    assert_test(test_case, [get_relevancy_metric()])


@pytest.mark.parametrize("test_data", SUPPORT_TEST_CASES)
def test_support_agent_tool_usage(test_data):
    output = run_support_agent(test_data["input"])

    test_case = LLMTestCase(
        input=test_data["input"],
        actual_output=output,
    )

    assert_test(test_case, [get_tool_usage_metric()])


@pytest.mark.parametrize("test_data", SUPPORT_TEST_CASES)
def test_support_includes_ticket_ids(test_data):
    output = run_support_agent(test_data["input"])

    has_id = "ID" in output or "[" in output or "#" in output
    assert has_id, f"Response should include ticket IDs: {output[:200]}"
