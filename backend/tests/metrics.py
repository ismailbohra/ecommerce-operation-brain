# tests/metrics.py
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, GEval
from deepeval.test_case import LLMTestCaseParams
from deepeval.models.base_model import DeepEvalBaseLLM
from config import Config


class AzureOpenAIModel(DeepEvalBaseLLM):
    def __init__(self):
        from langchain_openai import AzureChatOpenAI

        self.model = AzureChatOpenAI(
            api_key=Config.API_KEY,
            azure_endpoint=Config.AZURE_ENDPOINT,
            api_version=Config.API_VERSION,
            azure_deployment=Config.MODEL_SUPERVISOR,
            temperature=0,
        )

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        return self.model.invoke(prompt).content

    async def a_generate(self, prompt: str) -> str:
        result = await self.model.ainvoke(prompt)
        return result.content

    def get_model_name(self) -> str:
        return Config.MODEL_SUPERVISOR


MODEL = AzureOpenAIModel()


def get_relevancy_metric(threshold: float = 0.7):
    return AnswerRelevancyMetric(threshold=threshold, model=MODEL)


def get_faithfulness_metric(threshold: float = 0.7):
    return FaithfulnessMetric(threshold=threshold, model=MODEL)


def get_completeness_metric(threshold: float = 0.7):
    return GEval(
        name="Completeness",
        criteria="Does the response address all aspects of the question with specific data?",
        threshold=threshold,
        model=MODEL,
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    )


def get_tool_usage_metric(threshold: float = 0.7):
    return GEval(
        name="ToolUsage",
        criteria="Does the response contain specific data that could only come from tool calls (real numbers, IDs, dates)?",
        threshold=threshold,
        model=MODEL,
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    )


def get_action_correctness_metric(threshold: float = 0.7):
    return GEval(
        name="ActionCorrectness",
        criteria="Are the proposed actions valid JSON with correct types and required parameters?",
        threshold=threshold,
        model=MODEL,
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    )


def get_routing_accuracy_metric(threshold: float = 0.7):
    return GEval(
        name="RoutingAccuracy",
        criteria="Does the routing decision correctly identify the relevant agents based on the query topic?",
        threshold=threshold,
        model=MODEL,
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
    )


def get_synthesis_quality_metric(threshold: float = 0.7):
    return GEval(
        name="SynthesisQuality",
        criteria="Does the synthesis effectively combine information from multiple sources into a coherent response?",
        threshold=threshold,
        model=MODEL,
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    )


def get_memory_relevance_metric(threshold: float = 0.7):
    return GEval(
        name="MemoryRelevance",
        criteria="Are the retrieved historical incidents relevant to the current query?",
        threshold=threshold,
        model=MODEL,
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    )


def get_data_accuracy_metric(threshold: float = 0.7):
    return GEval(
        name="DataAccuracy",
        criteria="Does the response contain accurate, specific data (numbers, IDs, names) that matches the expected values?",
        threshold=threshold,
        model=MODEL,
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    )


def get_response_structure_metric(threshold: float = 0.7):
    return GEval(
        name="ResponseStructure",
        criteria="Is the response well-structured with clear sections, proper formatting, and logical organization?",
        threshold=threshold,
        model=MODEL,
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    )


def get_action_proposal_metric(threshold: float = 0.7):
    return GEval(
        name="ActionProposal",
        criteria="Does the response correctly identify and propose appropriate actions based on the analysis?",
        threshold=threshold,
        model=MODEL,
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    )


def get_cross_domain_metric(threshold: float = 0.7):
    return GEval(
        name="CrossDomain",
        criteria="Does the response effectively correlate information from multiple domains (sales, inventory, marketing, support)?",
        threshold=threshold,
        model=MODEL,
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    )


def get_historical_context_metric(threshold: float = 0.7):
    return GEval(
        name="HistoricalContext",
        criteria="Does the response appropriately use historical data and past incidents to inform the analysis?",
        threshold=threshold,
        model=MODEL,
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
    )
