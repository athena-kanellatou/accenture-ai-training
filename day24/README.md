# Day 24 — Deep Agents with Azure OpenAI

Το project δείχνει πώς χτίζουμε έναν **Deep Agent** για διερεύνηση IT
incidents. Σε αντίθεση με ένα απλό LLM call, ο agent μπορεί να σχεδιάζει την
εργασία, να χρησιμοποιεί tools και να αναθέτει εξειδικευμένα tasks σε
subagents με ξεχωριστό context.

## Τι περιλαμβάνει

- Lead incident-response Deep Agent
- `application-investigator` subagent για logs, metrics και dependencies
- `risk-reviewer` subagent για risk, rollback και verification
- Τρία custom tools με deterministic mock enterprise data
- Azure OpenAI configuration μέσω environment variables
- Offline unit tests χωρίς API calls

## Δομή

```text
day24/
├── src/day24/
│   ├── agent.py       # model, subagents και execution
│   ├── data.py        # mock incidents, telemetry και runbooks
│   └── tools.py       # custom LangChain tools
├── tests/
│   └── test_tools.py
├── .env.example
└── pyproject.toml
```

## Εγκατάσταση

```powershell
cd day24
uv sync
Copy-Item .env.example .env
```

Συμπλήρωσε στο `.env` τα πραγματικά Azure credentials. Μην κάνεις commit το
`.env`.

## Εκτέλεση

Με το έτοιμο demo incident:

```powershell
uv run day24
```

Με δικό σου request:

```powershell
uv run day24 "Investigate INC-2026-024 and explain the safest remediation."
```

## Tests

```powershell
uv run pytest -q
```

## Πώς λειτουργεί

1. Ο lead agent δημιουργεί πλάνο.
2. Καλεί το `get_incident` για τα βασικά στοιχεία.
3. Χρησιμοποιεί τον application investigator για evidence-based diagnosis.
4. Αναθέτει το remediation review στον risk reviewer.
5. Συνθέτει τελικό report χωρίς να ισχυρίζεται ότι εκτέλεσε πραγματικές αλλαγές.

Τα built-in Deep Agents εργαλεία προσθέτουν planning, filesystem/context
management και το `task` tool που επιτρέπει την ανάθεση εργασίας στους
subagents.
