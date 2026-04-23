import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset
from graph.agents import InventoryAgent
from tests.metrics import (
    get_relevancy_metric,
    get_tool_usage_metric,
    get_data_accuracy_metric,
)

agent = InventoryAgent()

INVENTORY_TEST_CASES = [
    {
        "input": "What products are out of stock?",
        "context": ["Inventory status with stock levels"],
        "expected_keywords": ["out of stock", "ID", "0 units"],
    },
    {
        "input": "Show me low stock items",
        "context": ["Products below reorder level"],
        "expected_keywords": ["low", "stock", "units", "reorder"],
    },
    {
        "input": "What is the inventory status?",
        "context": ["Full inventory list with stock and reorder levels"],
        "expected_keywords": ["stock", "units", "critical", "low", "ok"],
    },
    {
        "input": "Check stock for product ID 1",
        "context": ["Single product inventory details"],
        "expected_keywords": ["ID", "units", "stock"],
    },
    {
        "input": "Which products need restocking?",
        "context": ["Products needing restock based on levels"],
        "expected_keywords": ["restock", "units", "ID"],
    },
]


def run_inventory_agent(query: str) -> str:
    return agent.run(query)


@pytest.mark.parametrize("test_data", INVENTORY_TEST_CASES)
def test_inventory_agent_relevancy(test_data):
    output = run_inventory_agent(test_data["input"])

    test_case = LLMTestCase(
        input=test_data["input"],
        actual_output=output,
        context=test_data["context"],
    )

    assert_test(test_case, [get_relevancy_metric()])


@pytest.mark.parametrize("test_data", INVENTORY_TEST_CASES)
def test_inventory_agent_tool_usage(test_data):
    output = run_inventory_agent(test_data["input"])

    test_case = LLMTestCase(
        input=test_data["input"],
        actual_output=output,
    )

    assert_test(test_case, [get_tool_usage_metric()])


@pytest.mark.parametrize("test_data", INVENTORY_TEST_CASES)
def test_inventory_includes_product_ids(test_data):
    output = run_inventory_agent(test_data["input"])

    has_id = "ID" in output or "id:" in output.lower()
    assert (
        has_id
    ), f"Response should include product IDs for action support: {output[:200]}"


def test_inventory_agent_batch():
    test_cases = []

    for test_data in INVENTORY_TEST_CASES:
        output = run_inventory_agent(test_data["input"])
        test_cases.append(
            LLMTestCase(
                input=test_data["input"],
                actual_output=output,
                context=test_data["context"],
            )
        )

    from deepeval import evaluate

    evaluate(test_cases, [get_relevancy_metric(), get_tool_usage_metric()])
