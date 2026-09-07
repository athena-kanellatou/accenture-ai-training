import os

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI


REQUIRED_ENV_VARS = (
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "OPENAI_API_VERSION",
    "AZURE_OPENAI_DEPLOYMENT_NAME",
)


def validate_environment() -> None:
    """Check that real Azure credentials have been configured."""
    missing = [
        name
        for name in REQUIRED_ENV_VARS
        if not os.getenv(name) or "your-" in os.environ[name].lower()
    ]

    if missing:
        raise RuntimeError(
            "Replace the placeholder values for: " + ", ".join(missing)
        )


def create_chat_model() -> AzureChatOpenAI:
    """Create the Azure OpenAI chat model."""
    validate_environment()

    return AzureChatOpenAI(
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=os.environ["OPENAI_API_VERSION"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        temperature=0,
    )


def main() -> None:
    """Send one test prompt to Azure OpenAI."""
    load_dotenv()
    llm = create_chat_model()

    response = llm.invoke("What is the capital of France?")
    print(response.content)


if __name__ == "__main__":
    main()