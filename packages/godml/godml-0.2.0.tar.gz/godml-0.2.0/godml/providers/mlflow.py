import mlflow
import mlflow.xgboost
from godml.core.engine import BaseExecutor
from sklearn.base import BaseEstimator
from godml.core.models import PipelineDefinition
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import xgboost as xgb
import os
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import importlib
from godml.utils.log_model_generic import log_model_generic
from xgboost import Booster as XGBBooster
from godml.utils.predict_safely import predict_safely
from godml.utils.logger import get_logger

logger = get_logger()

class MLflowExecutor(BaseExecutor):
    def __init__(self, tracking_uri: str = None):
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment("godml-experiment")

    def preprocess_for_xgboost(self, df, target_col="target"):
        if target_col not in df.columns:
            raise ValueError("El dataset debe contener una columna llamada 'target'.")
        if df[target_col].dtype == object:
            df[target_col] = df[target_col].map({"Yes": 1, "No": 0})

        y = df[target_col]
        X = df.drop(columns=[target_col])

        cat_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
        if cat_cols:
            X = pd.get_dummies(X, columns=cat_cols, drop_first=True)
        return X, y

    def run(self, pipeline: PipelineDefinition):
        logger.info(f"🚀 Entrenando modelo con MLflow: {pipeline.name}")

        dataset_path = pipeline.dataset.uri
        if dataset_path.startswith("s3://"):
            raise ValueError("MLflowExecutor solo soporta datasets locales (CSV).")

        df = pd.read_csv(dataset_path)
        X, y = self.preprocess_for_xgboost(df, target_col="target")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=max(0.5, 2 / len(X)), random_state=42, stratify=y
        )

        params = pipeline.model.hyperparameters.dict()

        max_attempts = 3
        for attempt in range(max_attempts):
            with mlflow.start_run(run_name=pipeline.name):
                mlflow.log_artifact(dataset_path, artifact_path="dataset")

                mlflow.set_tag("dataset.uri", pipeline.dataset.uri)
                mlflow.set_tag("dataset.version", pipeline.version)
                mlflow.set_tag("version", pipeline.version)
                if hasattr(pipeline, "description"):
                    mlflow.set_tag("description", pipeline.description)
                if hasattr(pipeline.governance, "owner"):
                    mlflow.set_tag("owner", pipeline.governance.owner)
                if hasattr(pipeline.governance, "tags"):
                    for tag_dict in pipeline.governance.tags:
                        for k, v in tag_dict.items():
                            mlflow.set_tag(k, v)

                for param_name, param_value in params.items():
                    mlflow.log_param(param_name, param_value)

                model_type = pipeline.model.type.lower()
                module_path = f"godml.core.models_registry.{model_type}_model"
                model_module = importlib.import_module(module_path)

                booster, preds = model_module.train_model(X_train, y_train, X_test, y_test, params)
                
                input_example = X_train.iloc[:5]
                output_example = predict_safely(booster, input_example)

                signature = mlflow.models.signature.infer_signature(input_example, output_example)

                log_model_generic(
                    booster,
                    model_name="model",
                    registered_model_name=f"{pipeline.name}-{pipeline.model.type}"
                )

                y_pred_binary = (preds >= 0.5).astype(int)

                metrics_dict = {
                    "auc": roc_auc_score(y_test, preds),
                    "accuracy": accuracy_score(y_test, y_pred_binary),
                    "precision": precision_score(y_test, y_pred_binary, zero_division=0),
                    "recall": recall_score(y_test, y_pred_binary, zero_division=0),
                    "f1": f1_score(y_test, y_pred_binary, zero_division=0),
                }

                for metric_name, value in metrics_dict.items():
                    mlflow.log_metric(metric_name, value)

                logger.info("📊 Métricas:")
                for k, v in metrics_dict.items():
                    logger.info(f" - {k}: {v:.4f}")

                logger.info(f"✅ Entrenamiento finalizado. AUC: {metrics_dict['auc']:.4f}")

                all_metrics_passed = True
                for metric in pipeline.metrics:
                    metric_name = metric.name
                    threshold = metric.threshold
                    value = metrics_dict.get(metric_name)
                    if value is None:
                        logger.warning(f"⚠️ Advertencia: métrica '{metric_name}' no fue calculada.")
                        continue
                    if value < threshold:
                        logger.error(f"🚫 {metric_name.upper()} ({value:.4f}) por debajo del mínimo requerido ({threshold})")
                        all_metrics_passed = False

                if all_metrics_passed:
                    if pipeline.deploy.batch_output:
                        os.makedirs(os.path.dirname(pipeline.deploy.batch_output), exist_ok=True)
                        pd.DataFrame({"prediction": preds}).to_csv(pipeline.deploy.batch_output, index=False)
                        logger.info(f"📦 Predicciones guardadas en: {pipeline.deploy.batch_output}")
                    break
                elif attempt < max_attempts - 1:
                    logger.warning(f"🔁 Reentrenando... (intento {attempt + 2}/{max_attempts})")
                else:
                    logger.error("❌ Reentrenamiento fallido. Las métricas no alcanzaron los umbrales esperados.")
                    logger.info("💡 Sugerencias:")
                    logger.info("   - Ajusta los thresholds en godml.yml")
                    logger.info("   - Mejora la calidad del dataset")
                    logger.info("   - Prueba otros hiperparámetros")
                    return False  # En lugar de raise ValueError

    def validate(self, pipeline: PipelineDefinition):
        from godml.core.validators import validate_pipeline
        warnings = validate_pipeline(pipeline)
        for w in warnings:
            print("⚠️", w)
