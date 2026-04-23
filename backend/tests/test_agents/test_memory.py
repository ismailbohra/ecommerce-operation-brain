import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from graph.agents import MemoryAgent
from tests.metrics import (
    get_relevancy_metric,
    get_tool_usage_metric,
    get_faithfulness_metric,
)

agent = MemoryAgent()

MEMORY_TEST_CASES = [
    {
        "input": "Has this sales drop happened before?",
        "context": ["Historical sales drop incidents"],
        "retrieval_context": [
            "Past incidents include server crashes, stockouts, competitor sales"
        ],
    },
    {
        "input": "What did we do last time we had stockouts?",
        "context": ["Past stockout incidents and resolutions"],
        "retrieval_context": [
            "Stockout incidents involved emergency restock, pre-orders, supplier changes"
        ],
    },
    {
        "input": "Show me similar campaign failures",
        "context": ["Campaign failure incidents"],
        "retrieval_context": [
            "Past campaign issues include wrong targeting, timing errors, fake influencers"
        ],
    },
    {
        "input": "What patterns do we see in support spikes?",
        "context": ["Support ticket spike patterns"],
        "retrieval_context": [
            "Support spikes linked to holidays, product issues, shipping delays"
        ],
    },
    {
        "input": "How did we handle pricing errors before?",
        "context": ["Pricing error incidents"],
        "retrieval_context": [
            "Pricing errors were handled with order honoring, validation rules"
        ],
    },
]


def run_memory_agent(query: str) -> str:
    return agent.run(query)


@pytest.mark.parametrize("test_data", MEMORY_TEST_CASES)
def test_memory_agent_relevancy(test_data):
    output = run_memory_agent(test_data["input"])

    test_case = LLMTestCase(
        input=test_data["input"],
        actual_output=output,
        context=test_data["context"],
    )

    assert_test(test_case, [get_relevancy_metric()])


@pytest.mark.parametrize("test_data", MEMORY_TEST_CASES)
def test_memory_agent_tool_usage(test_data):
    output = run_memory_agent(test_data["input"])

    test_case = LLMTestCase(
        input=test_data["input"],
        actual_output=output,
    )

    assert_test(test_case, [get_tool_usage_metric()])


@pytest.mark.parametrize("test_data", MEMORY_TEST_CASES)
def test_memory_agent_faithfulness(test_data):
    output = run_memory_agent(test_data["input"])

    test_case = LLMTestCase(
        input=test_data["input"],
        actual_output=output,
        retrieval_context=test_data["retrieval_context"],
    )

    assert_test(test_case, [get_faithfulness_metric()])
