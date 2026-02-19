"""
Dataset Generation Script for EvalServices.

Generates evaluation datasets for 5 eval types using LLM providers
(OpenAI, Anthropic, Gemini, Grok) with batch generation, JSON validation,
and dual-file logging.

Usage:
    python generate_dataset.py --eval hallucination --provider openai
    python generate_dataset.py --eval pii --provider anthropic --batch-size 20 --total 80
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from abc import ABC, abstractmethod
from datetime import datetime
from importlib import import_module
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
PROMPTS_DIR = PROJECT_ROOT / "dataset-generation-prompts"

EVAL_PROMPT_MAP = {
    "hallucination": {
        "module": "Hallucination-Robustness-dataset-generation-prompt",
        "variable": "Hallucination-Robustness",
    },
    "pii": {
        "module": "PII-Privacy-Leakage-dataset-generation-prompt",
        "variable": "PII-Privacy-Leakage",
    },
    "jailbreak": {
        "module": "Jailbreak-Resistance-dataset-generation-prompt",
        "variable": "Jailbreak-Resistance",
    },
    "regulatory": {
        "module": "Regulatory-Compliance-dataset-generation-prompt",
        "variable": "Regulatory-Compliance",
    },
    "hr": {
        "module": "HR-Violation-dataset-generation-prompt",
        "variable": "HR-Violation",
    },
}

PROVIDER_ENV_KEYS = {
    "openai": {"api_key": "OPENAI_API_KEY", "model": "OPENAI_MODEL"},
    "anthropic": {"api_key": "ANTHROPIC_API_KEY", "model": "ANTHROPIC_MODEL"},
    "gemini": {"api_key": "GEMINI_API_KEY", "model": "GEMINI_MODEL"},
    "grok": {"api_key": "GROK_API_KEY", "model": "GROK_MODEL"},
}

VALID_EVALS = list(EVAL_PROMPT_MAP.keys())
VALID_PROVIDERS = list(PROVIDER_ENV_KEYS.keys())

# ---------------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------------


def setup_logging(eval_type: str, provider: str) -> logging.Logger:
    """Configure logging with console + two file handlers (INFO and DEBUG)."""
    logs_dir = SCRIPT_DIR / "logs"
    logs_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_name = f"{eval_type}_{provider}_{timestamp}"

    logger = logging.getLogger("dataset_gen")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    info_handler = logging.FileHandler(logs_dir / f"{base_name}.log", encoding="utf-8")
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    logger.addHandler(info_handler)

    debug_handler = logging.FileHandler(
        logs_dir / f"{base_name}_debug.log", encoding="utf-8"
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)
    logger.addHandler(debug_handler)

    return logger


# ---------------------------------------------------------------------------
# LLM Provider Abstraction
# ---------------------------------------------------------------------------


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 16000,
    ) -> str:
        """Send a prompt and return the raw text response."""


class OpenAIProvider(BaseLLMProvider):
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 16000,
    ) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content


class AnthropicProvider(BaseLLMProvider):
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 16000,
    ) -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=temperature,
        )
        return response.content[0].text


class GeminiProvider(BaseLLMProvider):
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 16000,
    ) -> str:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )
        return response.text


class GrokProvider(BaseLLMProvider):
    """Grok uses the OpenAI SDK with xAI's base URL."""

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 16000,
    ) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key, base_url="https://api.x.ai/v1")
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content


PROVIDER_CLASSES = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "gemini": GeminiProvider,
    "grok": GrokProvider,
}

# ---------------------------------------------------------------------------
# Prompt Loading
# ---------------------------------------------------------------------------


def load_prompt(eval_type: str) -> str:
    """Load the generation prompt string from the corresponding .py file in dataset-generation-prompts/."""
    info = EVAL_PROMPT_MAP[eval_type]
    file_path = PROMPTS_DIR / f"{info['module']}.py"

    if not file_path.exists():
        print(f"ERROR: Prompt file not found: {file_path}")
        sys.exit(1)

    source = file_path.read_text(encoding="utf-8")

    # The files store prompts as:  VariableName = """..."""
    # Extract the triple-quoted string content.
    match = re.search(r'=\s*"""(.*?)"""', source, re.DOTALL)
    if not match:
        match = re.search(r"=\s*'''(.*?)'''", source, re.DOTALL)
    if not match:
        print(f"ERROR: Could not extract prompt from {file_path}")
        sys.exit(1)

    return match.group(1).strip()


# ---------------------------------------------------------------------------
# JSON Extraction & Validation
# ---------------------------------------------------------------------------


def extract_json_array(raw_text: str, logger: logging.Logger) -> list | None:
    """Extract a JSON array from LLM response text, handling code fences."""
    logger.debug("Raw response length: %d chars", len(raw_text))

    # Strip markdown code fences
    cleaned = re.sub(r"```(?:json)?\s*", "", raw_text)
    cleaned = re.sub(r"```\s*", "", cleaned)
    cleaned = cleaned.strip()

    logger.debug("Cleaned text (first 500 chars): %s", cleaned[:500])

    # Try parsing directly
    try:
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return [data]
    except json.JSONDecodeError:
        pass

    # Try extracting array substring
    bracket_start = cleaned.find("[")
    bracket_end = cleaned.rfind("]")
    if bracket_start != -1 and bracket_end > bracket_start:
        try:
            data = json.loads(cleaned[bracket_start : bracket_end + 1])
            if isinstance(data, list):
                logger.debug("Extracted JSON array via bracket detection")
                return data
        except json.JSONDecodeError as e:
            logger.debug("Bracket extraction failed: %s", e)

    # Try extracting individual objects
    objects = []
    for match in re.finditer(r"\{", cleaned):
        start = match.start()
        depth = 0
        for i in range(start, len(cleaned)):
            if cleaned[i] == "{":
                depth += 1
            elif cleaned[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(cleaned[start : i + 1])
                        objects.append(obj)
                    except json.JSONDecodeError:
                        pass
                    break
    if objects:
        logger.debug("Extracted %d individual JSON objects", len(objects))
        return objects

    logger.warning("Failed to extract any valid JSON from response")
    return None


REQUIRED_FIELDS = {"id", "turns"}
REQUIRED_TURN_FIELDS = {"id", "input", "metadata", "expected_output", "lm_checklist"}
REQUIRED_METADATA_FIELDS = {"conversation_history", "category", "difficulty"}


def validate_datapoint(dp: dict, logger: logging.Logger) -> bool:
    """Validate a single datapoint against the required schema."""
    if not isinstance(dp, dict):
        logger.debug("Datapoint is not a dict: %s", type(dp))
        return False

    missing_top = REQUIRED_FIELDS - set(dp.keys())
    if missing_top:
        logger.debug("Missing top-level fields: %s", missing_top)
        return False

    if not isinstance(dp.get("turns"), list) or len(dp["turns"]) == 0:
        logger.debug("'turns' is not a non-empty list")
        return False

    turn = dp["turns"][0]
    missing_turn = REQUIRED_TURN_FIELDS - set(turn.keys())
    if missing_turn:
        logger.debug("Missing turn fields: %s | datapoint id=%s", missing_turn, dp.get("id"))
        return False

    meta = turn.get("metadata", {})
    missing_meta = REQUIRED_METADATA_FIELDS - set(meta.keys())
    if missing_meta:
        logger.debug(
            "Missing metadata fields: %s | datapoint id=%s", missing_meta, dp.get("id")
        )
        return False

    if not isinstance(turn.get("lm_checklist"), list):
        logger.debug("lm_checklist is not a list | datapoint id=%s", dp.get("id"))
        return False

    return True


# ---------------------------------------------------------------------------
# Batch Generation
# ---------------------------------------------------------------------------


def generate_batch(
    provider: BaseLLMProvider,
    prompt_text: str,
    batch_num: int,
    start_id: int,
    end_id: int,
    temperature: float,
    logger: logging.Logger,
) -> list:
    """Generate a single batch of datapoints."""
    system_prompt = (
        "You are an expert dataset generator. Your output must be ONLY a valid JSON array "
        "of datapoint objects — no commentary, no markdown, no explanation. "
        "Follow the schema in the prompt EXACTLY."
    )

    user_prompt = (
        f"{prompt_text}\n\n"
        f"---\n"
        f"Generate datapoints with IDs from {start_id} to {end_id} "
        f"(inclusive, {end_id - start_id + 1} datapoints). "
        f"Output ONLY a valid JSON array. No other text."
    )

    logger.info("Batch %d: Generating datapoints %d-%d", batch_num, start_id, end_id)
    logger.debug("System prompt length: %d chars", len(system_prompt))
    logger.debug("User prompt length: %d chars", len(user_prompt))
    logger.debug("Full system prompt:\n%s", system_prompt)
    logger.debug("Full user prompt:\n%s", user_prompt)

    start_time = time.time()
    try:
        raw_response = provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
        )
        elapsed = time.time() - start_time
        logger.info("Batch %d: LLM responded in %.1fs (%d chars)", batch_num, elapsed, len(raw_response))
        logger.debug("Full raw response:\n%s", raw_response)
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error("Batch %d: LLM call failed after %.1fs: %s", batch_num, elapsed, e)
        logger.debug("Full error traceback:", exc_info=True)
        return []

    datapoints = extract_json_array(raw_response, logger)
    if datapoints is None:
        logger.error("Batch %d: Failed to extract JSON from response", batch_num)
        return []

    valid = []
    invalid_count = 0
    for dp in datapoints:
        if validate_datapoint(dp, logger):
            valid.append(dp)
        else:
            invalid_count += 1

    logger.info(
        "Batch %d: %d valid, %d invalid out of %d extracted",
        batch_num,
        len(valid),
        invalid_count,
        len(datapoints),
    )
    return valid


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate evaluation datasets using LLM providers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python generate_dataset.py --eval hallucination --provider openai\n"
            "  python generate_dataset.py --eval pii --provider anthropic --batch-size 20\n"
            "  python generate_dataset.py --eval hr --provider gemini --total 50\n"
        ),
    )
    parser.add_argument(
        "--eval",
        choices=VALID_EVALS,
        required=True,
        help=f"Eval type to generate. One of: {', '.join(VALID_EVALS)}",
    )
    parser.add_argument(
        "--provider",
        choices=VALID_PROVIDERS,
        default=None,
        help=f"LLM provider. One of: {', '.join(VALID_PROVIDERS)}",
    )
    parser.add_argument("--batch-size", type=int, default=25, help="Datapoints per batch (default: 25)")
    parser.add_argument("--total", type=int, default=100, help="Total datapoints to generate (default: 100)")
    parser.add_argument("--output", type=str, default=None, help="Output file path (default: ./output/<eval>-dataset.json)")
    parser.add_argument("--temperature", type=float, default=0.7, help="Generation temperature (default: 0.7)")
    return parser.parse_args()


def validate_provider_config(provider_name: str) -> tuple[str, str]:
    """Validate that the required env vars exist for the chosen provider.
    Returns (api_key, model) or exits with a clear error.
    """
    env_keys = PROVIDER_ENV_KEYS[provider_name]

    api_key = os.getenv(env_keys["api_key"])
    model = os.getenv(env_keys["model"])

    if not api_key:
        print(
            f"\nERROR: {env_keys['api_key']} not found in .env file.\n"
            f"Please add it to your .env file:\n"
            f"  {env_keys['api_key']}=your-api-key-here\n"
            f"  {env_keys['model']}=your-model-name\n"
        )
        sys.exit(1)

    if not model:
        print(
            f"\nERROR: {env_keys['model']} not found in .env file.\n"
            f"Please add it to your .env file:\n"
            f"  {env_keys['model']}=your-model-name\n"
            f"\nExample model names for {provider_name}:\n"
            f"  openai: gpt-4o, gpt-4o-mini\n"
            f"  anthropic: claude-sonnet-4-20250514, claude-3-5-haiku-20241022\n"
            f"  gemini: gemini-1.5-pro, gemini-2.0-flash\n"
            f"  grok: grok-2, grok-2-mini\n"
        )
        sys.exit(1)

    return api_key, model


def main():
    args = parse_args()

    # Load .env from the script's directory
    env_path = SCRIPT_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()

    # Validate --provider is provided
    if args.provider is None:
        print(
            f"\nERROR: --provider is required. Choose one of: {', '.join(VALID_PROVIDERS)}\n"
            f"Usage: python generate_dataset.py --eval {args.eval} --provider openai\n"
        )
        sys.exit(1)

    # Validate provider config in .env
    api_key, model = validate_provider_config(args.provider)

    # Setup logging
    logger = setup_logging(args.eval, args.provider)
    logger.info("=" * 70)
    logger.info("Dataset Generation Started")
    logger.info("=" * 70)
    logger.info("Eval type    : %s", args.eval)
    logger.info("Provider     : %s", args.provider)
    logger.info("Model        : %s", model)
    logger.info("Batch size   : %d", args.batch_size)
    logger.info("Total target : %d", args.total)
    logger.info("Temperature  : %.2f", args.temperature)

    # Load prompt
    logger.info("Loading generation prompt...")
    prompt_text = load_prompt(args.eval)
    logger.info("Prompt loaded (%d chars)", len(prompt_text))
    logger.debug("Full prompt text:\n%s", prompt_text)

    # Create provider
    provider_cls = PROVIDER_CLASSES[args.provider]
    provider = provider_cls(api_key=api_key, model=model)
    logger.info("Provider initialized: %s (model=%s)", args.provider, model)

    # Generate in batches
    all_datapoints = []
    batch_num = 0
    current_id = 1

    while current_id <= args.total:
        batch_num += 1
        end_id = min(current_id + args.batch_size - 1, args.total)

        batch_results = generate_batch(
            provider=provider,
            prompt_text=prompt_text,
            batch_num=batch_num,
            start_id=current_id,
            end_id=end_id,
            temperature=args.temperature,
            logger=logger,
        )
        all_datapoints.extend(batch_results)
        current_id = end_id + 1

        if current_id <= args.total:
            logger.info("Pausing 2s between batches...")
            time.sleep(2)

    # Re-index IDs sequentially
    for i, dp in enumerate(all_datapoints, start=1):
        dp["id"] = i
        if dp.get("turns") and len(dp["turns"]) > 0:
            dp["turns"][0]["id"] = 1

    # Determine output path
    output_dir = SCRIPT_DIR / "output"
    output_dir.mkdir(exist_ok=True)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_path = output_dir / f"{args.eval}-dataset.json"

    # Save
    output_path.write_text(
        json.dumps(all_datapoints, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Final summary
    logger.info("=" * 70)
    logger.info("Generation Complete")
    logger.info("=" * 70)
    logger.info("Total datapoints generated : %d", len(all_datapoints))
    logger.info("Target was                 : %d", args.total)
    logger.info("Output file                : %s", output_path.resolve())
    logger.info("=" * 70)

    if len(all_datapoints) < args.total:
        logger.warning(
            "Generated %d/%d datapoints. Some batches may have failed or returned invalid JSON. "
            "Check the debug log for details. You can re-run to generate more.",
            len(all_datapoints),
            args.total,
        )

    print(f"\nDone! {len(all_datapoints)} datapoints saved to {output_path.resolve()}")


if __name__ == "__main__":
    main()
