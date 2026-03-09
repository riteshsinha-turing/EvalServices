"""
Dataset Improvement Script for EvalServices.

Improves existing evaluation datasets by processing each datapoint one-by-one
with an LLM, using the source generation prompt as the specification. Enriches
content (messages, scenario descriptions, golden responses, metadata) while
preserving the exact JSON structure. Avoids token limits by processing
per-datapoint.

Usage:
    python improve_dataset.py --prompt ../dataset-generation-prompts/RedTeam/04-brand-reputation-risk.py --dataset ../dataset/Red-Team/04-brand-reputation-risk_v1.json --provider anthropic
    python improve_dataset.py --prompt prompts/toxicity.txt --dataset data.json --output data_improved.json --provider openai --checkpoint-interval 10
"""

import argparse
import json
import logging
import re
import sys
import time
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

# Reuse provider abstraction and env config from generate_dataset
from generate_dataset import (
    PROVIDER_CLASSES,
    PROVIDER_ENV_KEYS,
    BaseLLMProvider,
    validate_provider_config,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
VALID_PROVIDERS = list(PROVIDER_ENV_KEYS.keys())

IMPROVEMENT_INSTRUCTION = """
You are improving a single evaluation datapoint that was generated from the specification above but may be thin or repetitive due to token limits.

Your task: output exactly one JSON object that is the **improved** version of the datapoint below.
- Preserve the exact same JSON structure and all keys (top-level and nested).
- Only improve the **content** of fields (e.g. user/assistant messages, scenario descriptions, golden/expected responses, metadata) so the datapoint is richer, more diverse, and fully aligned with the specification.
- Do not add or remove top-level keys.
- Output only the single JSON object, no markdown code fences and no explanation.
"""

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


def setup_logging(provider: str) -> logging.Logger:
    """Configure logging for the improve run."""
    from datetime import datetime

    logs_dir = SCRIPT_DIR / "logs"
    logs_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_name = f"improve_{provider}_{timestamp}"

    logger = logging.getLogger("improve_dataset")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

    fh = logging.FileHandler(logs_dir / f"{base_name}.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger


# ---------------------------------------------------------------------------
# Prompt loading
# ---------------------------------------------------------------------------


def load_prompt_from_file(prompt_path: Path, logger: logging.Logger) -> str:
    """
    Load the source prompt from a file.
    - If path has .py extension: extract first triple-quoted string (same as generate_dataset).
    - Otherwise: read entire file content as the prompt.
    """
    path = Path(prompt_path)
    if not path.is_absolute():
        path = (SCRIPT_DIR / path).resolve()
    if not path.exists():
        logger.error("Prompt file not found: %s", path)
        sys.exit(1)

    raw = path.read_text(encoding="utf-8")

    if path.suffix.lower() == ".py":
        match = re.search(r'=\s*"""(.*?)"""', raw, re.DOTALL)
        if not match:
            match = re.search(r"=\s*'''(.*?)'''", raw, re.DOTALL)
        if not match:
            logger.error("Could not extract prompt from .py file: %s", path)
            sys.exit(1)
        return match.group(1).strip()

    return raw.strip()


# ---------------------------------------------------------------------------
# JSON extraction (single object)
# ---------------------------------------------------------------------------


def extract_single_json_object(raw_text: str, logger: logging.Logger) -> Optional[dict]:
    """Extract a single JSON object from LLM response, handling markdown fences."""
    cleaned = re.sub(r"```(?:json)?\s*", "", raw_text)
    cleaned = re.sub(r"```\s*", "", cleaned)
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            return data[0]
    except json.JSONDecodeError as e:
        logger.debug("Initial JSON parse failed: %s", e)

    brace_start = cleaned.find("{")
    brace_end = cleaned.rfind("}")
    if brace_start != -1 and brace_end > brace_start:
        try:
            data = json.loads(cleaned[brace_start : brace_end + 1])
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

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
                        return json.loads(cleaned[start : i + 1])
                    except json.JSONDecodeError:
                        break
        break

    logger.debug("No JSON object found in response (%d chars)", len(raw_text))
    return None


# ---------------------------------------------------------------------------
# Improvement loop
# ---------------------------------------------------------------------------


def improve_one_datapoint(
    provider: BaseLLMProvider,
    source_prompt: str,
    datapoint: dict,
    temperature: float,
    logger: logging.Logger,
) -> Optional[dict]:
    """Call LLM to improve a single datapoint; return improved dict or None on failure."""
    system_prompt = source_prompt.strip() + "\n\n" + IMPROVEMENT_INSTRUCTION.strip()
    user_prompt = "Current datapoint (improve this):\n" + json.dumps(
        datapoint, indent=2, ensure_ascii=False
    )

    try:
        raw = provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=16000,
        )
    except Exception as e:
        logger.exception("LLM call failed: %s", e)
        return None

    improved = extract_single_json_object(raw, logger)
    if improved is None:
        logger.warning("Failed to parse improved JSON from response (length %d)", len(raw))
        return None
    return improved


def run_improvement(
    prompt_path: Path,
    dataset_path: Path,
    output_path: Path,
    provider_name: str,
    start_index: int,
    limit: Optional[int],
    checkpoint_interval: Optional[int],
    checkpoint_file: Optional[Path],
    temperature: float,
    logger: logging.Logger,
) -> None:
    """Load prompt and dataset, improve datapoints one-by-one, write output with optional checkpointing."""
    source_prompt = load_prompt_from_file(prompt_path, logger)
    logger.info("Loaded prompt from %s (%d chars)", prompt_path, len(source_prompt))

    dataset_path_resolved = (
        dataset_path if dataset_path.is_absolute() else (SCRIPT_DIR / dataset_path).resolve()
    )
    if not dataset_path_resolved.exists():
        logger.error("Dataset file not found: %s", dataset_path_resolved)
        sys.exit(1)

    data = json.loads(dataset_path_resolved.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        logger.error("Dataset must be a JSON array of datapoints")
        sys.exit(1)
    if not data:
        logger.error("Dataset is empty")
        sys.exit(1)

    total = len(data)
    api_key, model = validate_provider_config(provider_name)
    provider = PROVIDER_CLASSES[provider_name](api_key=api_key, model=model)

    result: List[dict] = []
    if checkpoint_file and checkpoint_file.exists():
        try:
            result = json.loads(checkpoint_file.read_text(encoding="utf-8"))
            if not isinstance(result, list):
                result = []
            if result:
                start_index = len(result)
                logger.info("Resuming from checkpoint: %d datapoints already improved", len(result))
        except Exception as e:
            logger.warning("Could not load checkpoint %s: %s; starting fresh", checkpoint_file, e)

    end_index = total
    if limit is not None and limit > 0:
        end_index = min(start_index + limit, total)
    slice_count = end_index - start_index
    logger.info("Dataset has %d datapoints; processing indices [%d, %d) (%d datapoints)", total, start_index, end_index, slice_count)

    for i in range(start_index, end_index):
        dp = data[i]
        if not isinstance(dp, dict):
            logger.warning("Skipping non-dict at index %d", i)
            result.append(dp)
            continue

        logger.info("Improving datapoint %d/%d (index %d)", i - start_index + 1, slice_count, i)
        start_time = time.time()
        improved = improve_one_datapoint(provider, source_prompt, dp, temperature, logger)
        elapsed = time.time() - start_time

        if improved is not None:
            result.append(improved)
            logger.info("Improved in %.1fs", elapsed)
        else:
            result.append(dp)
            logger.warning("Kept original datapoint after failure (%.1fs)", elapsed)

        if checkpoint_interval and checkpoint_file and len(result) % checkpoint_interval == 0:
            checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
            checkpoint_file.write_text(
                json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            logger.info("Checkpoint saved (%d datapoints)", len(result))

        if i < end_index - 1:
            time.sleep(0.5)

    output_path_resolved = output_path if output_path.is_absolute() else (SCRIPT_DIR / output_path).resolve()
    output_path_resolved.parent.mkdir(parents=True, exist_ok=True)
    output_path_resolved.write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info("Wrote %d datapoints to %s", len(result), output_path_resolved)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Improve evaluation dataset datapoints one-by-one using the source prompt.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--prompt", type=str, required=True, help="Path to prompt file (.py or .txt/.md)")
    parser.add_argument("--dataset", type=str, required=True, help="Path to dataset JSON (array of datapoints)")
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output JSON path (default: <dataset_dir>/<stem>_improved.json or improved/<name>.json)",
    )
    parser.add_argument(
        "--provider",
        choices=VALID_PROVIDERS,
        required=True,
        help="LLM provider: " + ", ".join(VALID_PROVIDERS),
    )
    parser.add_argument(
        "--start-index",
        type=int,
        default=0,
        help="0-based index to start processing (default: 0)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Max number of datapoints to process (default: all)",
    )
    parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=None,
        help="Save progress every N datapoints (optional)",
    )
    parser.add_argument(
        "--checkpoint-file",
        type=str,
        default=None,
        help="Path to checkpoint file for resume (optional)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="LLM temperature for enrichment (default: 0.3)",
    )
    return parser.parse_args()


def default_output_path(dataset_path: Path) -> Path:
    """Derive default output path from dataset path."""
    resolved = dataset_path if dataset_path.is_absolute() else (SCRIPT_DIR / dataset_path).resolve()
    parent = resolved.parent
    stem = resolved.stem
    base = stem + "_improved"
    return parent / (base + resolved.suffix)


def main() -> None:
    args = parse_args()

    env_path = SCRIPT_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()

    logger = setup_logging(args.provider)
    logger.info("Dataset improvement started (provider=%s)", args.provider)

    prompt_path = Path(args.prompt)
    dataset_path = Path(args.dataset)
    output_path = Path(args.output) if args.output else default_output_path(dataset_path)
    checkpoint_file = None
    if args.checkpoint_file:
        p = Path(args.checkpoint_file)
        checkpoint_file = p if p.is_absolute() else (SCRIPT_DIR / p).resolve()

    run_improvement(
        prompt_path=prompt_path,
        dataset_path=dataset_path,
        output_path=output_path,
        provider_name=args.provider,
        start_index=args.start_index,
        limit=args.limit,
        checkpoint_interval=args.checkpoint_interval,
        checkpoint_file=checkpoint_file,
        temperature=args.temperature,
        logger=logger,
    )

    print(f"Done. Output written to {output_path.resolve()}")


if __name__ == "__main__":
    main()
