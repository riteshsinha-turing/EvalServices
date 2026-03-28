#!/usr/bin/env python3
"""
Extract narrative strengths and weaknesses per model from metric explanations.

Reads .insights.md Section 2 ("Why the model received high/low scores") or, if missing,
falls back to eval result JSONs. Outputs per-eval, per-model narrative bullets (from
metric explanations only) for use in PRESENTATION-SLIDES.md.

Usage:
  python scripts/extract_narrative_strengths_weaknesses.py [--output-dir DIR] [--combined FILE]
  Run from eval_results/ directory.
"""

import argparse
import json
import re
from pathlib import Path


# Display names for models inferred from filenames
MODEL_DISPLAY_NAMES = {
    "haiku-4.5": "Haiku 4.5",
    "opus-4.5": "Opus 4.5",
    "nova-pro": "Nova Pro",
    "nemotron-12b": "Nemotron 12B",
}

# Eval folder to short label for output
EVAL_LABELS = {
    "rai/01-toxicity-harmful-content": "RAI 01 – Toxicity & Harmful Content",
    "rai/07-misinformation-disinformation": "RAI 07 – Misinformation & Disinformation",
    "rai/08-childsafety-cse": "RAI 08 – Child Safety (CSE)",
    "redteam/01-hallucination-robustness": "Red Team 01 – Hallucination Robustness",
    "redteam/02-jailbreak-resistance": "Red Team 02 – Jailbreak Resistance",
    "redteam/05-multi-turn-guardrail-decay": "Red Team 05 – Multi-Turn Guardrail Decay",
}


def infer_model_from_filename(filename: str) -> str | None:
    """Infer model key from insights filename, e.g. haiku-4.5-eval-results-599-... -> Haiku 4.5."""
    name = Path(filename).stem
    for key, display in MODEL_DISPLAY_NAMES.items():
        if name.startswith(key + "-") or name.startswith(key + "_"):
            return display
    return None


def first_sentence_or_truncate(text: str, max_chars: int = 150) -> str:
    """Return first sentence of text, or text truncated to max_chars, trimmed."""
    text = (text or "").strip()
    if not text:
        return ""
    # First sentence: up to first period followed by space or end
    match = re.match(r"^([^.]*\.)(?:\s|$)", text)
    if match:
        s = match.group(1).strip()
        return s if len(s) <= max_chars else s[: max_chars - 3].rsplit(" ", 1)[0] + "..."
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rsplit(" ", 1)[0] + "..."


def parse_section2_from_insights(content: str) -> tuple[list[str], list[str]]:
    """
    Parse Section 2 of an insights markdown file.
    Returns (list of high-score explanation bullets, list of low-score explanation bullets).
    """
    # Section 2 runs from "## 2. Score justification" until "## 3. Strengths"
    section2_start = re.search(r"## 2\.\s*Score justification summary by metric", content, re.IGNORECASE)
    section2_end = re.search(r"\n## 3\.\s*Strengths\s", content)
    if not section2_start:
        return [], []
    start = section2_start.end()
    end = section2_end.start() if section2_end else len(content)
    section2 = content[start:end]

    high_bullets: list[str] = []
    low_bullets: list[str] = []

    # Find all "**Why the model received high scores (8–10):**" or "**High scores (8–10) – sample reasoning:**"
    high_header = re.compile(
        r"\*\*Why the model received high scores \(8–10\):\*\*|\*\*High scores \(8–10\) – sample reasoning:\*\*",
        re.IGNORECASE,
    )
    # Find all "**Why the model received low scores (0–3):**" or "**Low scores (0–3) – sample reasoning:**"
    low_header = re.compile(
        r"\*\*Why the model received low scores \(0–3\):\*\*|\*\*Low scores \(0–3\) – sample reasoning:\*\*",
        re.IGNORECASE,
    )

    pos = 0
    while pos < len(section2):
        high_match = high_header.search(section2, pos)
        low_match = low_header.search(section2, pos)

        # Next block: either high or low, whichever comes first
        if high_match and (not low_match or high_match.start() < low_match.start()):
            # Collect bullets after high header until next ** or ### or ---
            block_start = high_match.end()
            block_end = len(section2)
            for stop in (r"\n\*\*", r"\n###", r"\n---"):
                m = re.search(stop, section2[block_start:])
                if m:
                    block_end = min(block_end, block_start + m.start())
            block = section2[block_start:block_end]
            for line in block.splitlines():
                line = line.strip()
                if line.startswith("- ") and len(line) > 2:
                    bullet = line[2:].strip()
                    if bullet and bullet not in high_bullets:
                        high_bullets.append(bullet)
            pos = block_end
            continue
        if low_match and (not high_match or low_match.start() < high_match.start()):
            block_start = low_match.end()
            block_end = len(section2)
            for stop in (r"\n\*\*", r"\n###", r"\n---"):
                m = re.search(stop, section2[block_start:])
                if m:
                    block_end = min(block_end, block_start + m.start())
            block = section2[block_start:block_end]
            for line in block.splitlines():
                line = line.strip()
                if line.startswith("- ") and len(line) > 2:
                    bullet = line[2:].strip()
                    if bullet and bullet not in low_bullets:
                        low_bullets.append(bullet)
            pos = block_end
            continue
        break

    return high_bullets, low_bullets


def extract_from_json(json_path: Path) -> tuple[list[str], list[str]]:
    """
    Fallback: extract high (>=8) and low (<=3) score explanations from eval result JSON.
    Handles both per-turn scores (metric_results[].scores[].score/explanation) and
    per-datapoint aggregate (metric_results[].score/explanation when scores is empty).
    Returns (strength_snippets, weakness_snippets), each up to 3 representative bullets.
    """
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return [], []

    high: list[str] = []
    low: list[str] = []
    for dp in data.get("datapoints") or []:
        for mr in dp.get("metric_results") or []:
            turn_scores = mr.get("scores") or []
            if turn_scores:
                for s in turn_scores:
                    score = s.get("score")
                    expl = (s.get("explanation") or "").strip()
                    if not expl:
                        continue
                    snippet = first_sentence_or_truncate(expl, 150)
                    if score is not None:
                        if score >= 8 and snippet and snippet not in high:
                            high.append(snippet)
                        elif score <= 3 and snippet and snippet not in low:
                            low.append(snippet)
            else:
                # Aggregate level: metric has score and explanation per datapoint
                score = mr.get("score")
                expl = (mr.get("explanation") or "").strip()
                if not expl:
                    continue
                snippet = first_sentence_or_truncate(expl, 150)
                if score is not None:
                    if score >= 8 and snippet and snippet not in high:
                        high.append(snippet)
                    elif score <= 3 and snippet and snippet not in low:
                        low.append(snippet)

    return high[:3], low[:3]


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract narrative strengths/weaknesses from metric explanations.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Base directory (eval_results); per-eval narratives go under rai/... and redteam/...",
    )
    parser.add_argument(
        "--combined",
        type=Path,
        default=None,
        help="If set, write one combined markdown file with all evals.",
    )
    parser.add_argument("--max-bullets", type=int, default=3, help="Max strength and weakness bullets per model.")
    parser.add_argument("--max-chars", type=int, default=150, help="Max chars per bullet (truncate with ...).")
    args = parser.parse_args()

    base = args.output_dir
    combined_lines: list[str] = []
    eval_dirs = [
        base / "rai" / "01-toxicity-harmful-content",
        base / "rai" / "07-misinformation-disinformation",
        base / "rai" / "08-childsafety-cse",
        base / "redteam" / "01-hallucination-robustness",
        base / "redteam" / "02-jailbreak-resistance",
        base / "redteam" / "05-multi-turn-guardrail-decay",
    ]

    for eval_dir in eval_dirs:
        if not eval_dir.is_dir():
            continue
        rel = str(eval_dir.relative_to(base)).replace("\\", "/")
        eval_label = EVAL_LABELS.get(rel, rel)

        insight_files = list(eval_dir.glob("*-eval-results-*.insights.md"))
        if not insight_files:
            continue

        by_model: dict[str, dict[str, list[str]]] = {}
        for insight_path in sorted(insight_files):
            model = infer_model_from_filename(insight_path.name)
            if not model:
                continue
            try:
                text = insight_path.read_text(encoding="utf-8")
            except OSError:
                continue
            high_bullets, low_bullets = parse_section2_from_insights(text)
            if not high_bullets and not low_bullets:
                # Fallback: same base name, .json (e.g. haiku-4.5-eval-results-641-2026-03-10.json)
                json_name = insight_path.stem.replace(".insights", "") + ".json"
                json_path = eval_dir / json_name
                if json_path.is_file():
                    high_bullets, low_bullets = extract_from_json(json_path)

            strengths = [first_sentence_or_truncate(b, args.max_chars) for b in high_bullets[: args.max_bullets]]
            weaknesses = [first_sentence_or_truncate(b, args.max_chars) for b in low_bullets[: args.max_bullets]]
            by_model[model] = {"strengths": strengths, "weaknesses": weaknesses}

        # Order models consistently
        model_order = [MODEL_DISPLAY_NAMES[k] for k in MODEL_DISPLAY_NAMES]
        ordered_models = [m for m in model_order if m in by_model]
        ordered_models += [m for m in sorted(by_model) if m not in ordered_models]

        # Per-eval markdown
        lines = [f"# Eval: {eval_label}", ""]
        for model in ordered_models:
            info = by_model[model]
            lines.append(f"## {model}")
            lines.append("- **Where it performs well:**")
            for s in info["strengths"] or ["(No high-score explanations extracted.)"]:
                lines.append(f"  - {s}")
            lines.append("- **Where it lags:**")
            for w in info["weaknesses"] or ["(No low-score explanations extracted.)"]:
                lines.append(f"  - {w}")
            lines.append("")
        lines.append("---")
        lines.append("")

        per_eval_path = eval_dir / "narrative_by_model.md"
        per_eval_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Wrote {per_eval_path}")

        if args.combined is not None:
            combined_lines.extend(lines)

    if args.combined is not None and combined_lines:
        args.combined.parent.mkdir(parents=True, exist_ok=True)
        args.combined.write_text("\n".join(combined_lines), encoding="utf-8")
        print(f"Wrote combined {args.combined}")


if __name__ == "__main__":
    main()
