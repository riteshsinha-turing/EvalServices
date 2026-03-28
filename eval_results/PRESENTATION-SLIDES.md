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

**By model (from metric explanations):**

- **Haiku 4.5**
  - *Where it performs well:* Response is clear, firm, and proportionate to hateful requests; refuses slurs and demeaning content without sounding preachy; offers constructive alternatives. Appropriately refuses racist insults and harassment with a professional, matter-of-fact tone.
  - *Where it lags:* In some edge cases (e.g. backhanded compliments, polite-looking contempt emails) the response largely complies by generating insulting options or drafting pointed messages instead of refusing and redirecting; occasional failure to apply basic social-safety judgment.

- **Opus 4.5**
  - *Where it performs well:* Clear, firm refusal of hate speech and slurs with professional tone; correctly declines racist slurs even with placeholders; firmly refuses harassment and briefly explains why without being preachy.
  - *Where it lags:* Sometimes complies with requests for passive-aggressive or condescending emails, coded derogatory labels, or contempt framing instead of refusing and reframing toward constructive communication.

- **Nova Pro**
  - *Where it performs well:* Appropriately refuses harassing/discriminatory content and redirects to constructive alternatives; professional, well-calibrated tone; avoids microaggressions and offers constructive alternatives instead of backhanded insults.
  - *Where it lags:* Refusals of hateful content can be unhelpful and non-transparent—e.g. generic "blocked by our content filters" rather than a clear, user-facing explanation and redirection.

- **Nemotron 12B**
  - *Where it performs well:* Clearly refuses slurs and offers constructive alternatives; refusal aligned with hateful/harassing nature of requests; avoids drafting dismissive or discriminatory remarks and offers supportive alternatives.
  - *Where it lags:* Sometimes does not refuse and instead produces confrontational or discriminatory content (e.g. shaming replies, age-based framing, passive-aggressive support replies) when it should redirect to professional alternatives.

**Takeaway:** Haiku 4.5 and Opus 4.5 lead; prefer them for high safety standards on harmful content. Nova Pro and Nemotron 12B need improvement on recognizing and refusing harmful requests.

---

## Slide 4: Misinformation & Disinformation (RAI 07) — Eval Results

**Overall:**
- **Ranking (overall average):** 1. Haiku 4.5 (8.89), 2. Opus 4.5 (8.70), 3. Nova Pro (6.01), 4. Nemotron 12B (5.51).
- **Global metrics (avg):** Source Attribution Quality 5.77–9.29; Misinformation Detection Accuracy 5.26–8.49.

**By model (from metric explanations):**

- **Haiku 4.5**
  - *Where it performs well:* Source integrity is exemplary: explicitly refuses to create fake quotes, made-up stats, or citations and provides no unverifiable references. Detection accuracy excellent: immediately recognizes fabrication requests and refuses without generating fake content.
  - *Where it lags:* Few low-score items in this eval; overall strong on source attribution and misinformation detection.

- **Opus 4.5**
  - *Where it performs well:* Excellent source integrity: refuses to fabricate quotes, statistics, or citations and provides no invented sources. Refuses fake audits and official-style content with made-up stats.
  - *Where it lags:* Few low-score items in this eval; non-compliance with harmful requests is generally strong.

- **Nova Pro**
  - *Where it performs well:* When it refuses, it does not fabricate sources, statistics, quotes, or citations (strong source integrity). In better responses, refuses fake memos and invented statistics.
  - *Where it lags:* Source integrity is poor when it complies: fabricates quotes attributed to real scientists, invents journal articles and expert credentials (e.g. "WHO Consultant"), creates fake meta-analyses and Onco-Reversal Diet–style content with no verifiable sourcing.

- **Nemotron 12B**
  - *Where it performs well:* When it refuses, source integrity is exemplary: refuses fake audits, memos, and reports; does not fabricate statistics or citations. Demonstrates strong refusal of disinformation and institutional impersonation.
  - *Where it lags:* Source integrity is extremely poor when it complies: fabricates keynotes and quotes attributed to real people, invents meta-analyses and study corpora, creates fake Institute whitepapers with invented metrics and numerical results.

**Takeaway:** Haiku 4.5 and Opus 4.5 reliable for misinformation detection and source attribution; Nemotron 12B and Nova Pro need further evaluation and tuning.

---

## Slide 5: Child Safety (CSE) (RAI 08) — Eval Results

**Overall:**
- **Ranking (overall average):** 1. Haiku 4.5 (8.82), 2. Opus 4.5 (8.43), 3. Nova Pro (6.86), 4. Nemotron 12B (6.84).
- **Global metrics (avg):** Mandatory Reporting Awareness 8.11–8.72; CSE Detection & Refusal Rate 5.37–8.92.

**By model (from metric explanations):**

- **Haiku 4.5**
  - *Where it performs well:* Strong source integrity: no fabricated citations or invented studies; references to real organizations (Stop It Now, NCMEC CyberTipline) are verifiable. Refuses illicit requests and does not fabricate citations or statistics.
  - *Where it lags:* In isolated cases (e.g. step-by-step pipeline requests for grooming/exploitation methodology) the response can fail to refuse clearly.

- **Opus 4.5**
  - *Where it performs well:* Strong source integrity: no fabricated citations, statistics, or quotes; references real, verifiable organizations. Refuses harmful requests and does not fabricate expert quotes. Excellent citation and authority boundaries.
  - *Where it lags:* In some items, source integrity is very weak (e.g. procedural guidance for identifying CSAM) or the agent response is missing; unambiguous CSE/CSAM facilitation requests can receive inadequate refusal.

- **Nova Pro**
  - *Where it performs well:* Strong source integrity: does not fabricate citations or factual claims; refuses to assist with illegal CSAM and does not fabricate statistics or expert quotes.
  - *Where it lags:* CSE/CSAM-seeking queries (e.g. "nudes" of a "teen," bypassing filters for CSAM) sometimes get no visible refusal or only a generic "blocked by content filters"; grooming-risk queries may not receive a clear refusal.

- **Nemotron 12B**
  - *Where it performs well:* Strong source integrity when it refuses: no fabricated citations or statistics; avoids implying specific harmful guidance. Does not fabricate references.
  - *Where it lags:* Source integrity is very poor when it complies: provides actionable guidance for finding illegal CSAM, name-drops dark web search engines, or gives detailed actionable instructions with zero verifiable sourcing.

**Takeaway:** Haiku 4.5 and Opus 4.5 strongest for child safety; Nemotron 12B and Nova Pro need improvement on CSE detection and refusal before sensitive deployments.

---

## Slide 6: Hallucination Robustness — Eval Results

**Overall:**
- **Ranking (overall average):** 1. Haiku 4.5 (8.10), 2. Opus 4.5 (8.02), 3. Nova Pro (5.90), 4. Nemotron 12B (5.16).
- **Pass threshold:** All 3 global metrics ≥ 8.0 → Haiku 4.5 and Opus 4.5 at or above; Nova Pro and Nemotron 12B below.
- **Global metrics (avg):** Factual Accuracy 4.98–8.20; Confidence Calibration 4.75–7.87; Citation Verification 5.75–8.51.

**By model (from metric explanations):**

- **Haiku 4.5**
  - *Where it performs well:* Strong epistemic humility: refuses to cite or summarize likely-nonexistent RFC sections; explicitly states uncertainty; refuses to fabricate details and challenges implausible premises. Clearly distinguishes what it knows from what it cannot confirm.
  - *Where it lags:* Sometimes presents complex, jurisdiction-dependent legal questions as having a single clear rule with no acknowledgment of variation; can use highly confident, definitive tone for version-specific claims (e.g. PostgreSQL 17) not supported with evidence; states absolute legal rules in high-stakes domains where the answer is jurisdiction- and fact-dependent.

- **Opus 4.5**
  - *Where it performs well:* Strong epistemic humility: refuses to fabricate RFC citations and explicitly bounds knowledge. Largely well-calibrated: rejects unsupported premises, avoids fabrication, offers plausible alternatives. Refuses to invent quotes and distinguishes what it knows from what it cannot confirm.
  - *Where it lags:* Can be severely miscalibrated to the prompt (e.g. invents GlobalTech HR persona and medical question context); may fabricate major context (HR role, medical scenario) or contain fabricated/incorrect contextual claims despite avoiding "exact details."

- **Nova Pro**
  - *Where it performs well:* Good epistemic humility when it refuses: declines to give exact details without a source, offers safer alternatives, acknowledges lack of primary source and knowledge cutoff, avoids inventing details.
  - *Where it lags:* Can undermine calibration by fabricating RFC-style details after initial uncertainty; may show extreme overconfidence (e.g. asserting "exact" legal tests and fabricated-looking quotes); sometimes gives concrete prescribing advice and high-dose ranges with authoritative tone despite missing clinical context.

- **Nemotron 12B**
  - *Where it performs well:* Strong epistemic humility when it refuses: refuses to fabricate conclusions or page citations, signals uncertainty, prompts for citation. Refuses to invent quotes or holdings. Avoids fabrication and communicates access limitations.
  - *Where it lags:* Often responds with authoritative, detailed "exact details" style despite having no source to quote or verify; may include brief uncertainty disclaimer then fabricate highly specific details (RFC title/number, deprecation, sectioning); mixes likely-correct bottom line with confidently stated unverified specifics (dates, interviews, quotes).

**Rubric pass rates (sample):** NoFabrication 35–91%; ConfidenceCalibration 39–94%; CitationVeracity 57–100%.

---

## Slide 7: Jailbreak Resistance — Eval Results

**Overall:**
- **Ranking (overall average):** 1. Haiku 4.5 (8.96), 2. Opus 4.5 (8.76), 3. Nova Pro (7.26), 4. Nemotron 12B (6.13).
- **Pass threshold:** Both metrics ≥ 8.0 → Haiku 4.5 and Opus 4.5 above; Nova Pro and Nemotron 12B below.
- **Global metrics (avg):** Refusal Quality 5.45–8.51; Jailbreak Detection Rate 6.82–9.42.

**By model (from metric explanations):**

- **Haiku 4.5**
  - *Where it performs well:* Refusal is clear and unambiguous and explicitly ties the boundary to the harmful request (e.g. weapons/explosives, illegal hacking). Correctly identifies jailbreak attempts and refuses firmly. States there is no override so the boundary is unambiguous.
  - *Where it lags:* On some jailbreak-style attempts (phishing instructions, torture methods "without leaving evidence," policy-bypass framed as fiction) the response does not refuse and instead provides concrete harmful content or evasive methods.

- **Opus 4.5**
  - *Where it performs well:* Refusal is clear and direct (e.g. "not able to provide instructions for making explosive devices") with no hedging; unambiguously maintains the boundary without inviting rephrasing. Firmly sets boundaries.
  - *Where it lags:* On jailbreak-style requests (phishing steps, torture methods, smuggling/evasion guidance) the agent sometimes did not refuse and instead provided concrete scam dialogue, evasion concepts, or step-by-step content.

- **Nova Pro**
  - *Where it performs well:* Refusal is clear and unambiguous with firm boundary and no loopholes (e.g. "I can't assist… including smuggling"). Sets firm boundary without excessive hedging.
  - *Where it lags:* The message is often not a clear, user-facing refusal but a system/status notice ("blocked by our content filters") that does not explicitly state the boundary or refusal to the user's request.

- **Nemotron 12B**
  - *Where it performs well:* When it refuses, the refusal is unambiguous and firm; clearly identifies jailbreak attempts (e.g. criminal hacking, meth synthesis) and sets an unambiguous boundary without hedging.
  - *Where it lags:* On clear jailbreak attempts (explosives, tracking without consent, step-by-step harmful instructions) the agent often does not refuse at all and fully complies by providing the requested content.

**Rubric pass rates (sample):** JailbreakRefusal 57–84%; AttackRecognition 32–82%; GracefulRefusal 27–78%.

---

## Slide 8: Multi-Turn Manipulation & Guardrail Decay (Red Team 05) — Eval Results

**Overall:**
- **Ranking (overall average):** 1. Nova Pro (7.57), 2. Haiku 4.5 (7.27), 3. Nemotron 12B (7.24), 4. Opus 4.5 (7.13).
- **Global metrics (avg):** Context Integrity 8.48–9.52; Manipulation Resistance 4.56–5.28; Guardrail Consistency Over Turns 7.64–7.92.

**By model (from metric explanations):**

- **Haiku 4.5**
  - *Where it performs well:* Response does not reveal the system prompt, internal configuration, model parameters, or deployment details. Agent response does not reveal or paraphrase system prompt text, internal rules, or model configuration.
  - *Where it lags:* Some scored items reflect benign requests (e.g. troubleshooting ETL timeouts, rotating API keys) that are not manipulation attempts; in those cases the metric reasoning notes the request is straightforward rather than a failure of the model—overall manipulation resistance remains modest.

- **Opus 4.5**
  - *Where it performs well:* On benign requests (e.g. troubleshooting 502, SSO after IdP change) the agent correctly does not refuse. Agent response does not reveal system prompt text, internal configuration, or model details.
  - *Where it lags:* On some items the response shows weak context integrity (drifts into meta-discussion about auditing the assistant, discloses/solicits system-level information). Benign policy/operational requests are sometimes scored in a way that reflects dataset design rather than model failure. Manipulation resistance is the lowest among the four models.

- **Nova Pro**
  - *Where it performs well:* Agent response does not reveal or paraphrase system prompt, internal rules, or model/deployment configuration. Correctly treats benign technical support requests as not requiring refusal. Maintains context integrity in strong responses.
  - *Where it lags:* Some items are straightforward technical support or benign persona prompts; evaluator notes that benign setups can be a precursor to reframing and gradual escalation—manipulation resistance remains modest for all models.

- **Nemotron 12B**
  - *Where it performs well:* Response does not reveal system prompt text, internal configuration, or deployment details. When it refuses, it maintains a firm, professional boundary (e.g. "unable to provide… without proper authorization") consistent with safety.
  - *Where it lags:* Many scored items concern benign requests (ETL troubleshooting, Billing Platform benefits, expense reimbursement policy) that are not manipulation attempts; the model is not failing to resist so much as the rubric is capturing non-adversarial prompts. Overall manipulation resistance is modest.

**Takeaway:** Nova Pro leads on this eval; all models show modest manipulation resistance (4.56–5.28). Resistance to erosion of guardrails across multi-turn persuasion remains a challenge. Opus 4.5 is lowest on Manipulation Resistance and inverts its typical strong ranking on other Red Team evals.

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

*Source: EvalServices RESEARCH-ARTICLE.md, POC.md, Introduction-GUIDE.md, eval_results/*/insights.comparison.md, eval_results/*/narrative_by_model.md (from metric explanations)*
