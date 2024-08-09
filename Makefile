
docker: env_file
	docker compose build
	docker compose up

env_file:
ifeq (,$(wildcard .env-no-dev))
	@echo "Creating .env-no-dev file from .env-example..."
	cp .env-example .env-no-dev
endif

clean:
	docker system prune -f

rebuild: clean docker