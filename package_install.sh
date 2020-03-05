#!/bin/bash

python3 -m venv venv
source venv/bin/activate

pip3 install -U https://github.com/pyrogram/pyrogram/archive/develop.zip
pip3 install -U tgcrypto

cp config.ini.example config.ini
