FROM python:3.11

COPY . /enrich
WORKDIR /enrich
RUN pip install .

ENTRYPOINT ["enrich"]