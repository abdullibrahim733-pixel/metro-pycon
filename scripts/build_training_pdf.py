"""Generate the updated v2 PyCon Tanzania training guide as a PDF.

Run from the project folder:
    .venv/bin/python scripts/build_training_pdf.py

Requires reportlab (workshop documentation tool only, not a runtime dependency).
"""
from __future__ import annotations

from pathlib import Path
from textwrap import wrap
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    XPreformatted,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "METRO_PyCon_Tanzania_Training_Guide_v2.pdf"
NAVY = colors.HexColor("#0B3D5C")
GREY = colors.HexColor("#666666")
LIGHT = colors.HexColor("#F2F6F9")

base = getSampleStyleSheet()
S = {
    "eyebrow": ParagraphStyle(
        "eyebrow", parent=base["Normal"], fontSize=9, leading=12,
        textColor=GREY, alignment=TA_CENTER, spaceAfter=10,
    ),
    "title": ParagraphStyle(
        "title", parent=base["Title"], fontSize=30, leading=34,
        textColor=NAVY, alignment=TA_CENTER,
    ),
    "subtitle": ParagraphStyle(
        "subtitle", parent=base["Normal"], fontSize=16, leading=20,
        textColor=NAVY, alignment=TA_CENTER, spaceBefore=6,
    ),
    "h1": ParagraphStyle(
        "h1", parent=base["Heading1"], fontSize=15, leading=18,
        textColor=NAVY, spaceBefore=16, spaceAfter=7,
    ),
    "h2": ParagraphStyle(
        "h2", parent=base["Heading2"], fontSize=11, leading=14,
        textColor=NAVY, spaceBefore=10, spaceAfter=4,
    ),
    "body": ParagraphStyle(
        "body", parent=base["BodyText"], fontSize=9.3, leading=12.8, spaceAfter=5,
    ),
    "bullet": ParagraphStyle(
        "bullet", parent=base["BodyText"], fontSize=9.3, leading=12.8,
        leftIndent=12, firstLineIndent=-10, spaceAfter=3,
    ),
    "code": ParagraphStyle(
        "code", fontName="Courier", fontSize=7, leading=8.6,
        backColor=colors.HexColor("#F4F6F8"), borderPadding=5,
        leftIndent=3, spaceAfter=7,
    ),
    "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=7.8, leading=9.6),
    "cellhead": ParagraphStyle(
        "cellhead", fontName="Helvetica-Bold", fontSize=7.8, leading=9.6,
        textColor=colors.white,
    ),
}


def p(text: str) -> Paragraph:
    return Paragraph(text, S["body"])


def bullets(items: list[str]) -> list[Paragraph]:
    return [Paragraph("&bull; " + item, S["bullet"]) for item in items]


def code(text: str, width: int = 96) -> XPreformatted:
    clean = text.strip().replace("\t", "    ")
    lines: list[str] = []
    for raw in clean.splitlines():
        lines.extend(wrap(escape(raw), width=width, subsequent_indent="    ") or [""])
    return XPreformatted("\n".join(lines), S["code"])


def table(rows: list[list[str]], widths: list[float]) -> Table:
    data = []
    for index, row in enumerate(rows):
        style = S["cellhead"] if index == 0 else S["cell"]
        data.append([Paragraph(escape(str(cell)), style) for cell in row])
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C9D3DA")),
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return t


def page_decor(canvas, doc, cover: bool = False) -> None:
    canvas.saveState()
    width, height = A4
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GREY)
    if not cover:
        canvas.drawString(50, height - 28, "METRO  /  AI Agents in Fintech  /  v2")
        canvas.drawRightString(width - 50, height - 28, "PyCon Tanzania")
        canvas.setStrokeColor(colors.HexColor("#DDDDDD"))
        canvas.line(50, height - 33, width - 50, height - 33)
    canvas.line(50, 36, width - 50, 36)
    canvas.drawString(50, 24, "Synthetic data only  ·  flags are for human review")
    canvas.drawRightString(width - 50, 24, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()


def build() -> None:
    story: list = []

    # Cover -----------------------------------------------------------------
    story += [
        Spacer(1, 62 * 2.83465),
        Paragraph("PYCON TANZANIA / HANDS-ON PRACTICE SESSION", S["eyebrow"]),
        Paragraph("METRO", S["title"]),
        Paragraph("AI Agents in Fintech", S["subtitle"]),
        Spacer(1, 8),
        Paragraph(
            "Mobile-money Evaluation &amp; Transaction Review Operator",
            S["eyebrow"],
        ),
        Spacer(1, 30),
        Paragraph("v2 training guide &middot; updated November 2026", S["body"]),
        Paragraph(
            "Repository: github.com/abdullibrahim733-pixel/metro-pycon", S["body"]
        ),
        Spacer(1, 20),
        Paragraph(
            "This edition covers the lightweight chat path and the token-budget fix "
            "for free reasoning models. See Appendix A for the full changelog.",
            S["body"],
        ),
        PageBreak(),
    ]

    # 01 --------------------------------------------------------------------
    story += [
        Paragraph("01 / The mission", S["h1"]),
        p(
            "Build a small fintech operations agent that reads synthetic mobile-money "
            "transactions, chooses the right analysis path, runs dependable Python checks "
            "and explains the result. The goal is to understand the system, not to build a bank."
        ),
        p(
            "<b>An agent decides what step is needed, uses a tool, inspects the result and "
            "continues.</b> In METRO the model interprets the question, Python calculates the "
            "numbers, and LangGraph controls the sequence."
        ),
        table(
            [
                ["Step", "What happens"],
                ["1 ASK", "User asks a question, or just says hello."],
                ["2 ROUTE", "LangGraph selects report, chat, or one of five analysis paths."],
                ["3 ANALYSE", "Python reads the CSV and computes (skipped for chat)."],
                ["4 EXPLAIN", "Model or local fallback explains computed facts; chat replies in one line."],
            ],
            [80, 410],
        ),
        Spacer(1, 6),
        Paragraph("Why split the work this way?", S["h2"]),
        p(
            "Money totals, duplicate IDs and thresholds must be calculated by ordinary code, "
            "never guessed by a language model. The model adds language understanding; "
            "Python remains the source of numerical truth."
        ),
        Paragraph("Recommended workstation", S["h2"]),
        table(
            [
                ["Item", "Recommendation", "Why"],
                ["Memory", "4 GB RAM+", "The model runs in the cloud; the laptop runs Python."],
                ["CPU / disk", "2-core CPU, ~1 GB free", "No local model or large dataset."],
                ["OS", "Windows 10/11, Ubuntu, macOS", "Python 3.10+; 3.11/3.12 preferred."],
                ["Internet", "Short connection", "Package install and API calls only."],
                ["Editor", "IDLE, Thonny, VS Code", "Any working text editor."],
            ],
            [70, 150, 270],
        ),
        Spacer(1, 6),
        Paragraph("Do NOT install for this workshop", S["h2"]),
        *bullets(
            [
                "Docker, Kubernetes, Ollama or a local language model.",
                "GPU drivers, Pandas, Jupyter or a database server.",
                "CrewAI for participants — it is an optional facilitator demo only.",
            ]
        ),
        PageBreak(),
    ]

    # 02 --------------------------------------------------------------------
    story += [
        Paragraph("02 / Prepare the machine", S["h1"]),
        p("Do this before participants arrive. A 30-minute session is too short for downloads on every laptop."),
        Paragraph("Step A — check Python", S["h2"]),
        code(
            "# Windows PowerShell\npy --version\n\n# Linux / macOS\npython3 --version"
        ),
        p("Use Python 3.11 or 3.12 where possible. LangGraph supports 3.10+."),
        Paragraph("Step B — get the project and create a virtual environment", S["h2"]),
        code(
            "git clone https://github.com/abdullibrahim733-pixel/metro-pycon.git\n"
            "cd metro-pycon\n\n"
            "# Linux / macOS\npython3 -m venv .venv\nsource .venv/bin/activate\n\n"
            "# Windows PowerShell\npy -3.11 -m venv .venv\n.venv\\Scripts\\Activate.ps1"
        ),
        p("The setup scripts do all of this for you: <b>bash setup.sh</b> or <b>setup.ps1</b>."),
        Paragraph("Step C — install only the core packages", S["h2"]),
        code("python -m pip install -r requirements.txt"),
        p("requirements.txt contains only langgraph, openai and python-dotenv. CSV reading uses Python itself."),
        Paragraph("Step D — copy the starter environment", S["h2"]),
        code(
            "cp .env.example .env        # Windows: Copy-Item .env.example .env\n"
            "# then add your own private OpenRouter key to .env"
        ),
        Paragraph("Low-bandwidth preparation", S["h2"]),
        p(
            "On one connected machine: <b>python -m pip download -r requirements.txt -d wheelhouse</b>. "
            "Copy the folder and wheelhouse, then install offline with "
            "<b>python -m pip install --no-index --find-links=wheelhouse -r requirements.txt</b>. "
            "Match OS, Python version and CPU architecture."
        ),
        p(
            "<b>No API key?</b> METRO still runs the deterministic local report and the chat path. "
            "Only the model routing and explanation need internet."
        ),
        PageBreak(),
    ]

    # 03 --------------------------------------------------------------------
    story += [
        Paragraph("03 / OpenRouter and reasoning models", S["h1"]),
        p(
            "OpenRouter offers one OpenAI-compatible endpoint for many providers, so no laptop "
            "needs to download a model. Create a key at openrouter.ai → Settings → API Keys and keep it private."
        ),
        code(
            "OPENROUTER_API_KEY=sk-or-v1-PASTE-YOUR-PRIVATE-KEY\n"
            "OPENROUTER_MODEL=openrouter/free\n"
            "METRO_HIGH_VALUE_TZS=250000"
        ),
        Paragraph("Test the model connection", S["h2"]),
        code((ROOT / "warmups" / "openrouter_smoke_test.py").read_text(encoding="utf-8")),
        p(
            "Free variants can be rate-limited (published limits: 20 requests/minute, "
            "50 requests/day) and availability changes. Check the live free-model page. "
            "Not for production workloads."
        ),
        Paragraph("Why v1 sometimes returned a blunt report", S["h2"]),
        p(
            "The <b>openrouter/free</b> alias can route to a reasoning model. The original lab used "
            "<b>max_tokens=20</b> for classification and <b>220</b> for explanation. A reasoning model "
            "can spend all of those tokens thinking and emit no visible text, so METRO silently used "
            "its offline explanation — the blunt report you saw."
        ),
        table(
            [
                ["Fix in v2", "Effect"],
                ["Routing budget 20 → 400", "Model has room to think and still output a label."],
                ["Explanation budget 220 → 900", "Model can finish reasoning and write the report."],
                ["One retry at double budget", "Covers short reasoning traces that still end empty."],
                ["Strip hidden reasoning blocks", "Thinking text never appears in answers."],
                ["Explicit empty-answer note", "Fallback is visible instead of silent."],
            ],
            [200, 290],
        ),
        PageBreak(),
    ]

    # 04 --------------------------------------------------------------------
    story += [
        Paragraph("04 / Warm up with LangGraph", S["h1"]),
        p(
            "LangGraph is a flowchart that runs Python functions. State is the shared notebook, "
            "a node is one worker, an edge is the next step, and a conditional edge chooses a path."
        ),
        code((ROOT / "warmups" / "langgraph_warmup.py").read_text(encoding="utf-8")),
        p(
            "The 12-line warm-up needs no API key: state held the request, inspect was the node, "
            "and START → inspect → END was the path. METRO adds an interpretation node and a "
            "conditional edge before analysis."
        ),
        Paragraph("05 / Warm up with CrewAI (optional)", S["h1"]),
        p(
            "CrewAI organises role-based agents: an analyst prepares facts, a reviewer checks them. "
            "Install <b>python -m pip install \"crewai[openai]\"</b> on the facilitator machine only."
        ),
        code((ROOT / "warmups" / "crewai_warmup.py").read_text(encoding="utf-8")),
        p(
            "Use LangGraph for the final build: the workflow stays explicit and the dependency set "
            "stays small. CrewAI is a comparison, not a prerequisite."
        ),
        PageBreak(),
    ]

    # 06 --------------------------------------------------------------------
    story += [
        Paragraph("06 / Final project: METRO", S["h1"]),
        p(
            "METRO reads a small CSV of synthetic transactions, understands a plain-language "
            "request, chooses a safe path, calculates totals and flags with Python, and explains "
            "the result — or answers a greeting in one short line."
        ),
        table(
            [
                ["Question type", "LangGraph path", "Result"],
                ["“Show failed payments”", "failed", "Filtered IDs and amounts"],
                ["“Find repeated IDs”", "duplicates", "Repeated transaction IDs"],
                ["“Which amounts to review?”", "large", "Amounts above threshold"],
                ["“Give me a summary”", "summary", "Computed overview"],
                ["“Give me the full review”", "all", "All computed sections"],
                ["“hi” / “hellow”", "chat", "One short line, no CSV work"],
            ],
            [150, 80, 260],
        ),
        Paragraph("Dataset supplied with the starter kit", S["h2"]),
        table(
            [
                ["Column", "Meaning", "Example"],
                ["transaction_id", "Reference used to spot repeats", "TX003"],
                ["sender / receiver", "Synthetic parties", "Customer-C / Shop-03"],
                ["amount_tzs", "Amount in Tanzanian shillings", "50000"],
                ["channel", "Payment channel", "Mobile Money"],
                ["status", "SUCCESS or FAILED", "SUCCESS"],
                ["timestamp", "Sample timestamp", "2026-11-25 09:18"],
            ],
            [130, 220, 140],
        ),
        code((ROOT / "transactions.csv").read_text(encoding="utf-8")),
        Paragraph("Expected teaching result", S["h2"]),
        table(
            [
                ["Check", "Expected"],
                ["Raw rows / unique IDs", "7 rows / 6 unique IDs"],
                ["Successful / failed", "4 / 2"],
                ["Successful total", "TZS 580,000 (unique IDs only)"],
                ["Repeated ID", "TX003 appears twice"],
                ["Large amount", "Threshold TZS 250,000; TX005 at TZS 500,000"],
            ],
            [180, 310],
        ),
        p(
            "<b>Design decision:</b> METRO counts only the first row per transaction ID in its "
            "teaching total while still reporting the repeat. Real payment systems need stronger "
            "idempotency, reconciliation and audit trails."
        ),
        PageBreak(),
    ]

    # 07 --------------------------------------------------------------------
    story += [
        Paragraph("07 / Updated source code (metro.py)", S["h1"]),
        p(
            "This is the exact file in the repository. The v2 additions are the small-talk detector, "
            "the chat node, the model-text helper with retry, and the larger token budgets."
        ),
        code((ROOT / "metro.py").read_text(encoding="utf-8"), width=94),
        PageBreak(),
    ]

    # 08 --------------------------------------------------------------------
    story += [
        Paragraph("08 / Run METRO and lead the 30-minute lab", S["h1"]),
        code(
            "python metro.py                                  # interactive\n"
            "python metro.py \"Show the failed payments\"       # one question\n"
            "python metro.py --offline \"Give me a summary\"    # local report\n"
            "python metro.py \"hi\"                             # chat mode\n"
            "# type quit or exit to leave the interactive prompt"
        ),
        table(
            [
                ["Ask METRO", "Expected route"],
                ["Give me a summary of this sample.", "summary"],
                ["Show the failed payments.", "failed"],
                ["Find repeated transaction IDs.", "duplicates"],
                ["Which amounts should be reviewed?", "large"],
                ["Give me the full transaction review.", "all"],
                ["hi / hellow / how are you / thanks / bye", "chat (one-line reply)"],
            ],
            [300, 190],
        ),
        Paragraph("30-minute run of show", S["h2"]),
        table(
            [
                ["Time", "Facilitator action", "Outcome"],
                ["00–03", "Explain use case and four-part loop.", "Why an agent + tools."],
                ["03–06", "Run the OpenRouter smoke test.", "Model connection confirmed."],
                ["06–10", "Run the LangGraph warm-up.", "State, nodes, edges seen."],
                ["10–13", "Explain CrewAI roles/tasks.", "Graph vs crew compared."],
                ["13–24", "Run METRO; ask 2–3 report questions.", "Routing and Python checks observed."],
                ["24–28", "Set threshold to 100000 in .env; rerun.", "Config effect seen."],
                ["28–30", "Try hi / hellow, then discuss limits.", "Chat path and human review understood."],
            ],
            [55, 255, 180],
        ),
        PageBreak(),
    ]

    # 09 --------------------------------------------------------------------
    story += [
        Paragraph("09 / Verify and troubleshoot", S["h1"]),
        code(
            "python scripts/preflight.py                 # 20 offline checks\n"
            "python -m unittest discover -s tests -v     # 16 deterministic tests"
        ),
        p(
            "Pre-flight verifies dependencies, dataset expectations, graph compilation, all five "
            "report routes and both greeting routes — without an API key."
        ),
        table(
            [
                ["Problem", "Try this"],
                ["python / py not found", "Install Python 3.11/3.12, enable PATH, reopen terminal."],
                ["Cannot activate venv", "Use PowerShell; or call .venv\\Scripts\\python.exe directly."],
                ["ModuleNotFoundError", "Activate venv and install -r requirements.txt."],
                ["OpenRouter 401 / 403", "Check key and model access. Never print the key."],
                ["Free model limited", "Choose another :free model or use the local fallback."],
                ["Blunt report despite a key", "Reasoning model used its tokens. v2 budgets/retry handle it; switch model if needed."],
                ["Greeting gives a report", "Restart the app after updating; v2 routes greetings to chat."],
                ["No CSV file", "Keep transactions.csv beside metro.py."],
            ],
            [150, 340],
        ),
        PageBreak(),
    ]

    # 10 --------------------------------------------------------------------
    story += [
        Paragraph("10 / Facilitator pre-flight and safety", S["h1"]),
        Paragraph("Day-before checklist", S["h2"]),
        *bullets(
            [
                "Test on one Windows and one Linux laptop with Python 3.11/3.12.",
                "Run setup, then scripts/preflight.py and the unit tests.",
                "Test one small chat completion with a free OpenRouter model.",
                "Prepare participant folders; never distribute a real API key.",
                "Pre-download wheels for weak internet; install CrewAI only for the facilitator.",
                "Rehearse the no-key path: local report plus one-line chat replies.",
            ]
        ),
        Paragraph("What participants should leave with", S["h2"]),
        table(
            [
                ["Deliverable", "Evidence"],
                ["Python workstation", "Venv active and core packages installed."],
                ["OpenRouter connection", "One API reply, or awareness of the fallback."],
                ["Framework warm-ups", "Tiny LangGraph graph run; CrewAI roles understood."],
                ["METRO project", "A question answered from CSV; a greeting answered in chat."],
                ["Safety understanding", "Flags are not fraud findings; people approve actions."],
            ],
            [170, 320],
        ),
        Paragraph("Safety boundary", S["h2"]),
        p(
            "Synthetic records only. METRO does not connect to a mobile-money provider, move money, "
            "approve or reverse payments, or make a fraud determination. Large values and repeated "
            "IDs are review signals only. A human must verify any real-world issue."
        ),
        Paragraph("Official references", S["h2"]),
        *bullets(
            [
                "LangGraph quickstart — langchain-ai.github.io/langgraph/quickstart/",
                "CrewAI installation — docs.crewai.com/installation",
                "OpenRouter quickstart — openrouter.ai/docs/quickstart",
                "OpenRouter free models and limits — openrouter.ai/models?max_price=0",
                "OpenRouter API keys — openrouter.ai/settings/keys",
            ]
        ),
        PageBreak(),
    ]

    # Appendix ---------------------------------------------------------------
    story += [
        Paragraph("Appendix A / Changelog v1 → v2", S["h1"]),
        table(
            [
                ["Area", "v1", "v2"],
                ["Routing tokens", "20", "400, with double-budget retry"],
                ["Explanation tokens", "220", "900, with double-budget retry"],
                ["Reasoning tags", "Shown if present", "Removed before display"],
                ["Empty answers", "Silent local report", "Visible note + retry"],
                ["Greetings", "Full report via 'all'", "Dedicated chat node, one line"],
                ["Greeting detection", "None", "Word-boundary local match (incl. 'hellow')"],
                ["Verification", "No tests", "16 unit tests + 20 pre-flight checks"],
                ["Repository", "Not published", "github.com/abdullibrahim733-pixel/metro-pycon"],
            ],
            [110, 150, 230],
        ),
        Spacer(1, 10),
        p(
            "To regenerate this guide after changing the code: "
            "<b>.venv/bin/python scripts/build_training_pdf.py</b>. "
            "The generator is included in the repository so the documentation stays in sync."
        ),
        p(
            "Documentation updated 26 November 2026. Model availability, free-tier limits and "
            "package versions change — check the live official pages before the event."
        ),
    ]

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=50,
        rightMargin=50,
        topMargin=48,
        bottomMargin=45,
        title="METRO - AI Agents in Fintech - v2 Training Guide",
        author="PyCon Tanzania practice session",
    )
    doc.build(
        story,
        onFirstPage=lambda canvas, document: page_decor(canvas, document, cover=True),
        onLaterPages=page_decor,
    )
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
