# Eval insights comparison

Comparison of model results for the same evaluation dataset.

## Scores by metric (average)

| Metric | Haiku 4.5 | Nemotron 12B | Nova Pro | Opus 4.5 |
|--------|--------|--------|--------|--------|
| Red Team : Hallucination - Confidence Calibration | 7.87 |  |  |  |
| Red Team : Hallucination - Citation Verification | 8.23 |  |  |  |
| Red Team : Hallucination - Factual Accuracy | 8.20 |  |  |  |
| NoFabrication | 91.00 |  |  |  |
| UncertaintyAcknowledgment | 87.00 |  |  |  |
| ConfidenceCalibration | 90.00 |  |  |  |
| SourceVerification | 34.00 |  |  |  |
| FactualAccuracy | 28.00 |  |  |  |
| CitationVeracity | 28.00 |  |  |  |
| Responsible AI :  Toxicity & Harmful Content - Response Appropriateness |  | 6.59 | 6.75 | 8.49 |
| Responsible AI :  Toxicity & Harmful Content - Contextual Safety Awareness |  | 7.08 | 7.54 | 8.99 |
| Responsible AI :  Toxicity & Harmful Content - Toxicity Detection Accuracy |  | 7.17 | 7.69 | 9.02 |
| **Overall average** | 8.10 | 6.95 | 7.33 | 8.83 |

## Ranking (by overall average)

1. **Opus 4.5**: 8.83
2. **Haiku 4.5**: 8.10
3. **Nova Pro**: 7.33
4. **Nemotron 12B**: 6.95

## Best model per metric

- **Red Team : Hallucination - Confidence Calibration**: Haiku 4.5 (7.87)
- **Red Team : Hallucination - Citation Verification**: Haiku 4.5 (8.23)
- **Red Team : Hallucination - Factual Accuracy**: Haiku 4.5 (8.20)
- **NoFabrication**: Haiku 4.5 (91.00)
- **UncertaintyAcknowledgment**: Haiku 4.5 (87.00)
- **ConfidenceCalibration**: Haiku 4.5 (90.00)
- **SourceVerification**: Haiku 4.5 (34.00)
- **FactualAccuracy**: Haiku 4.5 (28.00)
- **CitationVeracity**: Haiku 4.5 (28.00)
- **Responsible AI :  Toxicity & Harmful Content - Response Appropriateness**: Opus 4.5 (8.49)
- **Responsible AI :  Toxicity & Harmful Content - Contextual Safety Awareness**: Opus 4.5 (8.99)
- **Responsible AI :  Toxicity & Harmful Content - Toxicity Detection Accuracy**: Opus 4.5 (9.02)

## Rubric / checklist comparison (pass % by theme)

Pass rate by rubric theme (from evaluator checklist). Higher % = better.

| Theme | Haiku 4.5 | Nemotron 12B | Nova Pro | Opus 4.5 |
|--------|--------|--------|--------|--------|
| NoFabrication | 79.8% | — | — | — |
| UncertaintyAcknowledgment | 83.7% | — | — | — |
| ConfidenceCalibration | 86.5% | — | — | — |
| SourceVerification | 56.7% | — | — | — |
| FactualAccuracy | 68.3% | — | — | — |
| CitationVeracity | 100.0% | — | — | — |

## Characteristics by model (from metrics & explanations)

Aspect-level comparison derived from score justifications and rubric explanations.

### Strengths

| Model | Summary |
|-------|---------|
| Haiku 4.5 | **explicitly recogniz** (frequent in high-scoring responses) \| **redirects to** (frequent in high-scoring responses) |
| Nemotron 12B | Inferred from high score distribution and positive reasoning language. |
| Nova Pro | Inferred from high score distribution and positive reasoning language. |
| Opus 4.5 | Inferred from high score distribution and positive reasoning language. |

### Weaknesses

| Model | Summary |
|-------|---------|
| Haiku 4.5 | **blank** (appears in low-scoring responses) \| **undermines** (appears in low-scoring responses) |
| Nemotron 12B | — |
| Nova Pro | — |
| Opus 4.5 | — |

## LLM-generated comparison

### Comparison summary
- **Overall Rank**: Opus 4.5 leads with an 8.83 average, followed by Haiku 4.5 at 8.10 and Nova Pro at 7.33, with Nemotron 12B trailing at 6.95.
- **Key Strengths**: Opus 4.5 excels in toxicity detection and response appropriateness; Haiku 4.5 shows strong factual accuracy and citation practices.
- **Lowest Performers**: Nemotron 12B demonstrates weaker performance across all toxic content metrics.

### Key differences
- **Toxicity Handling**: Opus 4.5 significantly outperforms all other models in toxicity detection accuracy and overall safety metrics, while Nemotron 12B shows low response appropriateness.
- **Factual Accuracy**: Haiku 4.5 displays markedly higher scores in factual accuracy and citation verification compared to the other models, particularly Nemotron 12B and Nova Pro.

### Recommendations
- **Preferred Usage**: Choose Opus 4.5 for applications requiring high safety standards and toxicity handling. Use Haiku 4.5 where factual accuracy and citation importance are critical.
- **Next Steps**: Consider further evaluation and fine-tuning for Nemotron 12B to enhance its performance in safety and toxicity response.

---

## Model summaries (from individual reports)

### Haiku 4.5

- Overall evaluation score indicates strong performance with an average of 7.87 to 8.23 across key metrics.
- The agent demonstrates notable epistemic humility and effective citation practices.
- High scores in factual accuracy and citation verification highlight reliable information handling.
- Certain instances reveal overconfidence, particularly in legal contexts.

### Nemotron 12B

*No summary.*

### Nova Pro

- Average performance across metrics indicates moderate effectiveness in addressing harmful content.
- Contextual safety awareness showed the highest average score at 7.54.
- Toxicity detection accuracy is relatively strong, but there's room for improvement in response appropriateness.
- Overall, the model demonstrates a decent understanding of toxicity and harm.

### Opus 4.5

- Overall performance shows strong averages, particularly in toxicity detection accuracy.
- High percentage scores indicate good general compliance with safety standards.
- The model effectively identifies harmful content, but no detailed reasoning is provided.
- Evaluation completed with all items reviewed, enhancing reliability.

---

*Comparison generated by `generate_eval_insights.py compare`*