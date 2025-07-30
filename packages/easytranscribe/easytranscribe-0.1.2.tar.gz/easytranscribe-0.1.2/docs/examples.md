# Examples

This page provides practical examples showing how to use EasyTranscribe in various real-world scenarios.

## Basic Examples

### Simple Voice Note Taking

```python
#!/usr/bin/env python3
"""Simple voice note taking application."""

import datetime
from pathlib import Path
from easytranscribe import capture_and_transcribe

def take_voice_note():
    """Capture and save a voice note."""
    print("🎤 Speak your note (will stop after 3 seconds of silence)...")

    text = capture_and_transcribe(model_name="base", verbose=True)

    if text.strip():
        # Create filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"voice_note_{timestamp}.txt"

        # Save note
        with open(filename, 'w') as f:
            f.write(f"Voice Note - {datetime.datetime.now()}\n")
            f.write("=" * 50 + "\n\n")
            f.write(text)

        print(f"📝 Note saved to: {filename}")
    else:
        print("❌ No speech detected")

if __name__ == "__main__":
    take_voice_note()
```

### Audio File Batch Processing

```python
#!/usr/bin/env python3
"""Batch process audio files for transcription."""

from pathlib import Path
from easytranscribe import transcribe_audio_file

def process_audio_directory(input_dir, output_dir="transcripts"):
    """Process all audio files in a directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Supported audio extensions
    audio_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']

    # Find all audio files
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(input_path.glob(f"*{ext}"))

    print(f"Found {len(audio_files)} audio files")

    for audio_file in audio_files:
        print(f"Processing: {audio_file.name}")

        try:
            # Transcribe file
            text = transcribe_audio_file(str(audio_file), model_name="base")

            # Save transcript
            output_file = output_path / f"{audio_file.stem}_transcript.txt"
            with open(output_file, 'w') as f:
                f.write(f"Transcript of: {audio_file.name}\n")
                f.write("=" * 50 + "\n\n")
                f.write(text)

            print(f"  ✅ Saved: {output_file}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

# Usage
if __name__ == "__main__":
    process_audio_directory("audio_files/")
```

## Advanced Examples

### Meeting Transcription with Speaker Detection

```python
#!/usr/bin/env python3
"""Advanced meeting transcription with metadata."""

import json
import re
from datetime import datetime
from pathlib import Path
from easytranscribe import transcribe_audio_file

class MeetingTranscriber:
    def __init__(self, output_dir="meeting_transcripts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def transcribe_meeting(self, audio_file, meeting_info=None):
        """Transcribe a meeting with metadata."""
        print(f"🎧 Transcribing meeting: {audio_file}")

        # Transcribe with high accuracy
        transcript = transcribe_audio_file(
            audio_file,
            model_name="medium",
            verbose=True
        )

        # Process transcript
        processed_transcript = self._process_transcript(transcript)

        # Create meeting data
        meeting_data = {
            "metadata": {
                "title": meeting_info.get("title", "Untitled Meeting") if meeting_info else "Untitled Meeting",
                "date": meeting_info.get("date", datetime.now().isoformat()) if meeting_info else datetime.now().isoformat(),
                "attendees": meeting_info.get("attendees", []) if meeting_info else [],
                "audio_file": str(audio_file),
                "transcription_date": datetime.now().isoformat()
            },
            "transcript": {
                "raw": transcript,
                "processed": processed_transcript,
                "word_count": len(transcript.split()),
                "estimated_duration": f"{len(transcript.split()) / 150:.1f} minutes"
            },
            "analysis": self._analyze_transcript(transcript)
        }

        # Save transcript
        output_file = self.output_dir / f"meeting_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(output_file, 'w') as f:
            json.dump(meeting_data, f, indent=2)

        # Also save plain text version
        text_file = output_file.with_suffix('.txt')
        with open(text_file, 'w') as f:
            f.write(f"Meeting: {meeting_data['metadata']['title']}\n")
            f.write(f"Date: {meeting_data['metadata']['date']}\n")
            f.write(f"Attendees: {', '.join(meeting_data['metadata']['attendees'])}\n")
            f.write("=" * 60 + "\n\n")
            f.write(processed_transcript)

        print(f"📄 Transcript saved: {text_file}")
        print(f"📊 Data saved: {output_file}")

        return meeting_data

    def _process_transcript(self, transcript):
        """Process transcript for better readability."""
        # Add paragraphs at sentence boundaries
        sentences = re.split(r'[.!?]+', transcript)

        processed = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                processed.append(sentence + '.')

        # Group sentences into paragraphs (every 3-4 sentences)
        paragraphs = []
        current_paragraph = []

        for i, sentence in enumerate(processed):
            current_paragraph.append(sentence)

            if len(current_paragraph) >= 3 or i == len(processed) - 1:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []

        return '\n\n'.join(paragraphs)

    def _analyze_transcript(self, transcript):
        """Analyze transcript for key information."""
        words = transcript.split()

        # Simple keyword analysis
        action_keywords = ['decide', 'action', 'task', 'todo', 'follow up', 'deadline']
        question_keywords = ['question', 'unclear', 'clarify', 'explain']

        action_items = []
        questions = []

        # Simple analysis (in practice, you'd use more sophisticated NLP)
        sentences = re.split(r'[.!?]+', transcript)
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in action_keywords):
                action_items.append(sentence.strip())
            if any(keyword in sentence_lower for keyword in question_keywords):
                questions.append(sentence.strip())

        return {
            "word_count": len(words),
            "estimated_speaking_time": f"{len(words) / 150:.1f} minutes",
            "potential_action_items": action_items[:5],  # Top 5
            "potential_questions": questions[:3],  # Top 3
            "keywords": self._extract_keywords(transcript)
        }

    def _extract_keywords(self, transcript):
        """Extract potential keywords from transcript."""
        words = re.findall(r'\b[a-zA-Z]{4,}\b', transcript.lower())
        word_freq = {}

        # Simple frequency analysis
        stop_words = {'that', 'this', 'with', 'have', 'will', 'they', 'were', 'been', 'have', 'their'}

        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Return top 10 most frequent words
        return sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]

# Usage example
if __name__ == "__main__":
    transcriber = MeetingTranscriber()

    meeting_info = {
        "title": "Weekly Team Standup",
        "date": "2025-07-13",
        "attendees": ["Alice Johnson", "Bob Smith", "Carol Davis"]
    }

    result = transcriber.transcribe_meeting("team_meeting.wav", meeting_info)
    print(f"Meeting transcribed successfully!")
```

### Voice-Controlled Task Manager

```python
#!/usr/bin/env python3
"""Voice-controlled task management system."""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from easytranscribe import capture_and_transcribe

class VoiceTaskManager:
    def __init__(self, tasks_file="tasks.json"):
        self.tasks_file = Path(tasks_file)
        self.tasks = self._load_tasks()

    def _load_tasks(self):
        """Load tasks from file."""
        if self.tasks_file.exists():
            with open(self.tasks_file, 'r') as f:
                return json.load(f)
        return {"tasks": [], "completed": []}

    def _save_tasks(self):
        """Save tasks to file."""
        with open(self.tasks_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)

    def listen_for_command(self):
        """Listen for voice commands."""
        print("🎤 Listening for task command...")
        print("Say things like:")
        print("  - 'Add task: Buy groceries'")
        print("  - 'Complete task: Review code'")
        print("  - 'List tasks'")
        print("  - 'Show completed tasks'")
        print("  - 'Stop listening'")

        while True:
            try:
                command = capture_and_transcribe(model_name="base", verbose=False)
                if not command.strip():
                    continue

                print(f"Heard: {command}")

                if "stop listening" in command.lower():
                    print("👋 Stopping voice task manager")
                    break

                response = self._process_command(command)
                print(f"Response: {response}")
                print("-" * 40)

            except KeyboardInterrupt:
                print("\n👋 Stopping voice task manager")
                break

    def _process_command(self, command):
        """Process voice commands."""
        command_lower = command.lower()

        # Add task
        if "add task" in command_lower:
            return self._add_task(command)

        # Complete task
        elif "complete task" in command_lower or "done task" in command_lower:
            return self._complete_task(command)

        # List tasks
        elif "list task" in command_lower or "show task" in command_lower:
            return self._list_tasks()

        # Show completed
        elif "completed" in command_lower or "finished" in command_lower:
            return self._show_completed()

        # Delete task
        elif "delete task" in command_lower or "remove task" in command_lower:
            return self._delete_task(command)

        else:
            return "Command not recognized. Try 'add task', 'list tasks', or 'complete task'."

    def _add_task(self, command):
        """Add a new task."""
        # Extract task text after "add task:"
        match = re.search(r'add task:?\s*(.+)', command, re.IGNORECASE)
        if not match:
            return "Please say 'add task: [task description]'"

        task_text = match.group(1).strip()

        task = {
            "id": len(self.tasks["tasks"]) + 1,
            "text": task_text,
            "created": datetime.now().isoformat(),
            "priority": "normal"
        }

        # Check for priority keywords
        if any(word in task_text.lower() for word in ["urgent", "important", "asap"]):
            task["priority"] = "high"

        # Check for due dates
        due_date = self._extract_due_date(task_text)
        if due_date:
            task["due_date"] = due_date

        self.tasks["tasks"].append(task)
        self._save_tasks()

        return f"Added task: '{task_text}'"

    def _complete_task(self, command):
        """Mark a task as completed."""
        # Try to extract task text
        match = re.search(r'(?:complete|done) task:?\s*(.+)', command, re.IGNORECASE)
        if not match:
            return "Please say 'complete task: [task description]' or use task number"

        task_text = match.group(1).strip()

        # Find matching task
        for i, task in enumerate(self.tasks["tasks"]):
            if task_text.lower() in task["text"].lower():
                completed_task = self.tasks["tasks"].pop(i)
                completed_task["completed"] = datetime.now().isoformat()
                self.tasks["completed"].append(completed_task)
                self._save_tasks()
                return f"Completed task: '{task['text']}'"

        return f"Task not found: '{task_text}'"

    def _list_tasks(self):
        """List current tasks."""
        if not self.tasks["tasks"]:
            return "No tasks found"

        task_list = ["Current tasks:"]
        for task in self.tasks["tasks"]:
            priority_marker = "🔥" if task.get("priority") == "high" else "📝"
            due_info = f" (due: {task['due_date']})" if task.get("due_date") else ""
            task_list.append(f"{priority_marker} {task['text']}{due_info}")

        return "\n".join(task_list)

    def _show_completed(self):
        """Show completed tasks."""
        if not self.tasks["completed"]:
            return "No completed tasks"

        recent_completed = self.tasks["completed"][-5:]  # Last 5
        task_list = ["Recently completed:"]
        for task in recent_completed:
            task_list.append(f"✅ {task['text']}")

        return "\n".join(task_list)

    def _delete_task(self, command):
        """Delete a task."""
        match = re.search(r'(?:delete|remove) task:?\s*(.+)', command, re.IGNORECASE)
        if not match:
            return "Please say 'delete task: [task description]'"

        task_text = match.group(1).strip()

        for i, task in enumerate(self.tasks["tasks"]):
            if task_text.lower() in task["text"].lower():
                deleted_task = self.tasks["tasks"].pop(i)
                self._save_tasks()
                return f"Deleted task: '{deleted_task['text']}'"

        return f"Task not found: '{task_text}'"

    def _extract_due_date(self, text):
        """Extract due date from task text."""
        today = datetime.now().date()

        # Simple date extraction
        if "today" in text.lower():
            return today.isoformat()
        elif "tomorrow" in text.lower():
            return (today + timedelta(days=1)).isoformat()
        elif "next week" in text.lower():
            return (today + timedelta(days=7)).isoformat()

        return None

# Usage
if __name__ == "__main__":
    manager = VoiceTaskManager()
    manager.listen_for_command()
```

### Multi-Language Transcription

```python
#!/usr/bin/env python3
"""Multi-language transcription with language detection."""

from easytranscribe import transcribe_audio_file, capture_and_transcribe
from pathlib import Path

class MultiLanguageTranscriber:
    def __init__(self):
        # Language mapping for Whisper
        self.language_codes = {
            'english': 'en',
            'spanish': 'es',
            'french': 'fr',
            'german': 'de',
            'italian': 'it',
            'portuguese': 'pt',
            'russian': 'ru',
            'japanese': 'ja',
            'chinese': 'zh'
        }

    def transcribe_with_language_detection(self, audio_file=None):
        """Transcribe with automatic language detection."""
        if audio_file:
            print(f"🌍 Transcribing file with language detection: {audio_file}")
            text = transcribe_audio_file(audio_file, model_name="medium")
        else:
            print("🌍 Listening for speech in any language...")
            text = capture_and_transcribe(model_name="medium")

        # Whisper automatically detects language
        detected_language = self._detect_language_simple(text)

        print(f"Detected language: {detected_language}")
        print(f"Transcribed text: {text}")

        return {
            "text": text,
            "detected_language": detected_language,
            "audio_file": audio_file
        }

    def _detect_language_simple(self, text):
        """Simple language detection based on common words."""
        text_lower = text.lower()

        # Simple heuristics for common languages
        if any(word in text_lower for word in ['the', 'and', 'is', 'to', 'of']):
            return 'English'
        elif any(word in text_lower for word in ['el', 'la', 'es', 'de', 'que']):
            return 'Spanish'
        elif any(word in text_lower for word in ['le', 'de', 'et', 'à', 'un']):
            return 'French'
        elif any(word in text_lower for word in ['der', 'die', 'das', 'und', 'ist']):
            return 'German'
        else:
            return 'Unknown'

    def batch_transcribe_multilingual(self, audio_dir):
        """Batch transcribe multiple files with language detection."""
        audio_path = Path(audio_dir)
        results = []

        for audio_file in audio_path.glob("*.{wav,mp3,m4a}"):
            try:
                result = self.transcribe_with_language_detection(str(audio_file))
                results.append(result)

                # Save individual result
                output_file = audio_file.with_suffix('.txt')
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"Language: {result['detected_language']}\n")
                    f.write("=" * 40 + "\n\n")
                    f.write(result['text'])

                print(f"✅ Processed: {audio_file.name}")

            except Exception as e:
                print(f"❌ Error processing {audio_file}: {e}")

        return results

# Usage
if __name__ == "__main__":
    transcriber = MultiLanguageTranscriber()

    # Single file
    result = transcriber.transcribe_with_language_detection("spanish_audio.wav")

    # Live transcription
    # result = transcriber.transcribe_with_language_detection()

    # Batch processing
    # results = transcriber.batch_transcribe_multilingual("multilingual_audio/")
```

### Real-time Subtitles Generator

```python
#!/usr/bin/env python3
"""Real-time subtitle generator for live streams or meetings."""

import time
import threading
from datetime import datetime, timedelta
from easytranscribe import capture_and_transcribe

class RealTimeSubtitles:
    def __init__(self, output_file="subtitles.srt"):
        self.output_file = output_file
        self.subtitle_count = 0
        self.start_time = datetime.now()
        self.running = False

    def start_subtitle_generation(self):
        """Start generating real-time subtitles."""
        print("🎬 Starting real-time subtitle generation...")
        print("Press Ctrl+C to stop")

        self.running = True
        self.start_time = datetime.now()

        # Clear subtitle file
        with open(self.output_file, 'w') as f:
            f.write("")

        try:
            while self.running:
                # Capture speech segment
                text = capture_and_transcribe(model_name="base", verbose=False)

                if text.strip():
                    self._add_subtitle(text)
                    print(f"Added subtitle: {text[:50]}...")

        except KeyboardInterrupt:
            print(f"\n🎬 Subtitle generation stopped")
            print(f"Subtitles saved to: {self.output_file}")

    def _add_subtitle(self, text):
        """Add a subtitle entry to the SRT file."""
        self.subtitle_count += 1

        # Calculate timing
        current_time = datetime.now()
        start_offset = current_time - self.start_time
        end_offset = start_offset + timedelta(seconds=len(text.split()) * 0.5)  # ~0.5s per word

        # Format SRT timestamps
        start_srt = self._format_srt_time(start_offset)
        end_srt = self._format_srt_time(end_offset)

        # Create subtitle entry
        subtitle_entry = f"{self.subtitle_count}\n{start_srt} --> {end_srt}\n{text}\n\n"

        # Append to file
        with open(self.output_file, 'a', encoding='utf-8') as f:
            f.write(subtitle_entry)

    def _format_srt_time(self, time_delta):
        """Format timedelta for SRT format (HH:MM:SS,mmm)."""
        total_seconds = int(time_delta.total_seconds())
        milliseconds = int((time_delta.total_seconds() - total_seconds) * 1000)

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

# Usage
if __name__ == "__main__":
    subtitles = RealTimeSubtitles("live_subtitles.srt")
    subtitles.start_subtitle_generation()
```

These examples demonstrate the versatility of EasyTranscribe for various applications, from simple note-taking to complex workflow automation. Each example can be adapted and extended based on your specific needs.
