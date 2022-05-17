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

# build database
python main.py rebuild
# run the script
python main.py
```

### levels

- Group

```mermaid
graph TD;
    INCOMING([Messages])
    CHOICE_SERVICE{service}
    CHOICE_BLACKLIST{in blacklist}

    END([END])
    
    subgraph black list user
    BLACKLIST_START([start])
    --> BLACKLIST_DELETE_MESSAGES[Delete messages from user] 
    --> BLACKLIST_BAN_USER[Ban user]
    --> BLACKLIST_END([end])
    end
    
    INCOMING --> CHOICE_SERVICE
    CHOICE_SERVICE --> |Yes| CHOICE_BLACKLIST
    CHOICE_SERVICE --> |No| END
    CHOICE_BLACKLIST --> |Yes| BLACKLIST_START
    CHOICE_BLACKLIST --> |No| END
```

### docker

- due to docker limit, it is not possible to login inside docker image.
- docker is not support until I have idea how to login with docker container.

## author

- [allen0099](https://github.com/allen0099)
