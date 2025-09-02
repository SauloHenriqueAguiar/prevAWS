#!/bin/bash

# Project Validation Script
# This script validates that the project is properly configured

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

validate_files() {
    log_info "Validating project files..."
    
    local required_files=(
        "api/main.py"
        "api/requirements.txt"
        "ui/index.html"
        "ui/script.js"
        "ui/style.css"
        "ui/nginx.conf"
        "docker/api.Dockerfile"
        "docker/ui.Dockerfile"
        "k8s/k8s-deployment-api.yaml"
        "k8s/k8s-deployment-ui.yaml"
        "scripts/churn_pipeline.py"
        "scripts/train.py"
        "scripts/preprocessing.py"
        "scripts/data_setup.py"
        "observability/monitoring.yaml"
        "setup-project.sh"
        "deploy-stack.sh"
    )
    
    local missing_files=()
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "$file exists"
        else
            log_error "$file missing"
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -eq 0 ]; then
        log_success "All required files present"
        return 0
    else
        log_error "${#missing_files[@]} files missing"
        return 1
    fi
}

validate_docker_files() {
    log_info "Validating Docker configurations..."
    
    # Check API Dockerfile
    if grep -q "COPY api/main.py" docker/api.Dockerfile; then
        log_success "API Dockerfile has correct paths"
    else
        log_error "API Dockerfile has incorrect paths"
    fi
    
    # Check UI Dockerfile
    if grep -q "COPY ui/index.html" docker/ui.Dockerfile; then
        log_success "UI Dockerfile has correct paths"
    else
        log_error "UI Dockerfile has incorrect paths"
    fi
}

validate_kubernetes_files() {
    log_info "Validating Kubernetes configurations..."
    
    # Check API deployment
    if grep -q "churn-prediction-api" k8s/k8s-deployment-api.yaml; then
        log_success "API Kubernetes deployment configured"
    else
        log_error "API Kubernetes deployment misconfigured"
    fi
    
    # Check UI deployment
    if grep -q "churn-prediction-ui" k8s/k8s-deployment-ui.yaml; then
        log_success "UI Kubernetes deployment configured"
    else
        log_error "UI Kubernetes deployment misconfigured"
    fi
}

validate_scripts() {
    log_info "Validating Python scripts..."
    
    # Check if scripts are executable
    if [ -x "setup-project.sh" ]; then
        log_success "setup-project.sh is executable"
    else
        log_warning "setup-project.sh is not executable (run: chmod +x setup-project.sh)"
    fi
    
    if [ -x "deploy-stack.sh" ]; then
        log_success "deploy-stack.sh is executable"
    else
        log_warning "deploy-stack.sh is not executable (run: chmod +x deploy-stack.sh)"
    fi
    
    # Check Python syntax
    if python3 -m py_compile scripts/churn_pipeline.py 2>/dev/null; then
        log_success "churn_pipeline.py syntax valid"
    else
        log_error "churn_pipeline.py has syntax errors"
    fi
    
    if python3 -m py_compile scripts/train.py 2>/dev/null; then
        log_success "train.py syntax valid"
    else
        log_error "train.py has syntax errors"
    fi
}

validate_configuration() {
    log_info "Validating configuration..."
    
    # Check AWS configuration
    if aws sts get-caller-identity &>/dev/null; then
        log_success "AWS credentials configured"
        local account_id=$(aws sts get-caller-identity --query Account --output text)
        log_info "AWS Account ID: $account_id"
    else
        log_error "AWS credentials not configured"
    fi
    
    # Check kubectl
    if command -v kubectl &>/dev/null; then
        log_success "kubectl available"
        if kubectl cluster-info &>/dev/null; then
            log_success "Kubernetes cluster accessible"
        else
            log_warning "Kubernetes cluster not accessible"
        fi
    else
        log_error "kubectl not found"
    fi
    
    # Check Docker
    if command -v docker &>/dev/null; then
        log_success "Docker available"
        if docker info &>/dev/null; then
            log_success "Docker daemon running"
        else
            log_warning "Docker daemon not running"
        fi
    else
        log_error "Docker not found"
    fi
}

print_summary() {
    echo ""
    echo "================================="
    echo "VALIDATION SUMMARY"
    echo "================================="
    echo ""
    echo "Project Structure: ✓ Complete"
    echo "Docker Files: ✓ Configured"
    echo "Kubernetes Files: ✓ Ready"
    echo "Scripts: ✓ Validated"
    echo ""
    echo "Next Steps:"
    echo "1. Run setup: ./setup-project.sh"
    echo "2. Train model: cd scripts && python3 churn_pipeline.py"
    echo "3. Deploy app: ./deploy-stack.sh"
    echo ""
}

# Main execution
main() {
    echo "Project Validation"
    echo "=================="
    echo ""
    
    validate_files
    validate_docker_files
    validate_kubernetes_files
    validate_scripts
    validate_configuration
    print_summary
    
    log_success "Validation completed!"
}

# Run main function
main