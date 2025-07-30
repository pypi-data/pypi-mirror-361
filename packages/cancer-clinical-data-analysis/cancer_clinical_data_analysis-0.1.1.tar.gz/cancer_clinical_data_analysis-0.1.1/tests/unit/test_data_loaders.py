"""
Unit tests for data loading functionality.
"""

import pandas as pd
import pytest
import requests

from cancer_analysis.data.loaders import DataLoader


class TestDataLoader:
    """Test suite for DataLoader class."""

    def test_init_with_default_study_id(self):
        """Test DataLoader initialization with default study ID."""
        loader = DataLoader()
        assert loader.study_id == "luad_tcga_gdc"
        assert "cbioportal.org" in loader.base_url

    def test_init_with_custom_study_id(self):
        """Test DataLoader initialization with custom study ID."""
        custom_study = "custom_study_id"
        loader = DataLoader(study_id=custom_study)
        assert loader.study_id == custom_study

    def test_load_patient_data_success(
        self, requests_mock, sample_cbioportal_patient_response
    ):
        """Test successful patient data loading."""
        loader = DataLoader(study_id="test_study")

        # Mock the exact URL being requested
        requests_mock.get(
            "https://www.cbioportal.org/api/studies/test_study/clinical-data?clinicalDataType=PATIENT",
            json=sample_cbioportal_patient_response,
        )

        result = loader.load_patient_data()

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert "patientId" in result.columns
        assert "clinicalAttributeId" in result.columns
        assert "value" in result.columns

    def test_load_sample_data_success(
        self, requests_mock, sample_cbioportal_sample_response
    ):
        """Test successful sample data loading."""
        loader = DataLoader(study_id="test_study")

        # Mock the exact URL being requested
        requests_mock.get(
            "https://www.cbioportal.org/api/studies/test_study/clinical-data?clinicalDataType=SAMPLE",
            json=sample_cbioportal_sample_response,
        )

        result = loader.load_sample_data()

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert "sampleId" in result.columns

    def test_load_patient_data_api_error(self, requests_mock):
        """Test handling of API errors during patient data loading."""
        loader = DataLoader(study_id="test_study")

        # Mock the exact URL with error status code
        requests_mock.get(
            "https://www.cbioportal.org/api/studies/test_study/clinical-data?clinicalDataType=PATIENT",
            status_code=500,
        )

        with pytest.raises(requests.RequestException):
            loader.load_patient_data()

    def test_load_all_data(
        self,
        requests_mock,
        sample_cbioportal_patient_response,
        sample_cbioportal_sample_response,
    ):
        """Test loading both patient and sample data."""
        loader = DataLoader(study_id="test_study")

        # Mock both endpoints with the exact URLs
        requests_mock.get(
            "https://www.cbioportal.org/api/studies/test_study/clinical-data?clinicalDataType=PATIENT",
            json=sample_cbioportal_patient_response,
        )
        requests_mock.get(
            "https://www.cbioportal.org/api/studies/test_study/clinical-data?clinicalDataType=SAMPLE",
            json=sample_cbioportal_sample_response,
        )

        patient_data, sample_data = loader.load_all_data()

        assert isinstance(patient_data, pd.DataFrame)
        assert isinstance(sample_data, pd.DataFrame)
        assert not patient_data.empty
        assert not sample_data.empty
