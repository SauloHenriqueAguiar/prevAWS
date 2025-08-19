from fastapi import FastAPI
from pydantic import BaseModel, Field
import xgboost as xgb
import pandas as pd
import os

app = FastAPI(title="Churn Prediction API")

# This Pydantic model defines the structure of the input data for a single prediction.
# It should match the raw features before preprocessing.
class CustomerFeatures(BaseModel):
    gender: str = "Male"
    SeniorCitizen: int = 0
    Partner: str = "Yes"
    Dependents: str = "No"
    tenure: int = 1
    PhoneService: str = "No"
    MultipleLines: str = "No phone service"
    InternetService: str = "DSL"
    OnlineSecurity: str = "No"
    OnlineBackup: str = "Yes"
    DeviceProtection: str = "No"
    TechSupport: str = "No"
    StreamingTV: str = "No"
    StreamingMovies: str = "No"
    Contract: str = "Month-to-month"
    PaperlessBilling: str = "Yes"
    PaymentMethod: str = "Electronic check"
    MonthlyCharges: float = 29.85
    TotalCharges: float = 29.85

model = None
model_columns = None

@app.on_event("startup")
def load_model():
    """Load the XGBoost model and expected columns from disk at startup."""
    global model, model_columns
    model_path = os.environ.get("MODEL_PATH", "model.xgb")
    model = xgb.Booster()
    model.load_model(model_path)
    # The columns used for training are needed to ensure prediction data has the same structure.
    # In a real pipeline, these columns would be saved as an artifact during training.
    # For now, we define them here based on the preprocessing script's output.
    global model_columns
    model_columns = ['SeniorCitizen', 'tenure', 'MonthlyCharges', 'TotalCharges', 'gender_Male', 'Partner_Yes', 
                     'Dependents_Yes', 'PhoneService_Yes', 'MultipleLines_No phone service', 'MultipleLines_Yes', 
                     'InternetService_Fiber optic', 'InternetService_No', 'OnlineSecurity_No internet service', 
                     'OnlineSecurity_Yes', 'OnlineBackup_No internet service', 'OnlineBackup_Yes', 
                     'DeviceProtection_No internet service', 'DeviceProtection_Yes', 'TechSupport_No internet service',
                     'TechSupport_Yes', 'StreamingTV_No internet service', 'StreamingTV_Yes', 
                     'StreamingMovies_No internet service', 'StreamingMovies_Yes', 'Contract_One year', 
                     'Contract_Two year', 'PaperlessBilling_Yes', 'PaymentMethod_Credit card (automatic)',
                     'PaymentMethod_Electronic check', 'PaymentMethod_Mailed check']

@app.get("/")
def read_root():
    return {"message": "Welcome to the Churn Prediction API"}

@app.post("/predict")
def predict_churn(features: CustomerFeatures):
    """Predict churn probability based on customer features."""
    # Convert input data to a pandas DataFrame
    input_df = pd.DataFrame([features.dict()])
    
    # Preprocess the input data to match the training format
    # This uses one-hot encoding similar to the training script.
    processed_df = pd.get_dummies(input_df)
    
    # Align columns with the model's training data
    processed_df = processed_df.reindex(columns=model_columns, fill_value=0)
    
    # Create DMatrix for XGBoost
    dmatrix = xgb.DMatrix(processed_df)
    
    # Make prediction
    probability = model.predict(dmatrix)[0]
    
    return {
        "churn_prediction": "Yes" if probability > 0.5 else "No",
        "churn_probability": float(probability)
    }