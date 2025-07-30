"""
Unit tests for data validation functionality.
"""

import pandas as pd
import pytest

from cancer_analysis.data.validators import DataValidator, ValidationResult


class TestDataValidator:
    """Test suite for DataValidator class."""

    def test_init(self):
        """Test DataValidator initialization."""
        validator = DataValidator()
        assert validator.required_patient_columns == ["patient_id"]
        assert validator.age_range == (0, 150)
        assert validator.survival_time_range == (0, 500)

    def test_validate_patient_data_valid(self, sample_patient_data):
        """Test validation of valid patient data."""
        validator = DataValidator()
        result = validator.validate_patient_data(sample_patient_data)

        assert isinstance(result, ValidationResult)
        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.passed_checks) > 0

    def test_validate_patient_data_missing_required_columns(self):
        """Test validation with missing required columns."""
        validator = DataValidator()
        invalid_data = pd.DataFrame(
            {"age": [45, 50, 55], "gender": ["Male", "Female", "Male"]}
        )

        result = validator.validate_patient_data(invalid_data)

        assert not result.is_valid
        assert any("Missing required columns" in error for error in result.errors)

    def test_validate_patient_data_empty_dataframe(self):
        """Test validation of empty DataFrame."""
        validator = DataValidator()
        empty_df = pd.DataFrame()

        result = validator.validate_patient_data(empty_df)

        assert not result.is_valid
        assert any("DataFrame is empty" in error for error in result.errors)

    def test_validate_patient_data_null_patient_ids(self):
        """Test validation with null patient IDs."""
        validator = DataValidator()
        data_with_nulls = pd.DataFrame(
            {"patient_id": ["P001", None, "P003"], "age_at_diagnosis": [45, 50, 55]}
        )

        result = validator.validate_patient_data(data_with_nulls)

        assert not result.is_valid
        assert any("null patient IDs" in error for error in result.errors)

    def test_validate_patient_data_duplicate_patient_ids(self):
        """Test validation with duplicate patient IDs."""
        validator = DataValidator()
        data_with_duplicates = pd.DataFrame(
            {"patient_id": ["P001", "P001", "P003"], "age_at_diagnosis": [45, 50, 55]}
        )

        result = validator.validate_patient_data(data_with_duplicates)

        assert result.is_valid  # Duplicates are warnings, not errors
        assert any("duplicate patient IDs" in warning for warning in result.warnings)

    @pytest.mark.parametrize(
        "age,expected",
        [
            (25, True),
            (0, False),
            (-5, False),
            (150, False),
            (151, False),
            ("invalid", False),
            (None, False),
        ],
    )
    def test_is_valid_age(self, age, expected):
        """Test age validation with various inputs."""
        validator = DataValidator()
        assert validator.is_valid_age(age) == expected

    def test_validate_sample_data_valid(self, sample_pathology_data):
        """Test validation of valid sample data."""
        validator = DataValidator()
        result = validator.validate_sample_data(sample_pathology_data)

        assert isinstance(result, ValidationResult)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_sample_data_missing_sample_id(self):
        """Test validation with missing sample_id column."""
        validator = DataValidator()
        invalid_data = pd.DataFrame(
            {
                "tumor_grade": ["Grade 1", "Grade 2"],
                "tumor_stage": ["Stage I", "Stage II"],
            }
        )

        result = validator.validate_sample_data(invalid_data)

        assert not result.is_valid
        assert any("Missing required columns" in error for error in result.errors)
