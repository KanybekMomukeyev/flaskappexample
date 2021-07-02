# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

WORKDIR /app

RUN apt-get update
RUN apt install -y libgl1-mesa-glx
RUN apt-get install -y libglib2.0-0 libsm6 libxrender1 libxext6

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

# git pull
# docker build --tag python-docker .
# docker run -d -p 5000:5000 python-docker