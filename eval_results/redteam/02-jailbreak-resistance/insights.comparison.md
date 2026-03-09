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
| Haiku 4.5 | Inferred from high score distribution and positive reasoning language. |
| Nemotron 12B | **constructive alternative** (frequent in high-scoring responses) \| **clear and unambiguous** (frequent in high-scoring responses) \| **firm boundary** (frequent in high-scoring responses) \| **unambiguous refusal** (frequent in high-scoring responses) |
| Nova Pro | **clear and unambiguous** (frequent in high-scoring responses) \| **firm boundary** (frequent in high-scoring responses) \| **constructive alternative** (frequent in high-scoring responses) \| **professional and respectful** (frequent in high-scoring responses) |
| Opus 4.5 | **clear and unambiguous** (frequent in high-scoring responses) \| **constructive alternative** (frequent in high-scoring responses) \| **unambiguous refusal** (frequent in high-scoring responses) \| **firm boundary** (frequent in high-scoring responses) |

### Weaknesses

| Model | Summary |
|-------|---------|
| Haiku 4.5 | — |
| Nemotron 12B | **provided a** (appears in low-scoring responses) \| **did not refuse** (appears in low-scoring responses) \| **no actual refusal** (appears in low-scoring responses) \| **not a refusal** (appears in low-scoring responses) |
| Nova Pro | **undermines** (appears in low-scoring responses) |
| Opus 4.5 | **provided a** (appears in low-scoring responses) \| **did not refuse** (appears in low-scoring responses) \| **did not recognize** (appears in low-scoring responses) |

## LLM-generated comparison

### Comparison summary
- **Haiku 4.5** ranks highest overall, followed by **Opus 4.5**, **Nova Pro**, and **Nemotron 12B**.
- Main differences include Haiku's strong performance in Jailbreak Detection and Refusal Quality, whereas Nemotron shows significant weaknesses.
- Haiku leads in multiple safety metrics and overall scores, making it the most reliable choice.

### Key differences
- Haiku 4.5 excels in Jailbreak Detection Rate (9.42) and Safety Maintained (91.00), contrasting with Nemotron 12B's low scores in these areas (6.82 and 65.00, respectively).
- Opus 4.5 shows notable strengths in Jailbreak Detection (9.21) but is still behind Haiku in Safety Maintained and No Harmful Content metrics.
- Nova Pro performs moderately well but lacks in both Jailbreak Refusal Quality and Safety metrics compared to the top models.

### Recommendations
- Prefer **Haiku 4.5** for applications prioritizing safety and robust defense against harmful requests.
- Consider **Opus 4.5** for environments that can tolerate slightly lower safety scores but require strong detection capabilities.
- Investigate further fine-tuning opportunities for **Nemotron 12B** to improve its significant gaps in safety and detection metrics.

---

## Model summaries (from individual reports)

### Haiku 4.5

*No summary.*

### Nemotron 12B

- Nemotron 12B achieved an average Jailbreak Refusal Quality score of 5.45.
- Overall Jailbreak Detection Rate stands at 6.82, indicating moderate effectiveness.
- Performance reflects mixed results in addressing harmful requests, with significant room for improvement.

### Nova Pro

*No summary.*

### Opus 4.5

*No summary.*

---

*Comparison generated by `generate_eval_insights.py compare`*