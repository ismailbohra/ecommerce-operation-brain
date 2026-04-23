import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from graph.agents import MarketingAgent
from tests.metrics import (
    get_relevancy_metric,
    get_tool_usage_metric,
    get_data_accuracy_metric,
)

agent = MarketingAgent()

MARKETING_TEST_CASES = [
    {
        "input": "How are our campaigns performing?",
        "context": ["Campaign performance metrics"],
        "expected_keywords": ["campaign", "CTR", "%", "budget"],
    },
    {
        "input": "Which campaigns are underperforming?",
        "context": ["Low CTR campaigns"],
        "expected_keywords": ["CTR", "%", "ID", "poor"],
    },
    {
        "input": "What's our total ad spend?",
        "context": ["Campaign budget and spend data"],
        "expected_keywords": ["$", "spent", "budget"],
    },
    {
        "input": "Show me email campaign performance",
        "context": ["Email channel campaigns"],
        "expected_keywords": ["email", "CTR", "%"],
    },
    {
        "input": "What's the ROI of our campaigns?",
        "context": ["Campaign ROI analysis"],
        "expected_keywords": ["ROI", "%", "revenue"],
    },
]


def run_marketing_agent(query: str) -> str:
    return agent.run(query)


@pytest.mark.parametrize("test_data", MARKETING_TEST_CASES)
def test_marketing_agent_relevancy(test_data):
    output = run_marketing_agent(test_data["input"])

    test_case = LLMTestCase(
        input=test_data["input"],
        actual_output=output,
        context=test_data["context"],
    )

    assert_test(test_case, [get_relevancy_metric()])


@pytest.mark.parametrize("test_data", MARKETING_TEST_CASES)
def test_marketing_agent_tool_usage(test_data):
    output = run_marketing_agent(test_data["input"])

    test_case = LLMTestCase(
        input=test_data["input"],
        actual_output=output,
    )

    assert_test(test_case, [get_tool_usage_metric()])


@pytest.mark.parametrize("test_data", MARKETING_TEST_CASES)
def test_marketing_includes_campaign_ids(test_data):
    output = run_marketing_agent(test_data["input"])

    has_id = "ID" in output or "id:" in output.lower()
    assert has_id, f"Response should include campaign IDs: {output[:200]}"
