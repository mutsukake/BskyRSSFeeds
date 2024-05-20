#!/bin/zsh

# Initialize Pyenv
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
if command -v pyenv 1>/dev/null 2>&1; then
  eval "$(pyenv init --path)"
  eval "$(pyenv virtualenv-init -)"
fi

# Activate the virtual environment
source "$(dirname "$0")"/venv/bin/activate

# Run the Python script with the absolute path to the Python executable
"$(dirname "$0")"/venv/bin/python "$(dirname "$0")"/main.py
