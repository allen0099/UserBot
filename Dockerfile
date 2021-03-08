FROM python:3.9-alpine

WORKDIR /usr/src/app

RUN apk add --no-cache  build-base

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]