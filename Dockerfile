FROM python:3.9-slim-bullseye

WORKDIR /usr/src/app

# Forces stdout and stderr streams to be unbuffered
#ENV PYTHONUNBUFFERED 1
#ENV TZ="America/New_York"

RUN  apt-get update \
 && apt-get upgrade -y \
 && apt-get install -yq --no-install-recommends \
 && apt-get autoremove -y \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* 


COPY ./..env ./
COPY ./*.py ./
COPY ./requirements.txt ./
RUN mkdir scripts
COPY ./scripts/* ./scripts/


RUN useradd autouser && chown -R autouser /usr/src/app
RUN chown -R autouser:autouser .





#RUN sleep 10000

ENTRYPOINT ["./scripts/entrypoint.sh"]

