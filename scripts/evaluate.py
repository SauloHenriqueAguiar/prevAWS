import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import argparse
import os
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, default="/opt/ml/processing/test")
    parser.add_argument("--model-path", type=str, default="/opt/ml/processing/model")
    parser.add_argument("--output-path", type=str, default="/opt/ml/processing/evaluation")
    args = parser.parse_args()

    # Load data and model
    test_df = pd.read_csv(os.path.join(args.test, 'test.csv'))
    y_test = test_df['Churn']
    X_test = test_df.drop('Churn', axis=1)
    
    model = xgb.Booster()
    model.load_model(os.path.join(args.model_path, 'model.xgb'))
    dtest = xgb.DMatrix(X_test)

    # Evaluate model
    y_pred_proba = model.predict(dtest)
    y_pred = (y_pred_proba > 0.5).astype(int)

    # Create evaluation report
    report = {
        'metrics': {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred)
        }
    }
    
    os.makedirs(args.output_path, exist_ok=True)
    with open(os.path.join(args.output_path, 'evaluation.json'), 'w') as f:
        json.dump(report, f, indent=4)
    
    print("Evaluation report generated.")
    print(report)