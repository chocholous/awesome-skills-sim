#!/usr/bin/env bash
# lint_telemetry.sh — verify every apify CLI invocation in SKILL.md files
# follows the three telemetry rules from CONTRIBUTING.md:
#   Rule 1 — --user-agent apify-awesome-skills/<skill-name>
#   Rule 2 — --json (or --format json for `datasets get-items`)
#   Rule 3 — 2>/dev/null stderr redirect
# Exception: commands fetching an Actor README (--readme) return markdown,
# not JSON — Rules 2 and 3 do not apply to them (Rule 1 still does).
#
# Only lines INSIDE fenced code blocks (``` ... ```) are checked.
# Prose mentions of apify commands are ignored.
#
# Exit 0 if all checks pass, exit 1 if any violation is found.
# Requires bash 4+ (available on all GitHub Actions runners).

set -euo pipefail

FAIL=0
WINDOW=5  # lines after a CLI command to look for the --user-agent flag

# Patterns that signal an apify CLI invocation
CLI_PATTERNS=(
  "apify actors call"
  "apify actors run"
  "apify actors info"
  "apify datasets get-items"
  "apify call"
  "apify run"
)

# Find all SKILL.md files under skills/
SKILL_FILES=()
while IFS= read -r f; do
  SKILL_FILES+=("$f")
done < <(find skills -name "SKILL.md" | sort)

if [ ${#SKILL_FILES[@]} -eq 0 ]; then
  echo "lint: no SKILL.md files found under skills/"
  exit 0
fi

for file in "${SKILL_FILES[@]}"; do
  # Read file lines into indexed array
  idx=0
  unset LINES
  declare -a LINES
  while IFS= read -r raw_line; do
    LINES[$idx]="$raw_line"
    (( idx++ )) || true
  done < "$file"
  total=${#LINES[@]}

  in_code_block=0

  for (( i=0; i<total; i++ )); do
    line="${LINES[$i]}"

    # Track fenced code block boundaries (``` or ~~~)
    if [[ "$line" =~ ^[[:space:]]*(\`\`\`|~~~) ]]; then
      if [ "$in_code_block" -eq 0 ]; then
        in_code_block=1
      else
        in_code_block=0
      fi
      continue
    fi

    # Only check lines inside code blocks
    [ "$in_code_block" -eq 0 ] && continue

    # Skip shell comment lines
    if [[ "$line" =~ ^[[:space:]]*# ]]; then
      continue
    fi

    # Check if this line contains any CLI trigger pattern
    matched=0
    for pat in "${CLI_PATTERNS[@]}"; do
      if [[ "$line" == *"$pat"* ]]; then
        matched=1
        break
      fi
    done
    [ "$matched" -eq 0 ] && continue

    # Look for the required flags on this line or within WINDOW lines
    found_ua=0
    found_json=0
    found_stderr=0
    has_readme=0
    end=$(( i + WINDOW ))
    [ $end -ge $total ] && end=$(( total - 1 ))

    for (( j=i; j<=end; j++ )); do
      window_line="${LINES[$j]}"
      [[ "$window_line" == *"--user-agent apify-awesome-skills/"* ]] && found_ua=1
      if [[ "$window_line" == *"--json"* ]] || [[ "$window_line" == *"--format json"* ]]; then
        found_json=1
      fi
      [[ "$window_line" == *"2>/dev/null"* ]] && found_stderr=1
      [[ "$window_line" == *"--readme"* ]] && has_readme=1
      # Stop at the closing fence of the code block
      if [ "$j" -gt "$i" ] && [[ "$window_line" =~ ^[[:space:]]*(\`\`\`|~~~) ]]; then
        break
      fi
      # Stop at blank lines unless the previous line is a continuation (\)
      if [ "$j" -gt "$i" ]; then
        prev="${LINES[$((j-1))]}"
        if [[ "$prev" != *\\ ]] && [[ -z "${window_line// /}" ]]; then
          break
        fi
      fi
    done

    lineno=$(( i + 1 ))
    clean_line="$(printf '%s' "$line" | sed 's/^[[:space:]]*//')"

    if [ "$found_ua" -eq 0 ]; then
      echo "lint: $file:$lineno: missing --user-agent apify-awesome-skills/ flag"
      echo "      offending line: $clean_line"
      FAIL=$(( FAIL + 1 ))
    fi

    # Rules 2 + 3 do not apply to README fetches (--readme output is markdown)
    if [ "$has_readme" -eq 0 ]; then
      if [ "$found_json" -eq 0 ]; then
        echo "lint: $file:$lineno: missing --json flag (or --format json for datasets get-items)"
        echo "      offending line: $clean_line"
        FAIL=$(( FAIL + 1 ))
      fi
      if [ "$found_stderr" -eq 0 ]; then
        echo "lint: $file:$lineno: missing 2>/dev/null stderr redirect"
        echo "      offending line: $clean_line"
        FAIL=$(( FAIL + 1 ))
      fi
    fi
  done
done

if [ "$FAIL" -gt 0 ]; then
  echo ""
  echo "lint: $FAIL violation(s) found."
  echo "      Every apify CLI call in SKILL.md code blocks must include:"
  echo "        --user-agent apify-awesome-skills/<skill-dir-name>"
  echo "        --json (or --format json for datasets get-items)"
  echo "        2>/dev/null"
  echo "      Exception: --readme commands are exempt from --json and 2>/dev/null."
  echo "      See CONTRIBUTING.md § 'Telemetry on CLI commands' for details."
  exit 1
fi

echo "lint: all SKILL.md telemetry checks passed."
exit 0
