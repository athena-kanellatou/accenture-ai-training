from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

from day03.models_clients import build_llm


def build_chain():
    """Create a prompt template connected to the Azure OpenAI model."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful programming tutor. "
                "Give clear and concise explanations.",
            ),
            (
                "human",
                "Explain {topic} to a beginner using one simple example.",
            ),
        ]
    )

    llm = build_llm()

    return prompt | llm


def main() -> None:
    """Run the prompt chain."""
    load_dotenv()

    chain = build_chain()
    response = chain.invoke({"topic": "Python functions"})

    print("=== Prompt Template and LCEL Chain ===")
    print(response.content)


if __name__ == "__main__":
    main()
