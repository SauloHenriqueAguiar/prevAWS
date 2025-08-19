import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score
import argparse
import os
import mlflow
import mlflow.xgboost

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # SageMaker and MLflow arguments
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN"))
    parser.add_argument("--model_dir", type=str, default=os.environ.get("SM_MODEL_DIR"))
    parser.add_argument("--mlflow_tracking_uri", type=str)

    args = parser.parse_args()

    # Set up MLflow
    mlflow.set_tracking_uri(args.mlflow_tracking_uri)
    mlflow.set_experiment("churn-prediction-sagemaker")

    with mlflow.start_run():
        # Load data
        train_df = pd.read_csv(os.path.join(args.train, 'train.csv'))
        y_train = train_df['Churn']
        X_train = train_df.drop('Churn', axis=1)

        # Train XGBoost model
        params = {
            'objective': 'binary:logistic',
            'eval_metric': 'logloss',
            'max_depth': 5,
            'eta': 0.1,
            'gamma': 0.1,
            'subsample': 0.8
        }
        model = xgb.XGBClassifier(**params)
        model.fit(X_train, y_train)

        # Log parameters and metrics
        mlflow.log_params(params)
        y_pred = model.predict(X_train)
        accuracy = accuracy_score(y_train, y_pred)
        mlflow.log_metric("train_accuracy", accuracy)
        print(f"Train Accuracy: {accuracy}")

        # Log model with MLflow
        mlflow.xgboost.log_model(
            xgb_model=model,
            artifact_path="model",
            registered_model_name="churn-xgboost-model"
        )
        
        # Save model artifact for SageMaker
        model_path = os.path.join(args.model_dir, "model.xgb")
        model.save_model(model_path)
        print(f"Model saved to {model_path}")