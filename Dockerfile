# FROM  nexus:443/python:3.8
FROM python:3.8
USER root
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./app
WORKDIR /app
RUN python3 -m pip install -U pip
RUN apt update
RUN apt install docker.io -y
RUN apt install ffmpeg
EXPOSE 8000