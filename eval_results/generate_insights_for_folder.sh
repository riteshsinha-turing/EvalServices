#!/usr/bin/env bash
# Generate .insights.md for every .json in a single folder, then build a comparison report.
# Usage (run from eval_results):
#   ./generate_insights_for_folder.sh redteam/05-multi-turn-guardrail-decay
#   ./generate_insights_for_folder.sh redteam/05-multi-turn-guardrail-decay --llm
#   ./generate_insights_for_folder.sh redteam/05-multi-turn-guardrail-decay -o comparison.md
#
# Options:
#   --llm           Add LLM-generated narrative to each report and to comparison
#   --llm-summaries Use LLM to generate per-model summary in comparison (with --llm for compare)
#   -o FILE         Comparison output filename (default: <folder-name>.comparison.md in that folder)

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

FOLDER="${1:-}"
if [[ -z "$FOLDER" || ! -d "$FOLDER" ]]; then
  echo "Usage: $0 <folder> [--llm] [--llm-summaries] [-o comparison.md]" >&2
  echo "  folder: path under eval_results, e.g. redteam/05-multi-turn-guardrail-decay" >&2
  exit 1
fi
shift || true

USE_LLM=""
USE_LLM_SUMMARIES=""
COMPARISON_OUT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --llm)           USE_LLM="--llm"; shift ;;
    --llm-summaries) USE_LLM_SUMMARIES="--llm-summaries"; shift ;;
    -o)              COMPARISON_OUT="$2"; shift 2 ;;
    *)               echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

# Default comparison output: <folder-basename>.comparison.md in that folder
if [[ -z "$COMPARISON_OUT" ]]; then
  BASE_NAME="$(basename "$FOLDER")"
  COMPARISON_OUT="$FOLDER/${BASE_NAME}.comparison.md"
fi

echo ">>> Target folder: $FOLDER"
echo ">>> Comparison output: $COMPARISON_OUT"
echo ""

# 1) Generate insights for each JSON in the folder only
INSIGHTS=()
while IFS= read -r -d '' json_path; do
  dir="$(dirname "$json_path")"
  base="$(basename "$json_path" .json)"
  out_path="$dir/${base}.insights.md"
  echo ">>> $json_path -> $out_path"
  python generate_eval_insights.py "$json_path" --output "$out_path" $USE_LLM
  INSIGHTS+=("$out_path")
done < <(find "$FOLDER" -maxdepth 1 -type f -name "*.json" -print0 | sort -z)

if [[ ${#INSIGHTS[@]} -eq 0 ]]; then
  echo "No .json files found in $FOLDER" >&2
  exit 1
fi

echo ""
echo ">>> Building comparison from ${#INSIGHTS[@]} reports -> $COMPARISON_OUT"
python generate_eval_insights.py compare "${INSIGHTS[@]}" -o "$COMPARISON_OUT" $USE_LLM $USE_LLM_SUMMARIES

echo "Done."
