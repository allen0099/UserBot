#!/bin/bash

SCRIPT=$(readlink -f "$0")
SCRIPT_PATH=$(dirname "$SCRIPT")
PROGRAM_ROOT="$(dirname "$SCRIPT_PATH")"
PYTHON_VERSION="3.10"

function failed() {
  local error=${1:-Undefined error}
  echo "Failed: $error" >&2
  exit 1
}

function venv_notfound() {
  rm -rf "${PROGRAM_ROOT}/venv"
  failed "Python venv not installed!"
}

function install_requirement() {
  sudo apt install python$PYTHON_VERSION-dev libpq-dev
}

# Check python is installed
if [ ! -x "$(command -v "python$PYTHON_VERSION")" ]; then
  failed "Python$PYTHON_VERSION could not be found"
else
  if [ ! -d "${PROGRAM_ROOT}/venv" ]; then
    echo "Creating new venv folder!"
    python$PYTHON_VERSION -m venv "${PROGRAM_ROOT}/venv" || venv_notfound
  fi
fi

cd "${PROGRAM_ROOT}"
source "${PROGRAM_ROOT}/venv/bin/activate" || failed "Failed to activate virtual environment!"
pip install -r requirements.txt || failed "Failed to install requirements!"
alembic upgrade head || failed "Failed to upgrade database!"

echo "Prepare finished!"
exit 0
