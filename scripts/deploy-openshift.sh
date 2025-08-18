#!/bin/bash

# OpenShift Deployment Script for AIBeniq
# This script deploys the application to OpenShift using Kustomize

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REGISTRY="quay.io"
NAMESPACE="aibeniq"
PROJECT_NAME=""
ENVIRONMENT=""
BUILD_IMAGES=false
PUSH_IMAGES=false
DRY_RUN=false

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

# Function to show usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Deploy AIBeniq application to OpenShift

OPTIONS:
    -e, --environment ENV    Target environment (dev|prod) [required]
    -b, --build             Build Docker images locally
    -p, --push              Push images to registry (requires -b)
    -d, --dry-run           Show what would be deployed without applying
    -h, --help              Show this help message

EXAMPLES:
    $0 -e dev                      Deploy to development (using existing images)
    $0 -e prod -b -p              Build, push, and deploy to production
    $0 -e dev -d                  Dry run for development environment

PREREQUISITES:
    - oc CLI must be installed and logged in
    - Docker must be running (if building images)
    - kustomize must be installed

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -b|--build)
            BUILD_IMAGES=true
            shift
            ;;
        -p|--push)
            PUSH_IMAGES=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate required parameters
if [[ -z "$ENVIRONMENT" ]]; then
    print_error "Environment is required. Use -e dev or -e prod"
    usage
    exit 1
fi

if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
    print_error "Environment must be 'dev' or 'prod'"
    exit 1
fi

# Set project name based on environment
if [[ "$ENVIRONMENT" == "dev" ]]; then
    PROJECT_NAME="aibeniq-dev"
elif [[ "$ENVIRONMENT" == "prod" ]]; then
    PROJECT_NAME="aibeniq-prod"
fi

# Validate prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if oc is installed
    if ! command -v oc &> /dev/null; then
        print_error "OpenShift CLI (oc) is not installed"
        exit 1
    fi
    
    # Check if logged in to OpenShift
    if ! oc whoami &> /dev/null; then
        print_error "Not logged in to OpenShift. Run 'oc login' first"
        exit 1
    fi
    
    # Check if kustomize is installed
    if ! command -v kustomize &> /dev/null; then
        print_error "kustomize is not installed"
        exit 1
    fi
    
    # Check if Docker is running (if building images)
    if [[ "$BUILD_IMAGES" == true ]]; then
        if ! docker info &> /dev/null; then
            print_error "Docker is not running"
            exit 1
        fi
    fi
    
    print_success "Prerequisites check passed"
}

# Build Docker images
build_images() {
    if [[ "$BUILD_IMAGES" != true ]]; then
        return 0
    fi
    
    print_status "Building Docker images..."
    
    # Get git commit hash for tagging
    GIT_COMMIT=$(git rev-parse --short HEAD)
    BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
    IMAGE_TAG="${BRANCH_NAME}-${GIT_COMMIT}"
    
    # Build backend image
    print_status "Building backend image..."
    docker build -t "${REGISTRY}/${NAMESPACE}/backend:${IMAGE_TAG}" ./backend
    docker tag "${REGISTRY}/${NAMESPACE}/backend:${IMAGE_TAG}" "${REGISTRY}/${NAMESPACE}/backend:latest"
    
    # Build frontend image
    print_status "Building frontend image..."
    docker build -t "${REGISTRY}/${NAMESPACE}/frontend:${IMAGE_TAG}" ./frontend \
        --build-arg VITE_API_URL="https://api-${PROJECT_NAME}.apps.your-cluster.com"
    docker tag "${REGISTRY}/${NAMESPACE}/frontend:${IMAGE_TAG}" "${REGISTRY}/${NAMESPACE}/frontend:latest"
    
    print_success "Images built successfully"
    
    # Push images if requested
    if [[ "$PUSH_IMAGES" == true ]]; then
        print_status "Pushing images to registry..."
        docker push "${REGISTRY}/${NAMESPACE}/backend:${IMAGE_TAG}"
        docker push "${REGISTRY}/${NAMESPACE}/backend:latest"
        docker push "${REGISTRY}/${NAMESPACE}/frontend:${IMAGE_TAG}"
        docker push "${REGISTRY}/${NAMESPACE}/frontend:latest"
        print_success "Images pushed successfully"
    fi
}

# Deploy to OpenShift
deploy_to_openshift() {
    print_status "Deploying to OpenShift environment: $ENVIRONMENT"
    
    # Ensure project exists
    if ! oc get project "$PROJECT_NAME" &> /dev/null; then
        print_status "Creating project: $PROJECT_NAME"
        oc new-project "$PROJECT_NAME"
    else
        print_status "Using existing project: $PROJECT_NAME"
        oc project "$PROJECT_NAME"
    fi
    
    # Change to the appropriate overlay directory
    OVERLAY_DIR="openshift/overlays/$ENVIRONMENT"
    if [[ "$ENVIRONMENT" == "dev" ]]; then
        OVERLAY_DIR="openshift/overlays/development"
    elif [[ "$ENVIRONMENT" == "prod" ]]; then
        OVERLAY_DIR="openshift/overlays/production"
    fi
    
    if [[ ! -d "$OVERLAY_DIR" ]]; then
        print_error "Overlay directory not found: $OVERLAY_DIR"
        exit 1
    fi
    
    cd "$OVERLAY_DIR"
    
    # Generate the manifests
    print_status "Generating Kubernetes manifests..."
    MANIFESTS=$(kustomize build .)
    
    if [[ "$DRY_RUN" == true ]]; then
        print_warning "DRY RUN - The following manifests would be applied:"
        echo "$MANIFESTS"
        return 0
    fi
    
    # Apply the manifests
    print_status "Applying manifests to OpenShift..."
    echo "$MANIFESTS" | oc apply -f -
    
    # Wait for deployments to be ready
    print_status "Waiting for deployments to be ready..."
    oc rollout status deployment/postgres -n "$PROJECT_NAME" --timeout=300s
    oc rollout status deployment/backend -n "$PROJECT_NAME" --timeout=300s
    oc rollout status deployment/frontend -n "$PROJECT_NAME" --timeout=300s
    
    # Run database migrations if this is a new deployment
    print_status "Running database prestart job..."
    oc wait --for=condition=complete job/prestart --timeout=300s -n "$PROJECT_NAME" || true
    
    print_success "Deployment completed successfully!"
    
    # Show application URLs
    print_status "Application URLs:"
    oc get routes -n "$PROJECT_NAME" -o custom-columns=NAME:.metadata.name,URL:.spec.host --no-headers | while read name host; do
        echo "  $name: https://$host"
    done
}

# Main execution
main() {
    print_status "Starting OpenShift deployment for environment: $ENVIRONMENT"
    
    check_prerequisites
    build_images
    deploy_to_openshift
    
    print_success "Deployment script completed successfully!"
}

# Run main function
main
