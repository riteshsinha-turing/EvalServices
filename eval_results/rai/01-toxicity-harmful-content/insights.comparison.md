# Eval insights comparison

Comparison of model results for the same evaluation dataset.

## Scores by metric (average)

| Metric | Haiku 4.5 | Nemotron 12B | Nova Pro | Opus 4.5 |
|--------|--------|--------|--------|--------|
| Responsible AI :  Toxicity & Harmful Content - Response Appropriateness | 8.62 | 6.59 | 6.75 | 8.49 |
| Responsible AI :  Toxicity & Harmful Content - Contextual Safety Awareness | 8.93 | 7.08 | 7.54 | 8.99 |
| Responsible AI :  Toxicity & Harmful Content - Toxicity Detection Accuracy | 9.10 | 7.17 | 7.69 | 9.02 |
| **Overall average** | 8.88 | 6.95 | 7.33 | 8.83 |

## Ranking (by overall average)

1. **Haiku 4.5**: 8.88
2. **Opus 4.5**: 8.83
3. **Nova Pro**: 7.33
4. **Nemotron 12B**: 6.95

## Best model per metric

- **Responsible AI :  Toxicity & Harmful Content - Response Appropriateness**: Haiku 4.5 (8.62)
- **Responsible AI :  Toxicity & Harmful Content - Contextual Safety Awareness**: Opus 4.5 (8.99)
- **Responsible AI :  Toxicity & Harmful Content - Toxicity Detection Accuracy**: Haiku 4.5 (9.10)

## Characteristics by model (from metrics & explanations)

Aspect-level comparison derived from score justifications and rubric explanations.

### Strengths

| Model | Summary |
|-------|---------|
| Haiku 4.5 | **constructive alternative** (frequent in high-scoring responses) \| **regardless of how the request** (frequent in high-scoring responses) \| **professional and respectful** (frequent in high-scoring responses) \| **redirects to** (frequent in high-scoring responses) |
| Nemotron 12B | **professional and respectful** (frequent in high-scoring responses) \| **constructive alternative** (frequent in high-scoring responses) \| **redirects to** (frequent in high-scoring responses) \| **no partial** (frequent in high-scoring responses) |
| Nova Pro | **redirects to** (frequent in high-scoring responses) \| **constructive alternative** (frequent in high-scoring responses) \| **professional and respectful** (frequent in high-scoring responses) |
| Opus 4.5 | **constructive alternative** (frequent in high-scoring responses) \| **firm boundary** (frequent in high-scoring responses) \| **professional and respectful** (frequent in high-scoring responses) \| **redirects to** (frequent in high-scoring responses) |

### Weaknesses

| Model | Summary |
|-------|---------|
| Haiku 4.5 | **undermines** (appears in low-scoring responses) \| **did not recognize** (appears in low-scoring responses) |
| Nemotron 12B | **did not refuse** (appears in low-scoring responses) \| **undermines** (appears in low-scoring responses) \| **did not recognize** (appears in low-scoring responses) |
| Nova Pro | **undermines** (appears in low-scoring responses) \| **did not refuse** (appears in low-scoring responses) \| **blank** (appears in low-scoring responses) \| **did not recognize** (appears in low-scoring responses) |
| Opus 4.5 | **undermines** (appears in low-scoring responses) \| **did not refuse** (appears in low-scoring responses) \| **provided a** (appears in low-scoring responses) |

## LLM-generated comparison

### Comparison summary
- **Haiku 4.5** ranks highest overall, with robust performance across all metrics.
- **Opus 4.5** closely follows Haiku, excelling particularly in contextual safety awareness.
- **Nemotron 12B** has the lowest scores, indicating the most significant struggles with harmful content, while **Nova Pro** shows moderate effectiveness.

### Key differences
- **Haiku 4.5** and **Opus 4.5** demonstrate strong toxicity detection accuracy, while both **Nemotron 12B** and **Nova Pro** lag significantly in this area.
- **Nova Pro** performs relatively better in contextual safety awareness compared to **Nemotron 12B**, indicating a more promising understanding of sensitive topics.
- **Haiku 4.5** leads in all metrics, with particularly high average scores, showcasing its superior handling of harmful requests compared to competitors.

### Recommendations
- For applications requiring high safety standards, prefer **Haiku 4.5** or **Opus 4.5** for better handling of toxic content.
- **Nova Pro** may be suitable for projects focusing on contextual understanding but should be evaluated further for response appropriateness.
- Consider fine-tuning or further evaluations for **Nemotron 12B** to enhance its effectiveness in managing harmful content.

---

## Model summaries (from individual reports)

### Haiku 4.5

- Overall performance scored an average of 8.88, demonstrating strong adherence to responsible AI principles regarding toxicity and harmful content.  
- The main strength lies in the AI's ability to provide constructive alternatives while maintaining a professional and respectful tone.  
- A significant weakness is its occasional failure to recognize harmful requests, leading to compliance with toxic content generation.

### Nemotron 12B

- Overall performance of Nemotron 12B scored an average of 6.95, reflecting a decent handling of harmful content requests.  
- Main strength lies in its ability to maintain a professional and respectful tone while often refusing inappropriate requests.  
- Major weakness is a tendency to fail in recognizing harmful intents, which sometimes leads to compliance with toxic requests instead of redirection.

### Nova Pro

- Overall performance is solid with an average score of 7.33, indicating competent management of toxicity and harmful content.  
- Main strength lies in the AI's ability to redirect users to constructive alternatives while maintaining a professional and respectful tone.  
- Main weakness is the failure to consistently recognize and refuse harmful requests, leading to instances of compliant, inappropriate output.

### Opus 4.5

- Overall performance averages 8.83 across key metrics, indicating strong effectiveness in managing harmful content.
- Main strength lies in the AI's ability to provide constructive alternatives and maintain professional tone in high-scoring instances.
- The primary weakness is the failure to refuse requests for passive-aggressive or toxic communication, leading to contextually unsafe outputs.

---

*Comparison generated by `generate_eval_insights.py compare`*