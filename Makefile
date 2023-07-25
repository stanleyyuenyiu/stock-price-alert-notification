SHELL = /bin/bash

.PHONY: api
api:
	cd src && uvicorn applications.api.main:app --reload

.PHONY: consumer-outbox
consumer-outbox:
	cd src && python3 consumer.py -c outbox

.PHONY: consumer-match
consumer-match:
	cd src && python3 consumer.py -c consumer_search_alert

.PHONY: broker-up
broker-up:
	docker-compose -f docker-compose-kafka.yml up

.PHONY: broker-down
broker-down:
	docker-compose -f docker-compose-kafka.yml down

.PHONY: elk-up
elk-up:
	docker-compose -f docker-compose-elk.yml up

.PHONY: elk-down
elk-down:
	docker-compose -f docker-compose-elk.yml down

.PHONY: migration
migration:
	alembic upgrade head

.PHONY: migration-rev
migration-rev:
	@read -p "Enter Revision Name:" revision; \
	cd src && alembic revision -m "$$revision"