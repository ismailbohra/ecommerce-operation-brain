from abc import ABC, abstractmethod
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage


class BaseAgent(ABC):
    name: str = "base"

    @abstractmethod
    def get_llm(self):
        pass

    @abstractmethod
    def get_prompt(self) -> str:
        pass

    @abstractmethod
    def get_tools(self) -> list:
        pass

    def run(self, query: str) -> str:
        llm = self.get_llm()
        tools = self.get_tools()
        tool_map = {t.name: t for t in tools} if tools else {}

        if tools:
            llm = llm.bind_tools(tools)

        tool_descriptions = ""
        if tools:
            tool_descriptions = (
                "\n\nYou have these tools available - USE THEM to get real data:\n"
            )
            for t in tools:
                tool_descriptions += f"- {t.name}: {t.description}\n"

        messages = [
            SystemMessage(content=self.get_prompt() + tool_descriptions),
            HumanMessage(content=query),
        ]

        max_iterations = 10
        c = 0
        for _ in range(max_iterations):
            response = llm.invoke(messages)

            if not hasattr(response, "tool_calls") or not response.tool_calls:
                return response.content or "No response generated."

            messages.append(response)

            for tc in response.tool_calls:
                tool = tool_map.get(tc["name"])
                if tool:
                    try:
                        result = tool.invoke(tc["args"])
                    except Exception as e:
                        result = f"Error: {str(e)}"
                else:
                    result = f"Unknown tool: {tc['name']}"

                messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))
                c += 1
                print(c)

        return messages[-1].content if messages else "Max iterations reached."
