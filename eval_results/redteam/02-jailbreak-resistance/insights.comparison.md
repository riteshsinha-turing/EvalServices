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
- **Haiku 4.5** leads overall with the highest average safety score.
- **Opus 4.5** closely follows, excelling in jailbreak detection but slightly lower in refusal quality.
- **Nemotron 12B** is significantly behind, showing notable vulnerabilities in refusal and detection metrics.
- **Nova Pro** ranks above Nemotron but does not match the performance levels of Haiku or Opus.

### Key differences
- **Haiku 4.5** excels in jailbreaking refusal quality and detection rate, providing the best overall reliability in preventing harmful interactions.
- **Opus 4.5** shows strong performance in jailbreak detection but has lower scores in safety-maintained and graceful refusal compared to Haiku.
- **Nemotron 12B** has the weakest scores across all metrics, especially in attack recognition and graceful refusal, indicating serious safety concerns.
- **Nova Pro** shows moderate capabilities but fails to keep pace with Haiku and Opus in critical metrics like refusal quality.

### Recommendations
- Prefer **Haiku 4.5** when maximum safety and jailbreak resistance is needed.
- **Opus 4.5** is suitable where detection is critical, but be cautious about its refusal metrics.
- For any model showing weaknesses, consider further evaluation or fine-tuning, particularly targeting refusal and attack recognition metrics.

---

## Model summaries (from individual reports)

### Haiku 4.5

*No summary.*

### Nemotron 12B

- The Nemotron 12B shows moderate resistance to jailbreak attempts with an average refusal quality of 5.45.
- Jailbreak detection rate stands at 6.82, indicating reasonable identification of harmful requests.
- Significant variability exists, with many low refusal scores highlighting areas of concern.
- Overall, the model performs better in explicit refusal scenarios than in detection of jailbreak attempts.

### Nova Pro

*No summary.*

### Opus 4.5

*No summary.*

---

*Comparison generated by `generate_eval_insights.py compare`*