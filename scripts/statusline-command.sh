#!/bin/bash

# NOTE: MODIFY ~/.claude/settings.json to add this:
# {
#    "statusLine": {
#      "type": "command",
#      "command": "~/.claude/statusline-command.sh"
#    }
#  }

# Read JSON input from stdin
INPUT=$(cat)

# Extract values from JSON
CWD=$(echo "$INPUT" | jq -r '.workspace.current_dir')
MODEL_NAME=$(echo "$INPUT" | jq -r '.model.display_name')
TRANSCRIPT_PATH=$(echo "$INPUT" | jq -r '.transcript_path')

# ANSI color codes
RESET='\033[00m'
GREEN='\033[01;32m'
BLUE='\033[01;34m'
YELLOW='\033[01;33m'
RED='\033[01;31m'
CYAN='\033[01;36m'
MAGENTA='\033[01;35m'
DIM='\033[02m'

# User and hostname
USER_HOST=$(printf "${GREEN}%s@%s${RESET}" "$(whoami)" "$(hostname -s)")

# Current directory
DIR_PATH=$(printf "${BLUE}%s${RESET}" "$CWD")

# Git information
GIT_INFO=""
if git -C "$CWD" rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git -C "$CWD" branch --show-current 2>/dev/null || git -C "$CWD" rev-parse --short HEAD 2>/dev/null)

    # Check if repo is dirty (skip optional locks for performance)
    if git -C "$CWD" diff --quiet --no-optional-locks 2>/dev/null && \
       git -C "$CWD" diff --cached --quiet --no-optional-locks 2>/dev/null; then
        GIT_STATUS=$(printf "${GREEN}✓${RESET}")
    else
        GIT_STATUS=$(printf "${RED}✗${RESET}")
    fi

    GIT_INFO=$(printf " ${DIM}|${RESET} ${CYAN}⎇ %s${RESET} %s" "$BRANCH" "$GIT_STATUS")
fi

# Python virtual environment
VENV_INFO=""
if [ -n "$CONDA_DEFAULT_ENV" ]; then
    VENV_INFO=$(printf " ${DIM}|${RESET} ${YELLOW}🐍 %s${RESET}" "$CONDA_DEFAULT_ENV")
elif [ -n "$VIRTUAL_ENV" ]; then
    VENV_NAME=$(basename "$VIRTUAL_ENV")
    VENV_INFO=$(printf " ${DIM}|${RESET} ${YELLOW}🐍 %s${RESET}" "$VENV_NAME")
fi

# Claude model
MODEL_INFO=$(printf " ${DIM}|${RESET} ${MAGENTA}🤖 %s${RESET}" "$MODEL_NAME")

# Session metrics from JSON input
SESSION_METRICS=""
# Extract cost and metrics from the JSON input (not transcript file)
TOTAL_COST=$(echo "$INPUT" | jq -r '.cost.total_cost_usd // 0' 2>/dev/null || echo 0)
COST=$(awk "BEGIN {printf \"%.2f\", $TOTAL_COST}")

# Get duration from the JSON input
TOTAL_DURATION_MS=$(echo "$INPUT" | jq -r '.cost.total_duration_ms // 0' 2>/dev/null || echo 0)

# Calculate tokens from transcript JSONL file
if [ -f "$TRANSCRIPT_PATH" ]; then
    # JSONL format: each line is a JSON object, use -s to slurp into array
    # Calculate total tokens used (input + output)
    TOTAL_INPUT_TOKENS=$(jq -s '[.[] | select(.message.usage != null) | .message.usage.input_tokens // 0] | add // 0' "$TRANSCRIPT_PATH" 2>/dev/null || echo 0)
    TOTAL_OUTPUT_TOKENS=$(jq -s '[.[] | select(.message.usage != null) | .message.usage.output_tokens // 0] | add // 0' "$TRANSCRIPT_PATH" 2>/dev/null || echo 0)
    TOTAL_TOKENS=$((TOTAL_INPUT_TOKENS + TOTAL_OUTPUT_TOKENS))

    # Get cache tokens if available
    CACHE_READ_TOKENS=$(jq -s '[.[] | select(.message.usage != null) | .message.usage.cache_read_input_tokens // 0] | add // 0' "$TRANSCRIPT_PATH" 2>/dev/null || echo 0)
    CACHE_WRITE_TOKENS=$(jq -s '[.[] | select(.message.usage != null) | .message.usage.cache_creation_input_tokens // 0] | add // 0' "$TRANSCRIPT_PATH" 2>/dev/null || echo 0)

    # Format tokens (K for thousands)
    if [ $TOTAL_TOKENS -ge 1000 ]; then
        TOKENS_DISPLAY=$(awk "BEGIN {printf \"%.0fK\", $TOTAL_TOKENS / 1000}")
    else
        TOKENS_DISPLAY="${TOTAL_TOKENS}"
    fi

    # Context window limit for Claude Sonnet 4.5
    CONTEXT_LIMIT="200K"
    CONTEXT_INFO=$(printf "${CYAN}📊 %s/%s${RESET}" "$TOKENS_DISPLAY" "$CONTEXT_LIMIT")

    # Add cache info if cache tokens are present
    CACHE_INFO=""
    if [ $CACHE_READ_TOKENS -gt 0 ] || [ $CACHE_WRITE_TOKENS -gt 0 ]; then
        if [ $CACHE_READ_TOKENS -ge 1000 ]; then
            CACHE_READ_DISPLAY=$(awk "BEGIN {printf \"%.0fK\", $CACHE_READ_TOKENS / 1000}")
        else
            CACHE_READ_DISPLAY="${CACHE_READ_TOKENS}"
        fi
        if [ $CACHE_WRITE_TOKENS -ge 1000 ]; then
            CACHE_WRITE_DISPLAY=$(awk "BEGIN {printf \"%.0fK\", $CACHE_WRITE_TOKENS / 1000}")
        else
            CACHE_WRITE_DISPLAY="${CACHE_WRITE_TOKENS}"
        fi
        CACHE_INFO=$(printf " ${DIM}(cache: R:%s W:%s)${RESET}" "$CACHE_READ_DISPLAY" "$CACHE_WRITE_DISPLAY")
    fi

    # Calculate duration from milliseconds
    DURATION_SEC=$((TOTAL_DURATION_MS / 1000))

    if [ $DURATION_SEC -ge 3600 ]; then
        DURATION=$(printf "%dh %dm" $((DURATION_SEC / 3600)) $(((DURATION_SEC % 3600) / 60)))
    elif [ $DURATION_SEC -ge 60 ]; then
        DURATION=$(printf "%dm" $((DURATION_SEC / 60)))
    else
        DURATION=$(printf "%ds" $DURATION_SEC)
    fi

    SESSION_METRICS=$(printf " ${DIM}|${RESET} %s%s ${DIM}|${RESET} ${CYAN}💰 \$%s${RESET} ${DIM}|${RESET} ${CYAN}⏱ %s${RESET}" "$CONTEXT_INFO" "$CACHE_INFO" "$COST" "$DURATION")
else
    # No transcript file available yet
    DURATION="0s"
    SESSION_METRICS=$(printf " ${DIM}|${RESET} ${CYAN}💰 \$%s${RESET} ${DIM}|${RESET} ${CYAN}⏱ %s${RESET}" "$COST" "$DURATION")
fi

# Combine all parts
printf "%s:%s%s%s%s%s\n" "$USER_HOST" "$DIR_PATH" "$GIT_INFO" "$VENV_INFO" "$MODEL_INFO" "$SESSION_METRICS"
