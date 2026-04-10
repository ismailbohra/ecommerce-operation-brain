import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset
from graph.agents import SalesAgent
from tests.metrics import (
    get_relevancy_metric,
    get_tool_usage_metric,
    get_data_accuracy_metric,
    get_completeness_metric,
)

agent = SalesAgent()

SALES_TEST_CASES = [
    {
        "input": "What were the sales yesterday?",
        "context": ["Sales data includes daily revenue and order counts"],
        "expected_keywords": ["$", "revenue", "orders"],
    },
    {
        "input": "Show me the top selling products this week",
        "context": ["Product sales data with revenue and units sold"],
        "expected_keywords": ["product", "$", "units"],
    },
    {
        "input": "Compare sales from last week to this week",
        "context": ["Period comparison with revenue and order changes"],
        "expected_keywords": ["%", "change", "revenue"],
    },
    {
        "input": "Which region has the highest sales?",
        "context": ["Regional sales breakdown"],
        "expected_keywords": ["region", "$", "North", "South", "East", "West"],
    },
    {
        "input": "How are sales trending over the past 7 days?",
        "context": ["Daily sales trend data"],
        "expected_keywords": ["$", "day", "revenue"],
    },
]


def run_sales_agent(query: str) -> str:
    return agent.run(query)


@pytest.mark.parametrize("test_data", SALES_TEST_CASES)
def test_sales_agent_relevancy(test_data):
    output = run_sales_agent(test_data["input"])

    test_case = LLMTestCase(
        input=test_data["input"],
        actual_output=output,
        context=test_data["context"],
    )

    assert_test(test_case, [get_relevancy_metric()])


@pytest.mark.parametrize("test_data", SALES_TEST_CASES)
def test_sales_agent_tool_usage(test_data):
    output = run_sales_agent(test_data["input"])

    test_case = LLMTestCase(
        input=test_data["input"],
        actual_output=output,
    )

    assert_test(test_case, [get_tool_usage_metric()])


@pytest.mark.parametrize("test_data", SALES_TEST_CASES)
def test_sales_agent_data_accuracy(test_data):
    output = run_sales_agent(test_data["input"])

    test_case = LLMTestCase(
        input=test_data["input"],
        actual_output=output,
        context=test_data["context"],
    )

    assert_test(test_case, [get_data_accuracy_metric()])


def test_sales_agent_batch():
    test_cases = []

    for test_data in SALES_TEST_CASES:
        output = run_sales_agent(test_data["input"])
        test_cases.append(
            LLMTestCase(
                input=test_data["input"],
                actual_output=output,
                context=test_data["context"],
            )
        )

    from deepeval import evaluate

    evaluate(test_cases, [get_relevancy_metric(), get_tool_usage_metric()])
