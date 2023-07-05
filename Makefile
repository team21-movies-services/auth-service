create_network:
	@docker network create movies-network 2>/dev/null || echo "movies-network is up-to-date"
	@docker network create auth-network 2>/dev/null || echo "auth-network is up-to-date"

create_test_network:
	@docker network create test-auth-network 2>/dev/null || echo "test-auth-network is up-to-date"

# prod start
.PHONY: up
up: create_network ## up services
	@docker-compose -f docker-compose.override.yml -f docker-compose.yml up -d

.PHONY: logs
logs: ## tail logs services
	@docker-compose -f docker-compose.override.yml -f docker-compose.yml logs -n 1000 -f

.PHONY: down
down: ## down services
	@docker-compose -f docker-compose.override.yml -f docker-compose.yml down

.PHONY: build
build: ## build services
	@docker-compose -f docker-compose.override.yml -f docker-compose.yml build

.PHONY: restart
restart: down up ## restart services

.PHONY: uninstall
uninstall: ## uninstall all services
	@docker-compose -f docker-compose.override.yml -f docker-compose.yml down --remove-orphans --volumes
# prod end

# local start

.PHONY: up-local
up-local: create_network ## up local services
	@docker-compose -f docker-compose.local.yml -f docker-compose.override.yml up -d

.PHONY: down-local
down-local: ## down local services
	@docker-compose -f docker-compose.local.yml -f docker-compose.override.yml down

.PHONY: build-local
build-local: ## build local services
	@docker-compose -f docker-compose.local.yml -f docker-compose.override.yml build --force-rm

.PHONY: build-force-local
build-force-local: ## build force services
	@docker-compose -f docker-compose.local.yml -f docker-compose.override.yml build --no-cache

.PHONY: logs-local
logs-local: ## logs local services
	@docker-compose -f docker-compose.local.yml -f docker-compose.override.yml logs -f

.PHONY: restart-local
restart-local: down-local up-local ## logs local services

.PHONY: uninstall-local
uninstall-local: ## uninstall local services
	@docker-compose -f docker-compose.override.yml -f docker-compose.local.yml down --remove-orphans --volumes

# local end

# test start
.PHONY: up-test
up-test: create_test_network ## up test services
	@docker-compose -p test_auth_api -f docker-compose.test.yml up

.PHONY: down-test
down-test: ## down test services
	@docker-compose -p test_auth_api -f docker-compose.test.yml down

.PHONY: run-test
run-test: create_test_network ## run and uninstall tests services
	@docker-compose -p test_auth_api -f docker-compose.test.yml up --abort-on-container-exit

.PHONY: build-test
build-test: create_test_network
	@docker-compose -p test_auth_api -f docker-compose.test.yml build --force-rm

.PHONY: logs-test
logs-test: ## logs test services
	@docker-compose -p test_auth_api -f docker-compose.test.yml logs -f

.PHONY: uninstall-test
uninstall-test: ## uninstall test services
	@docker-compose -p test_auth_api -f docker-compose.test.yml down --remove-orphans --volumes
# test end

.PHONY: help
help: ## Help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort -d | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

