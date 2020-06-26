#!/bin/bash

if [ ! -d "./venv" ]; then
  python3 -m venv venv
  source venv/bin/activate

  cp config.ini.example config.ini
else
  echo "Virtual environment exist!"
fi

pip3 install -U https://github.com/pyrogram/pyrogram/archive/develop.zip
pip3 install -U tgcrypto
pip3 install -r requirements.txt
