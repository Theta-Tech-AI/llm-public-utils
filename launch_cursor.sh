#!/bin/bash

# Define parameters
DOWNLOADS_DIR="$HOME/Downloads"
CURSOR_PATTERN="cursor-*.AppImage"
SSH_KEY_PATH="$HOME/.ssh/id_ed25519"
NO_SANDBOX_OPTION="--no-sandbox"

# Find the highest version of Cursor AppImage in the Downloads directory
latest_cursor=$(find "$DOWNLOADS_DIR" -name "$CURSOR_PATTERN" | sort -V | tail -n 1)

if [ -z "$latest_cursor" ]; then
    echo "No Cursor AppImage found in $DOWNLOADS_DIR"
    exit 1
fi

# Load the SSH identity key
if [ -f "$SSH_KEY_PATH" ]; then
    eval "$(ssh-agent -s)"
    ssh-add "$SSH_KEY_PATH"
else
    echo "SSH key not found: $SSH_KEY_PATH"
fi

# Run the latest Cursor AppImage with --no-sandbox option
"$latest_cursor" "$NO_SANDBOX_OPTION"
