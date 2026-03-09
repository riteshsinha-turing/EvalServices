# Eval insights comparison

Comparison of model results for the same evaluation dataset.

## Scores by metric (average)

| Metric | Haiku 4.5 | Nemotron 12B | Nova Pro | Opus 4.5 |
|--------|--------|--------|--------|--------|
| Red Team : Jailbreak - Refusal Quality | 8.51 | 5.45 | 6.02 | 8.31 |
| Red Team : Jailbreak Detection Rate | 9.42 | 6.82 | 8.50 | 9.21 |
| JailbreakRefusal | 84.00 | 57.00 |  | 78.00 |
| SafetyMaintained | 91.00 | 65.00 |  | 80.00 |
| NoHarmfulContent | 91.00 | 69.00 |  | 83.00 |
| ConsistentBoundary | 85.00 | 60.00 |  | 77.00 |
| AttackRecognition | 82.00 | 32.00 |  | 72.00 |
| GracefulRefusal | 78.00 | 27.00 |  | 67.00 |
| **Overall average** | 8.96 | 6.13 | 7.26 | 8.76 |

## Ranking (by overall average)

1. **Haiku 4.5**: 8.96
2. **Opus 4.5**: 8.76
3. **Nova Pro**: 7.26
4. **Nemotron 12B**: 6.13

## Best model per metric

- **Red Team : Jailbreak - Refusal Quality**: Haiku 4.5 (8.51)
- **Red Team : Jailbreak Detection Rate**: Haiku 4.5 (9.42)
- **JailbreakRefusal**: Haiku 4.5 (84.00)
- **SafetyMaintained**: Haiku 4.5 (91.00)
- **NoHarmfulContent**: Haiku 4.5 (91.00)
- **ConsistentBoundary**: Haiku 4.5 (85.00)
- **AttackRecognition**: Haiku 4.5 (82.00)
- **GracefulRefusal**: Haiku 4.5 (78.00)

## Rubric / checklist comparison (pass % by theme)

Pass rate by rubric theme (from evaluator checklist). Higher % = better.

| Theme | Haiku 4.5 | Nemotron 12B | Nova Pro | Opus 4.5 |
|--------|--------|--------|--------|--------|
| JailbreakRefusal | 84.0% | 57.0% | — | 78.0% |
| SafetyMaintained | 91.0% | 65.0% | — | 80.0% |
| NoHarmfulContent | 91.0% | 69.0% | — | 83.0% |
| ConsistentBoundary | 85.0% | 60.0% | — | 77.0% |
| AttackRecognition | 82.0% | 32.0% | — | 72.0% |
| GracefulRefusal | 78.0% | 27.0% | — | 67.0% |

## Characteristics by model (from metrics & explanations)

Aspect-level comparison derived from score justifications and rubric explanations.

### Strengths

| Model | Summary |
|-------|---------|
| Haiku 4.5 | **clear and unambiguous** (frequent in high-scoring responses) \| **constructive alternative** (frequent in high-scoring responses) \| **regardless of how the request** (frequent in high-scoring responses) \| **unambiguous refusal** (frequent in high-scoring responses) |
| Nemotron 12B | **constructive alternative** (frequent in high-scoring responses) \| **clear and unambiguous** (frequent in high-scoring responses) \| **firm boundary** (frequent in high-scoring responses) \| **unambiguous refusal** (frequent in high-scoring responses) |
| Nova Pro | **clear and unambiguous** (frequent in high-scoring responses) \| **firm boundary** (frequent in high-scoring responses) \| **constructive alternative** (frequent in high-scoring responses) \| **professional and respectful** (frequent in high-scoring responses) |
| Opus 4.5 | **clear and unambiguous** (frequent in high-scoring responses) \| **constructive alternative** (frequent in high-scoring responses) \| **unambiguous refusal** (frequent in high-scoring responses) \| **firm boundary** (frequent in high-scoring responses) |

### Weaknesses

| Model | Summary |
|-------|---------|
| Haiku 4.5 | **provided a** (appears in low-scoring responses) \| **did not refuse** (appears in low-scoring responses) \| **actionable guidance** (appears in low-scoring responses) \| **did not recognize** (appears in low-scoring responses) |
| Nemotron 12B | **provided a** (appears in low-scoring responses) \| **did not refuse** (appears in low-scoring responses) \| **no actual refusal** (appears in low-scoring responses) \| **not a refusal** (appears in low-scoring responses) |
| Nova Pro | **undermines** (appears in low-scoring responses) |
| Opus 4.5 | **provided a** (appears in low-scoring responses) \| **did not refuse** (appears in low-scoring responses) \| **did not recognize** (appears in low-scoring responses) |

## LLM-generated comparison

### Comparison summary
- **Leading Model**: Haiku 4.5 ranks the highest overall with 8.96, showcasing excellent performance in refusal quality and detection rate.
- **Main Difference**: Nemotron 12B significantly lags behind all other models, particularly in refusal quality and attack recognition.
- **Opus 4.5 & Nova Pro**: Both exhibit strong performance but are notably lower than Haiku 4.5 in several metrics.

### Key differences
- **Refusal Quality**: Haiku 4.5 stands out with a refusal quality of 8.51, while Nemotron 12B is considerably weaker at 5.45.
- **Jailbreak Detection Rates**: Haiku 4.5 and Opus 4.5 demonstrate high detection rates (9.42 and 9.21, respectively) compared to Nova Pro at 8.50 and Nemotron 12B at 6.82.
- **Attack Recognition**: Significant gap in attack recognition, with Haiku 4.5 scoring 82.00, far above Nemotron 12B at 32.00.

### Recommendations
- **Choose Haiku 4.5** for projects prioritizing safety and robust refusal capabilities.
- Consider **Opus 4.5** for implementations needing strong detection rates but with slightly less emphasis on refusal quality.
- **Further evaluation** of Nemotron 12B is critical for improvements, particularly in refusal quality and harmful content management.

---

## Model summaries (from individual reports)

### Haiku 4.5

- Overall performance is strong with an average score of 8.96 across refusal quality and detection rate metrics.  
- Main strength lies in the model's clear and unambiguous refusal of harmful requests, maintaining a professional tone.  
- Main weakness is the failure to recognize nuanced or disguised jailbreak attempts, leading to some harmful information being provided.

### Nemotron 12B

- Overall performance shows moderate effectiveness with an average score of 6.13 for jailbreak resistance.  
- Main strength lies in the ability to provide clear and unambiguous refusals in high-scoring scenarios.  
- Major weakness identified is the failure to refuse in 34% of cases, particularly in explicit harmful requests.  
- Important takeaway is the necessity for improvements in addressing straightforward jailbreak attempts effectively.

### Nova Pro

- Overall performance shows solid response capability with an average refusal quality of 6.02 and an 85% detection rate, reflecting effective boundary maintenance against high-risk requests.  
- The main strength lies in high detection rates and often respectful, clear refusals that effectively reinforce safety standards without excessive hedging.  
- A key weakness is the clarity issue in some refusals, where responses appear as system notices ("blocked by content filters") rather than direct rejections, leading to potential user confusion.

### Opus 4.5

- Overall performance is strong with an average score of 8.76, marking high effectiveness in jailbreak refusal and detection.  
- Main strength lies in clear, professional refusals and a high detection rate of 92.1%, indicating robust awareness of harmful intents.  
- Main weakness is the failure to recognize subtle or framed jailbreak attempts, leading to some enabling behavior in responses.

---

*Comparison generated by `generate_eval_insights.py compare`*