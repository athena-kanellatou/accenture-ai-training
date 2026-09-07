from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

from day03.models_clients import build_llm


@tool
def multiply(first_number: int, second_number: int) -> int:
    """Multiply two integer numbers."""
    return first_number * second_number


def main() -> None:
    """Demonstrate tool calling with Azure OpenAI."""
    load_dotenv()

    tools = [multiply]
    tools_by_name = {tool.name: tool for tool in tools}

    llm = build_llm()
    llm_with_tools = llm.bind_tools(tools)

    messages = [
        HumanMessage(content="What is 17 multiplied by 24? Use the available tool.")
    ]

    ai_message = llm_with_tools.invoke(messages)
    messages.append(ai_message)

    if not ai_message.tool_calls:
        print("The model did not request a tool.")
        print(ai_message.content)
        return

    for tool_call in ai_message.tool_calls:
        selected_tool = tools_by_name[tool_call["name"]]
        tool_message = selected_tool.invoke(tool_call)
        messages.append(tool_message)

        print("=== Tool Request ===")
        print("Tool:", tool_call["name"])
        print("Arguments:", tool_call["args"])
        print("Result:", tool_message.content)

    final_response = llm_with_tools.invoke(messages)

    print("\n=== Final Model Response ===")
    print(final_response.content)


if __name__ == "__main__":
    main()