# TCP Security System Docker Management

.PHONY: help build run demo shell logs health clean stop restart

# Default target
help: ## Show this help message
	@echo "🔐 TCP Security System Docker Commands"
	@echo "====================================="
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build the TCP Security Docker image
	@echo "🔨 Building TCP Security System..."
	docker-compose build

run: ## Start the TCP Security System
	@echo "🚀 Starting TCP Security System..."
	docker-compose up -d
	@echo "✅ System started! Use 'make shell' to access."

demo: ## Run the demonstration menu
	@echo "🎬 Starting TCP Security Demo..."
	docker-compose exec tcp-security /tcp-security/run-demo.sh

shell: ## Access the interactive TCP shell
	@echo "🐚 Accessing TCP Security Shell..."
	docker-compose exec tcp-security /tcp-security/tcp-shell.sh

bash: ## Access basic bash shell
	@echo "🐚 Accessing container bash..."
	docker-compose exec tcp-security bash

logs: ## Show container logs
	@echo "📋 Showing container logs..."
	docker-compose logs -f tcp-security

health: ## Check system health
	@echo "🏥 Checking system health..."
	docker-compose exec tcp-security /tcp-security/health-check.sh

status: ## Show container status
	@echo "📊 Container status:"
	docker-compose ps

stop: ## Stop the TCP Security System
	@echo "🛑 Stopping TCP Security System..."
	docker-compose down

restart: ## Restart the system
	@echo "🔄 Restarting TCP Security System..."
	docker-compose restart

clean: ## Clean up containers and images
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v
	docker system prune -f
	@echo "✅ Cleanup complete"

# Development targets
dev-build: ## Build without cache for development
	@echo "🔨 Building TCP Security System (no cache)..."
	docker-compose build --no-cache

dev-run: ## Run with logs for development
	@echo "🚀 Starting TCP Security System (development mode)..."
	docker-compose up

# Quick analysis targets
analyze-rm: ## Quick analysis of 'rm' command
	@echo "🔍 Analyzing 'rm' command..."
	docker-compose exec tcp-security bash -c "python3 -c \"from tcp.local_ollama_demo import OllamaLLMProcessor; from tcp.enrichment.manpage_enricher import ManPageEnricher; enricher = ManPageEnricher(); man_data = enricher.enrich_command('rm'); print(f'Security: {man_data.security_level.value if man_data else \"Failed\"}')\""

analyze-sudo: ## Quick analysis of 'sudo' command  
	@echo "🔍 Analyzing 'sudo' command..."
	docker-compose exec tcp-security bash -c "python3 -c \"from tcp.local_ollama_demo import OllamaLLMProcessor; from tcp.enrichment.manpage_enricher import ManPageEnricher; enricher = ManPageEnricher(); man_data = enricher.enrich_command('sudo'); print(f'Security: {man_data.security_level.value if man_data else \"Failed\"}')\""

# Ollama management
ollama-status: ## Check Ollama status
	@echo "🦙 Checking Ollama status..."
	docker-compose exec tcp-security ollama ps

ollama-models: ## List Ollama models
	@echo "🦙 Listing Ollama models..."
	docker-compose exec tcp-security ollama list

ollama-pull-model: ## Pull additional Ollama model (usage: make ollama-pull-model MODEL=mistral)
	@echo "🦙 Pulling model: $(MODEL)"
	docker-compose exec tcp-security ollama pull $(MODEL)

# System information
info: ## Show system information
	@echo "📊 TCP Security System Information"
	@echo "=================================="
	@echo "Docker Compose Version:"
	@docker-compose version --short
	@echo ""
	@echo "Container Status:"
	@docker-compose ps
	@echo ""
	@echo "Volume Usage:"
	@docker volume ls | grep tcp

# Complete workflow
setup: build run ## Complete setup: build and run
	@echo "🎉 TCP Security System setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  make shell   - Access interactive shell"
	@echo "  make demo    - Run demonstrations"
	@echo "  make health  - Check system health"

# Advanced targets
backup-volumes: ## Backup persistent volumes
	@echo "💾 Backing up volumes..."
	docker run --rm -v tcp_data:/data -v tcp_cache:/cache -v ollama_models:/models -v $(PWD)/backup:/backup alpine tar czf /backup/tcp_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz -C / data cache models

restore-volumes: ## Restore from backup (usage: make restore-volumes BACKUP=tcp_backup_20231201_120000.tar.gz)
	@echo "🔄 Restoring from backup: $(BACKUP)"
	docker run --rm -v tcp_data:/data -v tcp_cache:/cache -v ollama_models:/models -v $(PWD)/backup:/backup alpine tar xzf /backup/$(BACKUP) -C /

# Integration tests
test-local: ## Test local Ollama integration
	@echo "🧪 Testing local Ollama integration..."
	docker-compose exec tcp-security python3 tcp/local_ollama_demo.py

test-security: ## Test security system
	@echo "🧪 Testing security system..."
	docker-compose exec tcp-security python3 tcp/demo_complete_security_system.py