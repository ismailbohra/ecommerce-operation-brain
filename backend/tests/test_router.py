import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset
from langchain_core.messages import SystemMessage, HumanMessage
from config import get_supervisor_llm, get_callbacks
from graph.prompts import ROUTER_PROMPT
from tests.metrics import get_routing_accuracy_metric

ROUTER_TEST_CASES = [
    {
        "input": "Why did sales drop yesterday?",
        "expected": "sales,inventory,marketing,memory",
        "must_include": ["sales"],
        "must_not_include": [],
    },
    {
        "input": "What products are out of stock?",
        "expected": "inventory",
        "must_include": ["inventory"],
        "must_not_include": ["marketing"],
    },
    {
        "input": "Show me support tickets",
        "expected": "support",
        "must_include": ["support"],
        "must_not_include": ["sales"],
    },
    {
        "input": "How are campaigns performing?",
        "expected": "marketing",
        "must_include": ["marketing"],
        "must_not_include": ["inventory"],
    },
    {
        "input": "Has this happened before?",
        "expected": "memory",
        "must_include": ["memory"],
        "must_not_include": [],
    },
    {
        "input": "Give me a full business summary",
        "expected": "sales,inventory,support,marketing",
        "must_include": ["sales", "inventory", "support", "marketing"],
        "must_not_include": [],
    },
    {
        "input": "Hello, how are you?",
        "expected": "none",
        "must_include": [],
        "must_not_include": ["sales", "inventory", "support", "marketing"],
    },
    {
        "input": "Restock the products",
        "expected": "inventory",
        "must_include": ["inventory"],
        "must_not_include": [],
    },
    {
        "input": "Pause underperforming campaigns",
        "expected": "marketing",
        "must_include": ["marketing"],
        "must_not_include": [],
    },
    {
        "input": "What's the weather today?",
        "expected": "none",
        "must_include": [],
        "must_not_include": ["sales", "inventory"],
    },
]


def run_router(query: str) -> str:
    llm = get_supervisor_llm()
    callbacks = get_callbacks()

    messages = [
        SystemMessage(content=ROUTER_PROMPT),
        HumanMessage(content=f"Query: {query}"),
    ]

    response = llm.invoke(messages, config={"callbacks": callbacks})
    return response.content.strip().lower()


@pytest.mark.parametrize("test_data", ROUTER_TEST_CASES)
def test_router_accuracy(test_data):
    output = run_router(test_data["input"])

    test_case = LLMTestCase(
        input=test_data["input"],
        actual_output=output,
        expected_output=test_data["expected"],
    )

    assert_test(test_case, [get_routing_accuracy_metric()])


@pytest.mark.parametrize("test_data", ROUTER_TEST_CASES)
def test_router_includes_required_agents(test_data):
    output = run_router(test_data["input"])
    agents = [a.strip() for a in output.split(",")]

    for required in test_data["must_include"]:
        assert (
            required in agents
        ), f"Expected '{required}' in routing for: {test_data['input']}"


@pytest.mark.parametrize("test_data", ROUTER_TEST_CASES)
def test_router_excludes_irrelevant_agents(test_data):
    output = run_router(test_data["input"])

    for excluded in test_data["must_not_include"]:
        assert (
            excluded not in output
        ), f"'{excluded}' should not be in routing for: {test_data['input']}"


def test_router_returns_valid_format():
    valid_agents = {"sales", "inventory", "support", "marketing", "memory", "none"}

    for test_data in ROUTER_TEST_CASES:
        output = run_router(test_data["input"])
        agents = [a.strip() for a in output.replace(".", "").split(",")]

        for agent in agents:
            assert (
                agent in valid_agents
            ), f"Invalid agent '{agent}' returned for: {test_data['input']}"


def test_router_batch():
    test_cases = []

    for test_data in ROUTER_TEST_CASES:
        output = run_router(test_data["input"])
        test_cases.append(
            LLMTestCase(
                input=test_data["input"],
                actual_output=output,
                expected_output=test_data["expected"],
            )
        )

    from deepeval import evaluate

    evaluate(test_cases, [get_routing_accuracy_metric()])
