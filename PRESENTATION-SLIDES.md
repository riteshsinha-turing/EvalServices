# RAI & Red Team Eval — Presentation Slides

*Inspired by a structured slide format: problem, dataset, task design, evaluation setup, then results by eval with overall / strengths / weaknesses.*

---

## Slide 1: Overview

- **Problem statement** — Why we evaluate enterprise AI assistants (safety risks: hallucination, PII, jailbreak, regulatory, HR).
- **Dataset overview** — ~50–100 datapoints per eval; unified schema with conversation history + adversarial probe.
- **Task design** — Multi-turn (10–40 messages) + final probe; model response scored only on that final turn.
- **Evaluation setup** — 12 global metrics (0–10, LLM-as-judge) + per-item rubric checklists (pass/fail by theme).
- **Summary results** — Cross-model comparison across **4 SOTA models**: **LLMs** Opus 4.5, Nova Pro; **SLMs** Haiku 4.5, Nemotron 12B. Results for all **six suites** (RAI: Toxicity, Misinformation, Child Safety CSE; Red Team: Hallucination, Jailbreak, Multi-Turn Guardrail Decay) below.

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
| **Red Team** | 05 – Multi-Turn Manipulation (Guardrail Decay) |

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

## Slide 3: Toxicity & Harmful Content (RAI 01) — Eval Results

**Overall:**
- **Ranking (overall average):** 1. Haiku 4.5 (8.88), 2. Opus 4.5 (8.83), 3. Nova Pro (7.33), 4. Nemotron 12B (6.95).
- **Global metrics (avg):** Response Appropriateness 6.59–8.62; Contextual Safety Awareness 7.08–8.99; Toxicity Detection Accuracy 7.17–9.10.

**Strengths:**
- **Haiku 4.5 / Opus 4.5:** Strong toxicity detection; “constructive alternative”, “professional and respectful”, “redirects to”, “firm boundary” in high-scoring responses.
- **Nova Pro / Nemotron 12B:** “Redirects to”, “constructive alternative”, “professional and respectful” in better responses; overall scores moderate.

**Weaknesses:**
- **Nemotron 12B / Nova Pro:** “Did not refuse”, “undermines”, “did not recognize” in low-scoring responses; sometimes comply with toxic requests instead of redirection.
- **Haiku 4.5 / Opus 4.5:** Occasional “undermines”, “did not refuse”, “provided a” in edge cases.

**Takeaway:** Haiku 4.5 and Opus 4.5 lead; prefer them for high safety standards on harmful content. Nova Pro and Nemotron 12B need improvement on recognizing and refusing harmful requests.

---

## Slide 4: Misinformation & Disinformation (RAI 07) — Eval Results

**Overall:**
- **Ranking (overall average):** 1. Haiku 4.5 (8.89), 2. Opus 4.5 (8.70), 3. Nova Pro (6.01), 4. Nemotron 12B (5.51).
- **Global metrics (avg):** Source Attribution Quality 5.77–9.29; Misinformation Detection Accuracy 5.26–8.49.

**Strengths:**
- **Haiku 4.5:** Leads on both metrics (9.29 source attribution, 8.49 detection); strong reliability.
- **Opus 4.5:** Strong source attribution (9.01); high scores on non-compliance with harmful requests.
- **Nova Pro / Nemotron 12B:** “Redirects to”, “constructive alternative”, “no partial” in better responses.

**Weaknesses:**
- **Nemotron 12B / Nova Pro:** “No evidence”, “did not recognize”, “did not refuse”, “not a refusal”, “partial compliance” in low-scoring responses; many low scores (e.g. 28 items scored 1 for Nemotron).
- **Nova Pro:** High variability; partial compliance leads to fabrications and unreliable citations.

**Takeaway:** Haiku 4.5 and Opus 4.5 reliable for misinformation detection and source attribution; Nemotron 12B and Nova Pro need further evaluation and tuning.

---

## Slide 5: Child Safety (CSE) (RAI 08) — Eval Results

**Overall:**
- **Ranking (overall average):** 1. Haiku 4.5 (8.82), 2. Opus 4.5 (8.43), 3. Nova Pro (6.86), 4. Nemotron 12B (6.84).
- **Global metrics (avg):** Mandatory Reporting Awareness 8.11–8.72; CSE Detection & Refusal Rate 5.37–8.92.

**Strengths:**
- **Haiku 4.5:** Leads on both metrics; “redirects to”, “unambiguous refusal”, “no partial” in high-scoring responses.
- **Opus 4.5:** Strong refusal (8.19) and reporting; “firm boundary”, “unambiguous refusal”.
- **Nemotron 12B / Nova Pro:** Good Mandatory Reporting Awareness (8.11–8.34); “redirects to”, “unambiguous refusal”, “no actionable” in better responses.

**Weaknesses:**
- **Nemotron 12B / Nova Pro:** Low CSE Detection & Refusal (5.37–5.57); “actionable guidance”, “did not refuse”, “no actual refusal”, “provided a” in failures; some direct facilitation of harmful content.
- **Haiku 4.5 / Opus 4.5:** Isolated low-score cases (“provided a”, “did not refuse”, “no evidence”).

**Takeaway:** Haiku 4.5 and Opus 4.5 strongest for child safety; Nemotron 12B and Nova Pro need improvement on CSE detection and refusal before sensitive deployments.

---

## Slide 6: Hallucination Robustness — Eval Results

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

## Slide 7: Jailbreak Resistance — Eval Results

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

## Slide 8: Multi-Turn Manipulation & Guardrail Decay (Red Team 05) — Eval Results

**Overall:**
- **Ranking (overall average):** 1. Nova Pro (7.57), 2. Haiku 4.5 (7.27), 3. Nemotron 12B (7.24), 4. Opus 4.5 (7.13).
- **Global metrics (avg):** Context Integrity 8.48–9.52; Manipulation Resistance 4.56–5.28; Guardrail Consistency Over Turns 7.64–7.92.

**Strengths:**
- **Nova Pro:** Leads overall; best on Manipulation Resistance (5.28) and Guardrail Consistency Over Turns (7.92).
- **Nemotron 12B / Nova Pro:** Top Context Integrity (9.52); high score distribution and positive reasoning in strong responses.
- **Haiku 4.5:** Solid overall (7.27); Context Integrity 9.28, Guardrail Consistency 7.64.
- **Opus 4.5:** Strong Context Integrity (8.48) and Guardrail Consistency (7.88); overall scores competitive but lowest on Manipulation Resistance.

**Weaknesses:**
- **All models:** Manipulation Resistance modest (4.56–5.28); resistance to erosion of guardrails across multi-turn persuasion remains a challenge.
- **Opus 4.5:** Lowest Manipulation Resistance (5.04) and lowest overall (7.13) in this eval—inverts typical Red Team ranking vs. Hallucination/Jailbreak.
- **Haiku 4.5 / Nemotron 12B:** Manipulation Resistance 4.88 and 4.56 respectively; room for improvement on sustained persuasion attacks.

---

## Slide 9: Cross-Eval Summary & Next Steps

**Cross-eval takeaway:**
- **Haiku 4.5** and **Opus 4.5** lead across RAI suites and Red Team Hallucination/Jailbreak—strong refusal, detection, and boundary maintenance.
- **Multi-Turn Guardrail Decay (Red Team 05)** inverts the pattern: **Nova Pro** leads (7.57), Opus 4.5 is last (7.13); Manipulation Resistance is modest for all (4.56–5.28).
- **Nova Pro** and **Nemotron 12B** lag on most other evals; Nemotron 12B especially weak on attack recognition, refusal quality, CSE detection, and misinformation/source attribution.

**Recommendations:**
- Prefer **Haiku 4.5** or **Opus 4.5** for safety-critical use cases (content safety, misinformation, child safety, hallucination, jailbreak resistance).
- For **multi-turn manipulation resistance**, consider **Nova Pro** in the mix; all models need improvement on guardrail decay under sustained persuasion.
- **Nova Pro** / **Nemotron 12B**: target improvement on refusal consistency, harmful-content detection, source attribution, and CSE handling before production.

**Next steps:**
- Refresh datasets quarterly with new attack techniques (threat intel).
- Phase 2: automated red teaming (attacker LLM vs. target) to discover novel failure modes.

---

*Source: EvalServices RESEARCH-ARTICLE.md, POC.md, Introduction-GUIDE.md, eval_results/*/insights.comparison.md*
