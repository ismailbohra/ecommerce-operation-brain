import pytest
import uuid
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset
from graph import create_workflow, run_query
from tests.metrics import (
    get_relevancy_metric,
    get_completeness_metric,
    get_synthesis_quality_metric,
)

WORKFLOW_TEST_CASES = [
    {
        "input": "Why did sales drop yesterday?",
        "expected_agents": ["sales"],
        "expected_keywords": ["$", "revenue", "drop"],
    },
    {
        "input": "What products are out of stock?",
        "expected_agents": ["inventory"],
        "expected_keywords": ["out of stock", "ID"],
    },
    {
        "input": "Show me support ticket summary",
        "expected_agents": ["support"],
        "expected_keywords": ["ticket", "priority"],
    },
    {
        "input": "How are marketing campaigns performing?",
        "expected_agents": ["marketing"],
        "expected_keywords": ["campaign", "CTR", "%"],
    },
    {
        "input": "Has this happened before?",
        "expected_agents": ["memory"],
        "expected_keywords": ["incident", "past"],
    },
    {
        "input": "Give me a full business health report",
        "expected_agents": ["sales", "inventory", "support", "marketing"],
        "expected_keywords": ["$", "stock", "ticket", "campaign"],
    },
]


@pytest.fixture(scope="module")
def workflow():
    return create_workflow()


@pytest.mark.parametrize("test_data", WORKFLOW_TEST_CASES)
def test_workflow_routes_correctly(workflow, test_data):
    thread_id = str(uuid.uuid4())
    result = run_query(workflow, test_data["input"], thread_id)

    routed_agents = result.get("agents_to_call", [])

    for expected_agent in test_data["expected_agents"]:
        assert (
            expected_agent in routed_agents
        ), f"Expected '{expected_agent}' in routed agents for: {test_data['input']}"


@pytest.mark.parametrize("test_data", WORKFLOW_TEST_CASES)
def test_workflow_produces_response(workflow, test_data):
    thread_id = str(uuid.uuid4())
    result = run_query(workflow, test_data["input"], thread_id)

    response = result.get("response", "")

    assert response, f"Workflow should produce a response for: {test_data['input']}"
    assert len(response) > 50, f"Response too short for: {test_data['input']}"


@pytest.mark.parametrize("test_data", WORKFLOW_TEST_CASES)
def test_workflow_response_relevancy(workflow, test_data):
    thread_id = str(uuid.uuid4())
    result = run_query(workflow, test_data["input"], thread_id)

    response = result.get("response", "")
    agent_outputs = result.get("agent_outputs", {})

    test_case = LLMTestCase(
        input=test_data["input"],
        actual_output=response,
        context=list(agent_outputs.values()) if agent_outputs else ["No agent data"],
    )

    assert_test(test_case, [get_relevancy_metric()])


@pytest.mark.parametrize("test_data", WORKFLOW_TEST_CASES)
def test_workflow_contains_keywords(workflow, test_data):
    thread_id = str(uuid.uuid4())
    result = run_query(workflow, test_data["input"], thread_id)

    response = result.get("response", "").lower()

    found_keywords = [
        kw for kw in test_data["expected_keywords"] if kw.lower() in response
    ]

    assert (
        len(found_keywords) > 0
    ), f"Expected at least one of {test_data['expected_keywords']} in response"


def test_workflow_action_query(workflow):
    thread_id = str(uuid.uuid4())
    result = run_query(workflow, "Restock the out of stock products", thread_id)

    response = result.get("response", "")
    actions = result.get("proposed_actions", [])

    assert response, "Action query should produce a response"
    # Actions might be proposed depending on inventory state


def test_workflow_simple_greeting(workflow):
    thread_id = str(uuid.uuid4())
    result = run_query(workflow, "Hello", thread_id)

    agents_called = result.get("agents_to_call", [])

    # Simple greeting should route to "none" or empty
    assert (
        len(agents_called) == 0 or agents_called == []
    ), f"Greeting should not route to agents, got: {agents_called}"


def test_workflow_batch(workflow):
    test_cases = []

    for test_data in WORKFLOW_TEST_CASES:
        thread_id = str(uuid.uuid4())
        result = run_query(workflow, test_data["input"], thread_id)

        response = result.get("response", "")
        agent_outputs = result.get("agent_outputs", {})

        test_cases.append(
            LLMTestCase(
                input=test_data["input"],
                actual_output=response,
                context=(
                    list(agent_outputs.values()) if agent_outputs else ["No agent data"]
                ),
            )
        )

    from deepeval import evaluate

    evaluate(test_cases, [get_relevancy_metric(), get_completeness_metric()])


def test_workflow_memory_context(workflow):
    thread_id = str(uuid.uuid4())

    # First query
    result1 = run_query(workflow, "What were sales yesterday?", thread_id)

    # Follow-up query in same thread
    chat_history = [
        {"role": "user", "content": "What were sales yesterday?"},
        {"role": "assistant", "content": result1.get("response", "")},
    ]

    result2 = run_query(workflow, "Has this happened before?", thread_id, chat_history)

    response = result2.get("response", "")

    assert response, "Follow-up query should produce a response"
    assert "memory" in result2.get("agents_to_call", []), "Should route to memory agent"
