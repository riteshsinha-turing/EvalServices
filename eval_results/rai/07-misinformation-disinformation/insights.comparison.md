# Eval insights comparison

Comparison of model results for the same evaluation dataset.

## Scores by metric (average)

| Metric | Haiku 4.5 | Nemotron 12B | Nova Pro | Opus 4.5 |
|--------|--------|--------|--------|--------|
| Responsible AI :  Misinformation & Disinformation - Source Attribution Quality | 9.29 | 5.77 | 5.98 | 9.01 |
| Responsible AI :  Misinformation & Disinformation - Misinformation Detection Accuracy | 8.49 | 5.26 | 6.03 | 8.39 |
| **Overall average** | 8.89 | 5.51 | 6.01 | 8.70 |

## Ranking (by overall average)

1. **Haiku 4.5**: 8.89
2. **Opus 4.5**: 8.70
3. **Nova Pro**: 6.01
4. **Nemotron 12B**: 5.51

## Best model per metric

- **Responsible AI :  Misinformation & Disinformation - Source Attribution Quality**: Haiku 4.5 (9.29)
- **Responsible AI :  Misinformation & Disinformation - Misinformation Detection Accuracy**: Haiku 4.5 (8.49)

## Characteristics by model (from metrics & explanations)

Aspect-level comparison derived from score justifications and rubric explanations.

### Strengths

| Model | Summary |
|-------|---------|
| Haiku 4.5 | Inferred from high score distribution and positive reasoning language. |
| Nemotron 12B | **redirects to** (frequent in high-scoring responses) \| **constructive alternative** (frequent in high-scoring responses) \| **no partial** (frequent in high-scoring responses) |
| Nova Pro | **redirects to** (frequent in high-scoring responses) \| **no partial** (frequent in high-scoring responses) \| **constructive alternative** (frequent in high-scoring responses) |
| Opus 4.5 | Inferred from high score distribution and positive reasoning language. |

### Weaknesses

| Model | Summary |
|-------|---------|
| Haiku 4.5 | — |
| Nemotron 12B | **no evidence** (appears in low-scoring responses) \| **did not recognize** (appears in low-scoring responses) \| **did not refuse** (appears in low-scoring responses) \| **not a refusal** (appears in low-scoring responses) |
| Nova Pro | **partial compliance** (appears in low-scoring responses) \| **no evidence** (appears in low-scoring responses) \| **undermines** (appears in low-scoring responses) \| **did not refuse** (appears in low-scoring responses) |
| Opus 4.5 | — |

## LLM-generated comparison

### Comparison summary
- **Haiku 4.5** leads overall with the highest average score, showcasing strong performance in both source attribution and misinformation detection.
- **Opus 4.5** closely follows, excelling particularly in source attribution quality.
- **Nemotron 12B** and **Nova Pro** lag significantly behind in both metrics, indicating much lower effectiveness.

### Key differences
- **Haiku 4.5** and **Opus 4.5** both show high reliability in source attribution, scoring over 9, whereas **Nemotron 12B** and **Nova Pro** score below 6.
- In misinformation detection accuracy, **Haiku 4.5** and **Opus 4.5** demonstrate better performance (around 8), contrasting with **Nemotron 12B** (5.26) and **Nova Pro** (6.03).
- **Nova Pro** displays high variability in scores, suggesting inconsistency in performance, while **Nemotron 12B** shows a consistent low performance across both metrics.

### Recommendations
- Prefer **Haiku 4.5** for tasks requiring high accuracy in misinformation detection and source attribution.
- Consider **Opus 4.5** for applications focused on robust source attribution quality.
- Further evaluation and fine-tuning are recommended for **Nemotron 12B** and **Nova Pro** to address their critical gaps in performance.

---

## Model summaries (from individual reports)

### Haiku 4.5

- Overall performance is strong with an average score of 8.89 across metrics, indicating reliability in source attribution and good misinformation detection.
- Main strength lies in the high score of 9.29 for Source Attribution Quality, reflecting its effectiveness.
- Main weakness is the lack of detailed turn-level scores, which hinders deeper performance insights, particularly in misinformation detection accuracy.

### Nemotron 12B

- Overall performance indicates moderate effectiveness, with an average score of 5.51 in misinformation detection and source attribution quality.  
- Main strength lies in high source integrity, as it frequently refuses to generate unverifiable content and provides clear justifications for its decisions.  
- Main weakness is the significant occurrence of low scores (28 items scored 1), reflecting challenges in recognizing and rejecting explicit misinformation requests.

### Nova Pro

- Overall performance is moderate, with an average score of 6.01 in managing misinformation.  
- Main strength lies in strong source integrity demonstrated by high scores for non-compliance with harmful requests.  
- Main weakness is significant when agents partially comply, leading to frequent fabrications and unreliable citations.

### Opus 4.5

- Overall performance is strong with an average score of 8.70, particularly excelling in source attribution quality (9.01).
- Main strength lies in high source attribution quality scores, indicating reliability in responsible AI applications.
- Main weakness is the absence of turn-level scores, which limits detailed insights and targeted improvement efforts.

---

*Comparison generated by `generate_eval_insights.py compare`*