#!/bin/bash

# Joulaa Platform Development Setup Script
# This script sets up the development environment for the Joulaa platform

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Docker and Docker Compose
check_docker() {
    print_status "Checking Docker installation..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Function to check Node.js
check_nodejs() {
    print_status "Checking Node.js installation..."
    
    if ! command_exists node; then
        print_warning "Node.js is not installed. Installing via nvm..."
        
        # Install nvm if not present
        if ! command_exists nvm; then
            curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
            export NVM_DIR="$HOME/.nvm"
            [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
        fi
        
        nvm install 18
        nvm use 18
    else
        NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$NODE_VERSION" -lt 18 ]; then
            print_warning "Node.js version is $NODE_VERSION. Recommended version is 18+"
        else
            print_success "Node.js $(node --version) is installed"
        fi
    fi
}

# Function to check Python
check_python() {
    print_status "Checking Python installation..."
    
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.11+ first."
        echo "Visit: https://www.python.org/downloads/"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    REQUIRED_VERSION="3.11"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        print_warning "Python version is $PYTHON_VERSION. Recommended version is 3.11+"
    else
        print_success "Python $PYTHON_VERSION is installed"
    fi
}

# Function to setup environment file
setup_env() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_success "Created .env file from .env.example"
        print_warning "Please review and update the .env file with your configuration"
    else
        print_warning ".env file already exists. Skipping..."
    fi
}

# Function to setup backend
setup_backend() {
    print_status "Setting up backend environment..."
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    print_success "Python dependencies installed"
    
    cd ..
}

# Function to setup frontend
setup_frontend() {
    print_status "Setting up frontend environment..."
    
    cd frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    print_success "Node.js dependencies installed"
    
    cd ..
}

# Function to start services
start_services() {
    print_status "Starting Docker services..."
    
    # Start core services
    docker-compose up -d postgres redis minio
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check if services are healthy
    if docker-compose ps | grep -q "Up (healthy)"; then
        print_success "Core services are running and healthy"
    else
        print_warning "Some services may not be fully ready yet. Check with 'docker-compose ps'"
    fi
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    cd backend
    source venv/bin/activate
    
    # Check if alembic is configured
    if [ -f "alembic.ini" ]; then
        alembic upgrade head
        print_success "Database migrations completed"
    else
        print_warning "Alembic not configured. Skipping migrations..."
    fi
    
    cd ..
}

# Function to create initial data
create_initial_data() {
    print_status "Creating initial data..."
    
    cd backend
    source venv/bin/activate
    
    # Check if initial data script exists
    if [ -f "scripts/create_initial_data.py" ]; then
        python scripts/create_initial_data.py
        print_success "Initial data created"
    else
        print_warning "Initial data script not found. Skipping..."
    fi
    
    cd ..
}

# Function to display final instructions
show_final_instructions() {
    echo ""
    echo "🎉 Development environment setup complete!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Review and update the .env file with your configuration"
    echo "2. Start the development servers:"
    echo ""
    echo "   Backend (FastAPI):"
    echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
    echo ""
    echo "   Frontend (React):"
    echo "   cd frontend && npm run dev"
    echo ""
    echo "   Or use Docker Compose:"
    echo "   docker-compose up -d"
    echo ""
    echo "🌐 Access points:"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend API: http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/docs"
    echo "   - MinIO Console: http://localhost:9001"
    echo "   - MailHog (dev): http://localhost:8025"
    echo "   - Adminer (dev): http://localhost:8080"
    echo ""
    echo "📚 For more information, see README.md"
    echo ""
}

# Main execution
main() {
    echo "🚀 Joulaa Platform Development Setup"
    echo "===================================="
    echo ""
    
    # Check prerequisites
    check_docker
    check_nodejs
    check_python
    
    echo ""
    print_status "All prerequisites are satisfied. Starting setup..."
    echo ""
    
    # Setup environment
    setup_env
    
    # Setup backend and frontend
    setup_backend
    setup_frontend
    
    # Start Docker services
    start_services
    
    # Run migrations and create initial data
    run_migrations
    create_initial_data
    
    # Show final instructions
    show_final_instructions
}

# Run main function
main "$@"