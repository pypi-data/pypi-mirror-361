"""
Pytest configuration and fixtures for cancer clinical data analysis tests.
"""

import shutil
import tempfile
from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_patient_data():
    """Provide sample patient clinical data for testing."""
    return pd.DataFrame(
        {
            "patient_id": ["P001", "P002", "P003", "P004", "P005"],
            "age_at_diagnosis": [45, 62, 38, 71, 55],
            "gender": ["Female", "Male", "Female", "Male", "Female"],
            "race": ["White", "Black", "Asian", "White", "Hispanic"],
            "ethnicity": [
                "Non-Hispanic",
                "Non-Hispanic",
                "Non-Hispanic",
                "Non-Hispanic",
                "Hispanic",
            ],
            "os_months": [24.5, 18.2, 36.1, 12.8, 42.3],
            "os_event": [1, 1, 0, 1, 0],
            "os_status": ["DECEASED", "DECEASED", "LIVING", "DECEASED", "LIVING"],
            "pfs_months": [22.1, 16.5, 35.2, 11.9, 40.8],
            "pfs_event": [1, 1, 0, 1, 0],
            "pfs_status": [
                "PROGRESS",
                "PROGRESS",
                "NO EVIDENCE",
                "PROGRESS",
                "NO EVIDENCE",
            ],
        }
    )


@pytest.fixture
def sample_pathology_data():
    """Provide sample pathology data for testing."""
    return pd.DataFrame(
        {
            "sample_id": ["S001", "S002", "S003", "S004", "S005"],
            "patient_id": ["P001", "P002", "P003", "P004", "P005"],
            "tumor_grade": ["Grade 2", "Grade 3", "Grade 1", "Grade 3", "Grade 2"],
            "tumor_stage": ["Stage II", "Stage III", "Stage I", "Stage IV", "Stage II"],
            "er_status": ["Positive", "Negative", "Positive", "Negative", "Positive"],
            "pr_status": ["Positive", "Negative", "Positive", "Negative", "Positive"],
            "her2_status": ["Negative", "Positive", "Negative", "Positive", "Negative"],
            "cancer_type": ["Breast", "Lung", "Breast", "Lung", "Breast"],
        }
    )


@pytest.fixture
def sample_cbioportal_patient_response():
    """Mock cBioPortal API response for patient data."""
    return [
        {"patientId": "P001", "clinicalAttributeId": "AGE", "value": "45"},
        {"patientId": "P001", "clinicalAttributeId": "SEX", "value": "Female"},
        {"patientId": "P001", "clinicalAttributeId": "OS_MONTHS", "value": "24.5"},
        {"patientId": "P001", "clinicalAttributeId": "OS_STATUS", "value": "DECEASED"},
    ]


@pytest.fixture
def sample_cbioportal_sample_response():
    """Mock cBioPortal API response for sample data."""
    return [
        {"sampleId": "S001", "clinicalAttributeId": "TUMOR_GRADE", "value": "Grade 2"},
        {"sampleId": "S001", "clinicalAttributeId": "TUMOR_STAGE", "value": "Stage II"},
        {"sampleId": "S001", "clinicalAttributeId": "ER_STATUS", "value": "Positive"},
    ]


@pytest.fixture
def invalid_patient_data():
    """Provide invalid patient data for testing validation."""
    return pd.DataFrame(
        {
            "patient_id": ["P001", "P002", None, "P004"],
            "age_at_diagnosis": [45, -5, 200, "invalid"],
            "os_months": [24.5, -10, None, "bad_data"],
            "os_event": [1, 2, 0, "invalid"],
        }
    )


@pytest.fixture
def mock_config():
    """Provide mock configuration for testing."""
    from cancer_analysis.utils.config import Config

    config = Config()
    config.api.default_study_id = "test_study"
    config.model.random_state = 42
    config.data.raw_data_dir = Path("test_data/raw")
    return config
