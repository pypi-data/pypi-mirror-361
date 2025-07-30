"""
Data validation utilities for cancer clinical data analysis.

This module provides classes for validating clinical data integrity,
format, and consistency before processing.
"""

import logging
from dataclasses import dataclass
from typing import Any, List

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of data validation."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    passed_checks: List[str]


class DataValidator:
    """Data validator for cancer clinical data."""

    def __init__(self):
        """Initialize the data validator."""
        self.required_patient_columns = ["patient_id"]
        self.required_sample_columns = ["sample_id"]
        self.age_range = (0, 150)
        self.survival_time_range = (0, 500)  # months

    def validate_patient_data(self, df: pd.DataFrame) -> ValidationResult:
        """
        Validate patient clinical data.

        Args:
            df: Patient DataFrame to validate

        Returns:
            ValidationResult with validation outcome
        """
        errors = []
        warnings = []
        passed_checks = []

        # Check required columns
        missing_cols = [
            col for col in self.required_patient_columns if col not in df.columns
        ]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")
        else:
            passed_checks.append("All required columns present")

        # Check for empty dataframe
        if df.empty:
            errors.append("DataFrame is empty")
        else:
            passed_checks.append("DataFrame is not empty")

        # Validate patient IDs
        if "patient_id" in df.columns:
            if df["patient_id"].isnull().any():
                errors.append("Found null patient IDs")
            elif df["patient_id"].duplicated().any():
                warnings.append("Found duplicate patient IDs")
            else:
                passed_checks.append("Patient IDs are valid")

        # Validate age data
        if "age_at_diagnosis" in df.columns:
            age_validation = self._validate_age_column(df["age_at_diagnosis"])
            errors.extend(age_validation.errors)
            warnings.extend(age_validation.warnings)
            passed_checks.extend(age_validation.passed_checks)

        # Validate survival data
        survival_validation = self._validate_survival_data(df)
        errors.extend(survival_validation.errors)
        warnings.extend(survival_validation.warnings)
        passed_checks.extend(survival_validation.passed_checks)

        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings, passed_checks)

    def validate_sample_data(self, df: pd.DataFrame) -> ValidationResult:
        """
        Validate sample/pathology data.

        Args:
            df: Sample DataFrame to validate

        Returns:
            ValidationResult with validation outcome
        """
        errors = []
        warnings = []
        passed_checks = []

        # Check required columns
        missing_cols = [
            col for col in self.required_sample_columns if col not in df.columns
        ]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")
        else:
            passed_checks.append("All required columns present")

        # Check for empty dataframe
        if df.empty:
            warnings.append("Sample DataFrame is empty")
        else:
            passed_checks.append("DataFrame is not empty")

        # Validate sample IDs
        if "sample_id" in df.columns:
            if df["sample_id"].isnull().any():
                errors.append("Found null sample IDs")
            elif df["sample_id"].duplicated().any():
                warnings.append("Found duplicate sample IDs")
            else:
                passed_checks.append("Sample IDs are valid")

        # Validate tumor stage
        if "tumor_stage" in df.columns:
            stage_validation = self._validate_tumor_stage(df["tumor_stage"])
            warnings.extend(stage_validation.warnings)
            passed_checks.extend(stage_validation.passed_checks)

        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings, passed_checks)

    def _validate_age_column(self, age_series: pd.Series) -> ValidationResult:
        """Validate age data."""
        errors = []
        warnings = []
        passed_checks = []

        # Convert to numeric
        age_numeric = pd.to_numeric(age_series, errors="coerce")

        # Check for non-numeric values
        non_numeric_count = age_series.notna().sum() - age_numeric.notna().sum()
        if non_numeric_count > 0:
            warnings.append(f"Found {non_numeric_count} non-numeric age values")

        # Check age range
        valid_ages = age_numeric.dropna()
        if len(valid_ages) > 0:
            min_age, max_age = self.age_range
            invalid_ages = valid_ages[(valid_ages < min_age) | (valid_ages > max_age)]
            if len(invalid_ages) > 0:
                errors.append(
                    f"Found {len(invalid_ages)} ages outside valid range ({min_age}-{max_age})"
                )
            else:
                passed_checks.append("All ages within valid range")

        # Check for missing values
        missing_pct = (age_series.isnull().sum() / len(age_series)) * 100
        if missing_pct > 50:
            warnings.append(f"High percentage of missing ages: {missing_pct:.1f}%")
        elif missing_pct > 0:
            warnings.append(f"Some missing ages: {missing_pct:.1f}%")
        else:
            passed_checks.append("No missing age values")

        return ValidationResult(len(errors) == 0, errors, warnings, passed_checks)

    def _validate_survival_data(self, df: pd.DataFrame) -> ValidationResult:
        """Validate survival time and event data."""
        errors = []
        warnings = []
        passed_checks = []

        # Check overall survival data
        if "os_months" in df.columns and "os_event" in df.columns:
            os_validation = self._validate_survival_pair(
                df["os_months"], df["os_event"], "OS"
            )
            errors.extend(os_validation.errors)
            warnings.extend(os_validation.warnings)
            passed_checks.extend(os_validation.passed_checks)

        # Check progression-free survival data
        if "pfs_months" in df.columns and "pfs_event" in df.columns:
            pfs_validation = self._validate_survival_pair(
                df["pfs_months"], df["pfs_event"], "PFS"
            )
            errors.extend(pfs_validation.errors)
            warnings.extend(pfs_validation.warnings)
            passed_checks.extend(pfs_validation.passed_checks)

        return ValidationResult(len(errors) == 0, errors, warnings, passed_checks)

    def _validate_survival_pair(
        self, time_series: pd.Series, event_series: pd.Series, survival_type: str
    ) -> ValidationResult:
        """Validate a pair of survival time and event columns."""
        errors = []
        warnings = []
        passed_checks = []

        # Convert time to numeric
        time_numeric = pd.to_numeric(time_series, errors="coerce")

        # Check for negative survival times
        if time_numeric.notna().any():
            negative_times = (time_numeric < 0).sum()
            if negative_times > 0:
                errors.append(
                    f"Found {negative_times} negative {survival_type} survival times"
                )
            else:
                passed_checks.append(f"No negative {survival_type} survival times")

        # Check for very long survival times (potential outliers)
        max_time = self.survival_time_range[1]
        if time_numeric.notna().any():
            long_times = (time_numeric > max_time).sum()
            if long_times > 0:
                warnings.append(
                    f"Found {long_times} {survival_type} times > {max_time} months (potential outliers)"
                )

        # Check event values
        event_numeric = pd.to_numeric(event_series, errors="coerce")
        if event_numeric.notna().any():
            valid_events = event_numeric.isin([0, 1])
            invalid_events = (~valid_events & event_numeric.notna()).sum()
            if invalid_events > 0:
                errors.append(
                    f"Found {invalid_events} invalid {survival_type} event values (should be 0 or 1)"
                )
            else:
                passed_checks.append(f"All {survival_type} event values are valid")

        return ValidationResult(len(errors) == 0, errors, warnings, passed_checks)

    def _validate_tumor_stage(self, stage_series: pd.Series) -> ValidationResult:
        """Validate tumor stage data."""
        errors = []
        warnings = []
        passed_checks = []

        # Check for valid stage formats
        valid_stages = stage_series.dropna().astype(str)
        if len(valid_stages) > 0:
            # Common stage patterns
            stage_patterns = [
                "I",
                "II",
                "III",
                "IV",
                "i",
                "ii",
                "iii",
                "iv",
                "stage i",
                "stage ii",
                "stage iii",
                "stage iv",
            ]

            # Check if stages contain expected patterns
            has_valid_pattern = valid_stages.str.contains(
                "|".join(stage_patterns), case=False, na=False
            )
            invalid_stages = (~has_valid_pattern).sum()

            if invalid_stages > 0:
                warnings.append(
                    f"Found {invalid_stages} potentially invalid tumor stage formats"
                )
            else:
                passed_checks.append("Tumor stage formats appear valid")

        return ValidationResult(True, errors, warnings, passed_checks)

    def is_valid_age(self, age: Any) -> bool:
        """Check if a single age value is valid."""
        try:
            if age is None or not isinstance(age, (int, float)):
                return False
            return 0 < age < 150
        except (ValueError, TypeError):
            return False
