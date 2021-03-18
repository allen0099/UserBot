FROM python:3.9-alpine

WORKDIR /usr/src/app

RUN apk add --no-cache build-base

RUN apk add --no-cache musl-dev libffi-dev openssl-dev cargo

RUN apk add git

RUN git clone https://github.com/allen0099/UserBot .

RUN pip install --no-cache-dir -r requirements.txt

ARG API_ID
ARG API_HASH

COPY config.ini.example config.ini

RUN sed -i 's/api_id = .*/api_id = '${API_ID}'/g' config.ini
RUN sed -i 's/api_hash = .*/api_hash = '${API_HASH}'/g' config.ini

ARG DB_DATABASE
ARG DB_USERNAME
ARG DB_PASSWORD

COPY .env.example .env

RUN sed -i '/API_*/d' .env
RUN sed -i 's/DB_HOST=.*/DB_HOST=mysql/g' .env
RUN sed -i 's/DB_DATABASE=.*/DB_DATABASE='${DB_DATABASE}'/g' .env
RUN sed -i 's/DB_USERNAME=.*/DB_USERNAME='${DB_USERNAME}'/g' .env
RUN sed -i 's/DB_PASSWORD=.*/DB_PASSWORD='${DB_PASSWORD}'/g' .env

RUN cp empty.session bot.session

CMD [ "python", "./main.py" ]