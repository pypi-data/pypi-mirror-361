"""
Base model classes for cancer clinical data analysis.

This module provides abstract base classes and common functionality
for machine learning models used in cancer data analysis.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


class BaseModel(ABC):
    """Abstract base class for all cancer analysis models."""

    def __init__(self):
        """Initialize the base model."""
        self.is_trained = False
        self.features = []
        self.scaler = StandardScaler()

    @abstractmethod
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """Train the model with training data."""
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions on input data."""
        pass

    @abstractmethod
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """Evaluate the model performance."""
        pass

    def prepare_data(
        self,
        df: pd.DataFrame,
        target_column: str,
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare data for machine learning.

        Args:
            df: Input DataFrame
            target_column: Name of the target column
            test_size: Proportion of data for testing
            random_state: Random seed for reproducibility

        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        df = df.copy()

        # Drop unnecessary columns
        drop_cols = [
            "patient_id",
            "os_status",
            "pfs_status",
            "pfs_event",
            "pfs_months",
            "os_months",
        ]
        df.drop(
            columns=[col for col in drop_cols if col in df.columns],
            inplace=True,
            errors="ignore",
        )

        # Drop rows with missing target
        df.dropna(subset=[target_column], inplace=True)

        # Drop columns with all missing or only one value
        df = df.loc[:, df.nunique(dropna=False) > 1]
        df = df.loc[:, df.isnull().mean() < 0.5]

        # One-hot encode categorical variables
        df = pd.get_dummies(df, drop_first=True)

        # Replace inf and drop remaining NaNs
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.dropna(inplace=True)

        y = df[target_column].astype(int)
        X = df.drop(columns=[target_column])
        self.features = X.columns.tolist()

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        return train_test_split(
            X_scaled, y, test_size=test_size, random_state=random_state
        )

    def get_feature_names(self) -> List[str]:
        """Get the list of feature names."""
        return self.features.copy()

    def transform_features(self, X: pd.DataFrame) -> np.ndarray:
        """Transform new data using fitted scaler."""
        if not hasattr(self.scaler, "mean_"):
            raise ValueError("Model must be trained before transforming features")
        return self.scaler.transform(X)
