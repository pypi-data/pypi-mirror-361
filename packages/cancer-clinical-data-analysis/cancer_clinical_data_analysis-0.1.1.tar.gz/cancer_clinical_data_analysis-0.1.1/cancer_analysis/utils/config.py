"""
Configuration management for cancer clinical data analysis.

This module provides configuration classes and utilities for managing
application settings, data paths, and model parameters.
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class DataConfig:
    """Configuration for data handling."""

    raw_data_dir: Path = field(default_factory=lambda: Path("data/raw"))
    processed_data_dir: Path = field(default_factory=lambda: Path("data/processed"))
    external_data_dir: Path = field(default_factory=lambda: Path("data/external"))
    results_dir: Path = field(default_factory=lambda: Path("results"))

    def __post_init__(self):
        """Create directories if they don't exist."""
        for directory in [
            self.raw_data_dir,
            self.processed_data_dir,
            self.external_data_dir,
            self.results_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


@dataclass
class ModelConfig:
    """Configuration for machine learning models."""

    test_size: float = 0.2
    random_state: int = 42
    max_iter: int = 1000
    n_jobs: int = -1
    cross_validation_folds: int = 5


@dataclass
class APIConfig:
    """Configuration for external APIs."""

    cbioportal_base_url: str = "https://www.cbioportal.org/api/studies"
    default_study_id: str = "luad_tcga_gdc"
    request_timeout: int = 30


@dataclass
class LoggingConfig:
    """Configuration for logging."""

    level: str = "INFO"
    format: str = "[%(levelname)s] %(asctime)s - %(name)s - %(message)s"
    file_path: Optional[Path] = None


class Config:
    """Main configuration class for the application."""

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration.

        Args:
            config_file: Optional path to configuration file
        """
        self.data = DataConfig()
        self.model = ModelConfig()
        self.api = APIConfig()
        self.logging = LoggingConfig()

        if config_file and config_file.exists():
            self.load_from_file(config_file)

        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.logging.level.upper()),
            format=self.logging.format,
            filename=self.logging.file_path,
        )

    def load_from_file(self, config_file: Path):
        """
        Load configuration from file.

        Args:
            config_file: Path to configuration file
        """
        # Implementation would depend on chosen format (YAML, JSON, TOML)
        logger.info(f"Loading configuration from {config_file}")
        # For now, this is a placeholder
        pass

    def save_to_file(self, config_file: Path):
        """
        Save configuration to file.

        Args:
            config_file: Path to save configuration
        """
        logger.info(f"Saving configuration to {config_file}")
        # Implementation would depend on chosen format
        pass

    def get_data_path(self) -> Path:
        """Get the data directory path."""
        return self.data.raw_data_dir

    def get_results_path(self) -> Path:
        """Get the results directory path."""
        return self.data.results_dir

    def update_from_env(self):
        """Update configuration from environment variables."""
        # Data paths
        if os.getenv("DATA_RAW_DIR"):
            self.data.raw_data_dir = Path(os.getenv("DATA_RAW_DIR"))
        if os.getenv("DATA_PROCESSED_DIR"):
            self.data.processed_data_dir = Path(os.getenv("DATA_PROCESSED_DIR"))
        if os.getenv("RESULTS_DIR"):
            self.data.results_dir = Path(os.getenv("RESULTS_DIR"))

        # Model parameters
        if os.getenv("MODEL_RANDOM_STATE"):
            self.model.random_state = int(os.getenv("MODEL_RANDOM_STATE"))
        if os.getenv("MODEL_TEST_SIZE"):
            self.model.test_size = float(os.getenv("MODEL_TEST_SIZE"))

        # API configuration
        if os.getenv("CBIOPORTAL_BASE_URL"):
            self.api.cbioportal_base_url = os.getenv("CBIOPORTAL_BASE_URL")
        if os.getenv("DEFAULT_STUDY_ID"):
            self.api.default_study_id = os.getenv("DEFAULT_STUDY_ID")

        # Logging
        if os.getenv("LOG_LEVEL"):
            self.logging.level = os.getenv("LOG_LEVEL")


# Global configuration instance
_config = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
        _config.update_from_env()
    return _config


def get_data_path() -> Path:
    """Get the data directory path."""
    return get_config().get_data_path()


def get_results_path() -> Path:
    """Get the results directory path."""
    return get_config().get_results_path()
