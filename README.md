# Userbot

## run

### venv run

```shell
python3 -m vnev venv
source venv/bin/activate
# some libraries require, Google for each distro
pip install -r requirements.txt

# edit configs
cp .env.example .env
cp config.ini.example config.ini

# build database
python main.py rebuild
# run the script
python main.py
```

### docker run

- docker
- docker-compose

```shell
cp .env.example .env
# edit .env file


# login Telegram
# I don't know how to login without terminal

docker-compose up --build -d userbot mysql
```

## author

- [allen0099](https://github.com/allen0099)
