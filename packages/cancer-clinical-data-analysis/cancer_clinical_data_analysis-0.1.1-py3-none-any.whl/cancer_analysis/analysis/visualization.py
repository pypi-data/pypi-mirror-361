"""
Visualization module for cancer clinical data analysis.

This module provides comprehensive visualization capabilities including
Kaplan-Meier survival curves, demographic plots, and model performance visualizations.
"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from lifelines import KaplanMeierFitter
from lifelines.plotting import add_at_risk_counts
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix


class Visualizer:
    """Visualization class for cancer clinical data analysis."""

    def __init__(self, results_dir: str = "results"):
        """
        Initialize the visualizer.

        Args:
            results_dir: Directory to save visualization outputs
        """
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)

    def plot_kaplan_meier(
        self,
        df: pd.DataFrame,
        time_col: str,
        event_col: str,
        title: str,
        filename: str = "kaplan_meier.png",
    ) -> None:
        """
        Plot and save Kaplan-Meier survival curve.

        Args:
            df: DataFrame containing survival data
            time_col: Column name for survival time
            event_col: Column name for event indicator (1=event, 0=censored)
            title: Plot title
            filename: Output filename
        """
        df = df.dropna(subset=[time_col, event_col])
        kmf = KaplanMeierFitter()
        kmf.fit(df[time_col], event_observed=df[event_col])

        ax = kmf.plot(ci_show=True, figsize=(8, 6))
        add_at_risk_counts(kmf, ax=ax)
        ax.set_title(title)
        ax.set_xlabel("Time (months)")
        ax.set_ylabel("Probability of Survival")
        ax.grid(True, linestyle="--")

        plt.tight_layout()
        path = os.path.join(self.results_dir, filename)
        plt.savefig(path)
        plt.close()

    def plot_demographics(
        self, df: pd.DataFrame, filename: str = "demographics.png"
    ) -> None:
        """
        Plot and save bar charts for gender, race, and ethnicity.

        Args:
            df: DataFrame with demographic info
            filename: Output filename
        """
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        columns = ["gender", "race", "ethnicity"]
        titles = ["Gender Distribution", "Race Distribution", "Ethnicity Distribution"]

        for ax, col, title in zip(axes, columns, titles):
            if col in df:
                df[col].fillna("Missing").value_counts().plot.bar(
                    ax=ax, color="skyblue"
                )
                ax.set_title(title)
                ax.set_ylabel("Count")
                ax.tick_params(axis="x", rotation=45)

        plt.tight_layout()
        path = os.path.join(self.results_dir, filename)
        plt.savefig(path)
        plt.close()

    def plot_age_distribution(
        self,
        df: pd.DataFrame,
        column: str = "age_at_diagnosis",
        filename: str = "age_distribution.png",
    ) -> None:
        """
        Plot and save histogram and boxplot of age at diagnosis.

        Args:
            df: DataFrame with age column
            column: Column name for age
            filename: Output filename
        """
        if column not in df:
            return
        age = pd.to_numeric(df[column], errors="coerce").dropna()
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        ax1.hist(age, bins=20, color="lightgreen", edgecolor="black")
        ax1.set_title("Age at Diagnosis (Histogram)")
        ax1.set_xlabel("Age (years)")
        ax1.set_ylabel("Count")

        ax2.boxplot(
            age, vert=True, patch_artist=True, boxprops=dict(facecolor="lightblue")
        )
        ax2.set_title("Age at Diagnosis (Boxplot)")
        ax2.set_ylabel("Age (years)")

        plt.tight_layout()
        path = os.path.join(self.results_dir, filename)
        plt.savefig(path)
        plt.close()

    def plot_feature_importance(
        self,
        df_importance: pd.DataFrame,
        top_n: int = 10,
        filename: str = "feature_importance.png",
    ) -> None:
        """
        Plot and save a bar chart of top N features sorted by importance.

        Args:
            df_importance: DataFrame with 'feature' and 'importance' columns
            top_n: Number of top features to plot
            filename: Output filename
        """
        top_features = df_importance.head(top_n)

        plt.figure(figsize=(10, 6))
        sns.barplot(x="importance", y="feature", data=top_features, palette="viridis")
        plt.title(f"Top {top_n} Most Influential Features", fontsize=14)
        plt.xlabel("Importance (absolute value of coefficient)", fontsize=12)
        plt.ylabel("Feature", fontsize=12)
        plt.grid(axis="x", linestyle="--", alpha=0.7)

        for index, value in enumerate(top_features["importance"]):
            plt.text(value + 0.01, index, f"{value:.2f}", va="center")

        plt.tight_layout()
        file_path = os.path.join(self.results_dir, filename)
        plt.savefig(file_path)
        plt.close()

    def plot_confusion_matrix(
        self, y_true, y_pred, filename: str = "confusion_matrix.png"
    ) -> None:
        """
        Plot and save confusion matrix.

        Args:
            y_true: Ground truth labels
            y_pred: Predicted labels
            filename: Output filename
        """
        cm = confusion_matrix(y_true, y_pred)
        labels = ["Survived", "Died"]
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
        fig, ax = plt.subplots(figsize=(6, 5))
        disp.plot(cmap="Blues", ax=ax, values_format="d")

        ax.set_title("Confusion Matrix: Survival Prediction", fontsize=14)
        ax.set_xlabel("Predicted Label", fontsize=12)
        ax.set_ylabel("True Label", fontsize=12)
        plt.grid(False)
        plt.tight_layout()

        file_path = os.path.join(self.results_dir, filename)
        plt.savefig(file_path)
        plt.close()


# Legacy functions for backward compatibility
def plot_kaplan_meier(
    df: pd.DataFrame, time_col: str, event_col: str, title: str, results_dir: str
):
    """Legacy function for backward compatibility."""
    visualizer = Visualizer(results_dir)
    visualizer.plot_kaplan_meier(df, time_col, event_col, title)


def plot_demographics(df: pd.DataFrame, results_dir: str):
    """Legacy function for backward compatibility."""
    visualizer = Visualizer(results_dir)
    visualizer.plot_demographics(df)


def plot_age_distribution(
    df: pd.DataFrame, results_dir: str, column="age_at_diagnosis"
):
    """Legacy function for backward compatibility."""
    visualizer = Visualizer(results_dir)
    visualizer.plot_age_distribution(df, column)


def plot_feature_importance(df_importance: pd.DataFrame, save_path: str, top_n=10):
    """Legacy function for backward compatibility."""
    visualizer = Visualizer(save_path)
    visualizer.plot_feature_importance(df_importance, top_n)


def plot_confusion(y_true, y_pred, save_path: str):
    """Legacy function for backward compatibility."""
    visualizer = Visualizer(save_path)
    visualizer.plot_confusion_matrix(y_true, y_pred)
