#!/usr/bin/env python3
"""
Integration test for the complete transcription and logging system.
This test simulates the transcription process without requiring actual audio input.
"""

import sys
import os
import time

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from easytranscribe.transcription_logger import log_transcription


def test_integration():
    """Test the complete integration of logging with transcription."""
    print("🔧 Running integration test...")

    # Test 1: Basic logging
    print("\n1. Testing basic transcription logging...")

    test_cases = [
        {
            "model": "turbo",
            "text": "Hello world, this is a test transcription.",
            "duration": 3.5,
            "processing": 1.2,
        },
        {
            "model": "base",
            "text": "Another test with a different model configuration.",
            "duration": 4.1,
            "processing": 2.1,
        },
        {"model": "turbo", "text": "Short test.", "duration": 1.8, "processing": 0.8},
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"   Test case {i}: {test_case['model']} model")
        try:
            log_transcription(
                model_name=str(test_case["model"]),
                transcribed_text=str(test_case["text"]),
                audio_duration=float(test_case["duration"]),
                processing_time=float(test_case["processing"]),
            )
            print(f"   ✅ Test case {i} logged successfully")
        except Exception as e:
            print(f"   ❌ Test case {i} failed: {e}")
            return False

    # Test 2: File transcription logging
    print("\n2. Testing file transcription logging...")
    try:
        log_transcription(
            model_name="base",
            transcribed_text="This is a test from an audio file.",
            audio_file="/path/to/test/audio.wav",
            processing_time=1.5,
        )
        print("   ✅ File transcription logged successfully")
    except Exception as e:
        print(f"   ❌ File transcription logging failed: {e}")
        return False

    # Test 3: Test log viewer functionality
    print("\n3. Testing log viewer integration...")
    try:
        from easytranscribe.view_logs import view_logs, get_available_log_dates

        print("   ✅ Log viewer module imported successfully")

        # Test getting available dates
        dates = get_available_log_dates()
        print(f"   ✅ Found {len(dates)} log dates")

        # Test viewing logs
        logs = view_logs(date="today", stats=True)
        if "entries" in logs:
            print(f"   ✅ Retrieved {logs['total_count']} log entries")
        else:
            print(f"   ⚠️ No log entries found: {logs}")

    except Exception as e:
        print(f"   ❌ Log viewer test failed: {e}")
        return False

    print("\n✅ All integration tests passed!")
    return True


if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)
