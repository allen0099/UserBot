#!/bin/bash

if [ ! -d "./venv" ]; then
  python3 -m venv venv
  source venv/bin/activate
fi

python3 main.py
