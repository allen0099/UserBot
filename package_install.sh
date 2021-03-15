#!/bin/bash

sudo apt install python3.9 python3.9-venv -y

if [ ! -d "./venv" ]; then
  python3.9 -m venv venv
  source venv/bin/activate

  cp .env.example .env
  cp config.ini.example config.ini
else
  echo "Virtual environment exist!"
fi

#sudo apt-get install gcc libpq-dev -y
#sudo apt-get install python-dev  python-pip -y
#sudo apt-get install python3-dev python3-pip python3-venv python3-wheel -y
#pip3 install wheel

pip install -r requirements.txt
pip install -U SQLAlchemy
pip install -U PyMySQL
pip install -U python-dotenv
pip install -U pyrogram tgcrypto
