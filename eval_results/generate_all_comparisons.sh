#!/usr/bin/env bash
# Generate insights.comparison.md in every directory that contains one or more
# *.insights.md files. Each comparison aggregates all model insights in that directory.
# Run from eval_results: ./generate_all_comparisons.sh
# With LLM narrative: ./generate_all_comparisons.sh --llm
# With progress logs:  ./generate_all_comparisons.sh -v   or   --llm -v

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

USE_LLM=""
VERBOSE=""
for arg in "$@"; do
  [[ "$arg" == "--llm" ]] && USE_LLM="--llm"
  [[ "$arg" == "-v" || "$arg" == "--verbose" ]] && VERBOSE="-v"
done

# Find all directories that contain at least one .insights.md file (individual model reports)
dirs_with_insights="$(find . -type f -name "*.insights.md" -exec dirname {} \; | sort -u)"

shopt -s nullglob
for dir in $dirs_with_insights; do
  insight_files=("$dir"/*.insights.md)
  # insights.comparison.md does not match *.insights.md, so we get only model reports
  if [[ ${#insight_files[@]} -lt 1 ]]; then
    continue
  fi
  out_path="$dir/insights.comparison.md"
  echo ">>> Comparing ${#insight_files[@]} reports in $dir -> $out_path"
  python generate_eval_insights.py compare "${insight_files[@]}" --output "$out_path" $USE_LLM $VERBOSE
done
shopt -u nullglob

echo "Done."
