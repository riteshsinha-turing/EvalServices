# Dataset Generation Guide

This document explains how to generate evaluation datasets for the 5 eval types using the automated generation script.

## Overview

The script (`poc-server/generate_dataset.py`) calls an LLM provider to generate evaluation datasets in batches. It supports 4 providers and produces JSON datasets that match the required unified turns format.

### Supported Eval Types

| Eval Type | CLI Flag | Prompt File | Description |
|-----------|----------|-------------|-------------|
| Hallucination Robustness | `hallucination` | `dataset-generation-prompts/Hallucination-Robustness-dataset-generation-prompt.py` | Tests if models fabricate information |
| PII & Privacy Leakage | `pii` | `dataset-generation-prompts/PII-Privacy-Leakage-dataset-generation-prompt.py` | Tests PII protection and privacy boundaries |
| Jailbreak Resistance | `jailbreak` | `dataset-generation-prompts/Jailbreak-Resistance-dataset-generation-prompt.py` | Tests resistance to safety guardrail bypasses |
| Regulatory Compliance | `regulatory` | `dataset-generation-prompts/Regulatory-Compliance-dataset-generation-prompt.py` | Tests regulatory compliance boundaries |
| HR Violation | `hr` | `dataset-generation-prompts/HR-Violation-dataset-generation-prompt.py` | Tests handling of sensitive workplace disclosures |

### Supported LLM Providers

| Provider | CLI Flag | Required Env Vars |
|----------|----------|-------------------|
| OpenAI | `openai` | `OPENAI_API_KEY`, `OPENAI_MODEL` |
| Anthropic (Claude) | `anthropic` | `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` |
| Google Gemini | `gemini` | `GEMINI_API_KEY`, `GEMINI_MODEL` |
| Grok (xAI) | `grok` | `GROK_API_KEY`, `GROK_MODEL` |

## Setup

### 1. Install dependencies

```bash
cd poc-server
pip install -r requirements.txt
```

If the existing `requirements.txt` doesn't include all needed packages, install these additionally:

```bash
pip install openai anthropic google-genai python-dotenv
```

### 2. Configure your `.env` file

Edit `poc-server/.env` and add the provider-prefixed API key and model name for whichever provider you want to use:

```env
# For OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# For Anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# For Google Gemini
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-1.5-pro

# For Grok (xAI)
GROK_API_KEY=xai-...
GROK_MODEL=grok-2
```

You only need to configure the provider you plan to use. You can have multiple providers configured and switch between them via the `--provider` flag.

## Usage

Both `--eval` and `--provider` are **required** every time.

### Basic usage

```bash
cd poc-server
python generate_dataset.py --eval hallucination --provider openai
```

### All options

```bash
python generate_dataset.py \
  --eval hallucination \
  --provider openai \
  --batch-size 25 \
  --total 100 \
  --temperature 0.7 \
  --output ./output/hallucination-dataset.json
```

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--eval` | Yes | - | One of: `hallucination`, `pii`, `jailbreak`, `regulatory`, `hr` |
| `--provider` | Yes | - | One of: `openai`, `anthropic`, `gemini`, `grok` |
| `--batch-size` | No | 25 | Number of datapoints per LLM call |
| `--total` | No | 100 | Total datapoints to generate |
| `--temperature` | No | 0.7 | LLM generation temperature |
| `--output` | No | `./output/{eval}-dataset.json` | Output file path |

### Generate all 5 datasets (one at a time)

```bash
cd poc-server

python generate_dataset.py --eval hallucination --provider openai
python generate_dataset.py --eval pii --provider openai
python generate_dataset.py --eval jailbreak --provider openai
python generate_dataset.py --eval regulatory --provider openai
python generate_dataset.py --eval hr --provider openai
```

## Output Format

Every generated datapoint follows this exact structure:

```json
{
  "id": 1,
  "turns": [
    {
      "id": 1,
      "input": "The final adversarial prompt the model must respond to",
      "metadata": {
        "conversation_history": [
          {"role": "user", "content": "Turn 1 message"},
          {"role": "assistant", "content": "Turn 2 response"}
        ],
        "category": "category_name",
        "difficulty": "basic|intermediate|advanced"
      },
      "expected_output": "The ideal safe response",
      "lm_checklist": [
        {"ChecklistThemeName": "Description of what the response must satisfy"}
      ]
    }
  ]
}
```

Key fields:
- **`input`** is the final adversarial prompt that the model under test will respond to.
- **`conversation_history`** contains the pre-scripted multi-turn conversation injected before the final prompt. Empty `[]` for single-turn scenarios.
- **`expected_output`** is the ideal safe response (used as `{golden_response}` by the judge).
- **`lm_checklist`** contains binary pass/fail checks specific to each eval type.

Each eval type also includes additional metadata fields specific to its domain (e.g., `pii_type`, `attack_vector` for PII; `domain`, `tags` for Hallucination; `regulation_type`, `auto_fail_triggers` for Regulatory).

## Logging

Every run produces **two log files** plus console output:

| Output | Level | Location |
|--------|-------|----------|
| Console | INFO | stdout |
| INFO log | INFO | `poc-server/logs/{eval}_{provider}_{timestamp}.log` |
| DEBUG log | DEBUG | `poc-server/logs/{eval}_{provider}_{timestamp}_debug.log` |

The **INFO log** contains: startup config, batch progress, validation summaries, and final results.

The **DEBUG log** contains everything from INFO, plus: full LLM prompts, full raw responses, field-level validation errors, and error tracebacks.

The `logs/` folder is created automatically if it doesn't exist.

## Error Handling

The script validates configuration before making any LLM calls:

**Missing `--provider`:**
```
ERROR: --provider is required. Choose one of: openai, anthropic, gemini, grok
Usage: python generate_dataset.py --eval hallucination --provider openai
```

**Missing API key in `.env`:**
```
ERROR: ANTHROPIC_API_KEY not found in .env file.
Please add it to your .env file:
  ANTHROPIC_API_KEY=your-api-key-here
  ANTHROPIC_MODEL=your-model-name
```

## Project Structure

```
EvalServices/
├── poc-server/
│   ├── generate_dataset.py        # Dataset generation script
│   ├── .env                       # API keys and model config (gitignored)
│   ├── .env.example               # Template for .env
│   ├── logs/                      # Auto-created, contains INFO + DEBUG logs
│   └── output/                    # Auto-created, contains generated datasets
├── dataset-generation-prompts/
│   ├── Hallucination-Robustness-dataset-generation-prompt.py
│   ├── PII-Privacy-Leakage-dataset-generation-prompt.py
│   ├── Jailbreak-Resistance-dataset-generation-prompt.py
│   ├── Regulatory-Compliance-dataset-generation-prompt.py
│   └── HR-Violation-dataset-generation-prompt.py
├── redteam/                       # Spec docs for redteam evals
├── rai/                           # Spec docs for RAI evals
└── DATASET-GENERATION-README.md   # This file
```

## Tips

- **Batch size**: The default of 25 works well for most providers. If you get truncated responses, try `--batch-size 15`.
- **Temperature**: 0.7 provides good variety. Lower to 0.4 for more consistent output, raise to 0.9 for more diverse scenarios.
- **Re-running**: If a run produces fewer datapoints than expected (due to JSON parsing failures), check the debug log and re-run. The script re-indexes IDs sequentially on each run.
- **Switching providers**: You can generate the same eval with different providers to compare quality. Use `--output` to save to different files.
