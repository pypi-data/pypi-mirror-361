# Advanced Usage

This section covers advanced techniques and patterns for getting the most out of EasyTranscribe in production environments and complex workflows.

## Custom Audio Processing

### Audio Preprocessing Pipeline

```python
#!/usr/bin/env python3
"""Advanced audio preprocessing for better transcription quality."""

import numpy as np
import soundfile as sf
from scipy import signal
from pathlib import Path
from easytranscribe import transcribe_audio_file

class AudioPreprocessor:
    def __init__(self, target_sample_rate=16000):
        self.target_sample_rate = target_sample_rate

    def preprocess_audio(self, input_file, output_file=None):
        """Preprocess audio for optimal Whisper performance."""
        # Load audio
        audio, sample_rate = sf.read(input_file)

        print(f"Original: {sample_rate} Hz, {len(audio)} samples")

        # Convert to mono if stereo
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)
            print("Converted to mono")

        # Resample to target rate
        if sample_rate != self.target_sample_rate:
            num_samples = int(len(audio) * self.target_sample_rate / sample_rate)
            audio = signal.resample(audio, num_samples)
            sample_rate = self.target_sample_rate
            print(f"Resampled to {self.target_sample_rate} Hz")

        # Normalize audio
        audio = self._normalize_audio(audio)

        # Apply noise reduction
        audio = self._reduce_noise(audio, sample_rate)

        # Apply bandpass filter (300Hz - 3400Hz for speech)
        audio = self._bandpass_filter(audio, sample_rate)

        # Save preprocessed audio
        if output_file:
            sf.write(output_file, audio, sample_rate)
            print(f"Saved preprocessed audio: {output_file}")

        return audio, sample_rate

    def _normalize_audio(self, audio):
        """Normalize audio amplitude."""
        max_amplitude = np.max(np.abs(audio))
        if max_amplitude > 0:
            return audio / max_amplitude * 0.9  # Leave some headroom
        return audio

    def _reduce_noise(self, audio, sample_rate):
        """Simple noise reduction using spectral gating."""
        # This is a simplified noise reduction
        # For production, consider using libraries like noisereduce

        # Calculate short-time energy
        frame_length = int(0.025 * sample_rate)  # 25ms frames
        hop_length = int(0.010 * sample_rate)    # 10ms hop

        # Simple energy-based noise gate
        energy_threshold = 0.01 * np.max(audio**2)

        processed_audio = audio.copy()
        for i in range(0, len(audio) - frame_length, hop_length):
            frame = audio[i:i + frame_length]
            energy = np.mean(frame**2)

            if energy < energy_threshold:
                # Reduce low-energy frames (likely noise)
                processed_audio[i:i + frame_length] *= 0.1

        return processed_audio

    def _bandpass_filter(self, audio, sample_rate):
        """Apply bandpass filter for speech frequencies."""
        # Design bandpass filter for speech (300Hz - 3400Hz)
        low_freq = 300
        high_freq = 3400

        nyquist = sample_rate / 2
        low = low_freq / nyquist
        high = high_freq / nyquist

        b, a = signal.butter(4, [low, high], btype='band')
        filtered_audio = signal.filtfilt(b, a, audio)

        return filtered_audio

def enhanced_transcription(audio_file):
    """Transcribe with audio preprocessing."""
    preprocessor = AudioPreprocessor()

    # Preprocess audio
    temp_file = "temp_processed.wav"
    preprocessor.preprocess_audio(audio_file, temp_file)

    # Transcribe preprocessed audio
    text = transcribe_audio_file(temp_file, model_name="medium", verbose=True)

    # Clean up
    Path(temp_file).unlink()

    return text

# Usage
if __name__ == "__main__":
    text = enhanced_transcription("noisy_audio.wav")
    print(f"Enhanced transcription: {text}")
```

## Parallel Processing and Performance Optimization

### High-Performance Batch Processor

```python
#!/usr/bin/env python3
"""High-performance batch transcription with parallel processing."""

import asyncio
import concurrent.futures
import multiprocessing as mp
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
import time
import json

from easytranscribe import transcribe_audio_file

@dataclass
class TranscriptionJob:
    input_file: Path
    output_file: Path
    model_name: str = "base"
    metadata: dict = None

@dataclass
class TranscriptionResult:
    job: TranscriptionJob
    success: bool
    text: Optional[str] = None
    error: Optional[str] = None
    processing_time: float = 0.0

class HighPerformanceBatchProcessor:
    def __init__(self, max_workers=None, chunk_size=4):
        self.max_workers = max_workers or mp.cpu_count()
        self.chunk_size = chunk_size

    def process_jobs(self, jobs: List[TranscriptionJob]) -> List[TranscriptionResult]:
        """Process transcription jobs in parallel."""
        print(f"Processing {len(jobs)} jobs with {self.max_workers} workers")

        start_time = time.time()
        results = []

        # Process in chunks to manage memory
        for i in range(0, len(jobs), self.chunk_size):
            chunk = jobs[i:i + self.chunk_size]
            chunk_results = self._process_chunk(chunk)
            results.extend(chunk_results)

            print(f"Completed chunk {i//self.chunk_size + 1}/{(len(jobs) + self.chunk_size - 1)//self.chunk_size}")

        total_time = time.time() - start_time
        successful = sum(1 for r in results if r.success)

        print(f"Batch processing complete:")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Success rate: {successful}/{len(jobs)} ({successful/len(jobs)*100:.1f}%)")
        print(f"  Average time per file: {total_time/len(jobs):.2f}s")

        return results

    def _process_chunk(self, jobs: List[TranscriptionJob]) -> List[TranscriptionResult]:
        """Process a chunk of jobs in parallel."""
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self._process_single_job, job) for job in jobs]
            return [future.result() for future in concurrent.futures.as_completed(futures)]

    @staticmethod
    def _process_single_job(job: TranscriptionJob) -> TranscriptionResult:
        """Process a single transcription job."""
        start_time = time.time()

        try:
            # Transcribe file
            text = transcribe_audio_file(
                str(job.input_file),
                model_name=job.model_name,
                verbose=False
            )

            # Save result
            job.output_file.parent.mkdir(parents=True, exist_ok=True)

            result_data = {
                "input_file": str(job.input_file),
                "transcription": text,
                "model": job.model_name,
                "processing_time": time.time() - start_time,
                "metadata": job.metadata or {}
            }

            with open(job.output_file, 'w') as f:
                json.dump(result_data, f, indent=2)

            return TranscriptionResult(
                job=job,
                success=True,
                text=text,
                processing_time=time.time() - start_time
            )

        except Exception as e:
            return TranscriptionResult(
                job=job,
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )

def create_batch_jobs(input_dir, output_dir, model_name="base"):
    """Create batch jobs from directory of audio files."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    jobs = []
    for audio_file in input_path.glob("*.{wav,mp3,m4a,flac}"):
        output_file = output_path / f"{audio_file.stem}_transcript.json"

        job = TranscriptionJob(
            input_file=audio_file,
            output_file=output_file,
            model_name=model_name,
            metadata={"source_dir": str(input_dir)}
        )
        jobs.append(job)

    return jobs

# Usage example
if __name__ == "__main__":
    # Create jobs
    jobs = create_batch_jobs("audio_files/", "transcripts/", model_name="base")

    # Process with high performance
    processor = HighPerformanceBatchProcessor(max_workers=4, chunk_size=2)
    results = processor.process_jobs(jobs)

    # Print summary
    print("\nProcessing Summary:")
    for result in results:
        status = "✅" if result.success else "❌"
        print(f"{status} {result.job.input_file.name} ({result.processing_time:.2f}s)")
```

## Advanced Monitoring and Analytics

### Transcription Analytics Dashboard

```python
#!/usr/bin/env python3
"""Advanced analytics for transcription performance and usage."""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import pandas as pd

@dataclass
class TranscriptionMetrics:
    timestamp: datetime
    model_name: str
    audio_duration: float
    processing_time: float
    word_count: int
    source_type: str  # 'live' or 'file'
    file_path: str = None

class TranscriptionAnalytics:
    def __init__(self, db_path="transcription_analytics.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for analytics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transcriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                model_name TEXT NOT NULL,
                audio_duration REAL,
                processing_time REAL NOT NULL,
                word_count INTEGER NOT NULL,
                source_type TEXT NOT NULL,
                file_path TEXT,
                text_sample TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def log_transcription(self, metrics: TranscriptionMetrics, text_sample: str = ""):
        """Log transcription metrics to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO transcriptions
            (timestamp, model_name, audio_duration, processing_time,
             word_count, source_type, file_path, text_sample)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metrics.timestamp.isoformat(),
            metrics.model_name,
            metrics.audio_duration,
            metrics.processing_time,
            metrics.word_count,
            metrics.source_type,
            metrics.file_path,
            text_sample[:200]  # First 200 chars as sample
        ))

        conn.commit()
        conn.close()

    def get_performance_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get performance statistics for the last N days."""
        conn = sqlite3.connect(self.db_path)

        # Get data from last N days
        since_date = (datetime.now() - timedelta(days=days)).isoformat()

        df = pd.read_sql_query('''
            SELECT * FROM transcriptions
            WHERE timestamp >= ?
            ORDER BY timestamp
        ''', conn, params=[since_date])

        conn.close()

        if df.empty:
            return {"error": "No data found for the specified period"}

        # Calculate statistics
        stats = {
            "total_transcriptions": len(df),
            "unique_days": df['timestamp'].str[:10].nunique(),
            "models_used": df['model_name'].value_counts().to_dict(),
            "source_breakdown": df['source_type'].value_counts().to_dict(),
            "performance_metrics": {
                "avg_processing_time": df['processing_time'].mean(),
                "median_processing_time": df['processing_time'].median(),
                "avg_words_per_minute": (df['word_count'] / (df['processing_time'] / 60)).mean(),
                "total_words_transcribed": df['word_count'].sum(),
                "total_processing_time": df['processing_time'].sum()
            },
            "daily_usage": df.groupby(df['timestamp'].str[:10]).size().to_dict()
        }

        return stats

    def generate_performance_report(self, output_dir="analytics_reports"):
        """Generate comprehensive performance report with visualizations."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Get data
        stats = self.get_performance_stats(days=30)

        if "error" in stats:
            print(f"Error generating report: {stats['error']}")
            return

        # Create visualizations
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('EasyTranscribe Performance Analytics (Last 30 Days)', fontsize=16)

        # 1. Model usage pie chart
        model_data = stats['models_used']
        axes[0, 0].pie(model_data.values(), labels=model_data.keys(), autopct='%1.1f%%')
        axes[0, 0].set_title('Model Usage Distribution')

        # 2. Daily usage line chart
        daily_data = stats['daily_usage']
        dates = list(daily_data.keys())
        counts = list(daily_data.values())
        axes[0, 1].plot(dates, counts, marker='o')
        axes[0, 1].set_title('Daily Transcription Count')
        axes[0, 1].tick_params(axis='x', rotation=45)

        # 3. Source type bar chart
        source_data = stats['source_breakdown']
        axes[1, 0].bar(source_data.keys(), source_data.values())
        axes[1, 0].set_title('Source Type Distribution')

        # 4. Performance metrics text
        perf_metrics = stats['performance_metrics']
        metrics_text = f"""
        Performance Metrics:

        Avg Processing Time: {perf_metrics['avg_processing_time']:.2f}s
        Median Processing Time: {perf_metrics['median_processing_time']:.2f}s
        Avg Words/Minute: {perf_metrics['avg_words_per_minute']:.1f}
        Total Words: {perf_metrics['total_words_transcribed']:,}
        Total Processing Time: {perf_metrics['total_processing_time']:.1f}s
        """

        axes[1, 1].text(0.1, 0.5, metrics_text, fontsize=10, verticalalignment='center')
        axes[1, 1].set_xlim(0, 1)
        axes[1, 1].set_ylim(0, 1)
        axes[1, 1].axis('off')

        plt.tight_layout()

        # Save report
        report_file = output_path / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M')}.png"
        plt.savefig(report_file, dpi=300, bbox_inches='tight')
        plt.close()

        # Save JSON report
        json_file = output_path / f"performance_data_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(json_file, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"📊 Performance report saved:")
        print(f"  Chart: {report_file}")
        print(f"  Data: {json_file}")

        return stats

# Integration with EasyTranscribe
class MonitoredTranscriber:
    def __init__(self, analytics_db="transcription_analytics.db"):
        self.analytics = TranscriptionAnalytics(analytics_db)

    def transcribe_with_monitoring(self, audio_file=None, model_name="base"):
        """Transcribe with automatic performance monitoring."""
        from easytranscribe import transcribe_audio_file, capture_and_transcribe

        start_time = time.time()

        if audio_file:
            text = transcribe_audio_file(audio_file, model_name=model_name)
            source_type = "file"
            file_path = audio_file
        else:
            text = capture_and_transcribe(model_name=model_name)
            source_type = "live"
            file_path = None

        processing_time = time.time() - start_time
        word_count = len(text.split())

        # Log metrics
        metrics = TranscriptionMetrics(
            timestamp=datetime.now(),
            model_name=model_name,
            audio_duration=None,  # Could be calculated from audio file
            processing_time=processing_time,
            word_count=word_count,
            source_type=source_type,
            file_path=file_path
        )

        self.analytics.log_transcription(metrics, text)

        return text

# Usage example
if __name__ == "__main__":
    # Use monitored transcriber
    transcriber = MonitoredTranscriber()

    # Transcribe with monitoring
    text = transcriber.transcribe_with_monitoring("meeting.wav", model_name="medium")
    print(f"Transcribed: {text}")

    # Generate performance report
    transcriber.analytics.generate_performance_report()
```

## Integration Patterns

### Webhook Integration for Real-time Processing

```python
#!/usr/bin/env python3
"""Webhook integration for real-time transcription processing."""

import asyncio
import aiohttp
import json
from datetime import datetime
from pathlib import Path
from easytranscribe import transcribe_audio_file

class WebhookTranscriptionService:
    def __init__(self, webhook_url, api_key=None):
        self.webhook_url = webhook_url
        self.api_key = api_key
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def process_audio_with_webhook(self, audio_file, metadata=None):
        """Process audio file and send results via webhook."""
        try:
            # Transcribe audio
            print(f"🎧 Transcribing: {audio_file}")
            text = transcribe_audio_file(str(audio_file), model_name="base")

            # Prepare webhook payload
            payload = {
                "transcription": {
                    "text": text,
                    "audio_file": str(audio_file),
                    "word_count": len(text.split()),
                    "timestamp": datetime.now().isoformat(),
                    "metadata": metadata or {}
                },
                "status": "success"
            }

            # Send webhook
            await self._send_webhook(payload)

            print(f"✅ Processed and sent: {Path(audio_file).name}")
            return payload

        except Exception as e:
            # Send error webhook
            error_payload = {
                "error": {
                    "message": str(e),
                    "audio_file": str(audio_file),
                    "timestamp": datetime.now().isoformat()
                },
                "status": "error"
            }

            await self._send_webhook(error_payload)
            print(f"❌ Error processing {audio_file}: {e}")
            return error_payload

    async def _send_webhook(self, payload):
        """Send webhook HTTP request."""
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        async with self.session.post(
            self.webhook_url,
            json=payload,
            headers=headers
        ) as response:
            if response.status == 200:
                print(f"📤 Webhook sent successfully")
            else:
                print(f"⚠️ Webhook failed: {response.status}")

# Usage example
async def main():
    webhook_url = "https://your-api.com/transcription-webhook"

    async with WebhookTranscriptionService(webhook_url, api_key="your-api-key") as service:
        # Process multiple files
        audio_files = ["meeting1.wav", "meeting2.wav", "interview.mp3"]

        tasks = []
        for audio_file in audio_files:
            metadata = {"source": "meeting", "priority": "high"}
            task = service.process_audio_with_webhook(audio_file, metadata)
            tasks.append(task)

        # Process all files concurrently
        results = await asyncio.gather(*tasks)

        print(f"\nProcessed {len(results)} files")

if __name__ == "__main__":
    asyncio.run(main())
```

### Custom Model Integration

```python
#!/usr/bin/env python3
"""Custom model integration and fine-tuning workflows."""

import torch
import whisper
from pathlib import Path
from easytranscribe import transcribe_audio_file

class CustomWhisperWrapper:
    def __init__(self, custom_model_path=None, base_model="base"):
        self.base_model = base_model
        self.custom_model_path = custom_model_path
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load custom or base Whisper model."""
        if self.custom_model_path and Path(self.custom_model_path).exists():
            print(f"Loading custom model: {self.custom_model_path}")
            # Load custom fine-tuned model
            self.model = whisper.load_model(self.custom_model_path)
        else:
            print(f"Loading base model: {self.base_model}")
            self.model = whisper.load_model(self.base_model)

    def transcribe_with_custom_model(self, audio_file, **kwargs):
        """Transcribe using custom model with additional options."""
        # Custom preprocessing options
        options = {
            "language": kwargs.get("language", None),
            "task": kwargs.get("task", "transcribe"),  # or "translate"
            "temperature": kwargs.get("temperature", 0.0),
            "best_of": kwargs.get("best_of", 1),
            "beam_size": kwargs.get("beam_size", 5),
            "patience": kwargs.get("patience", None),
            "length_penalty": kwargs.get("length_penalty", None),
            "suppress_tokens": kwargs.get("suppress_tokens", "-1"),
            "initial_prompt": kwargs.get("initial_prompt", None),
            "condition_on_previous_text": kwargs.get("condition_on_previous_text", True),
            "fp16": kwargs.get("fp16", True),
            "compression_ratio_threshold": kwargs.get("compression_ratio_threshold", 2.4),
            "logprob_threshold": kwargs.get("logprob_threshold", -1.0),
            "no_speech_threshold": kwargs.get("no_speech_threshold", 0.6),
        }

        # Remove None values
        options = {k: v for k, v in options.items() if v is not None}

        print(f"Transcribing with options: {options}")
        result = self.model.transcribe(audio_file, **options)

        return {
            "text": result["text"],
            "segments": result.get("segments", []),
            "language": result.get("language", "unknown")
        }

# Domain-specific transcription
class DomainSpecificTranscriber:
    def __init__(self):
        self.medical_model = CustomWhisperWrapper(base_model="medium")
        self.legal_model = CustomWhisperWrapper(base_model="large")
        self.general_model = CustomWhisperWrapper(base_model="base")

    def transcribe_medical(self, audio_file):
        """Transcribe medical audio with specialized settings."""
        return self.medical_model.transcribe_with_custom_model(
            audio_file,
            initial_prompt="This is a medical consultation recording.",
            temperature=0.0,  # More deterministic for medical terms
            beam_size=10,     # Higher beam size for accuracy
            patience=2.0      # More patience for medical terminology
        )

    def transcribe_legal(self, audio_file):
        """Transcribe legal audio with specialized settings."""
        return self.legal_model.transcribe_with_custom_model(
            audio_file,
            initial_prompt="This is a legal proceeding or consultation.",
            temperature=0.0,
            best_of=3,        # Multiple candidates for legal accuracy
            condition_on_previous_text=True  # Important for legal context
        )

    def transcribe_general(self, audio_file):
        """Transcribe general audio."""
        return self.general_model.transcribe_with_custom_model(audio_file)

# Usage
if __name__ == "__main__":
    transcriber = DomainSpecificTranscriber()

    # Medical transcription
    medical_result = transcriber.transcribe_medical("patient_consultation.wav")
    print(f"Medical transcription: {medical_result['text']}")

    # Legal transcription
    legal_result = transcriber.transcribe_legal("court_hearing.wav")
    print(f"Legal transcription: {legal_result['text']}")
```

These advanced usage patterns demonstrate how to extend EasyTranscribe for production environments, specialized domains, and complex integration scenarios. Each pattern can be adapted and combined based on your specific requirements.
