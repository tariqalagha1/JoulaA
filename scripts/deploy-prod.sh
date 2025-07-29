#!/bin/bash

# Joulaa Platform Production Deployment Script
# This script deploys the Joulaa platform to production environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="joulaa-platform"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-your-registry.com}"
KUBERNETES_NAMESPACE="${KUBERNETES_NAMESPACE:-joulaa}"
ENVIRONMENT="${ENVIRONMENT:-production}"
VERSION="${VERSION:-latest}"

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

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! command_exists kubectl; then
        print_error "kubectl is not installed"
        exit 1
    fi
    
    print_success "All prerequisites are satisfied"
}

# Function to validate environment
validate_environment() {
    print_status "Validating environment configuration..."
    
    if [ ! -f ".env.${ENVIRONMENT}" ]; then
        print_error "Environment file .env.${ENVIRONMENT} not found"
        exit 1
    fi
    
    # Source environment variables
    source ".env.${ENVIRONMENT}"
    
    # Check required variables
    required_vars=(
        "DATABASE_URL"
        "REDIS_URL"
        "SECRET_KEY"
        "MINIO_ACCESS_KEY"
        "MINIO_SECRET_KEY"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            print_error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    print_success "Environment configuration is valid"
}

# Function to build Docker images
build_images() {
    print_status "Building Docker images..."
    
    # Build backend image
    print_status "Building backend image..."
    docker build -t "${DOCKER_REGISTRY}/${APP_NAME}-backend:${VERSION}" \
        --target production \
        ./backend
    
    # Build frontend image
    print_status "Building frontend image..."
    docker build -t "${DOCKER_REGISTRY}/${APP_NAME}-frontend:${VERSION}" \
        --target production \
        ./frontend
    
    print_success "Docker images built successfully"
}

# Function to push images to registry
push_images() {
    print_status "Pushing images to registry..."
    
    # Login to registry if credentials are provided
    if [ -n "$DOCKER_USERNAME" ] && [ -n "$DOCKER_PASSWORD" ]; then
        echo "$DOCKER_PASSWORD" | docker login "$DOCKER_REGISTRY" -u "$DOCKER_USERNAME" --password-stdin
    fi
    
    # Push backend image
    docker push "${DOCKER_REGISTRY}/${APP_NAME}-backend:${VERSION}"
    
    # Push frontend image
    docker push "${DOCKER_REGISTRY}/${APP_NAME}-frontend:${VERSION}"
    
    print_success "Images pushed to registry"
}

# Function to create Kubernetes namespace
create_namespace() {
    print_status "Creating Kubernetes namespace..."
    
    kubectl create namespace "$KUBERNETES_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    print_success "Namespace $KUBERNETES_NAMESPACE is ready"
}

# Function to create secrets
create_secrets() {
    print_status "Creating Kubernetes secrets..."
    
    # Create secret from environment file
    kubectl create secret generic "${APP_NAME}-config" \
        --from-env-file=".env.${ENVIRONMENT}" \
        --namespace="$KUBERNETES_NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Create Docker registry secret if credentials are provided
    if [ -n "$DOCKER_USERNAME" ] && [ -n "$DOCKER_PASSWORD" ]; then
        kubectl create secret docker-registry "${APP_NAME}-registry" \
            --docker-server="$DOCKER_REGISTRY" \
            --docker-username="$DOCKER_USERNAME" \
            --docker-password="$DOCKER_PASSWORD" \
            --namespace="$KUBERNETES_NAMESPACE" \
            --dry-run=client -o yaml | kubectl apply -f -
    fi
    
    print_success "Secrets created"
}

# Function to deploy database
deploy_database() {
    print_status "Deploying PostgreSQL database..."
    
    # Apply PostgreSQL manifests
    envsubst < k8s/postgres.yaml | kubectl apply -f - -n "$KUBERNETES_NAMESPACE"
    
    # Wait for database to be ready
    kubectl wait --for=condition=ready pod -l app=postgres -n "$KUBERNETES_NAMESPACE" --timeout=300s
    
    print_success "Database deployed and ready"
}

# Function to deploy Redis
deploy_redis() {
    print_status "Deploying Redis cache..."
    
    # Apply Redis manifests
    envsubst < k8s/redis.yaml | kubectl apply -f - -n "$KUBERNETES_NAMESPACE"
    
    # Wait for Redis to be ready
    kubectl wait --for=condition=ready pod -l app=redis -n "$KUBERNETES_NAMESPACE" --timeout=300s
    
    print_success "Redis deployed and ready"
}

# Function to deploy MinIO
deploy_minio() {
    print_status "Deploying MinIO object storage..."
    
    # Apply MinIO manifests
    envsubst < k8s/minio.yaml | kubectl apply -f - -n "$KUBERNETES_NAMESPACE"
    
    # Wait for MinIO to be ready
    kubectl wait --for=condition=ready pod -l app=minio -n "$KUBERNETES_NAMESPACE" --timeout=300s
    
    print_success "MinIO deployed and ready"
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Create migration job
    envsubst < k8s/migration-job.yaml | kubectl apply -f - -n "$KUBERNETES_NAMESPACE"
    
    # Wait for migration to complete
    kubectl wait --for=condition=complete job/migration-job -n "$KUBERNETES_NAMESPACE" --timeout=300s
    
    print_success "Database migrations completed"
}

# Function to deploy backend
deploy_backend() {
    print_status "Deploying backend application..."
    
    # Update image tag in deployment
    sed "s|{{IMAGE_TAG}}|${VERSION}|g" k8s/backend.yaml | \
    sed "s|{{REGISTRY}}|${DOCKER_REGISTRY}|g" | \
    kubectl apply -f - -n "$KUBERNETES_NAMESPACE"
    
    # Wait for deployment to be ready
    kubectl rollout status deployment/backend -n "$KUBERNETES_NAMESPACE" --timeout=300s
    
    print_success "Backend deployed successfully"
}

# Function to deploy frontend
deploy_frontend() {
    print_status "Deploying frontend application..."
    
    # Update image tag in deployment
    sed "s|{{IMAGE_TAG}}|${VERSION}|g" k8s/frontend.yaml | \
    sed "s|{{REGISTRY}}|${DOCKER_REGISTRY}|g" | \
    kubectl apply -f - -n "$KUBERNETES_NAMESPACE"
    
    # Wait for deployment to be ready
    kubectl rollout status deployment/frontend -n "$KUBERNETES_NAMESPACE" --timeout=300s
    
    print_success "Frontend deployed successfully"
}

# Function to deploy ingress
deploy_ingress() {
    print_status "Deploying ingress controller..."
    
    # Apply ingress manifests
    envsubst < k8s/ingress.yaml | kubectl apply -f - -n "$KUBERNETES_NAMESPACE"
    
    print_success "Ingress deployed"
}

# Function to deploy monitoring
deploy_monitoring() {
    print_status "Deploying monitoring stack..."
    
    # Deploy Prometheus
    kubectl apply -f k8s/monitoring/prometheus.yaml -n "$KUBERNETES_NAMESPACE"
    
    # Deploy Grafana
    kubectl apply -f k8s/monitoring/grafana.yaml -n "$KUBERNETES_NAMESPACE"
    
    print_success "Monitoring stack deployed"
}

# Function to verify deployment
verify_deployment() {
    print_status "Verifying deployment..."
    
    # Check all pods are running
    kubectl get pods -n "$KUBERNETES_NAMESPACE"
    
    # Check services
    kubectl get services -n "$KUBERNETES_NAMESPACE"
    
    # Check ingress
    kubectl get ingress -n "$KUBERNETES_NAMESPACE"
    
    # Health check
    BACKEND_URL=$(kubectl get ingress -n "$KUBERNETES_NAMESPACE" -o jsonpath='{.items[0].spec.rules[0].host}')
    if [ -n "$BACKEND_URL" ]; then
        if curl -f "https://${BACKEND_URL}/health" >/dev/null 2>&1; then
            print_success "Health check passed"
        else
            print_warning "Health check failed. Please verify manually."
        fi
    fi
    
    print_success "Deployment verification completed"
}

# Function to show deployment info
show_deployment_info() {
    echo ""
    echo "🎉 Production deployment completed!"
    echo ""
    echo "📋 Deployment Information:"
    echo "   Environment: $ENVIRONMENT"
    echo "   Version: $VERSION"
    echo "   Namespace: $KUBERNETES_NAMESPACE"
    echo ""
    echo "🌐 Access Points:"
    
    # Get ingress URL
    INGRESS_HOST=$(kubectl get ingress -n "$KUBERNETES_NAMESPACE" -o jsonpath='{.items[0].spec.rules[0].host}' 2>/dev/null || echo "Not configured")
    echo "   Application: https://$INGRESS_HOST"
    echo "   API: https://$INGRESS_HOST/api/v1"
    echo "   API Docs: https://$INGRESS_HOST/docs"
    echo ""
    echo "📊 Monitoring:"
    echo "   kubectl port-forward svc/prometheus 9090:9090 -n $KUBERNETES_NAMESPACE"
    echo "   kubectl port-forward svc/grafana 3000:3000 -n $KUBERNETES_NAMESPACE"
    echo ""
    echo "🔍 Useful Commands:"
    echo "   kubectl get pods -n $KUBERNETES_NAMESPACE"
    echo "   kubectl logs -f deployment/backend -n $KUBERNETES_NAMESPACE"
    echo "   kubectl logs -f deployment/frontend -n $KUBERNETES_NAMESPACE"
    echo ""
}

# Function to rollback deployment
rollback_deployment() {
    print_status "Rolling back deployment..."
    
    kubectl rollout undo deployment/backend -n "$KUBERNETES_NAMESPACE"
    kubectl rollout undo deployment/frontend -n "$KUBERNETES_NAMESPACE"
    
    print_success "Rollback completed"
}

# Function to show help
show_help() {
    echo "Joulaa Platform Production Deployment Script"
    echo ""
    echo "Usage: $0 [OPTIONS] [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy     Deploy the application (default)"
    echo "  rollback   Rollback to previous version"
    echo "  verify     Verify current deployment"
    echo "  help       Show this help message"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Set environment (default: production)"
    echo "  -v, --version VERSION    Set version tag (default: latest)"
    echo "  -n, --namespace NS       Set Kubernetes namespace (default: joulaa)"
    echo "  -r, --registry REGISTRY  Set Docker registry (default: your-registry.com)"
    echo "  --skip-build            Skip building Docker images"
    echo "  --skip-push             Skip pushing images to registry"
    echo "  --monitoring            Deploy monitoring stack"
    echo ""
    echo "Environment Variables:"
    echo "  DOCKER_USERNAME         Docker registry username"
    echo "  DOCKER_PASSWORD         Docker registry password"
    echo "  KUBERNETES_NAMESPACE     Kubernetes namespace"
    echo "  ENVIRONMENT             Deployment environment"
    echo "  VERSION                 Application version"
    echo ""
}

# Parse command line arguments
SKIP_BUILD=false
SKIP_PUSH=false
DEPLOY_MONITORING=false
COMMAND="deploy"

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -n|--namespace)
            KUBERNETES_NAMESPACE="$2"
            shift 2
            ;;
        -r|--registry)
            DOCKER_REGISTRY="$2"
            shift 2
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --skip-push)
            SKIP_PUSH=true
            shift
            ;;
        --monitoring)
            DEPLOY_MONITORING=true
            shift
            ;;
        deploy|rollback|verify|help)
            COMMAND="$1"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
main() {
    echo "🚀 Joulaa Platform Production Deployment"
    echo "========================================="
    echo ""
    
    case $COMMAND in
        deploy)
            check_prerequisites
            validate_environment
            
            if [ "$SKIP_BUILD" = false ]; then
                build_images
            fi
            
            if [ "$SKIP_PUSH" = false ]; then
                push_images
            fi
            
            create_namespace
            create_secrets
            deploy_database
            deploy_redis
            deploy_minio
            run_migrations
            deploy_backend
            deploy_frontend
            deploy_ingress
            
            if [ "$DEPLOY_MONITORING" = true ]; then
                deploy_monitoring
            fi
            
            verify_deployment
            show_deployment_info
            ;;
        rollback)
            rollback_deployment
            ;;
        verify)
            verify_deployment
            ;;
        help)
            show_help
            ;;
        *)
            print_error "Unknown command: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"