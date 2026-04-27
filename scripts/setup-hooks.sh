#!/bin/bash
# Setup pre-commit hooks for PashuRaksha development
set -euo pipefail

if ! command -v pre-commit &>/dev/null; then
  echo "Installing pre-commit..."
  pip install pre-commit
fi

pre-commit install
pre-commit install --hook-type pre-push
echo "Pre-commit hooks installed successfully."
