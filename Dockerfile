FROM ubuntu:16.04

MAINTAINER Justin John "justinjohn7895@gmail.com"

RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update

RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip python3.6-venv

RUN python3.6 -m pip install pip --upgrade
RUN python3.6 -m pip install wheel

COPY ./requirements.txt /mood_app/requirements.txt

WORKDIR /mood_app

RUN pip install -r requirements.txt

COPY . /mood_app

ENTRYPOINT [ "python3.6" ]

EXPOSE 5000
CMD [ "mood_app.py" ]
