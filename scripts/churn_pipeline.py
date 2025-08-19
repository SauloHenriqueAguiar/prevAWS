import sagemaker
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import ProcessingStep, TrainingStep
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput
from sagemaker.estimator import Estimator
from sagemaker.inputs import TrainingInput
from sagemaker.workflow.step_collections import RegisterModel
import boto3

# --- Configuration ---
# !!! IMPORTANT: Replace with your specific details
UNIQUE_ID = "[YOUR-UNIQUE-ID]"
AWS_ACCOUNT_ID = "[YOUR-AWS-ACCOUNT-ID]"
AWS_REGION = "ap-south-1" # Or your preferred AWS region
MLFLOW_TRACKING_URI = "http://[YOUR-MLFLOW-EXTERNAL-IP]"

ROLE_ARN = f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/SageMakerChurnRole"
PIPELINE_NAME = "churn-pipeline"

# S3 Buckets
raw_data_s3_uri = f"s3://mlops-churn-raw-data-{UNIQUE_ID}"
processed_data_s3_uri = f"s3://mlops-churn-processed-data-{UNIQUE_ID}"
model_artifacts_s3_uri = f"s3://mlops-churn-model-artifacts-{UNIQUE_ID}"

# Get the default SageMaker session
sagemaker_session = sagemaker.Session()
sklearn_image_uri = sagemaker.image_uris.retrieve('sklearn', sagemaker_session.boto_region_name, '0.23-1')

# --- Step 1: Preprocessing ---
script_processor = ScriptProcessor(
    image_uri=sklearn_image_uri,
    command=['python3'],
    instance_type='ml.t3.medium',
    instance_count=1,
    base_job_name='churn-preprocess',
    role=ROLE_ARN,
    sagemaker_session=sagemaker_session
)

step_preprocess = ProcessingStep(
    name="PreprocessChurnData",
    processor=script_processor,
    inputs=[ProcessingInput(source=raw_data_s3_uri, destination='/opt/ml/processing/input')],
    outputs=[
        ProcessingOutput(output_name="train", source='/opt/ml/processing/train', destination=f"{processed_data_s3_uri}/train"),
        ProcessingOutput(output_name="test", source='/opt/ml/processing/test', destination=f"{processed_data_s3_uri}/test")
    ],
    code='scripts/preprocessing.py'
)

# --- Step 2: Training ---
image_uri = sagemaker.image_uris.retrieve(framework='xgboost', region=AWS_REGION, version='1.5-1')

xgb_estimator = Estimator(
    image_uri=image_uri,
    instance_type='ml.m5.large',
    instance_count=1,
    role=ROLE_ARN,
    output_path=f"{model_artifacts_s3_uri}/training-jobs",
    sagemaker_session=sagemaker_session,
    hyperparameters={
        'mlflow_tracking_uri': MLFLOW_TRACKING_URI
    },
    entry_point='train.py',
    source_dir='scripts'
)

step_train = TrainingStep(
    name="TrainXGBoostModel",
    estimator=xgb_estimator,
    inputs={
        "train": TrainingInput(s3_data=step_preprocess.properties.ProcessingOutputConfig.Outputs["train"].S3Output.S3Uri, content_type="text/csv")
    },
)

# --- Step 3: Evaluation ---
step_evaluate = ProcessingStep(
    name="EvaluateModel",
    processor=script_processor, # Re-using the sklearn processor
    inputs=[
        ProcessingInput(source=step_preprocess.properties.ProcessingOutputConfig.Outputs["test"].S3Output.S3Uri, destination="/opt/ml/processing/test"),
        ProcessingInput(source=step_train.properties.ModelArtifacts.S3ModelArtifacts, destination="/opt/ml/processing/model")
    ],
    outputs=[ProcessingOutput(output_name="evaluation", source="/opt/ml/processing/evaluation", destination=f"{model_artifacts_s3_uri}/evaluation-report")],
    code='scripts/evaluate.py'
)

# --- Step 4: Register Model ---
step_register = RegisterModel(
    name="RegisterChurnModel",
    estimator=xgb_estimator,
    model_data=step_train.properties.ModelArtifacts.S3ModelArtifacts,
    content_types=["text/csv"],
    response_types=["text/csv"],
    inference_instances=["ml.t2.medium", "ml.m5.large"],
    transform_instances=["ml.m5.large"],
    model_package_group_name="ChurnModelPackageGroup",
    approval_status="PendingManualApproval",
    model_metrics={
        "ModelQuality": {
            "Statistics": {
                "ContentType": "application/json",
                "S3Uri": step_evaluate.properties.ProcessingOutputConfig.Outputs["evaluation"].S3Output.S3Uri + "/evaluation.json"
            }
        }
    }
)

# --- Create and Execute Pipeline ---
pipeline = Pipeline(
    name=PIPELINE_NAME,
    parameters=[],
    steps=[step_preprocess, step_train, step_evaluate, step_register]
)

if __name__ == "__main__":
    print(f"Creating/Updating and executing pipeline: {PIPELINE_NAME}")
    pipeline.upsert(role_arn=ROLE_ARN)
    execution = pipeline.start()
    print(f"Pipeline execution started with ARN: {execution.arn}")