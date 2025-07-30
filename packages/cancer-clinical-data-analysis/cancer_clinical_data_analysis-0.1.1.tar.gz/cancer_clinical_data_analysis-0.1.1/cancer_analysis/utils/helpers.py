"""
Helper functions and utilities for cancer clinical data analysis.

This module provides common utility functions used across the package
for data manipulation, formatting, and validation.
"""

import re
from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd


def format_survival_time(months: Union[float, int], unit: str = "months") -> str:
    """
    Format survival time for display.

    Args:
        months: Survival time in months
        unit: Output unit ('months', 'years', 'auto')

    Returns:
        Formatted survival time string
    """
    if pd.isna(months):
        return "N/A"

    if unit == "years":
        years = months / 12
        return f"{years:.1f} years"
    elif unit == "auto":
        if months >= 24:
            years = months / 12
            return f"{years:.1f} years"
        else:
            return f"{months:.1f} months"
    else:
        return f"{months:.1f} months"


def validate_patient_data(
    df: pd.DataFrame, required_columns: List[str] = None
) -> Dict[str, Any]:
    """
    Validate patient data integrity.

    Args:
        df: Patient DataFrame to validate
        required_columns: List of required column names

    Returns:
        Dictionary with validation results
    """
    if required_columns is None:
        required_columns = ["patient_id"]

    validation_result = {"is_valid": True, "errors": [], "warnings": [], "stats": {}}

    # Check for required columns
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        validation_result["errors"].append(f"Missing required columns: {missing_cols}")
        validation_result["is_valid"] = False

    # Check for empty DataFrame
    if df.empty:
        validation_result["errors"].append("DataFrame is empty")
        validation_result["is_valid"] = False
        return validation_result

    # Collect statistics
    validation_result["stats"] = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_data_percentage": (df.isnull().sum().sum() / df.size) * 100,
        "duplicate_rows": df.duplicated().sum(),
    }

    # Check for duplicate patient IDs
    if "patient_id" in df.columns:
        duplicates = df["patient_id"].duplicated().sum()
        if duplicates > 0:
            validation_result["warnings"].append(
                f"Found {duplicates} duplicate patient IDs"
            )

    return validation_result


def clean_text_column(series: pd.Series, standardize_case: bool = True) -> pd.Series:
    """
    Clean text data in a pandas Series.

    Args:
        series: Pandas Series with text data
        standardize_case: Whether to convert to lowercase

    Returns:
        Cleaned Series
    """
    # Convert to string and handle missing values
    cleaned = series.astype(str).replace("nan", np.nan)

    # Remove extra whitespace
    cleaned = cleaned.str.strip()

    # Standardize case if requested
    if standardize_case:
        cleaned = cleaned.str.lower()

    # Replace empty strings with NaN
    cleaned = cleaned.replace("", np.nan)

    return cleaned


def categorize_age(age: Union[float, int], bins: List[int] = None) -> str:
    """
    Categorize age into groups.

    Args:
        age: Age value
        bins: Age bin boundaries

    Returns:
        Age category string
    """
    if pd.isna(age):
        return "Unknown"

    if bins is None:
        bins = [0, 40, 60, 80, 150]

    labels = [f"{bins[i]}-{bins[i + 1] - 1}" for i in range(len(bins) - 1)]
    labels[-1] = f"{bins[-2]}+"

    for i, upper_bound in enumerate(bins[1:]):
        if age < upper_bound:
            return labels[i]

    return labels[-1]


def standardize_tumor_stage(stage: str) -> str:
    """
    Standardize tumor stage notation.

    Args:
        stage: Raw tumor stage string

    Returns:
        Standardized stage string
    """
    if pd.isna(stage):
        return "Unknown"

    stage_str = str(stage).upper().strip()

    # Remove common prefixes
    stage_str = re.sub(r"^(STAGE\s*|T)", "", stage_str)

    # Standardize Roman numerals
    stage_mappings = {
        "I": "I",
        "II": "II",
        "III": "III",
        "IV": "IV",
        "1": "I",
        "2": "II",
        "3": "III",
        "4": "IV",
    }

    for key, value in stage_mappings.items():
        if key in stage_str:
            return f"Stage {value}"

    return stage_str if stage_str else "Unknown"


def calculate_summary_stats(
    df: pd.DataFrame, numeric_only: bool = True
) -> Dict[str, Dict[str, float]]:
    """
    Calculate summary statistics for DataFrame columns.

    Args:
        df: Input DataFrame
        numeric_only: Whether to calculate stats only for numeric columns

    Returns:
        Dictionary of column statistics
    """
    stats = {}

    columns = (
        df.select_dtypes(include=[np.number]).columns if numeric_only else df.columns
    )

    for col in columns:
        if df[col].dtype in [np.number]:
            series = pd.to_numeric(df[col], errors="coerce")
            stats[col] = {
                "count": series.notna().sum(),
                "mean": series.mean(),
                "std": series.std(),
                "min": series.min(),
                "max": series.max(),
                "median": series.median(),
                "missing_pct": (series.isna().sum() / len(series)) * 100,
            }
        else:
            series = df[col]
            stats[col] = {
                "count": series.notna().sum(),
                "unique": series.nunique(),
                "top": series.mode().iloc[0] if len(series.mode()) > 0 else None,
                "missing_pct": (series.isna().sum() / len(series)) * 100,
            }

    return stats


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format a decimal as a percentage string.

    Args:
        value: Decimal value (0-1)
        decimals: Number of decimal places

    Returns:
        Formatted percentage string
    """
    if pd.isna(value):
        return "N/A"
    return f"{value * 100:.{decimals}f}%"


def safe_divide(numerator: Union[float, int], denominator: Union[float, int]) -> float:
    """
    Safely divide two numbers, handling division by zero.

    Args:
        numerator: Numerator value
        denominator: Denominator value

    Returns:
        Division result or NaN if division by zero
    """
    if denominator == 0 or pd.isna(denominator) or pd.isna(numerator):
        return np.nan
    return numerator / denominator


def merge_clinical_pathology(
    clinical_df: pd.DataFrame, pathology_df: pd.DataFrame, join_key: str = "patient_id"
) -> pd.DataFrame:
    """
    Merge clinical and pathology data.

    Args:
        clinical_df: Clinical data DataFrame
        pathology_df: Pathology data DataFrame
        join_key: Column to join on

    Returns:
        Merged DataFrame
    """
    if join_key not in clinical_df.columns:
        raise ValueError(f"Join key '{join_key}' not found in clinical data")

    # For pathology data, we might need to map sample_id to patient_id
    if join_key == "patient_id" and "sample_id" in pathology_df.columns:
        # Assume sample_id can be mapped to patient_id (implementation specific)
        # This is a simplified approach - actual mapping might be more complex
        pass

    merged = clinical_df.merge(
        pathology_df, on=join_key, how="left", suffixes=("", "_path")
    )
    return merged
