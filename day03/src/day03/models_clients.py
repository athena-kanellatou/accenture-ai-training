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
    """Validate the Azure OpenAI configuration."""
    missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]

    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
        )


def build_llm() -> AzureChatOpenAI:
    """Create an Azure OpenAI chat client."""
    validate_environment()

    return AzureChatOpenAI(
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=os.environ["OPENAI_API_VERSION"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        temperature=0,
    )


def main() -> None:
    """Create the client and make one test call."""
    load_dotenv()

    llm = build_llm()
    response = llm.invoke("Say hello in exactly three words.")

    print("=== Azure OpenAI Client ===")
    print("Response:", response.content)


if __name__ == "__main__":
    main()