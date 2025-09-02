#!/usr/bin/env python3
"""
Data Setup Script for Churn Prediction Pipeline
This script processes the raw data and uploads it to S3 for the ML pipeline
"""

import pandas as pd
import boto3
import os
import logging
from botocore.exceptions import ClientError
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_s3_bucket(bucket_name, region='ap-south-1'):
    """Create S3 bucket if it doesn't exist"""
    s3_client = boto3.client('s3', region_name=region)
    
    try:
        # Check if bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
        logger.info(f"Bucket {bucket_name} already exists")
    except ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            # Bucket doesn't exist, create it
            try:
                if region == 'us-east-1':
                    s3_client.create_bucket(Bucket=bucket_name)
                else:
                    s3_client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': region}
                    )
                logger.info(f"Created bucket {bucket_name}")
            except ClientError as create_error:
                logger.error(f"Failed to create bucket: {create_error}")
                raise
        else:
            logger.error(f"Error checking bucket: {e}")
            raise

def process_and_upload_data():
    """Process the data files and upload to S3"""
    
    # Configuration
    bucket_name = 'mlops-churn-model-artifacts'
    region = 'ap-south-1'
    
    # Setup S3
    setup_s3_bucket(bucket_name, region)
    s3_client = boto3.client('s3', region_name=region)
    
    # Check if data files exist
    data_dir = 'date'  # Note: the directory is named 'date' not 'data'
    files_to_process = {
        'preprocessed.csv': 'preprocessed/preprocessed.csv',
        'train.csv': 'processed/train/train.csv', 
        'validation.csv': 'processed/validation/validation.csv'
    }
    
    for local_file, s3_key in files_to_process.items():
        local_path = os.path.join(data_dir, local_file)
        
        if os.path.exists(local_path):
            try:
                # Read and validate the CSV
                df = pd.read_csv(local_path)
                logger.info(f"Processing {local_file}: {df.shape[0]} rows, {df.shape[1]} columns")
                
                # Basic validation
                if df.empty:
                    logger.warning(f"File {local_file} is empty")
                    continue
                
                # Upload to S3
                logger.info(f"Uploading {local_file} to s3://{bucket_name}/{s3_key}")
                s3_client.upload_file(local_path, bucket_name, s3_key)
                logger.info(f"Successfully uploaded {local_file}")
                
            except Exception as e:
                logger.error(f"Error processing {local_file}: {str(e)}")
                
        else:
            logger.warning(f"File not found: {local_path}")
    
    # Create a sample data file for testing if preprocessed.csv doesn't exist
    if not os.path.exists(os.path.join(data_dir, 'preprocessed.csv')):
        logger.info("Creating sample preprocessed data...")
        create_sample_data(data_dir, bucket_name, s3_client)

def create_sample_data(data_dir, bucket_name, s3_client):
    """Create sample data for testing"""
    
    # Sample customer data
    sample_data = {
        'CustomerID': ['7590-VHVEG', '5575-GNVDE', '3668-QPYBK', '7795-CFOCW', '9237-HQITU'],
        'gender': ['Female', 'Male', 'Male', 'Male', 'Female'],
        'SeniorCitizen': [0, 0, 0, 0, 0],
        'Partner': ['Yes', 'No', 'No', 'No', 'No'],
        'Dependents': ['No', 'No', 'No', 'No', 'No'],
        'tenure': [1, 34, 2, 45, 2],
        'PhoneService': ['No', 'Yes', 'Yes', 'No', 'Yes'],
        'MultipleLines': ['No phone service', 'No', 'No', 'No phone service', 'No'],
        'InternetService': ['DSL', 'DSL', 'DSL', 'DSL', 'Fiber optic'],
        'OnlineSecurity': ['No', 'Yes', 'Yes', 'Yes', 'No'],
        'OnlineBackup': ['Yes', 'No', 'Yes', 'No', 'No'],
        'DeviceProtection': ['No', 'Yes', 'No', 'Yes', 'No'],
        'TechSupport': ['No', 'No', 'No', 'Yes', 'No'],
        'StreamingTV': ['No', 'No', 'No', 'No', 'No'],
        'StreamingMovies': ['No', 'No', 'No', 'No', 'No'],
        'Contract': ['Month-to-month', 'One year', 'Month-to-month', 'One year', 'Month-to-month'],
        'PaperlessBilling': ['Yes', 'No', 'Yes', 'No', 'Yes'],
        'PaymentMethod': ['Electronic check', 'Mailed check', 'Mailed check', 'Bank transfer (automatic)', 'Electronic check'],
        'MonthlyCharges': [29.85, 56.95, 53.85, 42.30, 70.70],
        'TotalCharges': ['29.85', '1889.5', '108.15', '1840.75', '151.65'],
        'Churn': ['No', 'No', 'Yes', 'No', 'Yes']
    }
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    # Expand to create more samples (duplicate with variations)
    expanded_data = []
    for _ in range(200):  # Create 1000 samples
        for _, row in df.iterrows():
            new_row = row.copy()
            # Add some variation
            new_row['CustomerID'] = f"SAMPLE-{len(expanded_data):05d}"
            new_row['tenure'] = max(1, new_row['tenure'] + np.random.randint(-10, 20))
            new_row['MonthlyCharges'] = max(20, new_row['MonthlyCharges'] + np.random.uniform(-10, 10))
            expanded_data.append(new_row)
    
    expanded_df = pd.DataFrame(expanded_data)
    
    # Save locally
    os.makedirs(data_dir, exist_ok=True)
    sample_file = os.path.join(data_dir, 'preprocessed.csv')
    expanded_df.to_csv(sample_file, index=False)
    logger.info(f"Created sample data with {len(expanded_df)} rows")
    
    # Upload to S3
    try:
        s3_client.upload_file(sample_file, bucket_name, 'preprocessed/preprocessed.csv')
        logger.info("Uploaded sample data to S3")
    except Exception as e:
        logger.error(f"Failed to upload sample data: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Setup data for churn prediction pipeline')
    parser.add_argument('--create-sample', action='store_true', help='Create sample data if files not found')
    
    args = parser.parse_args()
    
    try:
        # Import numpy for sample data creation
        import numpy as np
        
        logger.info("Starting data setup...")
        process_and_upload_data()
        logger.info("Data setup completed successfully")
        
    except ImportError:
        logger.error("numpy is required for sample data creation. Install with: pip install numpy")
    except Exception as e:
        logger.error(f"Data setup failed: {str(e)}")
        raise