"""
Dataset Structure Transformer.

Transforms generated evaluation dataset JSON files:
  1. Removes lm_checklist from every datapoint
  2. Keeps metadata inside each turn (with conversation_history removed)
  3. Expands conversation_history into separate turns (user->input, assistant->expected_output)

Usage:
    python transform_dataset.py                              # process all files in output/
    python transform_dataset.py --file output/pii-dataset.json  # process a single file
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT_DIR = SCRIPT_DIR / "output"
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "output" / "transformed"


def transform_datapoint(dp: dict) -> dict:
    """Transform a single datapoint to the new structure."""
    turn = dp["turns"][0]

    metadata = dict(turn.get("metadata", {}))
    conversation_history = metadata.pop("conversation_history", [])

    final_input = turn["input"]
    final_expected = turn.get("expected_output", "")

    new_turns = []
    turn_id = 1

    i = 0
    while i < len(conversation_history):
        entry = conversation_history[i]
        if entry["role"] == "user":
            user_input = entry["content"]
            assistant_output = ""
            if i + 1 < len(conversation_history) and conversation_history[i + 1]["role"] == "assistant":
                assistant_output = conversation_history[i + 1]["content"]
                i += 2
            else:
                i += 1
            new_turns.append({
                "id": turn_id,
                "role": "user",
                "input": user_input,
                "metadata": dict(metadata),
                "expected_output": assistant_output,
            })
            turn_id += 1
        else:
            i += 1

    new_turns.append({
        "id": turn_id,
        "role": "user",
        "input": final_input,
        "metadata": dict(metadata),
        "expected_output": final_expected,
    })

    return {
        "id": dp["id"],
        "turns": new_turns,
    }


def transform_file(input_path: Path, output_path: Path) -> dict:
    """Transform a single dataset file. Returns stats."""
    data = json.loads(input_path.read_text(encoding="utf-8"))

    if not isinstance(data, list):
        print(f"  SKIP: {input_path.name} is not a JSON array")
        return {"skipped": True}

    if len(data) == 0:
        print(f"  SKIP: {input_path.name} is empty")
        return {"skipped": True}

    transformed = []
    multi_turn_count = 0
    single_turn_count = 0

    for dp in data:
        if not isinstance(dp, dict) or "turns" not in dp or len(dp.get("turns", [])) == 0:
            continue

        history = dp["turns"][0].get("metadata", {}).get("conversation_history", [])
        if len(history) > 0:
            multi_turn_count += 1
        else:
            single_turn_count += 1

        transformed.append(transform_datapoint(dp))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(transformed, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    return {
        "skipped": False,
        "total": len(transformed),
        "single_turn": single_turn_count,
        "multi_turn": multi_turn_count,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Transform dataset JSON files to the multi-turn structure.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python transform_dataset.py\n"
            "  python transform_dataset.py --file output/pii-dataset.json\n"
            "  python transform_dataset.py --output-dir output/my-transformed\n"
        ),
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Path to a single dataset JSON file to transform. If omitted, all *.json in output/ are processed.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help=f"Output directory for transformed files (default: {DEFAULT_OUTPUT_DIR.relative_to(SCRIPT_DIR)})",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR

    if args.file:
        input_path = Path(args.file)
        if not input_path.is_absolute():
            input_path = SCRIPT_DIR / input_path
        if not input_path.exists():
            print(f"ERROR: File not found: {input_path}")
            sys.exit(1)
        files = [input_path]
    else:
        if not DEFAULT_INPUT_DIR.exists():
            print(f"ERROR: Input directory not found: {DEFAULT_INPUT_DIR}")
            sys.exit(1)
        files = sorted(DEFAULT_INPUT_DIR.glob("*.json"))
        if not files:
            print(f"ERROR: No JSON files found in {DEFAULT_INPUT_DIR}")
            sys.exit(1)

    print(f"Output directory: {output_dir.resolve()}")
    print(f"Files to process: {len(files)}")
    print("-" * 60)

    total_files = 0
    total_datapoints = 0
    total_single = 0
    total_multi = 0

    for input_path in files:
        output_path = output_dir / input_path.name
        print(f"\nProcessing: {input_path.name}")

        stats = transform_file(input_path, output_path)
        if stats.get("skipped"):
            continue

        total_files += 1
        total_datapoints += stats["total"]
        total_single += stats["single_turn"]
        total_multi += stats["multi_turn"]

        print(f"  Datapoints : {stats['total']}")
        print(f"  Single-turn: {stats['single_turn']}")
        print(f"  Multi-turn : {stats['multi_turn']}")
        print(f"  Saved to   : {output_path}")

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Files transformed    : {total_files}")
    print(f"Total datapoints     : {total_datapoints}")
    print(f"Single-turn          : {total_single}")
    print(f"Multi-turn           : {total_multi}")
    print(f"Output directory     : {output_dir.resolve()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
