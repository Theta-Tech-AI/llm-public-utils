#!/bin/bash

# Find the highest version of Cursor AppImage in the Downloads directory
latest_cursor=$(find "$HOME/Downloads" -name "cursor-*.AppImage" | sort -V | tail -n 1)

if [ -z "$latest_cursor" ]; then
    echo "No Cursor AppImage found in ~/Downloads"
    exit 1
fi

# Load the SSH identity key
if [ -f "$HOME/.ssh/id_ed25519" ]; then
    eval "$(ssh-agent -s)"
    ssh-add "$HOME/.ssh/id_ed25519"
else
    echo "SSH key not found: $HOME/.ssh/id_ed25519"
fi

# Run the latest Cursor AppImage with --no-sandbox option
"$latest_cursor" --no-sandbox
