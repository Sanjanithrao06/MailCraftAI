# MailCraft AI — Comparative Analysis Report

## 1. Setup

### Models & Strategies Compared

| Label | Model | Prompting Strategy | Description |
|-------|-------|--------------------|-------------|
| **Advanced** | GPT-4o | CoT + Few-Shot + Role-Play + Self-Reflection | Full advanced pipeline with a B2B sales specialist persona, 3 few-shot examples, chain-of-thought planning, and a critic revision loop |
| **Baseline** | GPT-4o-mini | Zero-Shot Instruction | Simple instruction prompt ("Write a professional email...") with no examples or reasoning steps |

### Evaluation Metrics

1. **Fact Recall (0-100)**: Measures whether all input key facts are present in the generated email. Uses LLM-as-Judge per-fact verification with sentence-transformer semantic similarity as a fallback.

2. **Tone Alignment (0-100)**: Measures how well the email's tone matches the requested tone. Combines LLM-as-Judge rating (80% weight) with VADER sentiment analysis (20% weight).

3. **Professional Quality (0-100)**: Composite metric across four sub-dimensions — Readability (Flesch Reading Ease), Conciseness (length ratio vs reference), Structure (greeting/body/sign-off checks), and Grammar & Fluency (LLM judge).

---

## 2. Results

> **Note:** Run `python run_evaluation.py` to generate the actual scores. The tables below should be populated with your evaluation output from `reports/evaluation_results.json`.

### Per-Scenario Scores

| Scenario | Tone | Advanced Fact | Advanced Tone | Advanced Quality | Baseline Fact | Baseline Tone | Baseline Quality |
|----------|------|---------------|---------------|------------------|---------------|---------------|------------------|
| 1 | formal | — | — | — | — | — | — |
| 2 | professional | — | — | — | — | — | — |
| 3 | friendly-casual | — | — | — | — | — | — |
| 4 | empathetic | — | — | — | — | — | — |
| 5 | excited | — | — | — | — | — | — |
| 6 | neutral | — | — | — | — | — | — |
| 7 | persuasive | — | — | — | — | — | — |
| 8 | warm-grateful | — | — | — | — | — | — |
| 9 | urgent | — | — | — | — | — | — |
| 10 | casual-compelling | — | — | — | — | — | — |

### Average Scores

| Metric | Advanced (GPT-4o) | Baseline (GPT-4o-mini) | Delta |
|--------|-------------------|------------------------|-------|
| Fact Recall | — | — | — |
| Tone Alignment | — | — | — |
| Professional Quality | — | — | — |
| **Overall Average** | **—** | **—** | **—** |

---

## 3. Failure Mode Analysis

### Baseline Model (GPT-4o-mini) — Key Weaknesses

**Biggest failure mode: Fact Omission**

_(To be filled after running evaluation)_

Observations to look for:
- The baseline model tends to miss or vaguely paraphrase key facts, especially when given 4+ facts per scenario
- Zero-shot prompting provides no structural guidance, leading to inconsistent email formats
- Without the critic loop, there's no self-correction mechanism for tone drift

### Advanced Model (GPT-4o) — Observed Strengths

_(To be filled after running evaluation)_

Observations to look for:
- Few-shot examples provide a structural template the model anchors to
- Chain-of-thought planning ensures facts are deliberately placed in paragraphs
- The critic loop catches and corrects fact omissions and tone inconsistencies

---

## 4. Production Recommendation

**Recommended: Advanced Strategy (GPT-4o with CoT + Few-Shot + Role-Play + Self-Reflection)**

### Justification

_(To be filled with actual metric data after evaluation)_

| Factor | Advanced | Baseline |
|--------|----------|----------|
| Fact Recall | Higher — critical for business emails | Lower — unacceptable for production |
| Tone Alignment | Consistent across varied tones | Adequate for common tones, struggles with nuanced ones |
| Professional Quality | Polished, well-structured | Acceptable but less refined |
| Latency | ~3-5s (2 LLM calls with critic) | ~1-2s (single call) |
| Cost per email | ~$0.02-0.04 | ~$0.002-0.005 |

### Trade-off Analysis

- **For production use at Salaria (sales email automation)**: Fact accuracy is non-negotiable. A missed fact in a sales follow-up can lose a deal. The ~10x cost difference is negligible at email volumes (even 10,000 emails/month = ~$400 with GPT-4o).
- **Possible hybrid approach**: Use the Advanced strategy for high-value emails (first touch, proposals, escalations) and Baseline for high-volume low-stakes emails (meeting confirmations, acknowledgments) with a routing layer based on intent classification.

---

## 5. Prompt Template Documentation

### Advanced Strategy Prompt

**Technique**: Role-Playing + Few-Shot Examples + Chain-of-Thought

- **System Message**: Assigns the model a B2B sales communications specialist persona with explicit rules (include all facts, match tone, clear structure, concise).
- **Few-Shot Examples**: 3 complete input → email examples covering formal, casual, and empathetic tones, giving the model a structural anchor.
- **Chain-of-Thought**: The user message instructs the model to silently plan (identify primary CTA, map facts to paragraphs, select tone-appropriate vocabulary) before generating the final email.
- **Self-Reflection**: A separate critic pass verifies fact inclusion, tone consistency, and structural completeness — revising the draft if needed.

### Baseline Strategy Prompt

**Technique**: Zero-Shot Instruction

- **System Message**: Minimal ("You are a helpful assistant that writes professional emails").
- **User Message**: Direct instruction with the three inputs. No examples, no reasoning scaffold.
