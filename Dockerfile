FROM python:3.6.6-alpine3.8

WORKDIR /

COPY cleaner.py /
COPY scm-source.json /
COPY requirements.txt /

RUN pip install -r requirements.txt

ENTRYPOINT ["/cleaner.py"]
