# Customer Churn Prediction MLOps Pipeline

A complete MLOps solution for customer churn prediction using AWS SageMaker, EKS, and modern ML practices.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │───▶│  SageMaker       │───▶│   Model         │
│   (S3 Bucket)   │    │  Pipeline        │    │   Registry      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Monitoring    │◀───│  EKS Cluster     │◀───│   FastAPI       │
│ (Prometheus/    │    │  (Kubernetes)    │    │   Application   │
│  Grafana)       │    └──────────────────┘    └─────────────────┘
└─────────────────┘             │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Web UI         │    │   Model         │
                       │   (React/HTML)   │    │   Inference     │
                       └──────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
prevAWS/
├── api/                    # FastAPI backend application
│   ├── main.py            # Main FastAPI application
│   └── requirements.txt   # Python dependencies
├── ui/                     # Frontend web application
│   ├── index.html         # Main HTML page
│   ├── script.js          # JavaScript functionality
│   ├── style.css          # CSS styling
│   └── nginx.conf         # Nginx configuration
├── scripts/               # ML pipeline scripts
│   ├── churn_pipeline.py  # SageMaker pipeline definition
│   ├── train.py           # Model training script
│   ├── preprocessing.py   # Data preprocessing
│   ├── evaluate.py        # Model evaluation
│   ├── inference.py       # Inference script
│   ├── data_setup.py      # Data setup utility
│   └── requirements.txt   # ML dependencies
├── docker/                # Docker configurations
│   ├── api.Dockerfile     # API container definition
│   └── ui.Dockerfile      # UI container definition
├── k8s/                   # Kubernetes manifests
│   ├── k8s-deployment-api.yaml  # API deployment
│   └── k8s-deployment-ui.yaml   # UI deployment
├── observability/         # Monitoring configuration
│   └── monitoring.yaml    # Prometheus/Grafana setup
├── date/                  # Data files
│   ├── preprocessed.csv   # Preprocessed dataset
│   ├── train.csv          # Training data
│   └── validation.csv     # Validation data
├── readdeploy/           # Documentation
│   ├── DEPLOYMENT_GUIDE.md
│   ├── CONFIGURATION_VERIFICATION.md
│   ├── deployapi.md
│   └── deployui.md
├── setup-project.sh      # Complete project setup
├── deploy-stack.sh       # Application deployment
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

- AWS CLI configured with appropriate permissions
- Docker installed and running
- kubectl configured for EKS access
- Python 3.8+ with pip
- An existing EKS cluster named "churnmodel"

### 1. Initial Setup

```bash
# Clone and navigate to project
cd prevAWS

# Make scripts executable
chmod +x setup-project.sh deploy-stack.sh

# Run complete project setup
./setup-project.sh
```

This script will:
- ✅ Validate prerequisites
- ✅ Setup Python environment
- ✅ Create S3 bucket for artifacts
- ✅ Setup SageMaker execution role
- ✅ Create model registry
- ✅ Process and upload data
- ✅ Configure EKS connection
- ✅ Create Kubernetes secrets

### 2. Train the Model

```bash
# Navigate to scripts directory
cd scripts

# Run the ML pipeline
python3 churn_pipeline.py
```

This will:
- Create a SageMaker pipeline
- Process the data
- Train an XGBoost model
- Register the model in SageMaker Model Registry

### 3. Deploy the Application

```bash
# Return to project root
cd ..

# Deploy the complete stack
./deploy-stack.sh
```

This will:
- Build and push Docker images to ECR
- Deploy FastAPI backend to EKS
- Deploy React frontend to EKS
- Setup monitoring with Prometheus/Grafana

### 4. Access the Application

After deployment, get your node IP:

```bash
kubectl get nodes -o wide
```

Access the application:
- **Web UI**: `http://<NODE_IP>:30081`
- **API Documentation**: `http://<NODE_IP>:30080/docs`
- **API Health**: `http://<NODE_IP>:30080/health`
- **Prometheus**: `http://<NODE_IP>:30090`
- **Grafana**: `http://<NODE_IP>:30030` (admin/admin123)

## 🔧 Configuration

### Environment Variables

The application uses the following environment variables:

```bash
# AWS Configuration
AWS_DEFAULT_REGION=ap-south-1
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>

# Application Configuration
MODEL_REGISTRY_GROUP=ChurnModelPackageGroup
S3_BUCKET=mlops-churn-model-artifacts

# MLflow (Optional)
MLFLOW_TRACKING_URI=http://localhost:5000/
MLFLOW_EXPERIMENT_NAME=ChurnPrediction
```

### AWS Resources

The project creates/uses these AWS resources:

- **S3 Bucket**: `mlops-churn-model-artifacts`
- **IAM Role**: `SageMakerChurnRole`
- **SageMaker Model Package Group**: `ChurnModelPackageGroup`
- **ECR Repositories**: 
  - `churn-prediction-api`
  - `churn-prediction-ui`

## 📊 Model Information

### Features Used

The model uses the following customer features:

- **Demographics**: Gender, Senior Citizen, Partner, Dependents
- **Account Info**: Tenure, Contract, Payment Method, Billing
- **Services**: Phone, Internet, Security, Backup, Support
- **Financial**: Monthly Charges, Total Charges

### Model Performance

The XGBoost model provides:
- Binary classification (Churn: Yes/No)
- Probability scores (0-1)
- Risk levels (Very Low, Low, Medium, High, Very High)
- Feature importance analysis

## 🔍 Monitoring

### Metrics Available

- **API Metrics**: Request count, latency, error rates
- **Model Metrics**: Prediction count, model load status
- **Infrastructure**: CPU, memory, pod status

### Dashboards

- **Prometheus**: Raw metrics and alerting
- **Grafana**: Visual dashboards and monitoring

## 🛠️ Development

### Local Development

1. **API Development**:
```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. **UI Development**:
```bash
cd ui
# Serve with any HTTP server
python3 -m http.server 8080
```

### Testing

```bash
# Test API health
curl http://localhost:8000/health

# Test prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d @sample_customer.json
```

## 📚 API Documentation

### Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /model-info` - Model information
- `POST /predict` - Make prediction
- `POST /reload-model` - Reload model
- `GET /metrics` - Prometheus metrics

### Sample Request

```json
{
  "gender": "Female",
  "SeniorCitizen": 0,
  "Partner": "Yes",
  "Dependents": "No",
  "tenure": 12,
  "PhoneService": "Yes",
  "MultipleLines": "No",
  "InternetService": "DSL",
  "OnlineSecurity": "Yes",
  "OnlineBackup": "No",
  "DeviceProtection": "No",
  "TechSupport": "No",
  "StreamingTV": "No",
  "StreamingMovies": "No",
  "Contract": "Month-to-month",
  "PaperlessBilling": "Yes",
  "PaymentMethod": "Electronic check",
  "MonthlyCharges": 50.00,
  "TotalCharges": "600.00"
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Model Not Loading**:
   - Check S3 bucket permissions
   - Verify SageMaker role exists
   - Check model registry for approved models

2. **API Connection Issues**:
   - Verify EKS cluster is running
   - Check pod status: `kubectl get pods`
   - Check service endpoints: `kubectl get svc`

3. **UI Not Loading**:
   - Check nginx configuration
   - Verify API endpoint in script.js
   - Check browser console for errors

### Debugging Commands

```bash
# Check pod logs
kubectl logs -l app=churn-prediction-api
kubectl logs -l app=churn-prediction-ui

# Check pod status
kubectl get pods,svc,ingress

# Check AWS resources
aws s3 ls s3://mlops-churn-model-artifacts/
aws sagemaker list-model-packages --model-package-group-name ChurnModelPackageGroup
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review the deployment guides in `readdeploy/`
- Open an issue in the repository

---

**Built with ❤️ using AWS SageMaker, EKS, FastAPI, and modern MLOps practices**