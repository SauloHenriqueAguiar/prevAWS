#!/bin/bash

# Complete Project Setup Script
# This script sets up the entire churn prediction MLOps project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION="ap-south-1"
AWS_ACCOUNT_ID="911167906047"
S3_BUCKET="mlops-churn-model-artifacts"
EKS_CLUSTER_NAME="churnmodel"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check required tools
    local tools=("aws" "docker" "kubectl" "python3" "pip3")
    for tool in "${tools[@]}"; do
        if ! command -v $tool &> /dev/null; then
            log_error "$tool not found. Please install $tool."
            exit 1
        fi
    done
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please configure AWS credentials."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

setup_python_environment() {
    log_info "Setting up Python environment..."
    
    # Install required Python packages for scripts
    pip3 install --user boto3 pandas numpy sagemaker scikit-learn xgboost mlflow
    
    log_success "Python environment setup completed"
}

setup_data() {
    log_info "Setting up data files..."
    
    # Run the data setup script
    if [ -f "scripts/data_setup.py" ]; then
        python3 scripts/data_setup.py --create-sample
        log_success "Data setup completed"
    else
        log_warning "Data setup script not found, skipping data setup"
    fi
}

setup_s3_bucket() {
    log_info "Setting up S3 bucket..."
    
    # Create S3 bucket if it doesn't exist
    if aws s3 ls "s3://$S3_BUCKET" 2>&1 | grep -q 'NoSuchBucket'; then
        log_info "Creating S3 bucket: $S3_BUCKET"
        if [ "$AWS_REGION" = "us-east-1" ]; then
            aws s3 mb "s3://$S3_BUCKET"
        else
            aws s3 mb "s3://$S3_BUCKET" --region "$AWS_REGION"
        fi
        log_success "S3 bucket created"
    else
        log_info "S3 bucket already exists: $S3_BUCKET"
    fi
    
    # Enable versioning
    aws s3api put-bucket-versioning \
        --bucket "$S3_BUCKET" \
        --versioning-configuration Status=Enabled
    
    log_success "S3 bucket setup completed"
}

setup_sagemaker_role() {
    log_info "Setting up SageMaker execution role..."
    
    local role_name="SageMakerChurnRole"
    local role_arn="arn:aws:iam::$AWS_ACCOUNT_ID:role/$role_name"
    
    # Check if role exists
    if aws iam get-role --role-name "$role_name" &> /dev/null; then
        log_info "SageMaker role already exists: $role_name"
    else
        log_info "Creating SageMaker role: $role_name"
        
        # Create trust policy
        cat > /tmp/trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "sagemaker.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF
        
        # Create role
        aws iam create-role \
            --role-name "$role_name" \
            --assume-role-policy-document file:///tmp/trust-policy.json
        
        # Attach policies
        aws iam attach-role-policy \
            --role-name "$role_name" \
            --policy-arn "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
        
        aws iam attach-role-policy \
            --role-name "$role_name" \
            --policy-arn "arn:aws:iam::aws:policy/AmazonS3FullAccess"
        
        log_success "SageMaker role created: $role_arn"
    fi
}

setup_model_registry() {
    log_info "Setting up SageMaker Model Registry..."
    
    local model_group_name="ChurnModelPackageGroup"
    
    # Check if model package group exists
    if aws sagemaker describe-model-package-group --model-package-group-name "$model_group_name" &> /dev/null; then
        log_info "Model package group already exists: $model_group_name"
    else
        log_info "Creating model package group: $model_group_name"
        aws sagemaker create-model-package-group \
            --model-package-group-name "$model_group_name" \
            --model-package-group-description "Churn prediction model package group"
        log_success "Model package group created: $model_group_name"
    fi
}

setup_eks_connection() {
    log_info "Setting up EKS cluster connection..."
    
    # Update kubeconfig
    aws eks update-kubeconfig --region "$AWS_REGION" --name "$EKS_CLUSTER_NAME"
    
    # Verify connection
    if kubectl cluster-info &> /dev/null; then
        log_success "EKS cluster connection established"
    else
        log_error "Failed to connect to EKS cluster: $EKS_CLUSTER_NAME"
        log_info "Please ensure the EKS cluster exists and you have proper permissions"
        exit 1
    fi
}

create_kubernetes_secrets() {
    log_info "Creating Kubernetes secrets..."
    
    # Get AWS credentials
    AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
    AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)
    
    if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
        log_error "AWS credentials not found in AWS CLI configuration"
        exit 1
    fi
    
    # Create AWS credentials secret
    kubectl create secret generic aws-credentials \
        --from-literal=aws-access-key-id="$AWS_ACCESS_KEY_ID" \
        --from-literal=aws-secret-access-key="$AWS_SECRET_ACCESS_KEY" \
        --namespace=default \
        --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "Kubernetes secrets created"
}

validate_setup() {
    log_info "Validating setup..."
    
    # Check S3 bucket
    if aws s3 ls "s3://$S3_BUCKET" &> /dev/null; then
        log_success "✓ S3 bucket accessible"
    else
        log_error "✗ S3 bucket not accessible"
    fi
    
    # Check SageMaker role
    if aws iam get-role --role-name "SageMakerChurnRole" &> /dev/null; then
        log_success "✓ SageMaker role exists"
    else
        log_error "✗ SageMaker role not found"
    fi
    
    # Check EKS connection
    if kubectl get nodes &> /dev/null; then
        log_success "✓ EKS cluster accessible"
    else
        log_error "✗ EKS cluster not accessible"
    fi
    
    # Check Kubernetes secrets
    if kubectl get secret aws-credentials &> /dev/null; then
        log_success "✓ Kubernetes secrets exist"
    else
        log_error "✗ Kubernetes secrets not found"
    fi
}

print_next_steps() {
    echo ""
    echo "================================="
    echo "PROJECT SETUP COMPLETED"
    echo "================================="
    echo ""
    echo "Next steps:"
    echo "1. Run the ML pipeline:"
    echo "   cd scripts && python3 churn_pipeline.py"
    echo ""
    echo "2. Deploy the application:"
    echo "   ./deploy-stack.sh"
    echo ""
    echo "3. Access the application:"
    echo "   - Get node IP: kubectl get nodes -o wide"
    echo "   - UI: http://<NODE_IP>:30081"
    echo "   - API: http://<NODE_IP>:30080"
    echo ""
    echo "Configuration:"
    echo "   - AWS Region: $AWS_REGION"
    echo "   - S3 Bucket: $S3_BUCKET"
    echo "   - EKS Cluster: $EKS_CLUSTER_NAME"
    echo ""
}

# Main execution
main() {
    echo "Starting Project Setup..."
    echo "========================="
    
    check_prerequisites
    setup_python_environment
    setup_s3_bucket
    setup_sagemaker_role
    setup_model_registry
    setup_data
    setup_eks_connection
    create_kubernetes_secrets
    validate_setup
    print_next_steps
    
    log_success "Project setup completed successfully!"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-data)
            SKIP_DATA=true
            shift
            ;;
        --skip-eks)
            SKIP_EKS=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --skip-data     Skip data setup"
            echo "  --skip-eks      Skip EKS setup"
            echo "  --help          Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main function
main