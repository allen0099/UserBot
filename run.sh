#!/bin/bash

if [ ! -d "./venv" ]; then
  ./package_install.sh
fi
source venv/bin/activate
python3 main.py
