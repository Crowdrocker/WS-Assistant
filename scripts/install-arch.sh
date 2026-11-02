#!/usr/bin/env bash
set -euo pipefail
sudo pacman -S --needed python python-pip git
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[dev]"
if [[ ! -f config/assistant.yaml ]]; then
  cp config/assistant.example.yaml config/assistant.yaml
fi
echo "Installed. Activate with: source .venv/bin/activate"
echo "Try: ws-assistant status"
