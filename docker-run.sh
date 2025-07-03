#!/bin/bash

# TCP Security System Docker Runner
# Provides easy commands to build, run, and manage the TCP Docker container

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="tcp-security-system"
IMAGE_NAME="tcp-security"
NETWORK_NAME="tcp-security-network"

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

show_header() {
    echo -e "${BLUE}"
    echo "🐳 TCP Security System Docker Manager"
    echo "====================================="
    echo -e "${NC}"
}

show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build       Build the TCP Security Docker image"
    echo "  run         Run the TCP Security container"
    echo "  start       Start existing container"
    echo "  stop        Stop the container"
    echo "  restart     Restart the container"
    echo "  shell       Open shell in running container"
    echo "  logs        Show container logs"
    echo "  status      Show container status"
    echo "  demo        Run the local Ollama demo"
    echo "  security    Run the security demo"
    echo "  clean       Remove container and image"
    echo "  health      Check container health"
    echo "  compose     Use docker-compose (build/up/down)"
    echo ""
    echo "Examples:"
    echo "  $0 build         # Build the image"
    echo "  $0 run           # Run container interactively"
    echo "  $0 demo          # Run Ollama demo inside container"
    echo "  $0 shell         # Get shell access"
    echo "  $0 compose up    # Use docker-compose to start"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
}

build_image() {
    log_info "Building TCP Security Docker image..."
    
    docker build -t "$IMAGE_NAME" . || {
        log_error "Failed to build Docker image"
        exit 1
    }
    
    log_success "Docker image built successfully: $IMAGE_NAME"
}

run_container() {
    log_info "Running TCP Security container..."
    
    # Stop existing container if running
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        log_warning "Stopping existing container..."
        docker stop "$CONTAINER_NAME" &> /dev/null || true
    fi
    
    # Remove existing container if exists
    if docker ps -aq -f name="$CONTAINER_NAME" | grep -q .; then
        log_warning "Removing existing container..."
        docker rm "$CONTAINER_NAME" &> /dev/null || true
    fi
    
    # Create network if it doesn't exist
    docker network create "$NETWORK_NAME" &> /dev/null || true
    
    # Run container
    docker run -it \
        --name "$CONTAINER_NAME" \
        --hostname tcp-ubuntu \
        --network "$NETWORK_NAME" \
        -p 11434:11434 \
        -p 8080:8080 \
        -v tcp-security-data:/tcp-security/data \
        -v tcp-security-cache:/tcp-security/cache \
        -v tcp-security-logs:/tcp-security/logs \
        -v tcp-ollama-models:/root/.ollama \
        --security-opt no-new-privileges:true \
        --memory="4g" \
        --cpus="2.0" \
        "$IMAGE_NAME"
}

start_container() {
    if ! docker ps -aq -f name="$CONTAINER_NAME" | grep -q .; then
        log_error "Container $CONTAINER_NAME does not exist. Run '$0 run' first."
        exit 1
    fi
    
    log_info "Starting container..."
    docker start "$CONTAINER_NAME"
    log_success "Container started"
}

stop_container() {
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        log_info "Stopping container..."
        docker stop "$CONTAINER_NAME"
        log_success "Container stopped"
    else
        log_warning "Container is not running"
    fi
}

restart_container() {
    log_info "Restarting container..."
    docker restart "$CONTAINER_NAME" &> /dev/null || {
        log_error "Failed to restart container. Container may not exist."
        exit 1
    }
    log_success "Container restarted"
}

open_shell() {
    if ! docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        log_error "Container is not running. Start it with '$0 start' or '$0 run'"
        exit 1
    fi
    
    log_info "Opening shell in container..."
    docker exec -it "$CONTAINER_NAME" /bin/bash
}

show_logs() {
    if ! docker ps -aq -f name="$CONTAINER_NAME" | grep -q .; then
        log_error "Container does not exist"
        exit 1
    fi
    
    log_info "Showing container logs..."
    docker logs -f "$CONTAINER_NAME"
}

show_status() {
    log_info "Container status:"
    
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        echo "  Status: ✅ Running"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" -f name="$CONTAINER_NAME"
        echo ""
        
        # Check health
        health_status=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "no-health-check")
        echo "  Health: $health_status"
        
        # Show resource usage
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" "$CONTAINER_NAME"
        
    elif docker ps -aq -f name="$CONTAINER_NAME" | grep -q .; then
        echo "  Status: ⏹️  Stopped"
        docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" -f name="$CONTAINER_NAME"
    else
        echo "  Status: ❌ Does not exist"
    fi
}

run_demo() {
    if ! docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        log_error "Container is not running. Start it with '$0 start' or '$0 run'"
        exit 1
    fi
    
    log_info "Running local Ollama demo inside container..."
    docker exec -it "$CONTAINER_NAME" bash -c "
        source /tcp-security/venv/bin/activate
        cd /tcp-security
        python tcp/local_ollama_demo.py
    "
}

run_security_demo() {
    if ! docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        log_error "Container is not running. Start it with '$0 start' or '$0 run'"
        exit 1
    fi
    
    log_info "Running complete security demo inside container..."
    docker exec -it "$CONTAINER_NAME" bash -c "
        source /tcp-security/venv/bin/activate
        cd /tcp-security
        python tcp/demo_complete_security_system.py
    "
}

clean_all() {
    log_warning "This will remove the container and image. Continue? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        # Stop and remove container
        if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
            log_info "Stopping container..."
            docker stop "$CONTAINER_NAME"
        fi
        
        if docker ps -aq -f name="$CONTAINER_NAME" | grep -q .; then
            log_info "Removing container..."
            docker rm "$CONTAINER_NAME"
        fi
        
        # Remove image
        if docker images -q "$IMAGE_NAME" | grep -q .; then
            log_info "Removing image..."
            docker rmi "$IMAGE_NAME"
        fi
        
        # Remove network
        docker network rm "$NETWORK_NAME" &> /dev/null || true
        
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

check_health() {
    if ! docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        log_error "Container is not running"
        exit 1
    fi
    
    log_info "Checking container health..."
    
    health_status=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "no-health-check")
    echo "Health Status: $health_status"
    
    # Test Ollama directly
    docker exec "$CONTAINER_NAME" curl -s http://localhost:11434/api/tags > /dev/null
    if [ $? -eq 0 ]; then
        log_success "Ollama is responsive"
    else
        log_error "Ollama is not responding"
    fi
    
    # Show health check logs
    docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' "$CONTAINER_NAME" 2>/dev/null || true
}

use_compose() {
    if [ -z "$2" ]; then
        log_error "Please specify compose command: build, up, down, logs, etc."
        exit 1
    fi
    
    log_info "Running docker-compose $2..."
    docker-compose "$2" "${@:3}"
}

# Main command handling
case "$1" in
    "build")
        show_header
        check_docker
        build_image
        ;;
    "run")
        show_header
        check_docker
        run_container
        ;;
    "start")
        show_header
        check_docker
        start_container
        ;;
    "stop")
        show_header
        check_docker
        stop_container
        ;;
    "restart")
        show_header
        check_docker
        restart_container
        ;;
    "shell")
        check_docker
        open_shell
        ;;
    "logs")
        check_docker
        show_logs
        ;;
    "status")
        show_header
        check_docker
        show_status
        ;;
    "demo")
        check_docker
        run_demo
        ;;
    "security")
        check_docker
        run_security_demo
        ;;
    "clean")
        show_header
        check_docker
        clean_all
        ;;
    "health")
        check_docker
        check_health
        ;;
    "compose")
        check_docker
        use_compose "$@"
        ;;
    "help"|"-h"|"--help")
        show_header
        show_usage
        ;;
    "")
        show_header
        show_usage
        ;;
    *)
        log_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac