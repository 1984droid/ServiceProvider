#!/bin/bash
# Wrapper script to generate .env with secure random values

# Change to project root
cd "$(dirname "$0")/.."

python scripts/generate_env.py
