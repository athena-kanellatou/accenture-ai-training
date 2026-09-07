# Day 1 — Python Project Setup

This project demonstrates:

- Python packaging with a `src` layout
- Dependency management with `uv`
- Local configuration with `python-dotenv`
- Environment-aware logging configuration
- Virtual environment detection

## Setup

```powershell
Copy-Item .env.example .env
uv sync
uv run day01
uv run day01-env