FROM ubuntu:16.04

MAINTAINER Your Name "justinjohn7895@gmail.com"

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

COPY ./requirements.txt /mood_app/requirements.txt

WORKDIR /mood_app

RUN pip install -r requirements.txt

COPY . /mood_app

ENTRYPOINT [ "python" ]

EXPOSE 5000
CMD [ "mood_app.py" ]