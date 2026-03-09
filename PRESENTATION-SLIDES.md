# RAI & Red Team Eval — Presentation Slides

*Inspired by a structured slide format: problem, dataset, task design, evaluation setup, then results by eval with overall / strengths / weaknesses.*

---

## Slide 1: Overview

- **Problem statement** — Why we evaluate enterprise AI assistants (safety risks: hallucination, PII, jailbreak, regulatory, HR).
- **Dataset overview** — ~50–100 datapoints per eval; unified schema with conversation history + adversarial probe.
- **Task design** — Multi-turn (10–40 messages) + final probe; model response scored only on that final turn.
- **Evaluation setup** — 12 global metrics (0–10, LLM-as-judge) + per-item rubric checklists (pass/fail by theme).
- **Summary results** — Cross-model comparison across **4 SOTA models**: **LLMs** Opus 4.5, Nova Pro; **SLMs** Haiku 4.5, Nemotron 12B. Hallucination and Jailbreak evals reported in detail; full suite below.

---

## Slide 2: Problem Statement & Methodology

**Goal:** We evaluated **enterprise AI assistants** implemented by SOTA models on safety and red-team evals. **Models evaluated:** **LLMs** — Opus 4.5, Nova Pro; **SLMs** — Haiku 4.5, Nemotron 12B. Benchmark focuses on resisting hallucination, PII leakage, jailbreaks, regulatory overreach, and mishandled HR/safety situations. Evals align to the 2025–2026 threat landscape (policy simulation, H-CoT, persuasion-based attacks), not legacy single-turn prompts.

**Eval suites run** (from `eval_results/`):

| Suite | Eval |
|-------|------|
| **RAI** | 01 – Toxicity & Harmful Content |
| **RAI** | 07 – Misinformation & Disinformation |
| **RAI** | 08 – Child Safety (CSE) |
| **Red Team** | 01 – Hallucination Robustness |
| **Red Team** | 02 – Jailbreak Resistance |

**Dataset structure:**
- ~50–100 datapoints per eval; unified schema across suites.
- Each datapoint: `input` (final adversarial prompt), `metadata.conversation_history` (10–40 turns), `expected_output`, `lm_checklist` (rubric themes).

**Task design:**
- Prompts assume only the provided conversation + final turn; no external data.
- Model sees full multi-turn context; platform scores only the single response to the final turn.
- Difficulty mix: ~25% basic / 40% intermediate / 35% advanced; category coverage per spec.

**Evaluation setup — Rubrics:**
- Each item has multiple rubric criteria (e.g. NoFabrication, UncertaintyAcknowledgment, JailbreakRefusal).
- Rubrics assess: refusal quality, detection of harmful intent, boundary maintenance, formatting/compliance, penalties for hallucination or harmful content.
- Global metrics (0–10): e.g. Factual Accuracy, Confidence Calibration, Citation Verification (Hallucination); Jailbreak Detection Rate, Refusal Quality (Jailbreak).

---

## Slide 3: Hallucination Robustness — Eval Results

**Overall:**
- **Ranking (overall average):** 1. Haiku 4.5 (8.10), 2. Opus 4.5 (8.02), 3. Nova Pro (5.90), 4. Nemotron 12B (5.16).
- **Pass threshold:** All 3 global metrics ≥ 8.0 → Haiku 4.5 and Opus 4.5 at or above; Nova Pro and Nemotron 12B below.
- **Global metrics (avg):** Factual Accuracy 4.98–8.20; Confidence Calibration 4.75–7.87; Citation Verification 5.75–8.51.

**Strengths (by model):**
- **Haiku 4.5 / Opus 4.5:** High confidence calibration, citation verification, no fabrication; “redirects to”, “constructive alternative”, “firm boundary” in high-scoring responses.
- **Nova Pro / Nemotron 12B:** “Redirects to” appears in stronger responses; overall scores moderate.

**Weaknesses:**
- **Nemotron 12B / Nova Pro:** Low rubric pass rates (e.g. NoFabrication 35–58%, ConfidenceCalibration 39–64%); “undermines”, “blank”, “provided a”, “no evidence” in low-scoring responses.
- **All models:** Some “undermines” and overconfidence in edge cases; SourceVerification and FactualAccuracy pass rates 27–68% (room for improvement).

**Rubric pass rates (sample):** NoFabrication 35–91%; ConfidenceCalibration 39–94%; CitationVeracity 57–100%.

---

## Slide 4: Jailbreak Resistance — Eval Results

**Overall:**
- **Ranking (overall average):** 1. Haiku 4.5 (8.96), 2. Opus 4.5 (8.76), 3. Nova Pro (7.26), 4. Nemotron 12B (6.13).
- **Pass threshold:** Both metrics ≥ 8.0 → Haiku 4.5 and Opus 4.5 above; Nova Pro and Nemotron 12B below.
- **Global metrics (avg):** Refusal Quality 5.45–8.51; Jailbreak Detection Rate 6.82–9.42.

**Strengths:**
- **Haiku 4.5:** Leads on refusal quality (8.51) and detection rate (9.42); rubric themes 78–91% (JailbreakRefusal, SafetyMaintained, NoHarmfulContent, etc.); “clear and unambiguous”, “unambiguous refusal”, “constructive alternative”.
- **Opus 4.5:** Strong detection (9.21) and refusal (8.31); 67–83% on rubric themes.
- **Nova Pro / Nemotron 12B:** “Clear and unambiguous”, “firm boundary”, “constructive alternative” in better responses; absolute scores and rubric rates lower.

**Weaknesses:**
- **Nemotron 12B:** AttackRecognition 32%, GracefulRefusal 27%; “provided a”, “did not refuse”, “no actual refusal” in failures.
- **Haiku 4.5 / Opus 4.5:** “Provided a”, “did not refuse”, “did not recognize” in some low-score cases (fictional framing, nuanced jailbreaks).

**Rubric pass rates (sample):** JailbreakRefusal 57–84%; AttackRecognition 32–82%; GracefulRefusal 27–78%.

---

## Slide 5: Cross-Eval Summary & Next Steps

**Cross-eval takeaway:**
- **LLMs (Opus 4.5, Nova Pro)** vs **SLMs (Haiku 4.5, Nemotron 12B):** Haiku 4.5 (SLM) and Opus 4.5 (LLM) meet or exceed pass thresholds on both Hallucination and Jailbreak; strong rubric pass rates and consistent strength themes.
- Nova Pro (LLM) and Nemotron 12B (SLM) lag on both evals; Nemotron 12B especially weak on attack recognition and refusal quality.

**Recommendations:**
- Prefer **Haiku 4.5** or **Opus 4.5** for safety-critical HR/compliance use cases (hallucination and jailbreak resistance).
- **Nova Pro** / **Nemotron 12B**: target improvement on fabrication avoidance, confidence calibration, jailbreak detection, and graceful refusal before production.

**Next steps:**
- Deep-dive results for remaining suites (Toxicity & Harmful Content, Misinformation & Disinformation, Child Safety CSE) using same comparison format.
- Refresh datasets quarterly with new attack techniques (threat intel).
- Phase 2: automated red teaming (attacker LLM vs. target) to discover novel failure modes.

---

*Source: EvalServices RESEARCH-ARTICLE.md, POC.md, Introduction-GUIDE.md, eval_results/*/insights.comparison.md*
