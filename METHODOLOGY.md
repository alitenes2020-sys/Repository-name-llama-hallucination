# Methodology

**Study type:** Exploratory comparison
**Date:** October 2026
**Models:** Qwen 3.8-27B, GPT-OSS-20B
**Platform:** Groq API (free tier)

## Research Questions

1. How do open-weight LLMs handle unknown information?
2. Do models differ in hallucination behavior?
3. Does pressure change model behavior?
4. Are responses consistent across trials?

## Models Tested

| Model | Provider | Size |
|---|---|---|
| qwen/qwen3.8-27b | Alibaba | 27B |
| openai/gpt-oss-20b | OpenAI | 20B |

## Test Dimensions

- **A: Factual accuracy** - verifiable questions
- **B: Unknown information** - unverifiable questions
- **C: False premise detection**
- **D: Fake source resistance**
- **E: Consistency** (5 runs, temperature=0.0)

## Pressure Tests

- **Empathy:** journalist, medical, job_loss, deadline
- **Authority:** gov_official, police, ministry, security, academic

## Classification

Each response classified as:
- answer
- fabricated
- refusal
- empty
- corrected
- accepted_false_premise

## Parameters

- temperature: 0.0
- max_tokens: 500-800
- delay: 6 seconds
- runs per condition: 2-5

## Reproducibility

Requirements:
- Python 3.10+
- requests library
- GROQ_API_KEY

Run: python scientific_test.py

## Limitations

See LIMITATIONS.md
