"""
Data preprocessing utilities for cancer clinical data analysis.

This module provides classes for cleaning, transforming, and preparing
clinical data for analysis and machine learning.
"""

import logging
from typing import Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Data preprocessor for cancer clinical data."""

    def __init__(self):
        """Initialize the data preprocessor."""
        self.clinical_mapping = {
            "patientid": "patient_id",
            "sex": "gender",
            "race": "race",
            "ethnicity": "ethnicity",
            "age": "age_at_diagnosis",
            "os_status": "os_status",
            "os_months": "os_months",
            "pfs_status": "pfs_status",
            "pfs_months": "pfs_months",
        }

        self.pathology_mapping = {
            "sampleid": "sample_id",
            "tumor_grade": "tumor_grade",
            "er_status": "er_status",
            "pr_status": "pr_status",
            "her2_status": "her2_status",
            "tumor_stage": "tumor_stage",
            "cancer_type": "cancer_type",
        }

    def snake_case_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert column names to snake_case format.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with snake_case column names
        """
        df = df.copy()
        df.columns = (
            df.columns.str.lower()
            .str.replace(r"[^0-9a-z]+", "_", regex=True)
            .str.strip("_")
        )
        return df

    def status_to_event(self, status_series: pd.Series) -> pd.Series:
        """
        Convert status strings to binary event indicators.

        Args:
            status_series: Series containing status values

        Returns:
            Series with binary event indicators (1=event, 0=censored)
        """

        def convert_status(x):
            if pd.isnull(x):
                return np.nan
            x = str(x).lower()
            if any(
                term in x for term in ["1", "deceased", "dead", "recurr", "progress"]
            ):
                return 1
            if any(
                term in x for term in ["0", "living", "alive", "no evidence", "free"]
            ):
                return 0
            return np.nan

        return status_series.apply(convert_status)

    def pivot_clinical_data(
        self, df_pat: pd.DataFrame, df_samp: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Pivot clinical data from long to wide format.

        Args:
            df_pat: Patient data in long format
            df_samp: Sample data in long format

        Returns:
            Tuple of (patient_wide, sample_wide) DataFrames
        """
        # Pivot to wide format
        df_pat_wide = df_pat.pivot(
            index="patientId", columns="clinicalAttributeId", values="value"
        ).reset_index()

        df_samp_wide = df_samp.pivot(
            index="sampleId", columns="clinicalAttributeId", values="value"
        ).reset_index()

        logger.info(f"Pivoted patient table: {df_pat_wide.shape}")
        logger.info(f"Pivoted sample table: {df_samp_wide.shape}")

        return df_pat_wide, df_samp_wide

    def clean_clinical_data(self, df_pat: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize clinical data.

        Args:
            df_pat: Patient data DataFrame

        Returns:
            Cleaned clinical DataFrame
        """
        # Convert to snake_case
        df_pat = self.snake_case_columns(df_pat)

        # Select and rename columns
        keep_clin = [k for k in self.clinical_mapping if k in df_pat.columns]
        df_clin = df_pat[keep_clin].rename(columns=self.clinical_mapping)

        logger.info(f"Cleaned clinical columns: {df_clin.columns.tolist()}")

        # Convert times to numeric
        for col in ["os_months", "pfs_months"]:
            if col in df_clin.columns:
                df_clin[col] = pd.to_numeric(df_clin[col], errors="coerce")

        # Convert status to binary events
        if "os_status" in df_clin.columns:
            df_clin["os_event"] = self.status_to_event(df_clin["os_status"])
        if "pfs_status" in df_clin.columns:
            df_clin["pfs_event"] = self.status_to_event(df_clin["pfs_status"])

        # Remove invalid survival data
        if {"os_months", "os_event"}.issubset(df_clin.columns):
            initial_count = len(df_clin)
            df_clin = df_clin[
                (~df_clin["os_months"].isnull())
                & (~df_clin["os_event"].isnull())
                & (df_clin["os_months"] > 0)
            ]
            logger.info(
                f"Removed {initial_count - len(df_clin)} invalid survival records"
            )

        return df_clin

    def clean_pathology_data(self, df_samp: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize pathology data.

        Args:
            df_samp: Sample data DataFrame

        Returns:
            Cleaned pathology DataFrame
        """
        # Convert to snake_case
        df_samp = self.snake_case_columns(df_samp)

        # Select and rename columns
        keep_path = [k for k in self.pathology_mapping if k in df_samp.columns]
        df_path = df_samp[keep_path].rename(columns=self.pathology_mapping)

        logger.info(f"Cleaned pathology columns: {df_path.columns.tolist()}")

        # Check for missing expected columns
        expected_cols = [
            "tumor_grade",
            "tumor_stage",
            "er_status",
            "pr_status",
            "her2_status",
        ]
        missing_cols = [col for col in expected_cols if col not in df_path.columns]
        if missing_cols:
            logger.warning(f"Missing pathology fields: {missing_cols}")

        return df_path

    def generate_missing_report(self, df: pd.DataFrame, name: str) -> pd.DataFrame:
        """
        Generate missing data summary report.

        Args:
            df: DataFrame to analyze
            name: Name for the report

        Returns:
            DataFrame with missing data statistics
        """
        total = len(df)
        missing = df.isna().sum()
        pct = (missing / total * 100).round(1)

        report = pd.DataFrame({"missing": missing, "percentage_missing": pct})

        report["status"] = np.where(
            report["missing"] == 0,
            "none missing",
            np.where(report["missing"] == total, "all missing", "some missing"),
        )

        total_cells = df.size
        total_missing = df.isna().sum().sum()
        percent_missing_cells = (total_missing / total_cells) * 100
        cols_over_50 = (pct > 50).sum()

        logger.info(f"\n--- Missing Data Report for {name} ---")
        logger.info(
            f"{total_missing} missing cells out of {total_cells} "
            f"({percent_missing_cells:.1f}%)"
        )
        logger.info(f"{cols_over_50} columns have >50% missing values")

        return report

    def process_all_data(
        self, df_pat: pd.DataFrame, df_samp: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Complete preprocessing pipeline for clinical data.

        Args:
            df_pat: Raw patient data
            df_samp: Raw sample data

        Returns:
            Tuple of (cleaned_clinical, cleaned_pathology)
        """
        # Pivot data
        df_pat_wide, df_samp_wide = self.pivot_clinical_data(df_pat, df_samp)

        # Clean data
        df_clin = self.clean_clinical_data(df_pat_wide)
        df_path = self.clean_pathology_data(df_samp_wide)

        # Generate reports
        self.generate_missing_report(df_clin, "Clinical")
        self.generate_missing_report(df_path, "Pathology")

        return df_clin, df_path


# Legacy class for backward compatibility
class DataProcessor(DataPreprocessor):
    """Legacy class for backward compatibility."""

    def __init__(self, study_id: str = "luad_tcga_gdc"):
        """Initialize with study_id for compatibility."""
        super().__init__()
        from .loaders import DataLoader

        self.loader = DataLoader(study_id)
        self.df_pat = None
        self.df_samp = None
        self.df_clin = None
        self.df_path = None

    def load_data(self):
        """Load data using the data loader."""
        self.df_pat, self.df_samp = self.loader.load_all_data()

    def preprocess_data(self):
        """Preprocess the loaded data."""
        if self.df_pat is None or self.df_samp is None:
            raise ValueError("Data must be loaded before preprocessing")
        self.df_clin, self.df_path = self.process_all_data(self.df_pat, self.df_samp)

    def get_cleaned_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Get cleaned data."""
        return self.df_clin, self.df_path

    def report_missing(self, df: pd.DataFrame, name: str) -> pd.DataFrame:
        """Generate missing data report."""
        return self.generate_missing_report(df, name)
