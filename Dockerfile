FROM python:3.6.6-alpine3.8

WORKDIR /

COPY requirements.txt /
RUN pip install -r requirements.txt

COPY cleaner.py /
COPY scm-source.json /

ENTRYPOINT ["/cleaner.py"]
