# Facilitator guide

Goal: protect the 30-minute session from downloads, missing keys and avoidable setup failures.

## Day-before checklist

- [ ] Test the complete project on one Windows laptop and one Linux laptop with Python 3.11/3.12.
- [ ] Run `bash setup.sh` (Linux) or `setup.ps1` (Windows), then `python scripts/preflight.py`.
- [ ] Install core packages and test one small chat completion with a free OpenRouter model.
- [ ] Prepare participant folders with `metro.py`, `transactions.csv`, `requirements.txt` and
      `.env.example`. **Do not distribute a real API key.**
- [ ] For weak internet, pre-download wheels (see below) and copy them to a USB drive or share.
- [ ] Install CrewAI only on the facilitator machine; it is an optional demonstration.
- [ ] Rehearse the no-internet path: unset the key and show the deterministic local report.

## Low-bandwidth preparation

On one internet-connected machine with the same OS, Python version and CPU architecture:

```bash
python -m pip download -r requirements.txt -d wheelhouse
```

Copy the project folder and `wheelhouse/` to participant machines, then install offline:

```bash
python -m pip install --no-index --find-links=wheelhouse -r requirements.txt
```

## 30-minute run of show

| Time | Facilitator action | Participant outcome |
| --- | --- | --- |
| 00–03 | Explain the use case and four-part loop: ask → route → analyse → explain. | Understand why the task needs an agent + tools. |
| 03–06 | Run `python warmups/openrouter_smoke_test.py` with keys prepared beforehand. | Confirm the model connection. |
| 06–10 | Run `python warmups/langgraph_warmup.py`. | See state, node and edges. |
| 10–13 | Explain CrewAI roles/tasks; run the prepared optional demo. | Compare graph workflow vs agent crew. |
| 13–24 | Run `python metro.py` and ask 2–3 questions from the table below. | Observe routing, Python checks and explanation. |
| 24–28 | Change `METRO_HIGH_VALUE_TZS=100000` in `.env` and rerun the `large` question. | See a configuration change affect flagged rows. |
| 28–30 | Discuss limits and human review. | Know what not to automate. |

Demo questions:

```text
Give me a summary of this sample.          → summary
Show the failed payments.                  → failed
Find repeated transaction IDs.             → duplicates
Which amounts should be reviewed?          → large
Give me the full transaction review.       → all
```

Useful one-shot commands during the session:

```bash
python metro.py "Show the failed payments"
python metro.py --offline "Give me the full transaction review"
python scripts/preflight.py
```

## Expected numbers to write on the board

| Check | Expected |
| --- | --- |
| Raw rows / unique IDs | 7 / 6 |
| Successful / failed | 4 / 2 |
| Successful total (unique IDs only) | TZS 580,000 |
| Repeated ID | TX003 |
| Large-amount flag (threshold 250,000) | TX005 at TZS 500,000 |

## Troubleshooting

| Problem | Try this |
| --- | --- |
| `python` / `py` not found | Install Python 3.11/3.12, enable PATH, reopen the terminal. |
| Cannot activate venv on Windows | Use PowerShell; if policy blocks it, call `.venv\Scripts\python.exe` directly. |
| `ModuleNotFoundError` | Activate the environment and `python -m pip install -r requirements.txt`. |
| OpenRouter 401 / 403 | Check the key, remove extra spaces, verify account/model access. Never print the key. |
| Free model unavailable / rate limited | Choose another current `:free` model or use the local fallback. Retry sparingly. |
| Model gives empty answers | Free reasoning models can spend their token budget thinking. METRO now uses larger budgets and retries once; switch models in `.env` if needed. |
| No CSV file | Keep `transactions.csv` beside `metro.py`. |

## What participants should leave with

| Deliverable | Evidence |
| --- | --- |
| Python workstation | Virtual environment activated and core requirements installed |
| OpenRouter connection | One successful API response, or awareness of the local fallback |
| Framework warm-ups | Tiny LangGraph graph executed; CrewAI roles/tasks understood |
| METRO final project | A question answered from the CSV data |
| Safety understanding | Flags are not fraud findings; people approve financial actions |

## Safety boundary

Synthetic records only. METRO does not connect to a mobile-money provider, move money, approve or
reverse payments, or make a fraud determination. Large values and repeated IDs are review signals
only. A human must verify any real-world issue.

## References

- [LangGraph quickstart](https://langchain-ai.github.io/langgraph/quickstart/)
- [CrewAI installation](https://docs.crewai.com/installation)
- [OpenRouter quickstart](https://openrouter.ai/docs/quickstart)
- [OpenRouter free models and limits](https://openrouter.ai/models?max_price=0)
- [OpenRouter API keys](https://openrouter.ai/settings/keys)

Documentation checked 25 November 2026. Model availability, free-tier limits and package versions
change; check the live pages before the event.
