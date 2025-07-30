#!/usr/bin/env python3
"""
Unit tests for the transcription logging functionality.
"""

import sys
import os
import tempfile
import unittest
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from easytranscribe.transcription_logger import log_transcription


class TestTranscriptionLogging(unittest.TestCase):
    """Test cases for transcription logging functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_model = "test_model"
        self.test_text = "This is a test transcription."
        self.test_duration = 5.0
        self.test_processing_time = 1.5

    def test_basic_logging(self):
        """Test basic transcription logging functionality."""
        try:
            log_transcription(
                model_name=self.test_model,
                transcribed_text=self.test_text,
                audio_duration=self.test_duration,
                processing_time=self.test_processing_time,
            )
            print("✅ Basic logging test passed")
        except Exception as e:
            self.fail(f"Basic logging test failed: {e}")

    def test_file_logging(self):
        """Test file transcription logging."""
        try:
            log_transcription(
                model_name=self.test_model,
                transcribed_text=self.test_text,
                audio_file="/path/to/test/file.wav",
                processing_time=self.test_processing_time,
            )
            print("✅ File logging test passed")
        except Exception as e:
            self.fail(f"File logging test failed: {e}")

    def test_minimal_logging(self):
        """Test logging with minimal parameters."""
        try:
            log_transcription(
                model_name=self.test_model,
                transcribed_text=self.test_text,
            )
            print("✅ Minimal logging test passed")
        except Exception as e:
            self.fail(f"Minimal logging test failed: {e}")

    def test_log_file_creation(self):
        """Test that log files are created correctly."""
        # Log something
        log_transcription(
            model_name=self.test_model,
            transcribed_text=self.test_text,
        )
        
        # Check if log file exists
        current_date = datetime.now().strftime("%Y-%m-%d")
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        log_file = os.path.join(log_dir, f"transcription_{current_date}.log")
        
        self.assertTrue(os.path.exists(log_file), "Log file was not created")
        print("✅ Log file creation test passed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
