from abc import ABC, abstractmethod
from langchain_core.messages import SystemMessage, HumanMessage


class BaseAgent(ABC):
    name: str = "base"

    @abstractmethod
    def get_llm(self):
        pass

    @abstractmethod
    def get_prompt(self) -> str:
        pass

    @abstractmethod
    def fetch_data(self, query: str) -> dict:
        pass

    @abstractmethod
    def format_data(self, data: dict) -> str:
        pass

    def run(self, query: str) -> str:
        data = self.fetch_data(query)
        formatted = self.format_data(data)
        llm = self.get_llm()

        messages = [
            SystemMessage(content=self.get_prompt()),
            HumanMessage(content=f"{formatted}\n\nUser Query: {query}"),
        ]

        return llm.invoke(messages).content
