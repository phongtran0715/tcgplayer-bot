CURRENT_DIRECTORY := $(shell pwd)
TESTSCOPE = apps
TESTFLAGS = --with-timer --timer-top-n 10 --keepdb


help:
	@echo "Docker Compose Help"
	@echo "-----------------------"
	@echo ""
	@echo "Run tests to ensure current state is good:"
	@echo "    make test"
	@echo ""
	@echo "If tests pass, add fixture data and start up the api:"
	@echo "    make begin"
	@echo ""
	@echo "Really, really start over:"
	@echo "    make clean"
	@echo ""
	@echo "See contents of Makefile for more targets."
.PHONY: help

install-dependencies:
	pip install -r requirements.txt
.PHONY: install-dependencies

test:
	pytest -n 8 --cov --cov-fail-under=40
.PHONY: test

checks:
	python manage.py check
.PHONY: checks

migrate:
	python manage.py migrate --no-input
.PHONY: migrate

make-migration:
	python manage.py makemigrations --merge --no-input
.PHONY: make-migration

collectstatic:
	python manage.py collectstatic --no-input
.PHONY: collectstatic

server:
	python manage.py runserver 0.0.0.0:8000
.PHONY: server

isort:
	isort --atomic .
.PHONY: isort

apply-isort:
	isort .
.PHONY: apply-isort

autopep8:
	autopep8 -ir .
.PHONY: autopep8

flake8:
	flake8 -v --count --show-source --statistics
.PHONY: flake8

celery:
	celery -A tcgplayer worker --autoscale=100,3 --loglevel=info --statedb=/app/worker.state --logfile=logs/celery.log
.PHONY: celery

celery_beat:
	celery -A tcgplayer beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler --logfile=logs/celery.log
.PHONY: celery_beat

dev-setup: \
	make-migration \
	migrate \
	collectstatic
.PHONY: dev-setup

local-ci: \
	autopep8 \
	checks \
	isort \
	flake8
.PHONY: local-ci

private-settings:
	echo 'SECRET_KEY="$(SECRET_KEY)"' > $$(pwd)/tcgplayer/settings/.env
	echo 'ALLOWED_HOSTS="$(ALLOWED_HOSTS)"' >> $$(pwd)/tcgplayer/settings/.env
.PHONY: private-settings