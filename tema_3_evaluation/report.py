import html as _html
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

METRIC_LABELS = {
    "relevance": "Answer Relevance",
    "bias": "Bias",
    "toxicity": "Toxicity",
    "correctness": "Correctness",
    "completeness": "Completeness",
}


def _score_color(score: float) -> str:
    if score >= 0.85:
        return "#22c55e"
    elif score >= 0.65:
        return "#f59e0b"
    return "#ef4444"


def _score_label(score: float) -> str:
    if score >= 0.85:
        return "Good"
    elif score >= 0.65:
        return "Acceptable"
    return "Poor"


def _metric_box_html(key: str, r: dict) -> str:
    score = r[f"{key}_score"]
    reason = r.get(f"{key}_reason") or ""
    color = _score_color(score)
    label = METRIC_LABELS.get(key, key)
    return f"""
        <div class="score-box" style="border-color:{color}">
            <div class="score-label">{label}</div>
            <div class="score-value" style="color:{color}">{score:.2f}</div>
            <div class="score-bar-bg">
                <div class="score-bar-fill" style="width:{score*100:.0f}%;background:{color}"></div>
            </div>
            <div class="score-tag" style="background:{color}">{_score_label(score)}</div>
            <p class="score-reason">{_html.escape(reason)}</p>
        </div>"""


def _card_html(i: int, r: dict) -> str:
    metric_boxes = "".join(_metric_box_html(key, r) for key in METRIC_LABELS)
    return f"""
    <div class="card">
        <div class="card-header">
            <span class="case-number">#{i}</span>
            <div>
                <p class="question">{_html.escape(r["input"])}</p>
                <p class="expected-label">Expected:</p>
                <p class="expected-text">{_html.escape(r["expected_output"])}</p>
            </div>
        </div>
        <div class="scores-row">
            {metric_boxes}
        </div>
        <div class="response-section">
            <div class="response-label">LLM Response</div>
            <div class="markdown-body" data-markdown="{_html.escape(r["response"])}"></div>
        </div>
    </div>"""


def save_report(results: list[dict], scores: dict[str, list[float]], threshold: float) -> Path:
    run_time = datetime.now().strftime("%d %B %Y, %H:%M:%S")
    cards = "".join(_card_html(i, r) for i, r in enumerate(results, 1))

    summary_boxes = ""
    for key, label in METRIC_LABELS.items():
        metric_scores = scores.get(key, [])
        if not metric_scores:
            continue
        pct = sum(s >= threshold for s in metric_scores) / len(metric_scores) * 100
        avg = sum(metric_scores) / len(metric_scores)
        color = _score_color(avg)
        summary_boxes += f"""
        <div class="summary-box">
            <div class="s-label">{label}</div>
            <div class="s-value" style="color:{color}">{pct:.0f}%</div>
            <div class="s-sub">avg: {avg:.2f} | pass ≥ {threshold}</div>
        </div>"""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Evaluation Report — Palo Alto Networks Assistant</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            padding: 2rem 1rem;
            min-height: 100vh;
        }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        .report-header {{ text-align: center; margin-bottom: 2.5rem; }}
        .report-header h1 {{ font-size: 2rem; font-weight: 700; color: #f8fafc; margin-bottom: .4rem; }}
        .report-header .subtitle {{ color: #94a3b8; font-size: .95rem; }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 1rem;
            margin-bottom: 2.5rem;
        }}
        .summary-box {{
            background: #1e293b;
            border-radius: 12px;
            padding: 1.2rem;
            text-align: center;
            border: 1px solid #334155;
        }}
        .summary-box .s-label {{ color: #94a3b8; font-size: .75rem; margin-bottom: .5rem; text-transform: uppercase; letter-spacing: .05em; }}
        .summary-box .s-value {{ font-size: 2rem; font-weight: 700; }}
        .summary-box .s-sub {{ color: #64748b; font-size: .75rem; margin-top: .3rem; }}
        .card {{
            background: #1e293b;
            border-radius: 14px;
            border: 1px solid #334155;
            margin-bottom: 1.5rem;
            overflow: hidden;
        }}
        .card-header {{
            padding: 1.25rem 1.5rem;
            border-bottom: 1px solid #334155;
            display: flex;
            gap: 1rem;
            align-items: flex-start;
        }}
        .case-number {{
            background: #f97316;
            color: #fff;
            font-weight: 700;
            font-size: .8rem;
            padding: .2rem .55rem;
            border-radius: 6px;
            white-space: nowrap;
            margin-top: 2px;
        }}
        .question {{ font-size: 1rem; color: #f1f5f9; line-height: 1.5; margin-bottom: .4rem; }}
        .expected-label {{ font-size: .72rem; color: #64748b; text-transform: uppercase; letter-spacing: .05em; margin-bottom: .2rem; }}
        .expected-text {{ font-size: .82rem; color: #64748b; line-height: 1.5; }}
        .scores-row {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 1px;
            background: #334155;
        }}
        .score-box {{
            background: #1e293b;
            padding: 1rem 1.25rem;
            border-top: 3px solid transparent;
        }}
        .score-label {{ font-size: .7rem; text-transform: uppercase; letter-spacing: .06em; color: #94a3b8; margin-bottom: .4rem; }}
        .score-value {{ font-size: 1.7rem; font-weight: 700; margin-bottom: .4rem; }}
        .score-bar-bg {{ background: #0f172a; border-radius: 4px; height: 5px; margin-bottom: .5rem; }}
        .score-bar-fill {{ height: 5px; border-radius: 4px; }}
        .score-tag {{
            display: inline-block;
            color: #fff;
            font-size: .68rem;
            font-weight: 600;
            padding: .12rem .45rem;
            border-radius: 20px;
            margin-bottom: .6rem;
            text-transform: uppercase;
            letter-spacing: .04em;
        }}
        .score-reason {{ font-size: .78rem; color: #94a3b8; line-height: 1.5; }}
        .response-section {{
            border-top: 1px solid #334155;
            padding: 1.25rem 1.5rem;
        }}
        .response-label {{
            font-size: .72rem;
            text-transform: uppercase;
            letter-spacing: .06em;
            color: #64748b;
            margin-bottom: .75rem;
        }}
        .markdown-body {{ font-size: .88rem; line-height: 1.7; color: #cbd5e1; }}
        .markdown-body h1,.markdown-body h2,.markdown-body h3 {{ color:#f1f5f9; margin: 1rem 0 .5rem; }}
        .markdown-body strong {{ color: #f8fafc; }}
        .markdown-body ul,.markdown-body ol {{ padding-left: 1.4rem; }}
        .markdown-body li {{ margin: .25rem 0; }}
        .markdown-body code {{ background: #0f172a; padding: .1rem .3rem; border-radius: 3px; font-size: .82rem; color: #f97316; }}
        .markdown-body pre {{ background: #0f172a; padding: 1rem; border-radius: 6px; overflow-x: auto; margin: .75rem 0; }}
        .footer {{ text-align: center; color: #334155; font-size: .8rem; margin-top: 3rem; }}
    </style>
</head>
<body>
<div class="container">
    <div class="report-header">
        <h1>🔥 Palo Alto Networks Assistant — Evaluation Report</h1>
        <p class="subtitle">Generated at {run_time} &nbsp;·&nbsp; {len(results)} test cases &nbsp;·&nbsp; Threshold: {threshold}</p>
    </div>
    <div class="summary">{summary_boxes}</div>
    {cards}
    <div class="footer">Palo Alto Networks RAG Assistant — LLM Evaluation</div>
</div>
<script>
    document.querySelectorAll(".markdown-body[data-markdown]").forEach(el => {{
        el.innerHTML = marked.parse(el.getAttribute("data-markdown"));
    }});
</script>
</body>
</html>"""

    output_file = OUTPUT_DIR / f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    output_file.write_text(html_content, encoding="utf-8")
    return output_file