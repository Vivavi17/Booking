#!/bin/bash

if [ "${1}" == "celery" ]; then
  celery --app=tasks.celery_app:celery_app worker -l INFO
elif [ "${1}" == "flower" ]; then
  celery --app=tasks.celery_app:celery_app flower
fi