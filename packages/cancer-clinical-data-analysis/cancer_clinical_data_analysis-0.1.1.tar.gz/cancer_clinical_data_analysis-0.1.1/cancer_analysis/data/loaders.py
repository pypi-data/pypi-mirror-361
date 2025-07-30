"""
Data loading utilities for cancer clinical data analysis.

This module provides classes for loading and fetching clinical data
from various sources including cBioPortal API.
"""

import logging
from typing import Tuple

import pandas as pd
import requests

logger = logging.getLogger(__name__)


class DataLoader:
    """Data loader for cancer clinical data from cBioPortal."""

    def __init__(self, study_id: str = "luad_tcga_gdc"):
        """
        Initialize the data loader with a cBioPortal study ID.

        Args:
            study_id: cBioPortal study identifier (e.g., 'luad_tcga_gdc')
        """
        self.study_id = study_id
        self.base_url = "https://www.cbioportal.org/api/studies"
        self.df_pat = None
        self.df_samp = None

    def load_patient_data(self) -> pd.DataFrame:
        """
        Fetch patient-level clinical data from cBioPortal API.

        Returns:
            DataFrame containing patient clinical data

        Raises:
            requests.RequestException: If API request fails
        """
        url_pat = (
            f"{self.base_url}/{self.study_id}/clinical-data?clinicalDataType=PATIENT"
        )

        try:
            resp_pat = requests.get(url_pat, timeout=10000)
            resp_pat.raise_for_status()
            self.df_pat = pd.json_normalize(resp_pat.json())
            logger.info(f"Loaded patient records: {self.df_pat.shape}")
            return self.df_pat
        except requests.RequestException as e:
            logger.error(f"Failed to load patient data: {e}")
            raise

    def load_sample_data(self) -> pd.DataFrame:
        """
        Fetch sample-level clinical data from cBioPortal API.

        Returns:
            DataFrame containing sample clinical data

        Raises:
            requests.RequestException: If API request fails
        """
        url_samp = (
            f"{self.base_url}/{self.study_id}/clinical-data?clinicalDataType=SAMPLE"
        )

        try:
            resp_samp = requests.get(url_samp, timeout=10000)
            resp_samp.raise_for_status()
            self.df_samp = pd.json_normalize(resp_samp.json())
            logger.info(f"Loaded sample records: {self.df_samp.shape}")
            return self.df_samp
        except requests.RequestException as e:
            logger.error(f"Failed to load sample data: {e}")
            raise

    def load_all_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load both patient and sample data.

        Returns:
            Tuple of (patient_data, sample_data) DataFrames
        """
        patient_data = self.load_patient_data()
        sample_data = self.load_sample_data()
        return patient_data, sample_data

    def get_available_studies(self) -> pd.DataFrame:
        """
        Get list of available studies from cBioPortal.

        Returns:
            DataFrame containing available studies
        """
        url = "https://www.cbioportal.org/api/studies"
        try:
            resp = requests.get(url, timeout=10000)
            resp.raise_for_status()
            studies = pd.json_normalize(resp.json())
            return studies[["studyId", "name", "description", "cancerTypeId"]]
        except requests.RequestException as e:
            logger.error(f"Failed to get available studies: {e}")
            raise


if __name__ == "__main__":
    # Example usage
    loader = DataLoader(study_id="luad_tcga_gdc")
    try:
        patient_data, sample_data = loader.load_all_data()
        print("Patient Data:", patient_data.head())
        print("Sample Data:", sample_data.head())
    except Exception as e:
        logger.error(f"Error loading data: {e}")
