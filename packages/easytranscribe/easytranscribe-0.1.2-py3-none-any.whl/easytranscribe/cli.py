#!/usr/bin/env python3
"""
Command-line interface for easytranscribe.
"""

import argparse
import sys
from pathlib import Path

from easytranscribe import (
    capture_and_transcribe,
    transcribe_audio_file,
    view_logs,
    get_available_log_dates,
    __version__,
)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Easy speech-to-text transcription using Whisper",
        prog="easytranscribe",
    )

    parser.add_argument(
        "--version", action="version", version=f"easytranscribe {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Live transcription command
    live_parser = subparsers.add_parser("live", help="Transcribe from microphone")
    live_parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large", "turbo"],
        help="Whisper model to use (default: base)",
    )
    live_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output (shows recording status and processing info)",
    )

    # File transcription command
    file_parser = subparsers.add_parser("file", help="Transcribe from audio file")
    file_parser.add_argument("filepath", help="Path to audio file")
    file_parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large", "turbo"],
        help="Whisper model to use (default: base)",
    )
    file_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output (shows processing info)",
    )

    # Logs command
    logs_parser = subparsers.add_parser("logs", help="View transcription logs")
    logs_parser.add_argument("--date", help="Date in YYYY-MM-DD format or 'today'")
    logs_parser.add_argument("--tail", type=int, help="Show last N entries")
    logs_parser.add_argument("--stats", action="store_true", help="Show statistics")
    logs_parser.add_argument(
        "--list-dates", action="store_true", help="List available log dates"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "live":
            if args.verbose:
                print(f"🎤 Starting live transcription with {args.model} model...")
            text = capture_and_transcribe(model_name=args.model, verbose=args.verbose)
            print(f"📝 Transcribed: {text}")

        elif args.command == "file":
            if not Path(args.filepath).exists():
                print(f"❌ Error: File not found: {args.filepath}")
                return 1

            if args.verbose:
                print(f"📁 Transcribing file: {args.filepath}")
            text = transcribe_audio_file(
                args.filepath, model_name=args.model, verbose=args.verbose
            )
            print(f"📝 Transcribed: {text}")

        elif args.command == "logs":
            if args.list_dates:
                dates = get_available_log_dates()
                if dates:
                    print("📅 Available log dates:")
                    for date in dates:
                        print(f"  - {date}")
                else:
                    print("📅 No log files found")
                return 0

            logs = view_logs(date=args.date, tail=args.tail, stats=args.stats)

            if "error" in logs:
                print(f"❌ {logs['error']}")
                return 1

            print(f"📋 Found {logs['total_count']} log entries")

            if args.stats and "statistics" in logs:
                stats = logs["statistics"]
                print("\n📊 Statistics:")
                print(f"  - Total audio duration: {stats['total_audio_duration']:.1f}s")
                print(
                    f"  - Total processing time: {stats['total_processing_time']:.1f}s"
                )
                print(
                    f"  - Average processing time: {stats['average_processing_time']:.1f}s"
                )
                print(f"  - Model usage: {stats['model_usage']}")

            if not args.stats:
                print("\nRecent entries:")
                for i, entry in enumerate(logs["entries"][-5:], 1):  # Show last 5
                    print(f"\n--- Entry {i} ---")
                    print(entry)

    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
