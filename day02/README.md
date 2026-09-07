# Day 2 — Azure OpenAI with LangChain

This project demonstrates how to:

- manage dependencies with `uv`;
- load local configuration with `python-dotenv`;
- validate required environment variables;
- connect to Azure OpenAI through LangChain;
- invoke a chat model from a packaged Python application.

## Setup

```powershell
Copy-Item .env.example .env
uv sync
uv run day02
```

Replace the placeholder values in `.env` with credentials provided through an approved secure channel.

Never commit or share the `.env` file.