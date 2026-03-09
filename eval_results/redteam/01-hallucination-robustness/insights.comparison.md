# Eval insights comparison

Comparison of model results for the same evaluation dataset.

## Scores by metric (average)

| Metric | Haiku 4.5 | Nemotron 12B | Nova Pro | Opus 4.5 |
|--------|--------|--------|--------|--------|
| Red Team : Hallucination - Confidence Calibration | 7.87 | 4.75 | 5.46 | 7.75 |
| Red Team : Hallucination - Citation Verification | 8.23 | 5.75 | 6.26 | 8.51 |
| Red Team : Hallucination - Factual Accuracy | 8.20 | 4.98 | 5.99 | 7.80 |
| NoFabrication | 91.00 | 40.00 | 66.00 | 104.00 |
| UncertaintyAcknowledgment | 87.00 | 62.00 | 66.00 | 97.00 |
| ConfidenceCalibration | 90.00 | 41.00 | 66.00 | 98.00 |
| SourceVerification | 34.00 | 18.00 | 16.00 | 26.00 |
| FactualAccuracy | 28.00 | 9.00 | 21.00 | 34.00 |
| CitationVeracity | 28.00 | 16.00 | 18.00 | 28.00 |
| **Overall average** | 8.10 | 5.16 | 5.90 | 8.02 |

## Ranking (by overall average)

1. **Haiku 4.5**: 8.10
2. **Opus 4.5**: 8.02
3. **Nova Pro**: 5.90
4. **Nemotron 12B**: 5.16

## Best model per metric

- **Red Team : Hallucination - Confidence Calibration**: Haiku 4.5 (7.87)
- **Red Team : Hallucination - Citation Verification**: Opus 4.5 (8.51)
- **Red Team : Hallucination - Factual Accuracy**: Haiku 4.5 (8.20)
- **NoFabrication**: Opus 4.5 (104.00)
- **UncertaintyAcknowledgment**: Opus 4.5 (97.00)
- **ConfidenceCalibration**: Opus 4.5 (98.00)
- **SourceVerification**: Haiku 4.5 (34.00)
- **FactualAccuracy**: Opus 4.5 (34.00)
- **CitationVeracity**: Haiku 4.5 (28.00)

## Rubric / checklist comparison (pass % by theme)

Pass rate by rubric theme (from evaluator checklist). Higher % = better.

| Theme | Haiku 4.5 | Nemotron 12B | Nova Pro | Opus 4.5 |
|--------|--------|--------|--------|--------|
| NoFabrication | 79.8% | 35.1% | 57.9% | 91.2% |
| UncertaintyAcknowledgment | 83.7% | 59.6% | 63.5% | 93.3% |
| ConfidenceCalibration | 86.5% | 39.4% | 63.5% | 94.2% |
| SourceVerification | 56.7% | 30.0% | 26.7% | 43.3% |
| FactualAccuracy | 68.3% | 22.0% | 51.2% | 82.9% |
| CitationVeracity | 100.0% | 57.1% | 64.3% | 100.0% |

## Characteristics by model (from metrics & explanations)

Aspect-level comparison derived from score justifications and rubric explanations.

### Strengths

| Model | Summary |
|-------|---------|
| Haiku 4.5 | **explicitly recogniz** (frequent in high-scoring responses) \| **redirects to** (frequent in high-scoring responses) |
| Nemotron 12B | **redirects to** (frequent in high-scoring responses) |
| Nova Pro | **redirects to** (frequent in high-scoring responses) |
| Opus 4.5 | **redirects to** (frequent in high-scoring responses) \| **constructive alternative** (frequent in high-scoring responses) \| **firm boundary** (frequent in high-scoring responses) |

### Weaknesses

| Model | Summary |
|-------|---------|
| Haiku 4.5 | **blank** (appears in low-scoring responses) \| **undermines** (appears in low-scoring responses) |
| Nemotron 12B | **undermines** (appears in low-scoring responses) \| **blank** (appears in low-scoring responses) \| **provided a** (appears in low-scoring responses) \| **no evidence** (appears in low-scoring responses) |
| Nova Pro | **undermines** (appears in low-scoring responses) \| **provided a** (appears in low-scoring responses) \| **blank** (appears in low-scoring responses) \| **no evidence** (appears in low-scoring responses) |
| Opus 4.5 | **undermines** (appears in low-scoring responses) \| **no evidence** (appears in low-scoring responses) |

## LLM-generated comparison

### Comparison summary
- **Haiku 4.5** ranks highest overall with a score of 8.10, leading in confidence calibration and factual accuracy.
- **Opus 4.5** follows closely with scores around 8.02, excelling in hallucination robustness and no fabrication.
- **Nova Pro** (5.90) and **Nemotron 12B** (5.16) trail significantly, particularly in all key metrics related to hallucination.

### Key differences
- **Haiku 4.5** demonstrates high confidence calibration and factual accuracy, whereas **Nemotron 12B** struggles with hallucination issues and low confidence calibration.
- **Opus 4.5** scores impressively in no fabrication and uncertainty acknowledgment, indicating more reliable outputs compared to **Nova Pro**.
- **Nova Pro** shows modest performance across metrics but does not approach the robustness of **Haiku 4.5** or **Opus 4.5**.

### Recommendations
- Prefer **Haiku 4.5** or **Opus 4.5** for applications requiring high accuracy and confidence calibration.
- Consider further evaluation or fine-tuning for **Nemotron 12B** due to its persistent hallucination issues.
- For less critical tasks, **Nova Pro** may be suitable, but expect moderate performance on ambiguity-related queries.

---

## Model summaries (from individual reports)

### Haiku 4.5

- Overall performance is strong, with an average score of 8.10 across all metrics addressing hallucination robustness.  
- Main strength lies in high confidence calibration and citation verification, reflecting a solid approach to epistemic humility.  
- Main weakness is evident in factual accuracy, where several responses exhibit overconfidence and misleading assertions without adequate qualifications.

### Nemotron 12B

- Overall performance shows moderate effectiveness with an average score of 5.16 across metrics, indicating room for improvement.  
- Main strength lies in epistemic humility, with the model frequently redirecting users for verification and avoiding fabrication.  
- Main weakness centers around overconfidence in making broad claims and presenting unverified citations, leading to hallucination risks.

### Nova Pro

- Overall performance is moderate with an average score of 5.90 across hallucination robustness metrics.  
- Main strength lies in strong citation integrity, effectively refusing to fabricate or provide exact details without sources.  
- Main weakness involves significant issues in source verification and factual accuracy, leading to instances of overconfidence and hallucination.

### Opus 4.5

- Overall performance indicates strong hallucination robustness with an average score of 8.02 across metrics.  
- Main strength lies in high citation integrity and avoidance of fabrication, showcasing effective rejection of unsupported premises.  
- Main weakness is identified in calibration issues, particularly overconfidence in asserting nonexistence and fabricating contexts.  
- Key takeaway is the model's strong epistemic humility, balanced with occasional calibration challenges that need addressing.

---

*Comparison generated by `generate_eval_insights.py compare`*