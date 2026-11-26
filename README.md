# METRO — AI Agents in Fintech

**M**obile-money **E**valuation & **T**ransaction **R**eview **O**perator.

A 30-minute, beginner-friendly build lab from PyCon Tanzania. METRO reads a small CSV of
synthetic mobile-money transactions, uses a hosted model to choose an analysis path, lets
ordinary Python calculate the numbers, and explains the result in plain language.

> Learning demo only. No payments are sent, changed, approved, or reversed. Repeated IDs and
> large amounts are **review signals, not fraud findings**. A human stays in control.

## Project structure

```
METRO/
├── metro.py                  # final LangGraph application
├── transactions.csv          # 7 synthetic rows (6 unique IDs)
├── requirements.txt          # langgraph, openai, python-dotenv
├── .env.example              # template for your private OpenRouter key
├── .env                      # local config (gitignored)
├── README.md                 # this guide
├── scripts/
│   └── preflight.py          # checks that the whole demo works offline
├── tests/
│   └── test_metro.py         # deterministic unit tests (no API key needed)
├── warmups/
│   ├── langgraph_warmup.py   # tiny state/node/edge demo
│   ├── openrouter_smoke_test.py
│   └── crewai_warmup.py      # optional role-based comparison
├── setup.sh                  # Linux/macOS setup
├── setup.ps1                 # Windows setup
└── docs/
    └── FACILITATOR.md        # day-before checklist and 30-minute run of show
```

## Quick start

### Linux / macOS

```bash
cd METRO
bash setup.sh
source .venv/bin/activate
python scripts/preflight.py
python metro.py
```

### Windows PowerShell

```powershell
cd METRO
powershell -ExecutionPolicy ByPass -File .\setup.ps1
.\.venv\Scripts\Activate.ps1
python scripts\preflight.py
python metro.py
```

If PowerShell blocks activation, use `.\.venv\Scripts\python.exe` in place of `python` in the
commands above.

### Manual setup

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
cp .env.example .env               # Windows: Copy-Item .env.example .env
```

Python 3.10+ is required; 3.11 or 3.12 is recommended. No Docker, GPU, local model, Jupyter,
Pandas, or database is needed.

## Configure the model (optional)

The demo runs fully offline without a key. To enable model routing and explanations:

1. Sign in at [openrouter.ai](https://openrouter.ai), open **Settings → API Keys**, and create
   a key.
2. Put the key in `.env` as `OPENROUTER_API_KEY=sk-or-v1-...`.
3. Check the current free-model page. The default `OPENROUTER_MODEL=openrouter/free` is a router
   alias; a current variant ending in `:free` also works.
4. Test with `python warmups/openrouter_smoke_test.py`.

Never commit, share, or paste your key. `.env` is listed in `.gitignore`.

Configuration in `.env`:

| Variable | Meaning | Default |
| --- | --- | --- |
| `OPENROUTER_API_KEY` | Private OpenRouter key; unset = local fallback | none |
| `OPENROUTER_MODEL` | Model alias or free variant | `openrouter/free` |
| `METRO_HIGH_VALUE_TZS` | Amounts at/above this are flagged for review | `250000` |

## Run METRO

```bash
python metro.py                                  # interactive prompt
python metro.py "Show the failed payments"       # one question, then exit
python metro.py --offline "Give me a summary"    # force local deterministic report
```

Type `quit` or `exit` to leave the interactive prompt. If an API call fails, METRO falls back to
the local report automatically.

| Ask METRO | Route |
| --- | --- |
| Give me a summary of this sample. | `summary` |
| Show the failed payments. | `failed` |
| Find repeated transaction IDs. | `duplicates` |
| Which amounts should be reviewed? | `large` |
| Give me the full transaction review. | `all` |

Expected teaching results from `transactions.csv`:

| Check | Expected |
| --- | --- |
| Raw rows / unique IDs | 7 / 6 |
| Successful / failed | 4 / 2 |
| Successful total (unique IDs only) | TZS 580,000 |
| Repeated ID | TX003 appears twice |
| Large amount (threshold 250,000) | TX005 at TZS 500,000 |

METRO counts only the **first** row for each transaction ID in its teaching total, while still
reporting the repeated ID. Real payment systems need proper idempotency, reconciliation and audit
trails.

## How it works

1. **Ask** — the user asks a plain-language question.
2. **Route** — LangGraph's `understand` node picks one of five safe labels. A conditional edge
   sends the state to the matching analysis node.
3. **Analyse** — ordinary Python reads the CSV and computes totals, failures, repeats and large
   amounts. The model never calculates money.
4. **Explain** — the model (or the offline fallback) turns the computed facts into a short report.

State passed between nodes: `question → intent → findings → answer`.

## Verify the project

```bash
python scripts/preflight.py                 # all checks should pass offline
python -m unittest discover -s tests -v     # 10 deterministic tests
```

Pre-flight verifies dependencies, the dataset expectations, graph compilation and all five routes
without using an API key.

## Warm-ups

```bash
python warmups/langgraph_warmup.py           # no API key required
python warmups/openrouter_smoke_test.py     # needs OPENROUTER_API_KEY
python -m pip install "crewai[openai]"       # optional, larger install
python warmups/crewai_warmup.py              # role-based comparison
```

LangGraph is used for the final build because the workflow stays explicit and the dependency set
stays small. CrewAI is a brief comparison of role-based collaboration, not a prerequisite.

## Troubleshooting

| Problem | Try this |
| --- | --- |
| `python` / `py` not found | Install Python 3.11/3.12, enable PATH, reopen the terminal. |
| Cannot activate venv on Windows | Use PowerShell; or call `.venv\Scripts\python.exe` directly. |
| `ModuleNotFoundError` | Activate the venv and rerun `python -m pip install -r requirements.txt`. |
| OpenRouter 401 / 403 | Check the key, remove extra spaces, verify model access. Never print the key. |
| Free model unavailable / rate limited | Pick a current `:free` model, retry sparingly, or use the local fallback. |
| Report looks offline even with a key | A free reasoning model may use its whole token budget before answering. METRO now allows larger budgets and retries once; if it persists, set a different `:free` model in `.env`. |
| No CSV file | Keep `transactions.csv` beside `metro.py`. |

See [`docs/FACILITATOR.md`](docs/FACILITATOR.md) for the day-before checklist, low-bandwidth
preparation and the 30-minute run of show.

## Safety boundary

Synthetic records only. METRO does not connect to a mobile-money provider, move money, approve or
reverse payments, or make a fraud determination. Flags are items for human review.

## References

- [LangGraph quickstart](https://langchain-ai.github.io/langgraph/quickstart/)
- [CrewAI installation](https://docs.crewai.com/installation)
- [OpenRouter quickstart](https://openrouter.ai/docs/quickstart)
- [OpenRouter free models](https://openrouter.ai/models?max_price=0)
- [OpenRouter API keys](https://openrouter.ai/settings/keys)
