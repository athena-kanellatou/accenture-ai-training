"""Build and run an Azure OpenAI-powered Deep Agent."""

import argparse
import os
from collections.abc import Sequence

from deepagents import SubAgent, create_deep_agent
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
from langchain_openai import AzureChatOpenAI

from day24.tools import get_incident, run_diagnostics, search_runbook


SYSTEM_PROMPT = """
You are the lead AI incident-response coordinator.

For every request:
1. Create and maintain a short plan.
2. Ground every claim in tool output; never invent telemetry.
3. Delegate focused investigation to the most relevant subagent.
4. Treat every remediation as a proposal only. Never claim that an action ran.
5. Finish with: incident summary, evidence, probable root cause, remediation,
   verification checks, risks, and confidence.
""".strip()


def require_env(name: str) -> str:
    """Read a required environment variable or raise a helpful error."""

    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing {name}. Copy .env.example to .env and add your Azure value."
        )
    return value


def build_model() -> AzureChatOpenAI:
    """Create the chat model from the standard Azure environment variables."""

    return AzureChatOpenAI(
        azure_deployment=require_env("AZURE_OPENAI_DEPLOYMENT_NAME"),
        azure_endpoint=require_env("AZURE_OPENAI_ENDPOINT"),
        api_key=require_env("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION", "2024-10-21"),
        temperature=0,
    )


def build_agent():
    """Compile the lead Deep Agent and its specialist subagents."""

    model = build_model()
    subagents: list[SubAgent] = [
        {
            "name": "application-investigator",
            "description": (
                "Investigates application errors, latency, logs, and dependencies."
            ),
            "system_prompt": (
                "You are an application reliability specialist. Use the available "
                "diagnostic evidence, distinguish facts from hypotheses, and return "
                "a concise root-cause assessment with confidence."
            ),
            "tools": [run_diagnostics, search_runbook],
            "model": model,
        },
        {
            "name": "risk-reviewer",
            "description": (
                "Reviews remediation plans for operational risk and safe verification."
            ),
            "system_prompt": (
                "You are a cautious SRE risk reviewer. Do not execute changes. Identify "
                "blast radius, rollback needs, approval requirements, and measurable "
                "post-change verification checks."
            ),
            "tools": [search_runbook],
            "model": model,
        },
    ]

    return create_deep_agent(
        model=model,
        tools=[get_incident, run_diagnostics, search_runbook],
        subagents=subagents,
        system_prompt=SYSTEM_PROMPT,
        name="incident-response-deep-agent",
    )


def final_text(messages: Sequence[BaseMessage]) -> str:
    """Extract a printable final answer from a Deep Agent result."""

    if not messages:
        return "The agent returned no messages."
    content = messages[-1].content
    return content if isinstance(content, str) else str(content)


def main() -> None:
    """Run the Deep Agent from the command line."""

    load_dotenv()
    parser = argparse.ArgumentParser(description="Run the Day 24 Deep Agent")
    parser.add_argument(
        "question",
        nargs="?",
        default=(
            "Investigate INC-2026-024 and produce a safe incident-response report."
        ),
    )
    args = parser.parse_args()

    agent = build_agent()
    result = agent.invoke(
        {"messages": [{"role": "user", "content": args.question}]},
        config={"recursion_limit": 50},
    )
    print(final_text(result["messages"]))


if __name__ == "__main__":
    main()
