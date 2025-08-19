import pandas as pd
from sklearn.model_selection import train_test_split
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-path", type=str, default="/opt/ml/processing/input")
    args = parser.parse_args()

    # Load data from the input path
    input_file = os.path.join(args.input_path, 'raw/churn_data.csv')
    df = pd.read_csv(input_file)

    # Simple data cleaning
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    df.dropna(inplace=True)
    df.drop(['customerID'], axis=1, inplace=True)
    df['Churn'] = df['Churn'].apply(lambda x: 1 if x == 'Yes' else 0)

    # One-hot encode categorical features
    # In a real-world scenario, you would use a more robust method like ColumnTransformer
    df_processed = pd.get_dummies(df, drop_first=True)

    # Split data
    train, test = train_test_split(df_processed, test_size=0.2, random_state=42)
    
    # Define output paths
    train_path = "/opt/ml/processing/train"
    test_path = "/opt/ml/processing/test"
    
    # Save processed data
    os.makedirs(train_path, exist_ok=True)
    os.makedirs(test_path, exist_ok=True)
    
    train.to_csv(os.path.join(train_path, 'train.csv'), index=False)
    test.to_csv(os.path.join(test_path, 'test.csv'), index=False)

    print("Preprocessing complete.")