## Technologies

* [Docker SDK for Python](https://docker-py.readthedocs.io/en/stable/client.html)

## Requirements

To use this example you will need an python virtual environment, and its requirements.txt.

## Usage

### Put list_tag.py into python:2.7.13-alpine
$ docker build . -t titanlien/list_tag

### Launch list_tag.py with local docker socket
$ docker run -ti --rm -v /var/run/docker.sock:/var/run/docker.sock titanlien/list_tag