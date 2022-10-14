# syntax=docker/dockerfile:1

FROM python:3.10.0-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN echo "deb http://deb.debian.org/debian bullseye-backports main" | tee "/etc/apt/sources.list.d/streamlink.list"
RUN apt update && apt -t bullseye-backports install streamlink -y && apt install -y ffmpeg

COPY . .

CMD [ "python3", "record.py"]