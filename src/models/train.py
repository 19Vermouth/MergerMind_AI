import os
import logging
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, precision_recall_fscore_support, classification_report
from sklearn.pipeline import Pipeline
import mlflow
import mlflow.sklearn

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    test_size: float = 0.2
    cv_folds: int = 5
    random_state: int = 42
    experiment_name: str = "dealsense_ma_prediction"


class MATrainingPipeline:
    def __init__(self, config: ModelConfig | None = None) -> None:
        self.config = config or ModelConfig()
        self.mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5001")
        mlflow.set_tracking_uri(self.mlflow_tracking_uri)
        mlflow.set_experiment(self.config.experiment_name)

        self.scaler = StandardScaler()
        self.models: dict[str, Any] = {}
        self.best_model: Any = None
        self.best_model_name: str = ""

    def load_training_data(self) -> pd.DataFrame:
        import sqlalchemy as sa
        from sqlalchemy import create_engine, text

        host = os.getenv("POSTGRES_HOST", "localhost")
        db = os.getenv("POSTGRES_DB", "dealsense")
        user = os.getenv("POSTGRES_USER", "dealsense_user")
        pw = os.getenv("POSTGRES_PASSWORD", "changeme")

        engine = create_engine(f"postgresql+psycopg2://{user}:{pw}@{host}:5432/{db}")

        query = text("""
            SELECT
                deal_id,
                historical_success_rate,
                log_deal_size,
                premium_paid,
                ev_revenue,
                ev_ebitda,
                synergy_ratio,
                cost_synergy_ratio,
                integration_cost_ratio,
                post_merger_score,
                deal_size_percentile,
                has_outcome
            FROM ml.feature_deal_model
            WHERE has_outcome = 1
        """)

        df = pd.read_sql(query, engine)
        logger.info(f"Loaded {len(df)} training records from ml.feature_deal_model")
        return df

    def prepare_data(self, df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        feature_cols = [
            "historical_success_rate", "log_deal_size", "premium_paid",
            "ev_revenue", "ev_ebitda", "synergy_ratio",
            "cost_synergy_ratio", "integration_cost_ratio",
            "post_merger_score", "deal_size_percentile",
        ]
        available_cols = [c for c in feature_cols if c in df.columns]
        missing = set(feature_cols) - set(available_cols)
        if missing:
            logger.warning(f"Missing feature columns: {missing}, using defaults")
            for col in missing:
                df[col] = 0.5

        X = df[available_cols].fillna(0).values
        y = df["has_outcome"].values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.config.test_size,
            random_state=self.config.random_state, stratify=y
        )

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        return X_train_scaled, X_test_scaled, y_train, y_test

    def initialize_models(self) -> dict[str, Any]:
        return {
            "logistic_regression": LogisticRegression(
                random_state=self.config.random_state, max_iter=1000, C=1.0
            ),
            "random_forest": RandomForestClassifier(
                n_estimators=100, max_depth=10,
                random_state=self.config.random_state, n_jobs=-1
            ),
        }

    def train_single_model(
        self, model: Any, model_name: str,
        X_train: np.ndarray, y_train: np.ndarray,
        X_test: np.ndarray, y_test: np.ndarray,
    ) -> dict[str, Any]:
        with mlflow.start_run(run_name=model_name):
            mlflow.log_param("model_type", model_name)
            mlflow.log_param("n_train", len(y_train))
            mlflow.log_param("n_test", len(y_test))
            mlflow.log_param("positive_ratio", round(y_train.mean(), 3))

            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1]

            roc_auc = roc_auc_score(y_test, y_proba)
            precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="binary")

            mlflow.log_metric("roc_auc", round(roc_auc, 4))
            mlflow.log_metric("precision", round(precision, 4))
            mlflow.log_metric("recall", round(recall, 4))
            mlflow.log_metric("f1_score", round(f1, 4))

            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_
                feature_names = [
                    "historical_success_rate", "log_deal_size", "premium_paid",
                    "ev_revenue", "ev_ebitda", "synergy_ratio",
                    "cost_synergy_ratio", "integration_cost_ratio",
                    "post_merger_score", "deal_size_percentile",
                ]
                for name, imp in zip(feature_names, importances):
                    mlflow.log_param(f"feature_importance_{name}", round(imp, 4))

            mlflow.sklearn.log_model(model, f"model_{model_name}")
            logger.info(f"{model_name}: ROC-AUC={roc_auc:.4f}, F1={f1:.4f}")

            return {
                "model": model,
                "roc_auc": roc_auc,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "model_name": model_name,
            }

    def run(self) -> dict[str, Any]:
        logger.info("Starting M&A prediction training pipeline")
        df = self.load_training_data()

        if len(df) < 10:
            logger.warning("Insufficient training data, using baseline model")
            return self._fallback_results()

        X_train, X_test, y_train, y_test = self.prepare_data(df)
        self.models = self.initialize_models()

        results = {}
        for name, model in self.models.items():
            result = self.train_single_model(model, name, X_train, y_train, X_test, y_test)
            results[name] = result

        self.best_model_name = max(results, key=lambda k: results[k]["roc_auc"])
        self.best_model = results[self.best_model_name]["model"]

        logger.info(f"Training complete. Best model: {self.best_model_name}")
        return {
            "best_model": self.best_model_name,
            "best_roc_auc": round(results[self.best_model_name]["roc_auc"], 4),
            "all_results": {k: {kk: vv for kk, vv in v.items() if kk != "model"} for k, v in results.items()},
            "n_train_samples": len(y_train),
            "n_test_samples": len(y_test),
        }

    def _fallback_results(self) -> dict[str, Any]:
        return {
            "best_model": "baseline",
            "best_roc_auc": 0.50,
            "all_results": {},
            "n_train_samples": 0,
            "n_test_samples": 0,
            "note": "Insufficient data for full training",
        }


def train_model() -> dict:
    pipeline = MATrainingPipeline()
    return pipeline.run()