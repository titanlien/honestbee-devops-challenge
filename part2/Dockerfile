FROM python:2.7.13-alpine

MAINTAINER Titan Lien <titan.lien@gmail.com>

RUN pip install docker

VOLUME /var/run/docker.sock

COPY list_tag.py /app/
WORKDIR /app

CMD ["python", "list_tag.py"]
