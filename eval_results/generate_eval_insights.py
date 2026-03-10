#!/usr/bin/env python3
"""
Generate insights from TI-Validation eval execution result JSON files.

Reads an exported eval-results-*.json, and produces:
- Overall scores (per metric and summary)
- Summarized score justifications per metric (from qualitative reasoning)
- Strengths and weaknesses derived from scores and explanations
- Optional: LLM-generated narrative analysis (works even when datapoints are empty)

Usage:
  python scripts/generate_eval_insights.py path/to/eval-results-478-2026-03-02.json
  python scripts/generate_eval_insights.py path/to/results.json -o insights.md
  python scripts/generate_eval_insights.py path/to/results.json -o insights.md --llm

  # Compare multiple insight reports (same eval, different models):
  python scripts/generate_eval_insights.py compare file1.insights.md file2.insights.md -o dir/insights.comparison.md
  python scripts/generate_eval_insights.py compare file1.insights.md file2.insights.md -o dir/insights.comparison.md --llm
  python scripts/generate_eval_insights.py compare *.insights.md -o insights.comparison.md --llm-summaries   # LLM-generated summary per model (no parsing)

LLM analysis (--llm, --llm-summaries):
  Set OPENAI_API_KEY or ANTHROPIC_API_KEY in the environment. Use --provider to choose.
  --llm-summaries: ask the LLM to write a short summary per report for the comparison (avoids parsing section 5).
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def load_eval_results(path: Path) -> dict:
    """Load and return eval results JSON."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_explanation(explanation: str) -> tuple[int | None, str]:
    """
    Parse a turn-level explanation string.
    Returns (score, reasoning_text). Score may be None if not found.
    Legacy format: "SCORE: 5" and "REASONING: ...". If no REASONING: prefix, whole text is reasoning.
    """
    if not explanation or not isinstance(explanation, str):
        return None, ""
    score = None
    m = re.search(r"SCORE:\s*(\d+)(?:/\d+)?", explanation, re.IGNORECASE)
    if m:
        score = int(m.group(1))
    reasoning = ""
    m = re.search(r"REASONING:\s*(.+)", explanation, re.IGNORECASE | re.DOTALL)
    if m:
        reasoning = m.group(1).strip()
    elif explanation.strip():
        # No "REASONING:" prefix: treat whole explanation as reasoning (e.g. eval-results-488 format)
        reasoning = explanation.strip()
    return score, reasoning


def parse_explanation_sections(explanation: str) -> dict[str, str]:
    """
    Parse structured rubric/checklist sections from an explanation string.
    Sections are ALL_CAPS (with optional underscores) followed by colon and content
    until the next such header or end. Returns dict of section_name -> content (stripped).
    E.g. CONFIDENCE_INDICATORS, KNOWLEDGE_ASSESSMENT, CALIBRATION_ANALYSIS, JUSTIFICATION, etc.
    """
    if not explanation or not isinstance(explanation, str):
        return {}
    out: dict[str, str] = {}
    # Match section header: at line start, word in ALL_CAPS/numbers/underscores, then colon and newline.
    # Lookahead: next section (same pattern) or end of string, so content stops before next header.
    pattern = re.compile(
        r"^([A-Z][A-Z0-9_]+):\s*\n([\s\S]*?)(?=^[A-Z][A-Z0-9_]+:\s*\n|\Z)",
        re.MULTILINE,
    )
    for m in pattern.finditer(explanation):
        name, body = m.group(1).strip(), (m.group(2) or "").strip()
        if name.upper() == "SCORE":
            continue  # skip SCORE, we already parse it elsewhere
        if body:
            out[name] = body
    return out


def collect_metric_data(data: dict) -> dict:
    """
    From eval results, collect per-metric:
    - global stats (avg, min, max, percentage)
    - list of (datapoint_index, datapoint_id, score, reasoning) for each turn-level score
    """
    metrics = data.get("global_global_metrics") or {}
    datapoints = data.get("datapoints") or []
    by_metric: dict[str, dict] = {}

    for metric_name, global_stats in metrics.items():
        by_metric[metric_name] = {
            "global": dict(global_stats),
            "scores": [],
            "reasoning": [],
        }

    for dp in datapoints:
        idx = dp.get("datapoint_index", -1)
        dp_id = dp.get("datapoint_id", -1)
        for mr in dp.get("metric_results") or []:
            name = mr.get("metric_name")
            if name not in by_metric:
                continue
            agg_score = mr.get("score")
            for s in mr.get("scores") or []:
                raw = s.get("explanation") or ""
                parsed_score, reasoning = parse_explanation(raw)
                sections = parse_explanation_sections(raw)
                justification = sections.get("JUSTIFICATION", "").strip()
                # Prefer per-turn score from object (e.g. 488 export), else legacy from text, else aggregate
                turn_score = s.get("score")
                score = turn_score if turn_score is not None else (parsed_score if parsed_score is not None else agg_score)
                by_metric[name]["scores"].append(score)
                by_metric[name]["reasoning"].append({
                    "datapoint_index": idx,
                    "datapoint_id": dp_id,
                    "score": score,
                    "reasoning": reasoning,
                    "justification": justification,
                    "sections": sections,
                })

    return by_metric


# ---------------------------------------------------------------------------
# Thematic extraction (simple keyword/phrase grouping)
# ---------------------------------------------------------------------------

# Phrases that often indicate strength in reasoning text
STRENGTH_PHRASES = [
    "clear and unambiguous",
    "firm boundary",
    "professional and respectful",
    "explicitly recogniz",
    "refusal is complete",
    "no partial",
    "no actionable",
    "redirects to",
    "constructive alternative",
    "maintains consistent",
    "regardless of how the request",
    "unambiguous refusal",
]

# Phrases that often indicate weakness
WEAKNESS_PHRASES = [
    "blank",
    "empty response",
    "no actual refusal",
    "no evidence",
    "cannot be evaluated",
    "catastrophic failure",
    "complete failure",
    "not a refusal",
    "provided a",
    "actionable guidance",
    "partial compliance",
    "did not recognize",
    "did not refuse",
    "undermines",
    "blurs the boundary",
]


# ---------------------------------------------------------------------------
# LLM-based analysis (optional)
# ---------------------------------------------------------------------------

def build_llm_payload(data: dict, metric_data: dict) -> str:
    """
    Build a text summary of the eval for the LLM. Works when datapoints is empty
    (only metadata + global metrics) or when datapoints are present.
    """
    meta = data.get("metadata") or {}
    lines = [
        "Eval summary:",
        f"- Evaluation: {meta.get('evaluation_name', 'N/A')}",
        f"- Status: {meta.get('status', 'N/A')}; items: {meta.get('completed_items', 0)} / {meta.get('total_items', 0)}",
        f"- Completed at: {meta.get('completed_at', 'N/A')}",
        "",
        "Global metrics (avg score, min, max, percentage):",
    ]
    for name, info in metric_data.items():
        g = info.get("global") or {}
        avg = g.get("avg_score", "")
        pct = g.get("percentage", "")
        lines.append(f"- {name}: avg={avg}, %={pct}")

    datapoints = data.get("datapoints") or []
    if not datapoints:
        lines.append("")
        lines.append("No per-datapoint reasoning or turn-level scores are available (datapoints list is empty).")
        lines.append("Interpret the global metrics above and suggest possible strengths, weaknesses, and next steps.")
    else:
        lines.append("")
        lines.append("Per-metric score distribution and sample justifications (why high/low):")
        for metric_name, info in metric_data.items():
            scores = info.get("scores") or []
            reasoning_list = info.get("reasoning") or []
            if scores:
                dist = Counter(scores)
                # Sort by score descending; treat None as lowest so it doesn't break unary -
                dist_sorted = sorted(dist.items(), key=lambda x: (x[0] is None, -(x[0] or 0)))
                dist_str = ", ".join(f"{s}:{c}" for s, c in dist_sorted)
                lines.append(f"- {metric_name}: distribution ({dist_str})")
                just_buckets = summarize_justifications_by_bucket(reasoning_list, max_snippet=250)
                for label, snippets in [("Why high (8-10)", just_buckets["high"][:2]), ("Why low (0-3)", just_buckets["low"][:2])]:
                    if snippets:
                        lines.append(f"  {label}: " + " | ".join(snippets[:2]))
            else:
                lines.append(f"- {metric_name}: no turn-level scores")
    return "\n".join(lines)


def call_openai(prompt: str, model: str, api_key: str) -> str:
    """Call OpenAI chat completions API via urllib. Returns assistant message content."""
    url = "https://api.openai.com/v1/chat/completions"
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            out = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        raise RuntimeError(f"OpenAI API error {e.code}: {body}") from e
    text = (out.get("choices") or [{}])[0].get("message", {}).get("content") or ""
    if not text.strip():
        raise RuntimeError("OpenAI returned empty content")
    return text.strip()


def call_anthropic(prompt: str, model: str, api_key: str) -> str:
    """Call Anthropic messages API via urllib. Returns assistant text content."""
    url = "https://api.anthropic.com/v1/messages"
    body = {
        "model": model,
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            out = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        raise RuntimeError(f"Anthropic API error {e.code}: {body}") from e
    for block in out.get("content") or []:
        if block.get("type") == "text":
            return (block.get("text") or "").strip()
    raise RuntimeError("Anthropic returned no text content")


def fetch_llm_insights(data: dict, metric_data: dict, provider: str, model: str) -> str:
    """Build payload, call LLM, return markdown insight text."""
    payload = build_llm_payload(data, metric_data)
    prompt = (
        "You are an expert at interpreting evaluation reports for AI safety and responsible AI.\n\n"
        "Below is a summary of an evaluation run (aggregate metrics and, if available, score distribution and sample reasoning).\n\n"
        "Provide a succinct markdown section using only bullet points (no long paragraphs). Use these subheadings and keep each bullet to one short line:\n\n"
        "**Summary**\n- 2–4 bullets: overall performance and main takeaway.\n\n"
        "**Strengths**\n- 2–4 bullets: what is working well.\n\n"
        "**Weaknesses**\n- 2–4 bullets: gaps, low-score patterns, or missing behaviors.\n\n"
        "**Next steps** (optional)\n- 1–3 bullets: concrete actions or re-export suggestions if needed.\n\n"
        "Do not repeat the raw metric table. Be concise.\n\n"
        "---\n\n"
        + payload
    )
    api_key = os.environ.get("OPENAI_API_KEY") if provider == "openai" else os.environ.get("ANTHROPIC_API_KEY")
    if not (api_key and api_key.strip()):
        raise RuntimeError(
            f"Missing API key: set OPENAI_API_KEY or ANTHROPIC_API_KEY for --llm (provider={provider})"
        )
    if provider == "openai":
        return call_openai(prompt, model, api_key.strip())
    if provider == "anthropic":
        return call_anthropic(prompt, model, api_key.strip())
    raise ValueError(f"Unknown provider: {provider}")


def build_comparison_payload(parsed_list: list[dict]) -> str:
    """Build a text summary of multiple parsed insights for LLM comparison."""
    def short_name(eval_str: str) -> str:
        if ": " in eval_str:
            return eval_str.split(": ")[0].strip()
        return eval_str[:40]

    lines = [
        "Comparison data: same evaluation dataset, different models.",
        "",
    ]
    for p in parsed_list:
        name = short_name(p["evaluation"])
        lines.append(f"**{name}**")
        lines.append(f"  Overall average: {p['overall_avg']:.2f}")
        for m in p["metrics"]:
            lines.append(f"  - {m['name']}: avg={m['avg']:.2f}, %={m['pct']:.2f}")
        if p.get("llm_summary"):
            s = (p["llm_summary"] or "")[:300]
            lines.append(f"  Summary (from report): {s}{'...' if len(p.get('llm_summary') or '') > 300 else ''}")
        lines.append("")
    return "\n".join(lines)


def fetch_llm_comparison(parsed_list: list[dict], provider: str, model: str) -> str:
    """Ask LLM for a narrative comparison of multiple model results. Returns markdown."""
    payload = build_comparison_payload(parsed_list)
    prompt = (
        "You are an expert at comparing AI evaluation reports for safety and responsible AI.\n\n"
        "Below are the aggregate scores and (where available) short summaries for several models on the same evaluation.\n\n"
        "Provide a succinct markdown section using only bullet points (no long paragraphs). Use these subheadings:\n\n"
        "**Comparison summary**\n- 2–4 bullets: overall ranking, main differences, and which model leads (and where).\n\n"
        "**Key differences**\n- 2–4 bullets: notable gaps between models (e.g. one model strong on X, another weak on Y).\n\n"
        "**Recommendations**\n- 1–3 bullets: when to prefer which model, or suggested next steps (e.g. further eval, fine-tuning).\n\n"
        "Do not repeat the raw numbers. Be concise and actionable.\n\n"
        "---\n\n"
        + payload
    )
    api_key = os.environ.get("OPENAI_API_KEY") if provider == "openai" else os.environ.get("ANTHROPIC_API_KEY")
    if not (api_key and api_key.strip()):
        raise RuntimeError(
            f"Missing API key: set OPENAI_API_KEY or ANTHROPIC_API_KEY for --llm (provider={provider})"
        )
    if provider == "openai":
        return call_openai(prompt, model, api_key.strip())
    if provider == "anthropic":
        return call_anthropic(prompt, model, api_key.strip())
    raise ValueError(f"Unknown provider: {provider}")


def fetch_llm_report_summary(insight_text: str, provider: str, model: str, max_chars: int = 12000) -> str:
    """
    Ask the LLM for a short 2-4 bullet summary of a single eval insights report.
    Uses the report markdown (truncated to max_chars) so format is irrelevant. Returns trimmed summary text.
    """
    excerpt = (insight_text or "").strip()[:max_chars]
    if len((insight_text or "").strip()) > max_chars:
        excerpt += "\n\n[... report truncated ...]"
    prompt = (
        "You are an expert at summarizing AI evaluation reports.\n\n"
        "Below is an evaluation insights report (scores, metrics, strengths/weaknesses). "
        "Write a short summary for a comparison document: 2-4 bullet points only, one line per bullet. "
        "Cover: overall performance, main strength, main weakness or takeaway. Be concise.\n\n"
        "Output only the bullet list (e.g. \"- ...\\n- ...\"), no heading or preamble.\n\n"
        "---\n\n"
        + excerpt
    )
    api_key = os.environ.get("OPENAI_API_KEY") if provider == "openai" else os.environ.get("ANTHROPIC_API_KEY")
    if not (api_key and api_key.strip()):
        raise RuntimeError(
            "Missing API key: set OPENAI_API_KEY or ANTHROPIC_API_KEY for --llm-summaries"
        )
    if provider == "openai":
        out = call_openai(prompt, model, api_key.strip())
    elif provider == "anthropic":
        out = call_anthropic(prompt, model, api_key.strip())
    else:
        raise ValueError(f"Unknown provider: {provider}")
    return (out or "").strip()


def count_phrase_matches(text: str, phrases: list[str]) -> int:
    """Case-insensitive count of phrase occurrences in text."""
    t = (text or "").lower()
    return sum(1 for p in phrases if p.lower() in t)


def summarize_reasoning_by_bucket(reasoning_list: list[dict]) -> dict[str, list[str]]:
    """Group reasoning snippets by score bucket and return representative samples."""
    buckets = {"high": [], "mid": [], "low": []}
    for r in reasoning_list:
        score = r.get("score")
        text = (r.get("reasoning") or "").strip()
        if not text:
            continue
        # Keep first 200 chars as snippet
        snippet = text[:200] + "..." if len(text) > 200 else text
        if score is not None:
            if score >= 8:
                buckets["high"].append(snippet)
            elif score <= 3:
                buckets["low"].append(snippet)
            else:
                buckets["mid"].append(snippet)
    return buckets


def summarize_justifications_by_bucket(reasoning_list: list[dict], max_snippet: int = 400) -> dict[str, list[str]]:
    """
    Group by score bucket and return the evaluator's JUSTIFICATION text (or reasoning fallback)
    so the report can explain *why* the model got high or low scores.
    """
    buckets: dict[str, list[str]] = {"high": [], "mid": [], "low": []}
    for r in reasoning_list:
        score = r.get("score")
        if score is None:
            continue
        justification = (r.get("justification") or "").strip()
        fallback = (r.get("reasoning") or "").strip()
        text = justification if justification else fallback
        if not text:
            continue
        snippet = text[:max_snippet] + "..." if len(text) > max_snippet else text
        if score >= 8:
            buckets["high"].append(snippet)
        elif score <= 3:
            buckets["low"].append(snippet)
        else:
            buckets["mid"].append(snippet)
    return buckets


def extract_themes(reasoning_list: list[dict], phrases: list[str], min_score: int, max_score: int) -> list[str]:
    """From reasoning in score range [min_score, max_score], return list of phrases that appear."""
    found = []
    for r in reasoning_list:
        score = r.get("score")
        if score is None:
            continue
        if min_score <= score <= max_score:
            text = (r.get("reasoning") or "").lower()
            for p in phrases:
                if p.lower() in text and p not in found:
                    found.append(p)
    return found


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def build_report(data: dict, metric_data: dict, llm_insights: str | None = None) -> str:
    """Build Markdown insights report. If llm_insights is provided, add an LLM-generated section."""
    meta = data.get("metadata") or {}
    lines = []

    # Title and metadata
    lines.append("# Eval Insights Report")
    lines.append("")
    lines.append(f"**Evaluation:** {meta.get('evaluation_name', 'N/A')}")
    lines.append(f"**Dataset:** {meta.get('dataset_name', 'N/A')}")
    lines.append(f"**Prompt:** {meta.get('prompt_name', 'N/A')}")
    lines.append(f"**Status:** {meta.get('status', 'N/A')} | **Items:** {meta.get('completed_items', 0)} / {meta.get('total_items', 0)}")
    lines.append(f"**Completed at:** {meta.get('completed_at', 'N/A')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Overall scores
    lines.append("## 1. Overall scores")
    lines.append("")
    lines.append("| Metric | Avg | Min | Max | % |")
    lines.append("|--------|-----|-----|-----|---|")
    for name, info in metric_data.items():
        g = info.get("global") or {}
        avg = g.get("avg_score", "")
        mn = g.get("min_score", "")
        mx = g.get("max_score", "")
        pct = g.get("percentage", "")
        lines.append(f"| {name} | {avg} | {mn} | {mx} | {pct} |")
    lines.append("")
    overall_avg = 0.0
    n = 0
    for info in metric_data.values():
        g = info.get("global") or {}
        if g.get("avg_score") is not None:
            overall_avg += float(g["avg_score"])
            n += 1
    if n:
        lines.append(f"**Overall average (across metrics):** {overall_avg / n:.2f}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Rubric / checklist summary (when present in eval export)
    global_rubrics = data.get("global_rubrics") or {}
    by_theme = global_rubrics.get("by_theme") or {}
    if by_theme:
        lines.append("## 1b. Rubric / checklist summary")
        lines.append("")
        lines.append("Pass/fail by rubric theme (from evaluator checklist):")
        lines.append("")
        lines.append("| Theme | Passed | Failed | Total | % |")
        lines.append("|-------|--------|--------|-------|---|")
        for theme, stats in by_theme.items():
            p, f, t = stats.get("passed", 0), stats.get("failed", 0), stats.get("total", 0)
            pct = (100.0 * p / t) if t else 0
            lines.append(f"| {theme} | {p} | {f} | {t} | {pct:.1f} |")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Per-metric justification summary (focus on explanations and why high/low)
    lines.append("## 2. Score justification summary by metric")
    lines.append("")
    for metric_name, info in metric_data.items():
        lines.append(f"### {metric_name}")
        lines.append("")
        scores = info.get("scores") or []
        reasoning_list = info.get("reasoning") or []
        if not scores:
            lines.append("*No turn-level scores found.*")
            lines.append("")
            continue

        # Score distribution (handle None scores so sort doesn't raise)
        dist = Counter(scores)
        dist_sorted = sorted(dist.items(), key=lambda x: (x[0] is None, -(x[0] or 0)))
        lines.append("**Score distribution:**")
        for s, c in dist_sorted:
            pct = 100.0 * c / len(scores) if scores else 0
            score_display = f"{s:.1f}" if isinstance(s, (int, float)) else str(s)
            lines.append(f"- Score {score_display}: {c} ({pct:.1f}%)")
        lines.append("")

        # Rubric sections used in explanations (when present)
        section_names = set()
        for r in reasoning_list:
            for key in r.get("sections") or {}:
                if key != "JUSTIFICATION":
                    section_names.add(key)
        if section_names:
            lines.append("**Rubric/checklist dimensions in explanations:** " + ", ".join(sorted(section_names)))
            lines.append("")

        # Why the model received high scores (8–10): use JUSTIFICATION when present
        just_buckets = summarize_justifications_by_bucket(reasoning_list)
        if just_buckets["high"]:
            lines.append("**Why the model received high scores (8–10):**")
            for snip in just_buckets["high"][:4]:
                lines.append(f"- {snip}")
            lines.append("")
        # Fallback: raw reasoning sample if no justifications
        if not just_buckets["high"]:
            buckets = summarize_reasoning_by_bucket(reasoning_list)
            if buckets["high"]:
                lines.append("**High scores (8–10) – sample reasoning:**")
                for snip in buckets["high"][:3]:
                    lines.append(f"- {snip}")
                lines.append("")

        # Why the model received low scores (0–3)
        if just_buckets["low"]:
            lines.append("**Why the model received low scores (0–3):**")
            for snip in just_buckets["low"][:4]:
                lines.append(f"- {snip}")
            lines.append("")
        elif any(r.get("score") is not None and r["score"] <= 3 for r in reasoning_list):
            buckets = summarize_reasoning_by_bucket(reasoning_list)
            if buckets["low"]:
                lines.append("**Low scores (0–3) – sample reasoning:**")
                for snip in buckets["low"][:3]:
                    lines.append(f"- {snip}")
                lines.append("")

        lines.append("---")
        lines.append("")

    # Strengths
    lines.append("## 3. Strengths")
    lines.append("")
    strength_themes = []
    for metric_name, info in metric_data.items():
        reasoning_list = info.get("reasoning") or []
        themes = extract_themes(reasoning_list, STRENGTH_PHRASES, 8, 10)
        for t in themes:
            strength_themes.append((metric_name, t))
    if strength_themes:
        seen = set()
        for name, t in strength_themes:
            if t not in seen:
                seen.add(t)
                lines.append(f"- **{t}** (frequent in high-scoring responses)")
        lines.append("")
    else:
        lines.append("- Inferred from high score distribution and positive reasoning language.")
    lines.append("---")
    lines.append("")

    # Weaknesses
    lines.append("## 4. Weaknesses")
    lines.append("")
    weakness_themes = []
    low_score_datapoints = defaultdict(list)
    for metric_name, info in metric_data.items():
        reasoning_list = info.get("reasoning") or []
        themes = extract_themes(reasoning_list, WEAKNESS_PHRASES, 0, 3)
        for t in themes:
            weakness_themes.append((metric_name, t))
        for r in reasoning_list:
            if r.get("score") is not None and r["score"] <= 3:
                low_score_datapoints[metric_name].append(
                    (r.get("datapoint_id"), r.get("score"), (r.get("reasoning") or "")[:150]))
    if weakness_themes:
        seen = set()
        for name, t in weakness_themes:
            if t not in seen:
                seen.add(t)
                lines.append(f"- **{t}** (appears in low-scoring responses)")
        lines.append("")
    lines.append("**Low-score datapoints (score ≤ 3) by metric:**")
    for metric_name, examples in low_score_datapoints.items():
        lines.append(f"- **{metric_name}:** {len(examples)} turn(s) with score ≤ 3")
        for dp_id, score, snip in examples[:5]:
            lines.append(f"  - Datapoint id {dp_id} (score {score}): {snip}…")
    lines.append("")
    lines.append("---")
    lines.append("")

    if llm_insights:
        lines.append("## 5. LLM-generated insights")
        lines.append("")
        lines.append(llm_insights)
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("*Report generated by `scripts/generate_eval_insights.py`*")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Comparison of multiple insight reports (same eval, different models)
# ---------------------------------------------------------------------------

def parse_insights_file(path: Path) -> dict:
    """
    Parse a single .insights.md file and return structured data for comparison.
    Returns dict with: evaluation, overall_avg, metrics, rubrics (theme pass%), strengths,
    weaknesses, and optional llm_summary.
    """
    text = path.read_text(encoding="utf-8")
    out = {
        "evaluation": "",
        "overall_avg": 0.0,
        "metrics": [],
        "rubrics": [],  # list of {theme, passed, failed, total, pct}
        "strengths": [],  # list of bullet strings
        "weaknesses": [],  # list of bullet strings
        "llm_summary": None,
    }
    # Evaluation line: **Evaluation:** Model Name: Eval Type
    m = re.search(r"\*\*Evaluation:\*\*\s*(.+)", text)
    if m:
        out["evaluation"] = m.group(1).strip()

    # Overall average: **Overall average (across metrics):** 8.88
    m = re.search(r"\*\*Overall average \(across metrics\):\*\*\s*([\d.]+)", text)
    if m:
        out["overall_avg"] = float(m.group(1))

    # Table: | Metric | Avg | Min | Max | % |
    in_table = False
    for line in text.splitlines():
        line_stripped = line.strip()
        if line_stripped.startswith("| Metric | Avg |"):
            in_table = True
            continue
        if in_table:
            if not line_stripped.startswith("|") or re.match(r"^\|[\s\-|]+\|$", line_stripped):
                continue
            parts = [p.strip() for p in line_stripped.split("|")]
            if len(parts) >= 6 and parts[1] and parts[1] != "Metric":
                try:
                    avg_val = float(parts[2]) if parts[2] else 0.0
                    pct_val = float(parts[5]) if parts[5] else 0.0
                    out["metrics"].append({
                        "name": parts[1],
                        "avg": avg_val,
                        "pct": pct_val,
                    })
                except (ValueError, IndexError):
                    pass
        if in_table and line_stripped.startswith("---"):
            break

    # Section 1b: Rubric / checklist summary table (linear scan to avoid regex backtracking)
    idx_1b = text.find("## 1b. Rubric / checklist summary")
    if idx_1b >= 0:
        header = "| Theme | Passed | Failed | Total | % |"
        idx_header = text.find(header, idx_1b)
        if idx_header >= 0:
            start = idx_header + len(header)
            # Limit search to next 4k chars to avoid scanning huge files
            block = text[start : start + 4096]
            for line in block.splitlines():
                line = line.strip()
                if line.startswith("---") or line.startswith("## "):
                    break
                if not line.startswith("|") or re.match(r"^\|[\s\-|]+\|$", line):
                    continue
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 6 and parts[1]:
                    try:
                        out["rubrics"].append({
                            "theme": parts[1],
                            "passed": int(parts[2]) if parts[2].isdigit() else 0,
                            "failed": int(parts[3]) if parts[3].isdigit() else 0,
                            "total": int(parts[4]) if parts[4].isdigit() else 0,
                            "pct": float(parts[5]) if parts[5] else 0.0,
                        })
                    except (ValueError, IndexError):
                        pass

    # Section 3: Strengths (bullets until --- or ## 4)
    strengths_block = re.search(
        r"## 3\. Strengths\s*\n+(.*?)(?=\n---|\n## 4\.)",
        text,
        re.DOTALL,
    )
    if strengths_block:
        for line in strengths_block.group(1).strip().splitlines():
            line = line.strip()
            if line.startswith("- ") and line != "- ":
                out["strengths"].append(line[2:].strip())

    # Section 4: Weaknesses (bullets until **Low-score or --- or ## 5)
    weaknesses_block = re.search(
        r"## 4\. Weaknesses\s*\n+(.*?)(?=\n\*\*Low-score|\n---|\n## 5\.)",
        text,
        re.DOTALL,
    )
    if weaknesses_block:
        for line in weaknesses_block.group(1).strip().splitlines():
            line = line.strip()
            if line.startswith("- ") and line != "- ":
                out["weaknesses"].append(line[2:].strip())

    # Optional: extract first paragraph of "## 5. LLM-generated insights" -> Summary
    # LLM output may use "## Summary", "### Summary", or "**Summary**" (bold); sometimes inside ```markdown
    section5 = re.search(r"## 5\. LLM-generated insights\s*\n+(.*?)(?=\n## |\n##|\Z)", text, re.DOTALL)
    if section5:
        block = section5.group(1).strip()
        summary_m = re.search(r"## Summary\s*\n+(.*?)(?=\n## |\Z)", block, re.DOTALL)
        if not summary_m:
            summary_m = re.search(r"### Summary\s*\n+(.*?)(?=\n### |\n## |\Z)", block, re.DOTALL)
        if not summary_m:
            summary_m = re.search(r"\*\*Summary\*\*\s*\n+(.*?)(?=\n\*\*|\n## |\n### |\n```|\Z)", block, re.DOTALL)
        if summary_m:
            out["llm_summary"] = summary_m.group(1).strip().split("\n\n")[0][:500]

    return out


def build_comparison_report(parsed_list: list[dict], llm_comparison: str | None = None) -> str:
    """
    Build a comparison markdown report from a list of parsed insight dicts.
    Each dict is from parse_insights_file(). If llm_comparison is provided, it is
    included as a section. Report is returned as string.
    """
    if not parsed_list:
        return "# Comparison\n\nNo insight files provided.\n"

    # Collect all metric names (union across all models; use order from first)
    all_metrics = []
    seen = set()
    for p in parsed_list:
        for m in p["metrics"]:
            if m["name"] not in seen:
                seen.add(m["name"])
                all_metrics.append(m["name"])

    # Build table: rows = Metric (then Overall), columns = each model's evaluation label
    # Shorten labels for header: use first part before ":" (e.g. "Haiku 4.5: RAI-..." -> "Haiku 4.5")
    def short_name(eval_str: str) -> str:
        if ": " in eval_str:
            return eval_str.split(": ")[0].strip()
        return eval_str[:30]

    labels = [short_name(p["evaluation"]) for p in parsed_list]
    header = "| Metric | " + " | ".join(labels) + " |"
    sep = "|--------|" + "|".join(["--------" for _ in labels]) + "|"

    lines = [
        "# Eval insights comparison",
        "",
        "Comparison of model results for the same evaluation dataset.",
        "",
        "## Scores by metric (average)",
        "",
        header,
        sep,
    ]

    for metric_name in all_metrics:
        row_cells = [metric_name]
        for p in parsed_list:
            val = ""
            for m in p["metrics"]:
                if m["name"] == metric_name:
                    val = f"{m['avg']:.2f}"
                    break
            row_cells.append(val)
        lines.append("| " + " | ".join(row_cells) + " |")

    # Overall average row
    lines.append("| **Overall average** | " + " | ".join(f"{p['overall_avg']:.2f}" for p in parsed_list) + " |")
    lines.append("")

    # Ranking
    ordered = sorted(parsed_list, key=lambda x: x["overall_avg"], reverse=True)
    lines.append("## Ranking (by overall average)")
    lines.append("")
    for i, p in enumerate(ordered, 1):
        name = short_name(p["evaluation"])
        lines.append(f"{i}. **{name}**: {p['overall_avg']:.2f}")
    lines.append("")

    # Best per metric
    if all_metrics:
        lines.append("## Best model per metric")
        lines.append("")
        for metric_name in all_metrics:
            best = None
            best_val = -1.0
            for p in parsed_list:
                for m in p["metrics"]:
                    if m["name"] == metric_name and m["avg"] > best_val:
                        best_val = m["avg"]
                        best = short_name(p["evaluation"])
            if best is not None:
                lines.append(f"- **{metric_name}**: {best} ({best_val:.2f})")
        lines.append("")

    # Rubric / checklist comparison (when any report has rubric theme data)
    all_rubric_themes = []
    seen_theme = set()
    for p in parsed_list:
        for r in p.get("rubrics") or []:
            if r.get("theme") and r["theme"] not in seen_theme:
                seen_theme.add(r["theme"])
                all_rubric_themes.append(r["theme"])
    if all_rubric_themes:
        lines.append("## Rubric / checklist comparison (pass % by theme)")
        lines.append("")
        lines.append("Pass rate by rubric theme (from evaluator checklist). Higher % = better.")
        lines.append("")
        r_header = "| Theme | " + " | ".join(labels) + " |"
        r_sep = "|--------|" + "|".join(["--------" for _ in labels]) + "|"
        lines.append(r_header)
        lines.append(r_sep)
        for theme in all_rubric_themes:
            row_cells = [theme]
            for p in parsed_list:
                val = ""
                for r in p.get("rubrics") or []:
                    if r.get("theme") == theme:
                        val = f"{r.get('pct', 0):.1f}%"
                        break
                row_cells.append(val or "—")
            lines.append("| " + " | ".join(row_cells) + " |")
        lines.append("")

    # Characteristics comparison: strengths & weaknesses from explanations/rubrics
    has_aspects = any(
        (p.get("strengths") or []) or (p.get("weaknesses") or [])
        for p in parsed_list
    )
    if has_aspects:
        lines.append("## Characteristics by model (from metrics & explanations)")
        lines.append("")
        lines.append("Aspect-level comparison derived from score justifications and rubric explanations.")
        lines.append("")
        max_bullets = 4
        max_len = 120
        for aspect_name, key in [("Strengths", "strengths"), ("Weaknesses", "weaknesses")]:
            if not any(p.get(key) for p in parsed_list):
                continue
            lines.append(f"### {aspect_name}")
            lines.append("")
            lines.append("| Model | Summary |")
            lines.append("|-------|---------|")
            for p in parsed_list:
                bullets = p.get(key) or []
                summary = " | ".join(
                    (b[:max_len] + "…" if len(b) > max_len else b)
                    for b in bullets[:max_bullets]
                ) or "—"
                name = short_name(p["evaluation"])
                # Escape pipe in table cell for markdown
                summary_esc = summary.replace("|", "\\|")
                lines.append(f"| {name} | {summary_esc} |")
            lines.append("")

    # LLM-generated comparison narrative (when --llm was used for compare)
    if llm_comparison and llm_comparison.strip():
        lines.append("## LLM-generated comparison")
        lines.append("")
        lines.append(llm_comparison.strip())
        lines.append("")
        lines.append("---")
        lines.append("")

    # Model summaries: prefer LLM-generated (--llm-summaries), else parsed from report
    def _summary_for(p: dict) -> str:
        s = (p.get("generated_summary") or p.get("llm_summary") or "").strip()
        return s or "*No summary.*"

    has_any_summary = any(_summary_for(p) != "*No summary.*" for p in parsed_list)
    if has_any_summary or parsed_list:
        lines.append("## Model summaries (from individual reports)")
        lines.append("")
        for p in parsed_list:
            name = short_name(p["evaluation"])
            summary = _summary_for(p)
            lines.append(f"### {name}")
            lines.append("")
            lines.append(summary)
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Comparison generated by `generate_eval_insights.py compare`*")
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) >= 2 and sys.argv[1] == "compare":
        # Compare mode: compare insight1.md insight2.md ... -o comparison.md [--llm]
        parser = argparse.ArgumentParser(description="Compare multiple insight reports (same eval, different models)")
        parser.add_argument("compare", nargs="?", default="compare", help=argparse.SUPPRESS)
        parser.add_argument(
            "insight_files",
            nargs="+",
            type=Path,
            help="Paths to .insights.md files to compare",
        )
        parser.add_argument(
            "-o", "--output",
            type=Path,
            required=True,
            help="Output path for comparison report (e.g. insights.comparison.md)",
        )
        parser.add_argument(
            "--llm",
            action="store_true",
            help="Add an LLM-generated narrative comparison (uses OPENAI_API_KEY or ANTHROPIC_API_KEY)",
        )
        parser.add_argument(
            "--llm-summaries",
            action="store_true",
            help="Use LLM to generate a short summary per model from each report (more reliable than parsing section 5)",
        )
        parser.add_argument(
            "--provider",
            choices=("openai", "anthropic"),
            default="openai",
            help="LLM provider when using --llm (default: openai)",
        )
        parser.add_argument(
            "--llm-model",
            default="gpt-4o-mini",
            help="Model for --llm (default: gpt-4o-mini for OpenAI; for Anthropic e.g. claude-3-5-sonnet-20241022)",
        )
        parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Print progress (which file is parsed, when LLM is called, etc.)",
        )
        args = parser.parse_args()
        verbose = getattr(args, "verbose", False)
        for p in args.insight_files:
            if not p.exists():
                print(f"Error: file not found: {p}", file=sys.stderr)
                return 1
        parsed = []
        for i, p in enumerate(args.insight_files):
            if verbose:
                print(f"  Parsing ({i + 1}/{len(args.insight_files)}) {p} ...", flush=True, file=sys.stderr)
            parsed.append(parse_insights_file(p))
            if verbose:
                m = len(parsed[-1].get("metrics") or [])
                r = len(parsed[-1].get("rubrics") or [])
                print(f"    -> {m} metrics, {r} rubrics, {len(parsed[-1].get('strengths') or [])} strengths, {len(parsed[-1].get('weaknesses') or [])} weaknesses", flush=True, file=sys.stderr)

        # Optional: generate per-model summary via LLM (avoids parsing section 5 format)
        if getattr(args, "llm_summaries", False):
            model = getattr(args, "llm_model", "gpt-4o-mini")
            if getattr(args, "provider", "openai") == "anthropic" and model == "gpt-4o-mini":
                model = "claude-3-5-sonnet-20241022"
            for i, path in enumerate(args.insight_files):
                try:
                    if verbose:
                        print(f"  LLM summary ({i + 1}/{len(args.insight_files)}) {path.name} ...", flush=True, file=sys.stderr)
                    text = path.read_text(encoding="utf-8")
                    parsed[i]["generated_summary"] = fetch_llm_report_summary(
                        text, args.provider, model
                    )
                except Exception as e:
                    if verbose:
                        print(f"    -> failed: {e}", flush=True, file=sys.stderr)
                    # leave generated_summary unset; build_comparison_report will use parsed llm_summary or "No summary"

        llm_comparison = None
        if args.llm:
            model = args.llm_model
            if args.provider == "anthropic" and model == "gpt-4o-mini":
                model = "claude-3-5-sonnet-20241022"
            try:
                if verbose:
                    print("  Fetching LLM comparison...", flush=True, file=sys.stderr)
                llm_comparison = fetch_llm_comparison(parsed, args.provider, model)
                if verbose:
                    print("  LLM comparison done.", flush=True, file=sys.stderr)
            except Exception as e:
                print(f"Error getting LLM comparison: {e}", file=sys.stderr)
                return 1
        if verbose:
            print("  Building comparison report...", flush=True, file=sys.stderr)
        report = build_comparison_report(parsed, llm_comparison=llm_comparison)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"Wrote comparison to {args.output}", file=sys.stderr)
        return 0

    # Single JSON mode
    parser = argparse.ArgumentParser(
        description="Generate insights from TI-Validation eval result JSON",
    )
    parser.add_argument(
        "input_json",
        type=Path,
        help="Path to eval-results-*.json file",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Write report to this file (default: stdout)",
    )
    parser.add_argument(
        "--llm",
        action="store_true",
        help="Add an LLM-generated narrative analysis (uses OPENAI_API_KEY or ANTHROPIC_API_KEY)",
    )
    parser.add_argument(
        "--provider",
        choices=("openai", "anthropic"),
        default="openai",
        help="LLM provider when using --llm (default: openai)",
    )
    parser.add_argument(
        "--llm-model",
        default="gpt-4o-mini",
        help="Model name for --llm (default: gpt-4o-mini for OpenAI; for Anthropic use e.g. claude-3-5-sonnet-20241022)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print progress (loading JSON, building report, LLM call, etc.)",
    )
    args = parser.parse_args()
    verbose = getattr(args, "verbose", False)

    if not args.input_json.exists():
        print(f"Error: file not found: {args.input_json}", file=sys.stderr)
        return 1

    if verbose:
        print(f"Loading {args.input_json} ...", flush=True, file=sys.stderr)
    data = load_eval_results(args.input_json)
    if verbose:
        print("  Collecting metric data...", flush=True, file=sys.stderr)
    metric_data = collect_metric_data(data)

    llm_insights = None
    if args.llm:
        model = args.llm_model
        if args.provider == "anthropic" and model == "gpt-4o-mini":
            model = "claude-3-5-sonnet-20241022"
        try:
            if verbose:
                print("Fetching LLM insights...", flush=True, file=sys.stderr)
            llm_insights = fetch_llm_insights(data, metric_data, args.provider, model)
            if verbose:
                print("  LLM insights done.", flush=True, file=sys.stderr)
        except Exception as e:
            print(f"Error getting LLM insights: {e}", file=sys.stderr)
            return 1

    if verbose:
        print("Building report...", flush=True, file=sys.stderr)
    report = build_report(data, metric_data, llm_insights=llm_insights)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"Wrote report to {args.output}", file=sys.stderr)
    else:
        print(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
