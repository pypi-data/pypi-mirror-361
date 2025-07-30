"""
Survival classification models for cancer clinical data analysis.

This module provides specialized models for survival prediction and classification
using various machine learning algorithms.
"""

from typing import Any, Dict

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)

from .base import BaseModel


class SurvivalClassifier(BaseModel):
    """
    Logistic Regression model for binary survival classification.
    Predicts the risk of death using clinical features.
    """

    def __init__(self, max_iter: int = 1000, random_state: int = 42):
        """
        Initialize the survival classifier.

        Args:
            max_iter: Maximum number of iterations for optimization
            random_state: Random seed for reproducibility
        """
        super().__init__()
        self.model = LogisticRegression(max_iter=max_iter, random_state=random_state)

    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """
        Train the logistic regression model.

        Args:
            X_train: Training features
            y_train: Training labels
        """
        self.model.fit(X_train, y_train)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions on input data.

        Args:
            X: Input features

        Returns:
            Predicted binary labels
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities.

        Args:
            X: Input features

        Returns:
            Predicted probabilities for each class
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        return self.model.predict_proba(X)

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """
        Evaluate the model performance.

        Args:
            X_test: Test features
            y_test: Test labels

        Returns:
            Dictionary containing evaluation metrics
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before evaluation")

        y_pred = self.predict(X_test)
        y_proba = self.predict_proba(X_test)[:, 1]

        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "auc_roc": roc_auc_score(y_test, y_proba),
            "classification_report": classification_report(
                y_test, y_pred, output_dict=True
            ),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        }

        return metrics

    def print_evaluation(self, X_test: np.ndarray, y_test: np.ndarray) -> None:
        """
        Print detailed evaluation report.

        Args:
            X_test: Test features
            y_test: Test labels
        """
        y_pred = self.predict(X_test)
        print("\nSurvival Classification Report:")
        print("=" * 50)
        print(classification_report(y_test, y_pred))
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))

    def get_feature_importance(self) -> pd.DataFrame:
        """
        Get feature importance based on model coefficients.

        Returns:
            DataFrame with features and their importance scores
        """
        if not self.is_trained:
            raise ValueError("Model must be trained to get feature importance")

        coefs = self.model.coef_[0]
        importance_df = pd.DataFrame(
            {
                "feature": self.features,
                "coefficient": coefs,
                "importance": np.abs(coefs),
            }
        ).sort_values(by="importance", ascending=False)

        return importance_df


# Legacy class for backward compatibility
class SurvivalModel(SurvivalClassifier):
    """Legacy class name for backward compatibility."""

    def __init__(self):
        """Initialize with original default parameters."""
        super().__init__(max_iter=1000, random_state=42)

    def prepare_data(self, df: pd.DataFrame) -> tuple:
        """
        Legacy method for backward compatibility.

        Args:
            df: Input DataFrame

        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        return super().prepare_data(df, target_column="os_event")

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> None:
        """Legacy evaluation method that prints results."""
        self.print_evaluation(X_test, y_test)
