# LLM Hallucination Study

An exploratory study of hallucination and abstention in 2026 open-weight LLMs.

## Models Tested

- Qwen 3.8-27B (Alibaba)
- GPT-OSS-20B (OpenAI)

## Key Findings

1. Two failure modes identified:
   - Qwen: rigid confabulation (100% consistency)
   - GPT-OSS: deliberation collapse (50% empty responses)

2. Template-based confabulation in Qwen:
   - Same fabricated year (1991) for two different universities

3. Authority pressure affects GPT-OSS:
   - Up to 232% increase in reasoning tokens
   - Academic framing triggers refusal

4. Empathy pressure is ineffective:
   - Neither model increases fabrication under emotional pressure

## Repository Structure

- README.md - this file
- RESULTS.md - findings and tables
- METHODOLOGY.md - protocol description
- LIMITATIONS.md - what this study cannot claim
- *.py - Python scripts
- *.csv - raw data files

## Data Summary

Total: 638 trials across 10 CSV files.

## Reproducing

export GROQ_API_KEY=gsk_...
python scientific_test.py

## Status

Exploratory pilot study. Not peer-reviewed. Small sample size.

See LIMITATIONS.md for full caveats.

## License

CC-BY-4.0
