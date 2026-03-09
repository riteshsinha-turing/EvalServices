#!/usr/bin/env bash
# Generate .insights.md for every .json file under eval_results (any subdirectory).
# Output files are written next to each source JSON in the same directory.
# Run from eval_results: ./generate_all_insights.sh
# With LLM: ./generate_all_insights.sh --llm

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

USE_LLM=""
[[ "${1:-}" == "--llm" ]] && USE_LLM="--llm"

while IFS= read -r -d '' json_path; do
  dir="$(dirname "$json_path")"
  base="$(basename "$json_path" .json)"
  out_path="$dir/${base}.insights.md"
  echo ">>> $json_path -> $out_path"
  python generate_eval_insights.py "$json_path" --output "$out_path" $USE_LLM
done < <(find . -type f -name "*.json" -print0 | sort -z)

echo "Done."
