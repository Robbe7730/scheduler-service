#!/bin/bash

pylint *.py || exit 1

mypy --install-types --non-interactive
mypy --ignore-missing-imports *.py || exit 1

docker build -t robbe7730/scheduler-service . || exit 1

pushd ../sproeierserver-backend/

docker-compose stop -t 1 scheduler
docker-compose up --build -d scheduler
docker-compose start scheduler

popd
