from dotenv import load_dotenv
from pydantic import BaseModel, Field

from day03.models_clients import build_llm


class CourseExplanation(BaseModel):
    """Structured explanation of a programming concept."""

    topic: str = Field(description="The programming topic")
    definition: str = Field(description="A beginner-friendly definition")
    example: str = Field(description="A short Python example")
    difficulty: str = Field(description="One of: beginner, intermediate, advanced")


def main() -> None:
    """Generate and validate structured model output."""
    load_dotenv()

    llm = build_llm()
    structured_llm = llm.with_structured_output(CourseExplanation)

    result = structured_llm.invoke(
        "Explain Python lists to a beginner."
    )

    print("=== Structured Output ===")
    print("Topic:", result.topic)
    print("Definition:", result.definition)
    print("Example:", result.example)
    print("Difficulty:", result.difficulty)

    print("\n=== Validated JSON ===")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()