#!/usr/bin/env python3
"""
Utility module to view and analyze transcription logs.
"""

import os
import glob
from datetime import datetime
from typing import Optional, List, Dict, Any


def view_logs(date: Optional[str] = None, tail: Optional[int] = None, stats: bool = False) -> Dict[str, Any]:
    """
    View transcription logs with various options.

    Args:
        date: Date in YYYY-MM-DD format, or 'today' for today's logs
        tail: Show last N entries
        stats: Show statistics summary

    Returns:
        Dictionary containing log data and statistics
    """
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    
    if not os.path.exists(logs_dir):
        return {"error": "No logs directory found"}

    # Determine which log files to read
    if date == "today" or date is None:
        target_date = datetime.now().strftime("%Y-%m-%d")
        log_pattern = f"transcription_{target_date}.log"
    elif date:
        log_pattern = f"transcription_{date}.log"
    else:
        log_pattern = "transcription_*.log"

    log_files = glob.glob(os.path.join(logs_dir, log_pattern))
    
    if not log_files:
        return {"error": f"No log files found for pattern: {log_pattern}"}

    # Read and parse log entries
    entries = []
    for log_file in sorted(log_files):
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Parse log entries (assuming our simple format)
            blocks = content.split('-' * 40)
            for block in blocks:
                if block.strip():
                    entries.append(block.strip())

    # Apply tail filter
    if tail and tail > 0:
        entries = entries[-tail:]

    result: Dict[str, Any] = {"entries": entries, "total_count": len(entries)}

    # Calculate statistics if requested
    if stats:
        model_counts: Dict[str, int] = {}
        total_duration = 0.0
        total_processing = 0.0
        
        for entry in entries:
            lines = entry.split('\n')
            for line in lines:
                if line.startswith('Model:'):
                    model = line.split(':', 1)[1].strip()
                    model_counts[model] = model_counts.get(model, 0) + 1
                elif line.startswith('Audio Duration:'):
                    try:
                        duration = float(line.split(':')[1].strip().replace('s', ''))
                        total_duration += duration
                    except (ValueError, IndexError):
                        pass
                elif line.startswith('Processing Time:'):
                    try:
                        processing = float(line.split(':')[1].strip().replace('s', ''))
                        total_processing += processing
                    except (ValueError, IndexError):
                        pass

        stats_dict: Dict[str, Any] = {
            "model_usage": model_counts,
            "total_audio_duration": total_duration,
            "total_processing_time": total_processing,
            "average_processing_time": total_processing / len(entries) if entries else 0.0
        }
        result["statistics"] = stats_dict

    return result


def get_available_log_dates() -> List[str]:
    """
    Get list of available log dates.

    Returns:
        List of date strings in YYYY-MM-DD format
    """
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    
    if not os.path.exists(logs_dir):
        return []

    log_files = glob.glob(os.path.join(logs_dir, "transcription_*.log"))
    dates = []
    
    for log_file in log_files:
        filename = os.path.basename(log_file)
        # Extract date from filename: transcription_YYYY-MM-DD.log
        if filename.startswith("transcription_") and filename.endswith(".log"):
            date_part = filename[14:-4]  # Remove prefix and suffix
            if len(date_part) == 10:  # YYYY-MM-DD format
                dates.append(date_part)
    
    return sorted(dates)
