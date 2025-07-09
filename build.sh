#!/bin/bash

# Replace the version in main.py
# Get the current version from the pyproject.toml
current_version=$(grep -o 'version = "[^"]*"' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "Current version: $current_version"

# Update the version in main.py
sed -i '' "s/__VERSION__ = \".*\"/__VERSION__ = \"$current_version\"/" src/cspcli/main.py
echo "Updated version in main.py"

# Build the package
python -m build
