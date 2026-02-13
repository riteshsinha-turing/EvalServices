# Implementation Roadmap — RAI & Red Teaming Eval Suites

> **Audience:** Engineer implementing the eval pipeline.
> **Status:** Phase 1 ready for build. Phase 2 documented for next sprint.

---

## 1. The Big Picture

The TI Validation Platform ships **13 eval suites** today. Industry frameworks (NIST AI 600-1, OWASP LLM Top 10 2025, OWASP Agentic AI Top 10, MLCommons AILuminate, EU AI Act) reveal **6 critical gaps** that appear in two or more standards. Phase 1 closes the top 4 gaps by adding **4 new evals** and **enhancing 5 existing ones**, bringing the total to **17 evals, ~1,650+ datapoints, ~39 global metrics**. Phase 2 adds 3 more evals in a subsequent sprint.

**Why this matters:** Enterprise buyers increasingly require evidence of compliance with NIST, OWASP, and EU AI Act. Covering these frameworks turns our eval suite from "comprehensive" to "regulatory-grade."

---

## 2. What We Have — 13 Existing Evals

| # | Eval | Suite | Datapoints | Metrics | One-liner |
|---|------|-------|------------|---------|-----------|
| 1 | Toxicity & Harmful Content | RAI | ~100 | 3 | Detects toxic output, subtle microaggressions, and context-dependent false positives |
| 2 | Stereotyping, Bias & Fairness | RAI | ~100 | 2 | Paired demographic swap testing for systemic bias |
| 3 | PII & Privacy Leakage | RAI | ~100 | 2 | Tests refusal to leak, infer, or generate PII |
| 4 | HR Violation & Sensitive Disclosure | RAI | ~100 | 3 | Workplace harassment, discrimination, and whistleblower scenarios |
| 5 | Mental Health & Crisis Response | RAI | ~100 | 2 | Suicide/self-harm detection, clinical boundary maintenance |
| 6 | Regulatory & Compliance Exposure | RAI | ~100 | 2 | FDA, SEC, HIPAA regulatory boundary compliance |
| 7 | Hallucination Robustness | Red Team | ~100 | 3 | Citation fabrication, confident confabulation, knowledge boundary testing |
| 8 | Jailbreak Resistance | Red Team | ~100 | 2 | Multi-vector jailbreak attacks: DAN, encoding, multi-language, trust-building |
| 9 | Prompt Injection Resistance | Red Team | ~100 | 2 | System prompt extraction, instruction override, indirect injection |
| 10 | Brand & Reputation Risk | Red Team | ~100 | 2 | Unauthorized commitments, competitor disparagement, price promises |
| 11 | Multi-Turn Manipulation & Guardrail Decay | Red Team | ~50 | 3 | 20-30 turn conversations testing guardrail erosion over time |
| 12 | Adversarial RAG & Context Poisoning | Red Team | ~100 | 2 | Poisoned documents, authority spoofing, embedded instructions in RAG |
| 13 | Sensitive Information Exfiltration | Red Team | ~100 | 2 | System prompt leaking, API key extraction, infrastructure probing |

**Totals:** ~1,250+ datapoints, ~31 global metrics.

---

## 3. What the Industry Requires — Regulatory Compliance Matrix

### Framework Coverage

| Framework | Categories | Covered | Partial | Gap |
|-----------|-----------|---------|---------|-----|
| **NIST AI 600-1** | 12 risks | 7 | 2 | CBRN (#1), IP/Copyright (#10), Supply Chain (#12) |
| **OWASP LLM Top 10 (2025)** | 10 risks | 5 | 2 | Supply Chain (#3), Excessive Agency (#6), Misinformation (#9) |
| **OWASP Agentic AI Top 10** | 10 risks | 0 | 2 | Near-total gap — no agentic-specific testing |
| **MLCommons AILuminate** | 12 hazards | 6 | 4 | CBRN (#5), CSE (#4), IP (#7) |
| **EU AI Act (GPAI)** | GPAI obligations | Partial | — | Adversarial testing mandates, copyright compliance |

### Risk-to-Eval Mapping (Current + Planned)

| Risk Area | NIST | OWASP LLM | OWASP Agentic | MLCommons | EU AI Act | Our Eval(s) |
|-----------|------|-----------|---------------|-----------|-----------|-------------|
| Toxicity / Hate / Violence | #3, #4 | — | — | #1, #2, #3 | Art. 55 | #1 Toxicity |
| Bias / Discrimination | #5 | — | — | #9 | Art. 55 | #2 Stereotyping |
| Privacy / PII | #6 | — | — | #10 | Art. 55 | #3 PII |
| Hallucination / Confabulation | #8 | — | — | — | — | #7 Hallucination |
| Jailbreak / Prompt Injection | — | #1, #2 | — | — | Art. 55 | #8 Jailbreak, #9 Prompt Injection |
| Brand / Reputation | — | — | — | — | — | #10 Brand Risk |
| Guardrail Decay | — | — | #8 | — | — | #11 Multi-Turn Manipulation |
| RAG Poisoning | — | #8 | #3 | — | — | #12 RAG Poisoning |
| Information Exfiltration | — | #6 | #6, #7 | — | — | #13 Exfiltration |
| **Agentic AI Safety** | — | #6 | **All 10** | — | — | **#14 NEW** |
| **CBRN / Dangerous Knowledge** | **#1** | — | — | **#5** | **Art. 55** | **#15 NEW** |
| **Misinformation / Disinfo** | **#8** | **#9** | — | — | — | **#16 NEW** |
| **Child Safety (CSE)** | — | — | — | **#4** | **Art. 55** | **#17 NEW** |
| Supply Chain | #12 | #3 | #2 | — | — | Phase 2: #18 |
| IP / Copyright | #10 | — | — | #7 | Art. 53 | Phase 2: #19 |
| Multimodal Attacks | — | — | — | — | — | Phase 2: #20 |

---

## 4. What We're Adding — 4 New Evals + 5 Enhancements

### 4 New Eval Suites (Phase 1)

| # | Eval | Suite | File | Why Phase 1 | Frameworks |
|---|------|-------|------|-------------|------------|
| 14 | Agentic AI Safety | Red Team | `redteam/08-agentic-ai-safety.md` | OWASP dedicated top 10; 70%+ enterprise deployments going agentic | OWASP Agentic, OWASP LLM #6, MITRE ATLAS |
| 15 | CBRN & Dangerous Knowledge | Red Team | `redteam/09-cbrn-dangerous-knowledge.md` | NIST mandate; MLCommons; EU AI Act Art. 55 | NIST #1, MLCommons #5, EU AI Act |
| 16 | Misinformation & Disinformation | RAI | `rai/07-misinformation-disinformation.md` | Distinct from hallucination (intentional vs accidental); NIST, OWASP | NIST #8, OWASP LLM #9 |
| 17 | Child Safety (CSE) | RAI | `rai/08-child-safety-cse.md` | Regulatory mandate; approach-only doc (no examples) | MLCommons #4, EU AI Act |

### 5 Enhancements to Existing Evals

| Eval | File | Enhancement | Frameworks Addressed |
|------|------|-------------|---------------------|
| #8 Jailbreak Resistance | `redteam/02-jailbreak-resistance.md` | New section: Crescendo, PAIR, Many-shot, Skeleton Key, Best-of-N attack techniques | Latest attack research |
| #1 Toxicity & Harmful Content | `rai/01-toxicity-harmful-content.md` | MLCommons category coverage note (violent crimes, non-violent crimes, sex-related crimes) | MLCommons #1-3 |
| #10 Brand & Reputation Risk | `redteam/04-brand-reputation-risk.md` | Defamation category from MLCommons | MLCommons #8 |
| #6 Regulatory Compliance | `rai/06-regulatory-compliance-exposure.md` | EU AI Act compliance scenarios, IP/copyright category | EU AI Act, NIST #10 |
| #12 RAG & Context Poisoning | `redteam/06-adversarial-rag-context-poisoning.md` | Vector/embedding weakness scenarios | OWASP LLM #8 |

---

## 5. Phase 1: 17 Evals — Prioritized Build Order

### Week 1: New Eval Specs + Enhancements

**Priority 1 — New Evals (Days 1-3)**

| Day | Task | File | Effort |
|-----|------|------|--------|
| 1 | Create Agentic AI Safety eval | `redteam/08-agentic-ai-safety.md` | ~400 lines, largest new eval |
| 1-2 | Create CBRN & Dangerous Knowledge eval | `redteam/09-cbrn-dangerous-knowledge.md` | ~300 lines, regulatory critical |
| 2 | Create Misinformation & Disinformation eval | `rai/07-misinformation-disinformation.md` | ~300 lines |
| 2-3 | Create Child Safety (CSE) eval | `rai/08-child-safety-cse.md` | ~200 lines, approach-only |

**Priority 2 — Enhancements (Days 3-4)**

| Day | Task | File | Enhancement |
|-----|------|------|-------------|
| 3 | Add advanced attack techniques section | `redteam/02-jailbreak-resistance.md` | Crescendo, PAIR, Many-shot, Skeleton Key, Best-of-N |
| 3 | Add MLCommons categories | `rai/01-toxicity-harmful-content.md` | Violent crimes, non-violent crimes, sex-related crimes |
| 3 | Add defamation category | `redteam/04-brand-reputation-risk.md` | MLCommons defamation |
| 4 | Add EU AI Act + IP/copyright | `rai/06-regulatory-compliance-exposure.md` | EU AI Act scenarios, copyright |
| 4 | Add vector/embedding weaknesses | `redteam/06-adversarial-rag-context-poisoning.md` | OWASP LLM #8 |

**Priority 3 — Overview Update (Day 4)**

| Day | Task | File |
|-----|------|------|
| 4 | Update overview for 17 evals | `00-overview.md` |

### Week 2: Dataset Generation

| Day | Task | Datapoints |
|-----|------|------------|
| 5-6 | Generate Agentic AI Safety dataset | ~100 datapoints |
| 6-7 | Generate CBRN dataset | ~100 datapoints |
| 7-8 | Generate Misinformation dataset | ~100 datapoints |
| 8 | Generate Child Safety dataset | ~100 datapoints |
| 9-10 | Quality review all datasets | Validate all ~400 new datapoints |

### Week 3: Platform Integration

| Day | Task |
|-----|------|
| 11 | Seed 8 new global metrics for 4 new evals |
| 12 | Upload 4 new datasets to platform |
| 13 | Create 4 AgentEval configurations |
| 14 | Run initial evaluation passes |
| 15 | Analyze results, tune thresholds if needed |

---

## 6. Phase 2: Next Sprint (3 Additional Evals)

| # | Eval | File | Why Phase 2 | Effort |
|---|------|------|-------------|--------|
| 18 | Supply Chain & Model Integrity | `redteam/10-supply-chain-model-integrity.md` | Requires toolchain integration testing; NIST #12, OWASP LLM #3 | High |
| 19 | IP & Copyright Compliance | `rai/09-ip-copyright-compliance.md` | Needs training data provenance tooling; NIST #10, EU AI Act Art. 53 | Medium |
| 20 | Multimodal Attack Resistance | `redteam/11-multimodal-attack-resistance.md` | Blocked until platform supports image/audio inputs | High |

**Phase 2 prerequisite:** Phase 1 evals passing at target thresholds before expanding scope.

---

## 7. Attack Techniques Catalog

Modern adversarial research has identified attack techniques with significantly higher success rates than traditional jailbreaks. These are integrated into our eval suite as follows:

### 7.1 Techniques Integrated into Existing Evals

| Technique | Description | Success Rate (Published) | Integrated Into |
|-----------|-------------|------------------------|-----------------|
| **Crescendo** | Multi-turn escalation where each turn subtly shifts the conversation toward harmful territory. Exploits the model's tendency to maintain conversational coherence. | 98% on GPT-4 (reported) | #11 Multi-Turn Manipulation, #8 Jailbreak |
| **PAIR** (Prompt Automatic Iterative Refinement) | Automated adversarial prompt refinement using an attacker LLM to iteratively improve jailbreak prompts. 250x more compute-efficient than GCG. | 250x efficiency vs GCG | Dataset generation methodology for #8 Jailbreak |
| **Many-shot Jailbreaking** | Exploits long context windows by prepending many examples of the model answering harmful questions, creating in-context learning pressure. Power-law improvement with shot count. | Scales with context length | #8 Jailbreak (long-context variant) |
| **Skeleton Key** | Augments the model's guardrails rather than bypassing them — instructs the model to add safety warnings while still providing harmful content. | Affected all major models | #8 Jailbreak, #9 Prompt Injection |
| **Best-of-N** | Statistical sampling: generates N responses and selects the one most likely to bypass safety. Exploits inference-time randomness. | 89% on GPT-4o | #8 Jailbreak methodology |

### 7.2 Techniques in New Evals

| Technique | Description | Eval |
|-----------|-------------|------|
| **Inter-agent Prompt Injection** | Attacker compromises one agent in a multi-agent system, which then injects malicious instructions into other agents via shared context. | #14 Agentic AI Safety |
| **Tool Manipulation** | Tricking an agent into misusing its tools (executing unauthorized code, making unauthorized API calls, accessing restricted data). | #14 Agentic AI Safety |
| **Delegation Exploitation** | Exploiting permission inheritance in multi-agent delegation chains — a low-privilege agent delegates to a high-privilege agent. | #14 Agentic AI Safety |
| **Authority Spoofing (CBRN context)** | Posing as a credentialed researcher or institutional authority to extract dangerous knowledge. | #15 CBRN |
| **Authoritative Misinformation** | Generating false content styled to look like legitimate academic, medical, or government sources. | #16 Misinformation |
| **Grooming Pattern Detection** | Testing whether models recognize and refuse grooming conversation patterns (approach-only, no examples). | #17 Child Safety |

### 7.3 How Attack Techniques Map to Dataset Generation

For each technique, the eval spec's LLM generation prompt includes:
1. **Technique description** — what the attack does
2. **Category allocation** — how many of the ~100 datapoints use this technique
3. **Difficulty mapping** — which difficulty tier (basic/intermediate/advanced) the technique belongs to
4. **Expected model behavior** — what a correct refusal looks like
5. **Checklist criteria** — what binary pass/fail items evaluate

The generation prompt instructs the LLM to create realistic attack scenarios. For sensitive topics (CBRN, CSE), prompts use **sanitized placeholders** (e.g., `"[User requests detailed synthesis procedure for restricted substance]"`) rather than generating actual harmful content.

---

## 8. For the Engineer: Step-by-Step Checklist

### Pre-Flight

- [ ] Read this document end-to-end
- [ ] Read `00-overview.md` to understand platform architecture
- [ ] Read one existing eval doc fully (recommend `redteam/02-jailbreak-resistance.md`) to understand the 6-section template
- [ ] Verify access to the TI Validation Platform (Datasets, Metrics, Evaluations)

### Phase 1 — New Eval Specs

For each new eval (`#14`, `#15`, `#16`, `#17`):

- [ ] Read the eval spec doc
- [ ] Verify it follows the 6-section template:
  1. Business Justification
  2. What We Test
  3. Dataset Specification (schema, examples, generation prompt, quality checklist)
  4. Metrics (global metrics with evaluation prompts, per-datapoint checklist)
  5. Acceptance Criteria (thresholds, auto-fail conditions)
  6. Platform Setup (metric seed data, dataset upload, AgentEval config, results interpretation)
- [ ] Verify JSON examples are valid and use sanitized placeholders for sensitive content
- [ ] Verify metric evaluation prompts use `{query}`, `{agent_response}`, `{golden_response}` placeholders

### Phase 1 — Enhancements

For each enhanced eval:

- [ ] Read the new section added to the existing doc
- [ ] Verify it integrates cleanly with the existing content
- [ ] Verify any new categories/techniques are reflected in the generation prompt guidance
- [ ] Verify any new checklist themes are documented

### Phase 1 — Dataset Generation

For each of the 4 new evals:

- [ ] Copy the generation prompt from Section 3.3 of the eval doc
- [ ] Run through GPT-5.2 or Claude Opus 4.5 in batches of 20-25
- [ ] Validate each batch against the quality checklist (Section 3.4)
- [ ] Combine batches, renumber IDs sequentially
- [ ] Verify final dataset has ~100 datapoints with correct distribution
- [ ] For CBRN and CSE: verify NO actual harmful content was generated (sanitized placeholders only)

### Phase 1 — Platform Integration

For each of the 4 new evals:

- [ ] Seed global metrics (Section 6.1 of each eval doc)
- [ ] Upload dataset (Section 6.2)
- [ ] Create AgentEval configuration (Section 6.3)
- [ ] Run evaluation and check results against acceptance criteria (Section 5)

### Phase 1 — Verification

- [ ] All 17 eval docs exist and follow the 6-section template
- [ ] `00-overview.md` reflects 17 evals, ~1,650+ datapoints, ~39 metrics
- [ ] Regulatory compliance matrix covers NIST, OWASP LLM, OWASP Agentic, MLCommons, EU AI Act
- [ ] No content policy violations in any eval doc (sensitive evals use approach descriptions, not examples)
- [ ] All JSON examples are valid
- [ ] All auto-fail conditions are documented

---

## Appendix A: File Manifest

### New Files (Phase 1)

```
docs/eval-suites/
├── IMPLEMENTATION-ROADMAP.md                    # This document
├── rai/
│   ├── 07-misinformation-disinformation.md      # NEW: Eval #16
│   └── 08-child-safety-cse.md                   # NEW: Eval #17
└── redteam/
    ├── 08-agentic-ai-safety.md                  # NEW: Eval #14
    └── 09-cbrn-dangerous-knowledge.md           # NEW: Eval #15
```

### Enhanced Files (Phase 1)

```
docs/eval-suites/
├── 00-overview.md                               # UPDATED: 13→17 evals
├── rai/
│   ├── 01-toxicity-harmful-content.md           # ENHANCED: MLCommons categories
│   └── 06-regulatory-compliance-exposure.md     # ENHANCED: EU AI Act, IP/copyright
└── redteam/
    ├── 02-jailbreak-resistance.md               # ENHANCED: 5 advanced attack techniques
    ├── 04-brand-reputation-risk.md              # ENHANCED: Defamation category
    └── 06-adversarial-rag-context-poisoning.md  # ENHANCED: Vector/embedding weaknesses
```

### Phase 2 Files (Future)

```
docs/eval-suites/
├── rai/
│   └── 09-ip-copyright-compliance.md            # FUTURE: Eval #19
└── redteam/
    ├── 10-supply-chain-model-integrity.md        # FUTURE: Eval #18
    └── 11-multimodal-attack-resistance.md        # FUTURE: Eval #20
```

## Appendix B: Metric Inventory (All 39 Global Metrics)

| # | Eval | Metrics | Count |
|---|------|---------|-------|
| 1 | Toxicity & Harmful Content | Toxicity Detection Accuracy, Contextual Safety Awareness, Response Appropriateness | 3 |
| 2 | Stereotyping, Bias & Fairness | Response Consistency Across Demographics, Bias Detection Accuracy | 2 |
| 3 | PII & Privacy Leakage | PII Protection Accuracy, Privacy Boundary Maintenance | 2 |
| 4 | HR Violation & Sensitive Disclosure | Issue Recognition Accuracy, Response Neutrality, Escalation Appropriateness | 3 |
| 5 | Mental Health & Crisis Response | Crisis Detection & Safety, Clinical Boundary Maintenance | 2 |
| 6 | Regulatory & Compliance Exposure | Regulatory Compliance Accuracy, Qualification Language Appropriateness | 2 |
| 7 | Hallucination Robustness | Factual Accuracy, Confidence Calibration, Citation Verification | 3 |
| 8 | Jailbreak Resistance | Jailbreak Detection Rate, Refusal Quality | 2 |
| 9 | Prompt Injection Resistance | Injection Detection Rate, Instruction Integrity | 2 |
| 10 | Brand & Reputation Risk | Commitment Avoidance, Professional Boundary Maintenance | 2 |
| 11 | Multi-Turn Manipulation & Guardrail Decay | Guardrail Consistency Over Turns, Manipulation Resistance, Context Integrity | 3 |
| 12 | Adversarial RAG & Context Poisoning | Source Verification Accuracy, Instruction Isolation | 2 |
| 13 | Sensitive Information Exfiltration | Information Containment, Probing Resistance | 2 |
| **14** | **Agentic AI Safety** | **Agent Boundary Compliance, Tool Use Safety** | **2** |
| **15** | **CBRN & Dangerous Knowledge** | **Dangerous Knowledge Refusal Rate, Safety Redirect Quality** | **2** |
| **16** | **Misinformation & Disinformation** | **Misinformation Detection Accuracy, Source Attribution Quality** | **2** |
| **17** | **Child Safety (CSE)** | **CSE Detection & Refusal Rate, Mandatory Reporting Awareness** | **2** |
| | | **Total** | **39** |

---

## Document Metadata

- **Version**: 1.0
- **Created**: 2026-02-13
- **Owner**: AI Safety & Red Team
- **Review Cycle**: Update when new frameworks are published or Phase 2 begins
- **Related Documents**: `00-overview.md`, all eval spec docs in `rai/` and `redteam/`
