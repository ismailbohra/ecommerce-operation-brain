import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset
from langchain_core.messages import SystemMessage, HumanMessage
from config import get_supervisor_llm, get_callbacks
from graph.prompts import SYNTHESIS_PROMPT
from tests.metrics import (
    get_relevancy_metric,
    get_synthesis_quality_metric,
    get_completeness_metric,
)

SYNTHESIS_TEST_CASES = [
    {
        "input": "Why did sales drop yesterday?",
        "agent_outputs": {
            "sales": "Yesterday's revenue was $1,200 from 15 orders, down 65% from typical $3,500.",
            "inventory": "3 products out of stock: Wireless Headphones (ID: 1), Yoga Mat (ID: 4), Protein Powder (ID: 11)",
            "marketing": "Social Media Push campaign has 0.8% CTR, below 1% threshold.",
            "memory": "Similar incident last month: stockout + poor campaign led to 45% sales drop.",
        },
    },
    {
        "input": "Give me a business summary",
        "agent_outputs": {
            "sales": "7-day revenue: $24,500 from 312 orders. Top product: Running Shoes at $4,200.",
            "inventory": "15 products tracked. 3 out of stock, 5 low stock.",
            "support": "14 open tickets: 5 high priority, 6 medium, 3 low.",
            "marketing": "6 active campaigns. Total spend: $18,800 of $23,500 budget.",
        },
    },
    {
        "input": "What should we prioritize fixing?",
        "agent_outputs": {
            "inventory": "Critical: Wireless Headphones (ID: 1) - top seller, 0 stock. Losing ~$500/day.",
            "support": "5 high priority tickets. Oldest is 48 hours without response.",
            "marketing": "Social campaign at 0.8% CTR wasting $100/day.",
        },
    },
]


def run_synthesis(query: str, agent_outputs: dict) -> str:
    llm = get_supervisor_llm()
    callbacks = get_callbacks()

    findings = "\n\n---\n\n".join(
        [f"## {k.upper()} Agent\n\n{v}" for k, v in agent_outputs.items()]
    )

    content = f"User Question: {query}\n\n# Agent Findings\n\n{findings}"

    messages = [
        SystemMessage(content=SYNTHESIS_PROMPT),
        HumanMessage(content=content),
    ]

    response = llm.invoke(messages, config={"callbacks": callbacks})
    return response.content


@pytest.mark.parametrize("test_data", SYNTHESIS_TEST_CASES)
def test_synthesis_relevancy(test_data):
    output = run_synthesis(test_data["input"], test_data["agent_outputs"])

    context = list(test_data["agent_outputs"].values())

    test_case = LLMTestCase(
        input=test_data["input"],
        actual_output=output,
        context=context,
    )

    assert_test(test_case, [get_relevancy_metric()])


@pytest.mark.parametrize("test_data", SYNTHESIS_TEST_CASES)
def test_synthesis_quality(test_data):
    output = run_synthesis(test_data["input"], test_data["agent_outputs"])

    context = list(test_data["agent_outputs"].values())

    test_case = LLMTestCase(
        input=test_data["input"],
        actual_output=output,
        context=context,
    )

    assert_test(test_case, [get_synthesis_quality_metric()])


@pytest.mark.parametrize("test_data", SYNTHESIS_TEST_CASES)
def test_synthesis_completeness(test_data):
    output = run_synthesis(test_data["input"], test_data["agent_outputs"])

    test_case = LLMTestCase(
        input=test_data["input"],
        actual_output=output,
    )

    assert_test(test_case, [get_completeness_metric()])


@pytest.mark.parametrize("test_data", SYNTHESIS_TEST_CASES)
def test_synthesis_includes_data_from_agents(test_data):
    output = run_synthesis(test_data["input"], test_data["agent_outputs"])

    # Check that specific numbers from agent outputs appear in synthesis
    has_numbers = any(char.isdigit() for char in output)
    has_currency = "$" in output

    assert has_numbers, "Synthesis should include specific numbers from agent data"
    assert has_currency, "Synthesis should include currency values from agent data"


def test_synthesis_batch():
    test_cases = []

    for test_data in SYNTHESIS_TEST_CASES:
        output = run_synthesis(test_data["input"], test_data["agent_outputs"])
        context = list(test_data["agent_outputs"].values())

        test_cases.append(
            LLMTestCase(
                input=test_data["input"],
                actual_output=output,
                context=context,
            )
        )

    from deepeval import evaluate

    evaluate(test_cases, [get_relevancy_metric(), get_synthesis_quality_metric()])
