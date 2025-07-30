"""
Statistical analysis module for cancer clinical data.

This module provides comprehensive statistical analysis capabilities including
descriptive statistics, distribution analysis, and data quality assessment.
"""

from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.stats import entropy, kurtosis, skew


class StatisticalAnalyzer:
    """Statistical analysis class for cancer clinical data."""

    def __init__(self):
        """Initialize the statistical analyzer."""
        pass

    def summarize_numeric_column(self, series: pd.Series) -> Optional[Dict[str, Any]]:
        """
        Compute summary statistics for a numeric column.

        Args:
            series: Pandas Series containing numeric data

        Returns:
            Dictionary containing statistical summaries or None if empty
        """
        series = pd.to_numeric(series, errors="coerce").dropna()
        if series.empty:
            return None
        return {
            "min": float(series.min()),
            "max": float(series.max()),
            "mean": float(series.mean()),
            "std": float(series.std()),
            "skew": float(skew(series)),
            "kurtosis": float(kurtosis(series)),
            "outliers": int(
                (
                    (series < series.mean() - 2 * series.std())
                    | (series > series.mean() + 2 * series.std())
                ).sum()
            ),
        }

    def summarize_categorical_column(
        self, series: pd.Series
    ) -> Tuple[pd.DataFrame, float, float, float]:
        """
        Compute frequency distribution, imbalance, and entropy for a categorical column.

        Args:
            series: Pandas Series containing categorical data

        Returns:
            Tuple containing (summary_df, imbalance_ratio, entropy, normalized_entropy)
        """
        series = series.fillna("<<NA>>").astype(str)
        freqs = series.value_counts(dropna=False)
        props = freqs / freqs.sum()
        nz = props[props > 0]

        imbalance = float(nz.max() / nz.min()) if len(nz) > 1 else np.nan
        H = float(entropy(nz, base=2))
        H_norm = float(H / np.log2(len(nz))) if len(nz) > 1 else 1.0

        summary_df = pd.DataFrame({"frequency": freqs, "proportion": props.round(3)})

        return summary_df, imbalance, H, H_norm

    def full_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive statistical summary of a DataFrame.

        Args:
            df: DataFrame containing clinical data

        Returns:
            Dictionary with 'numeric' and 'categorical' summaries
        """
        print("\n====== Full Statistical Summary ======")

        result = {"numeric": {}, "categorical": {}}

        # --- Numeric Summary ---
        num_cols = df.select_dtypes(include=[np.number]).columns
        print("\n=== Numeric Summary ===")
        for col in num_cols:
            stats = self.summarize_numeric_column(df[col])
            if stats:
                result["numeric"][col] = stats
                print(f"{col}:")
                print(
                    f"  min={stats['min']:.2f}, max={stats['max']:.2f}, "
                    f"mean={stats['mean']:.2f}, std={stats['std']:.2f}, "
                    f"skew={stats['skew']:.2f}, kurtosis={stats['kurtosis']:.2f}, "
                    f"outliers={stats['outliers']}"
                )

        # --- Categorical Summary ---
        cat_cols = df.select_dtypes(include=["object", "category"]).columns
        print("\n=== Categorical Summary ===")
        for col in cat_cols:
            summary_df, imbalance, H, H_norm = self.summarize_categorical_column(
                df[col]
            )
            result["categorical"][col] = {
                "imbalance_ratio": imbalance,
                "entropy": H,
                "normalized_entropy": H_norm,
                "frequencies": summary_df.to_dict(orient="index"),
            }

            print(
                f"\n{col} (imbalance={imbalance:.2f}, entropy={H:.2f} / {H_norm:.2f}):"
            )
            print(summary_df.to_string())

        print("\n--------------------------------------")
        return result


# Legacy function for backward compatibility
def full_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Legacy function for backward compatibility.

    Args:
        df: DataFrame containing clinical data

    Returns:
        Dictionary with statistical summaries
    """
    analyzer = StatisticalAnalyzer()
    return analyzer.full_summary(df)
