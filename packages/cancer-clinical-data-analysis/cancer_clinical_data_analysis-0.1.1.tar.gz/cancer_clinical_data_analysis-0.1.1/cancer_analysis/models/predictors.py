"""
Risk prediction models for cancer clinical data analysis.

This module provides specialized models for risk assessment and prediction
using various machine learning algorithms.
"""

from typing import Any, Dict

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from .base import BaseModel


class RiskPredictor(BaseModel):
    """
    Random Forest-based risk predictor for cancer patients.
    Provides risk scores and feature importance analysis.
    """

    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        """
        Initialize the risk predictor.

        Args:
            n_estimators: Number of trees in the forest
            random_state: Random seed for reproducibility
        """
        super().__init__()
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            class_weight="balanced",
        )

    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """
        Train the risk prediction model.

        Args:
            X_train: Training features
            y_train: Training labels
        """
        self.model.fit(X_train, y_train)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make risk predictions on input data.

        Args:
            X: Input features

        Returns:
            Predicted risk categories
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        return self.model.predict(X)

    def predict_risk_scores(self, X: np.ndarray) -> np.ndarray:
        """
        Predict risk scores (probabilities) for high-risk category.

        Args:
            X: Input features

        Returns:
            Risk scores between 0 and 1
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        return self.model.predict_proba(X)[:, 1]

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """
        Evaluate the model performance.

        Args:
            X_test: Test features
            y_test: Test labels

        Returns:
            Dictionary containing evaluation metrics
        """
        from sklearn.metrics import accuracy_score, classification_report, roc_auc_score

        if not self.is_trained:
            raise ValueError("Model must be trained before evaluation")

        y_pred = self.predict(X_test)
        y_proba = self.predict_risk_scores(X_test)

        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "auc_roc": roc_auc_score(y_test, y_proba),
            "classification_report": classification_report(
                y_test, y_pred, output_dict=True
            ),
        }

        return metrics

    def get_feature_importance(self) -> pd.DataFrame:
        """
        Get feature importance from the trained Random Forest model.

        Returns:
            DataFrame with features and their importance scores
        """
        if not self.is_trained:
            raise ValueError("Model must be trained to get feature importance")

        importance_scores = self.model.feature_importances_
        importance_df = pd.DataFrame(
            {"feature": self.features, "importance": importance_scores}
        ).sort_values(by="importance", ascending=False)

        return importance_df
