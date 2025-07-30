# Vocals SDK Python

[![PyPI version](https://badge.fury.io/py/vocals.svg)](https://badge.fury.io/py/vocals)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub issues](https://img.shields.io/github/issues/hairetsucodes/vocals-sdk-python)](https://github.com/hairetsucodes/vocals-sdk-python/issues)

A Python SDK for voice processing and real-time audio communication with AI assistants. Stream microphone input or audio files to receive live transcription, AI responses, and text-to-speech audio.

**Features both class-based and functional interfaces** for maximum flexibility and ease of use.

## Features

- 🎤 **Real-time microphone streaming** with voice activity detection
- 📁 **Audio file playback** support (WAV format)
- ✨ **Live transcription** with partial and final results
- 🤖 **Streaming AI responses** with real-time text display
- 🔊 **Text-to-speech playback** with automatic audio queueing
- 📊 **Conversation tracking** and session statistics
- 🚀 **Easy setup** with minimal configuration required
- 🔄 **Auto-reconnection** and robust error handling
- 🎛️ **Class-based API** with modern Python patterns
- 🔀 **Context manager support** for automatic cleanup

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [SDK Modes](#sdk-modes)
- [Advanced Usage](#advanced-usage)
- [Configuration](#configuration)
- [Complete API Reference](#complete-api-reference)
- [Testing Your Setup](#testing-your-setup)
- [CLI Tools](#cli-tools)
- [Error Handling](#error-handling)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)
- [Contributing](#contributing)
- [Support](#support)
- [License](#license)

## Installation

```bash
pip install vocals
```

### Quick Setup

After installation, use the built-in setup wizard to configure your environment:

```bash
vocals setup
```

Or test your installation:

```bash
vocals test
```

Run a quick demo:

```bash
vocals demo
```

### 🌐 Web UI Demo

**NEW!** Launch an interactive web interface to try the voice assistant:

```bash
vocals demo --ui
```

This will:

- ✅ **Automatically install Gradio** (if not already installed)
- 🚀 **Launch a web interface** in your browser
- 🎤 **Real-time voice interaction** with visual feedback
- 📱 **Easy-to-use interface** with buttons and live updates
- 🔊 **Live transcription and AI responses** in the browser

**Perfect for:**

- 🎯 **Quick demonstrations** and testing
- 👥 **Showing to others** without command line
- 🖥️ **Visual feedback** and status indicators
- 📊 **Real-time conversation tracking**

The web UI provides the same functionality as the command line demo but with an intuitive graphical interface that's perfect for demonstrations and interactive testing.

### System Requirements

- Python 3.8 or higher
- Working microphone (for microphone streaming)
- Audio output device (for TTS playback)

### Additional Dependencies

The SDK automatically installs all required Python dependencies including `pyaudio`, `sounddevice`, `numpy`, `websockets`, and others.

On some Linux systems, you may need to install system-level audio libraries:

**Ubuntu/Debian:**

```bash
sudo apt-get install portaudio19-dev
```

**Other Linux distributions:**

```bash
# Install portaudio development headers using your package manager
# For example, on CentOS/RHEL: sudo yum install portaudio-devel
```

## Quick Start

### 1. Get Your API Key

Set up your Vocals API key as an environment variable:

```bash
export VOCALS_DEV_API_KEY="your_api_key_here"
```

Or create a `.env` file in your project:

```
VOCALS_DEV_API_KEY=your_api_key_here
```

### 2. Basic Usage

The Vocals SDK provides a modern **class-based API** as the primary interface

#### Microphone Streaming (Minimal Example)

```python
import asyncio
from vocals import VocalsClient

async def main():
    # Create client instance
    client = VocalsClient()

    # Stream microphone for 10 seconds
    await client.stream_microphone(duration=10.0)

    # Clean up
    await client.disconnect()
    client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

#### Audio File Playback (Minimal Example)

```python
import asyncio
from vocals import VocalsClient

async def main():
    # Create client instance
    client = VocalsClient()

    # Stream audio file
    await client.stream_audio_file("path/to/your/audio.wav")

    # Clean up
    await client.disconnect()
    client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

#### Context Manager Usage (Recommended)

```python
import asyncio
from vocals import VocalsClient

async def main():
    # Use context manager for automatic cleanup
    async with VocalsClient() as client:
        await client.stream_microphone(duration=10.0)

if __name__ == "__main__":
    asyncio.run(main())
```

## SDK Modes

The Vocals SDK supports two usage patterns:

### Default Experience (No Modes)

When you create the client without specifying modes, you get a full auto-contained experience:

```python
# Full experience with automatic handlers, playback, and beautiful console output
client = VocalsClient()
```

**Features:**

- ✅ Automatic transcription display with partial updates
- ✅ Streaming AI response display in real-time
- ✅ Automatic TTS audio playback
- ✅ Speech interruption handling
- ✅ Beautiful console output with emojis
- ✅ Perfect for getting started quickly

### Controlled Experience (With Modes)

When you specify modes, the client becomes passive and you control everything:

```python
# Controlled experience - you handle all logic
client = VocalsClient(modes=['transcription', 'voice_assistant'])
```

**Available Modes:**

- `'transcription'`: Enables transcription-related internal processing
- `'voice_assistant'`: Enables AI response handling and speech interruption

**Features:**

- ✅ No automatic handlers attached
- ✅ No automatic playback
- ✅ You attach your own message handlers
- ✅ You control when to play audio
- ✅ Perfect for custom applications

### Example: Controlled Experience

```python
import asyncio
from vocals import VocalsClient

async def main():
    # Create client with controlled experience
    client = VocalsClient(modes=['transcription', 'voice_assistant'])

    # Custom message handler
    def handle_messages(message):
        if message.type == "transcription" and message.data:
            text = message.data.get("text", "")
            is_partial = message.data.get("is_partial", False)
            if not is_partial:
                print(f"You said: {text}")

        elif message.type == "tts_audio" and message.data:
            text = message.data.get("text", "")
            print(f"AI speaking: {text}")
            # Manually start playback
            asyncio.create_task(client.play_audio())

    # Register your handler
    client.on_message(handle_messages)

    # Stream microphone with context manager
    async with client:
        await client.stream_microphone(
            duration=30.0,
            auto_playback=False  # We control playback
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Usage

### Enhanced Microphone Streaming

```python
import asyncio
import logging
from vocals import (
    VocalsClient,
    create_enhanced_message_handler,
    create_default_connection_handler,
    create_default_error_handler,
)

async def main():
    # Configure logging for cleaner output
    logging.getLogger("vocals").setLevel(logging.WARNING)

    # Create client with default full experience
    client = VocalsClient()

    try:
        print("🎤 Starting microphone streaming...")
        print("Speak into your microphone!")

        # Stream microphone with enhanced features
        async with client:
            stats = await client.stream_microphone(
                duration=30.0,            # Record for 30 seconds
                auto_connect=True,        # Auto-connect if needed
                auto_playback=True,       # Auto-play received audio
                verbose=False,            # Client handles display automatically
                stats_tracking=True,      # Track session statistics
                amplitude_threshold=0.01, # Voice activity detection threshold
            )

        # Print session statistics
        print(f"\n📊 Session Statistics:")
        print(f"   • Transcriptions: {stats.get('transcriptions', 0)}")
        print(f"   • AI Responses: {stats.get('responses', 0)}")
        print(f"   • TTS Segments: {stats.get('tts_segments_received', 0)}")

    except Exception as e:
        print(f"Error: {e}")
        await client.disconnect()
        client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

### Conversation Tracking Example

```python
import asyncio
from vocals import (
    VocalsClient,
    create_conversation_tracker,
    create_enhanced_message_handler,
)

async def main():
    # Create client with controlled experience for custom tracking
    client = VocalsClient(modes=['transcription', 'voice_assistant'])
    conversation_tracker = create_conversation_tracker()

    # Custom message handler with conversation tracking
    def tracking_handler(message):
        # Custom display logic
        if message.type == "transcription" and message.data:
            text = message.data.get("text", "")
            is_partial = message.data.get("is_partial", False)
            if not is_partial and text:
                print(f"🎤 You: {text}")

        elif message.type == "llm_response" and message.data:
            response = message.data.get("response", "")
            if response:
                print(f"🤖 AI: {response}")

        elif message.type == "tts_audio" and message.data:
            text = message.data.get("text", "")
            if text:
                print(f"🔊 Playing: {text}")
                # Manually start playback since we're in controlled mode
                asyncio.create_task(client.play_audio())

        # Track conversation based on message type
        if message.type == "transcription" and message.data:
            text = message.data.get("text", "")
            is_partial = message.data.get("is_partial", False)
            if text and not is_partial:
                conversation_tracker["add_transcription"](text, is_partial)

        elif message.type == "llm_response" and message.data:
            response = message.data.get("response", "")
            if response:
                conversation_tracker["add_response"](response)

    # Set up handler
    client.on_message(tracking_handler)

    try:
        # Stream microphone with context manager
        async with client:
            await client.stream_microphone(
                duration=15.0,
                auto_playback=False  # We handle playback manually
            )

        # Print conversation history
        print("\n" + "="*50)
        print("📜 CONVERSATION HISTORY")
        print("="*50)
        conversation_tracker["print_conversation"]()

        # Print conversation statistics
        stats = conversation_tracker["get_stats"]()
        print(f"\n📈 Session lasted {stats['duration']:.1f} seconds")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Infinite Streaming with Signal Handling

```python
import asyncio
import signal
from vocals import VocalsClient

# Global shutdown event
shutdown_event = asyncio.Event()

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        if not shutdown_event.is_set():
            print(f"\n📡 Received signal {signum}, shutting down...")
            shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

async def main():
    setup_signal_handlers()

    # Create client
    client = VocalsClient()

    try:
        print("🎤 Starting infinite streaming...")
        print("Press Ctrl+C to stop")

        # Connect to service
        await client.connect()

        # Create streaming task
        async def stream_task():
            await client.stream_microphone(
                duration=0,  # 0 = infinite streaming
                auto_connect=True,
                auto_playback=True,
                verbose=False,
                stats_tracking=True,
            )

        # Run streaming and wait for shutdown
        streaming_task = asyncio.create_task(stream_task())
        shutdown_task = asyncio.create_task(shutdown_event.wait())

        # Wait for shutdown signal
        await shutdown_task

        # Stop recording gracefully
        await client.stop_recording()

    finally:
        # Cancel streaming task
        if 'streaming_task' in locals():
            streaming_task.cancel()
        await client.disconnect()
        client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

### Custom Audio Processing (Alternative to Local Playback)

Instead of playing audio locally, you can process audio segments with custom handlers - perfect for saving audio files, sending to external players, or implementing custom audio processing:

```python
import asyncio
import base64
from vocals import VocalsClient

async def main():
    """Advanced voice assistant with custom audio processing"""

    # Create client with controlled mode for manual audio handling
    client = VocalsClient(modes=["transcription", "voice_assistant"])

    # Custom state tracking
    conversation_state = {"listening": False, "processing": False, "speaking": False}

    def handle_messages(message):
        """Custom message handler with audio processing control"""

        if message.type == "transcription" and message.data:
            text = message.data.get("text", "")
            is_partial = message.data.get("is_partial", False)

            if is_partial:
                print(f"\r🎤 Listening: {text}...", end="", flush=True)
            else:
                print(f"\n✅ You said: {text}")

        elif message.type == "llm_response_streaming" and message.data:
            token = message.data.get("token", "")
            is_complete = message.data.get("is_complete", False)

            if token:
                print(token, end="", flush=True)
            if is_complete:
                print()  # New line

        elif message.type == "tts_audio" and message.data:
            text = message.data.get("text", "")
            if text and not conversation_state["speaking"]:
                print(f"🔊 AI speaking: {text}")
                conversation_state["speaking"] = True

                # Custom audio processing instead of local playback
                def custom_audio_handler(segment):
                    """Process each audio segment with custom logic"""
                    print(f"🎵 Processing audio: {segment.text}")

                    # Option 1: Save to file
                    audio_data = base64.b64decode(segment.audio_data)
                    filename = f"audio_{segment.segment_id}.wav"
                    with open(filename, "wb") as f:
                        f.write(audio_data)
                    print(f"💾 Saved audio to: {filename}")

                    # Option 2: Send to external audio player
                    # subprocess.run(["ffplay", "-nodisp", "-autoexit", filename])

                    # Option 3: Stream to audio device
                    # your_audio_device.play(audio_data)

                    # Option 4: Convert format
                    # converted_audio = convert_audio_format(audio_data, target_format)

                    # Option 5: Process with AI/ML
                    # audio_features = extract_audio_features(audio_data)
                    # emotion_score = analyze_emotion(audio_features)

                # Process all available audio segments
                processed_count = client.process_audio_queue(
                    custom_audio_handler,
                    consume_all=True
                )
                print(f"✅ Processed {processed_count} audio segments")

        elif message.type == "speech_interruption":
            print("\n🛑 Speech interrupted")
            conversation_state["speaking"] = False

    # Register message handler
    client.on_message(handle_messages)

    # Connection handler
    def handle_connection(state):
        if state.name == "CONNECTED":
            print("✅ Connected to voice assistant")
        elif state.name == "DISCONNECTED":
            print("❌ Disconnected from voice assistant")

    client.on_connection_change(handle_connection)

    try:
        print("🎤 Voice Assistant with Custom Audio Processing")
        print("Audio will be saved to files instead of played locally")
        print("Speak into your microphone...")
        print("Press Ctrl+C to stop")

        # Stream microphone with custom audio handling
        async with client:
            await client.stream_microphone(
                duration=0,           # Infinite recording
                auto_connect=True,    # Auto-connect to service
                auto_playback=False,  # Disable automatic playback - we handle it
                verbose=False,        # Clean output
            )

    except KeyboardInterrupt:
        print("\n👋 Custom audio processing stopped")
    finally:
        await client.disconnect()
        client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

**Key Features of Custom Audio Processing:**

- 🎛️ **Full Control**: Complete control over audio handling instead of automatic playback
- 💾 **Save to Files**: Save audio segments as individual WAV files
- 🔄 **Format Conversion**: Convert audio to different formats before processing
- 🎵 **External Players**: Send audio to external audio players or devices
- 🤖 **AI Processing**: Analyze audio with machine learning models
- 📊 **Audio Analytics**: Extract features, analyze emotion, or process speech patterns
- 🔌 **Integration**: Easily integrate with existing audio pipelines

**Use Cases:**

- Recording conversations for later playback
- Building custom audio players with UI controls
- Streaming audio to multiple devices simultaneously
- Processing audio with AI/ML models for analysis
- Converting audio formats for different platforms
- Creating audio archives or transcription systems

## Configuration

### Environment Variables

```bash
# Required: Your Vocals API key
export VOCALS_DEV_API_KEY="vdev_your_api_key_here"

```

### Audio Configuration

```python
from vocals import VocalsClient, AudioConfig

# Create custom audio configuration
audio_config = AudioConfig(
    sample_rate=24000,    # Sample rate in Hz
    channels=1,           # Number of audio channels
    format="pcm_f32le",   # Audio format
    buffer_size=1024,     # Audio buffer size
)

# Use with client
client = VocalsClient(audio_config=audio_config)
```

### SDK Configuration

```python
from vocals import VocalsClient, get_default_config

# Get default configuration
config = get_default_config()

# Customize configuration
config.max_reconnect_attempts = 5
config.reconnect_delay = 2.0
config.auto_connect = True
config.token_refresh_buffer = 60.0

# Use with client
client = VocalsClient(config=config)
```

## Complete API Reference

The Vocals SDK provides comprehensive control over voice processing, connection management, audio playback, and event handling. Here's a complete reference of all available controls:

**🎛️ Main Control Categories:**

- **SDK Creation & Configuration** - Initialize and configure the SDK
- **Stream Methods** - Control microphone and file streaming
- **Connection Management** - Connect, disconnect, and manage WebSocket connections
- **Audio Playback** - Control TTS audio playback, queueing, and timing
- **Event Handling** - Register handlers for messages, connections, errors, and audio data
- **State Management** - Access real-time state information
- **Device Management** - Manage and test audio devices

**📋 Quick Reference:**
| Control Category | Key Methods | Purpose |
|------------------|-------------|---------|
| **Streaming** | `stream_microphone()`, `stream_audio_file()` | Start voice/audio processing |
| **Connection** | `connect()`, `disconnect()`, `reconnect()` | Manage WebSocket connection |
| **Recording** | `start_recording()`, `stop_recording()` | Control audio input |
| **Playback** | `play_audio()`, `pause_audio()`, `stop_audio()` | Control TTS audio output |
| **Queue** | `clear_queue()`, `add_to_queue()`, `get_audio_queue()` | Manage audio queue |
| **Events** | `on_message()`, `on_connection_change()`, `on_error()` | Handle events |
| **State** | `get_is_connected()`, `get_is_playing()`, `get_recording_state()` | Check current state |

### Core Functions

- `VocalsClient(config?, audio_config?, user_id?, modes?)` - Create client instance
- `get_default_config()` - Get default configuration
- `AudioConfig(...)` - Audio configuration class

#### `VocalsClient()` Constructor

```python
VocalsClient(
    config: Optional[VocalsConfig] = None,
    audio_config: Optional[AudioConfig] = None,
    user_id: Optional[str] = None,
    modes: List[str] = []  # Controls client behavior
)
```

**Parameters:**

- `config`: Client configuration options (connection, logging, etc.)
- `audio_config`: Audio processing configuration (sample rate, channels, etc.)
- `user_id`: Optional user ID for token generation
- `modes`: List of modes to control client behavior

**Modes:**

- `[]` (empty list): **Default Experience** - Full auto-contained behavior with automatic handlers
- `['transcription']`: **Controlled** - Only transcription-related internal processing
- `['voice_assistant']`: **Controlled** - Only AI response handling and speech interruption
- `['transcription', 'voice_assistant']`: **Controlled** - Both features, but no automatic handlers

### Audio Configuration

```python
AudioConfig(
    sample_rate: int = 24000,     # Sample rate in Hz
    channels: int = 1,            # Number of audio channels
    format: str = "pcm_f32le",    # Audio format
    buffer_size: int = 1024,      # Audio buffer size
)
```

### Stream Methods

#### `stream_microphone()` Parameters

```python
await client.stream_microphone(
    duration: float = 30.0,           # Recording duration in seconds (0 for infinite)
    auto_connect: bool = True,        # Whether to automatically connect if not connected
    auto_playback: bool = True,       # Whether to automatically play received audio
    verbose: bool = True,             # Whether to log detailed progress
    stats_tracking: bool = True,      # Whether to track and return statistics
    amplitude_threshold: float = 0.01 # Minimum amplitude to consider as speech
)
```

**Important:** In **Controlled Experience** (with modes), TTS audio is always added to the queue, but `auto_playback=False` prevents automatic playback. You must manually call `client.play_audio()` to play queued audio.

#### `stream_audio_file()` Parameters

```python
await client.stream_audio_file(
    file_path: str,                   # Path to the audio file to stream
    chunk_size: int = 1024,           # Size of each chunk to send
    verbose: bool = True,             # Whether to log detailed progress
    auto_connect: bool = True         # Whether to automatically connect if not connected
)
```

### Connection & Recording Methods

```python
await client.connect()                # Connect to WebSocket
await client.disconnect()             # Disconnect from WebSocket
await client.reconnect()              # Reconnect to WebSocket
await client.start_recording()        # Start recording
await client.stop_recording()         # Stop recording
```

### Audio Playback Methods

```python
await client.play_audio()             # Start/resume audio playback
await client.pause_audio()            # Pause audio playback
await client.stop_audio()             # Stop audio playback
await client.fade_out_audio(duration) # Fade out audio over specified duration
client.clear_queue()                  # Clear the audio playback queue
client.add_to_queue(segment)          # Add audio segment to queue
```

### Event Handlers

```python
client.on_message(handler)            # Handle incoming messages
client.on_connection_change(handler)  # Handle connection state changes
client.on_error(handler)              # Handle errors
client.on_audio_data(handler)         # Handle audio data
```

**Handler Functions:**

- `handler(message)` - Message handler receives WebSocket messages
- `handler(connection_state)` - Connection handler receives connection state changes
- `handler(error)` - Error handler receives error objects
- `handler(audio_data)` - Audio data handler receives real-time audio data

### Properties

```python
# Connection properties
client.connection_state               # Get current connection state
client.is_connected                   # Check if connected
client.is_connecting                  # Check if connecting

# Recording properties
client.recording_state                # Get current recording state
client.is_recording                   # Check if recording

# Playback properties
client.playback_state                 # Get current playback state
client.is_playing                     # Check if playing audio
client.audio_queue                    # Get current audio queue
client.current_segment                # Get currently playing segment
client.current_amplitude              # Get current audio amplitude

# Token properties
client.token                          # Get current token
client.token_expires_at               # Get token expiration timestamp
```

### Utility Methods

```python
client.set_user_id(user_id)           # Set user ID for token generation
client.cleanup()                      # Clean up resources
client.process_audio_queue(handler)   # Process audio queue with custom handler
```

### Utility Functions

These utility functions work with both the class-based and functional APIs:

```python
# Message handlers
create_enhanced_message_handler(
    verbose: bool = True,
    show_transcription: bool = True,
    show_responses: bool = True,
    show_streaming: bool = True,
    show_detection: bool = False
)

# Conversation tracking
create_conversation_tracker()

# Statistics tracking
create_microphone_stats_tracker(verbose: bool = True)

# Connection handlers
create_default_connection_handler(verbose: bool = True)
create_default_error_handler(verbose: bool = True)
```

### Audio Device Management

```python
# Device management
list_audio_devices()                  # List available audio devices
get_default_audio_device()            # Get default audio device
test_audio_device(device_id, duration) # Test audio device
validate_audio_device(device_id)      # Validate audio device
get_audio_device_info(device_id)      # Get device information
print_audio_devices()                 # Print formatted device list
create_audio_device_selector()        # Interactive device selector
```

### Auto-Playback Behavior

**Default Experience (no modes):**

- `auto_playback=True` (default): TTS audio plays automatically
- `auto_playback=False`: TTS audio is added to queue but doesn't play automatically

**Controlled Experience (with modes):**

- `auto_playback=True`: TTS audio is added to queue and plays automatically
- `auto_playback=False`: TTS audio is added to queue but requires manual `client.play_audio()` call

**Key Point:** In controlled mode, TTS audio is **always** added to the queue regardless of `auto_playback` setting. The `auto_playback` parameter only controls whether playback starts automatically.

### Message Types

Common message types you'll receive in handlers:

```python
# Transcription messages
{
    "type": "transcription",
    "data": {
        "text": "Hello world",
        "is_partial": False,
        "segment_id": "abc123"
    }
}

# LLM streaming response
{
    "type": "llm_response_streaming",
    "data": {
        "token": "Hello",
        "accumulated_response": "Hello",
        "is_complete": False,
        "segment_id": "def456"
    }
}

# TTS audio
{
    "type": "tts_audio",
    "data": {
        "text": "Hello there",
        "audio_data": "base64_encoded_wav_data",
        "sample_rate": 24000,
        "segment_id": "ghi789",
        "duration_seconds": 1.5
    }
}

# Speech interruption
{
    "type": "speech_interruption",
    "data": {}
}
```

## Testing Your Setup

After setting up the SDK, you can test all the controls to ensure everything is working properly:

### 1. Test Basic Audio Setup

```bash
# List available audio devices
vocals devices

# Test your microphone
vocals test-device

# Run system diagnostics
vocals diagnose
```

### 2. Test Default Experience

```python
import asyncio
from vocals import VocalsClient

async def test_default():
    """Test default experience with automatic handlers"""
    client = VocalsClient()  # No modes = full automatic experience

    print("🎤 Testing default experience...")
    print("Speak and listen for AI responses...")

    # Test with automatic playback
    async with client:
        await client.stream_microphone(
            duration=15.0,
            auto_playback=True,  # Should auto-play TTS
            verbose=False
        )

    print("✅ Default experience test completed")

asyncio.run(test_default())
```

### 3. Test Controlled Experience

```python
import asyncio
from vocals import VocalsClient

async def test_controlled():
    """Test controlled experience with manual handlers"""
    client = VocalsClient(modes=['transcription', 'voice_assistant'])

    # Track what we receive
    received_messages = []

    def test_handler(message):
        received_messages.append(message.type)
        print(f"✅ Received: {message.type}")

        # Test manual playback control
        if message.type == "tts_audio":
            print("🔊 Manually triggering playback...")
            asyncio.create_task(client.play_audio())

    # Register handler
    client.on_message(test_handler)

    print("🎤 Testing controlled experience...")
    print("Should receive transcription and TTS messages...")

    # Test with manual playback control
    async with client:
        await client.stream_microphone(
            duration=15.0,
            auto_playback=False,  # We control playback manually
            verbose=False
        )

    print(f"📊 Received message types: {set(received_messages)}")

    # Verify we got the expected message types
    expected_types = ["transcription", "tts_audio"]
    for msg_type in expected_types:
        if msg_type in received_messages:
            print(f"✅ {msg_type} messages working")
        else:
            print(f"❌ {msg_type} messages not received")

    print("✅ Controlled experience test completed")

asyncio.run(test_controlled())
```

### 4. Test Audio Playback Controls

```python
import asyncio
from vocals import VocalsClient

async def test_playback_controls():
    """Test all audio playback controls"""
    client = VocalsClient(modes=['transcription', 'voice_assistant'])

    # Test queue management
    print("🎵 Testing audio playback controls...")

    # Check initial state
    print(f"Initial queue size: {len(client.audio_queue)}")
    print(f"Is playing: {client.is_playing}")

    def audio_handler(message):
        if message.type == "tts_audio":
            print(f"🎵 Audio received: {message.data.get('text', '')}")
            print(f"Queue size: {len(client.audio_queue)}")

    client.on_message(audio_handler)

    # Stream and collect audio
    async with client:
        await client.stream_microphone(
            duration=10.0,
            auto_playback=False,  # Don't auto-play
            verbose=False
        )

    # Test manual controls
    queue_size = len(client.audio_queue)
    if queue_size > 0:
        print(f"✅ {queue_size} audio segments in queue")

        print("🎵 Testing play_audio()...")
        await client.play_audio()

        # Wait a moment then test pause
        await asyncio.sleep(1)
        print("⏸️ Testing pause_audio()...")
        await client.pause_audio()

        print("▶️ Testing play_audio() again...")
        await client.play_audio()

        # Test stop
        await asyncio.sleep(1)
        print("⏹️ Testing stop_audio()...")
        await client.stop_audio()

        print("🗑️ Testing clear_queue()...")
        client.clear_queue()
        print(f"Queue size after clear: {len(client.audio_queue)}")

        print("✅ All playback controls working!")
    else:
        print("❌ No audio received to test playback controls")

    await client.disconnect()
    client.cleanup()

asyncio.run(test_playback_controls())
```

### 5. Test All Event Handlers

```python
import asyncio
from vocals import VocalsClient

async def test_event_handlers():
    """Test all event handler types"""
    client = VocalsClient(modes=['transcription', 'voice_assistant'])

    # Track events
    events_received = {
        'messages': 0,
        'connections': 0,
        'errors': 0,
        'audio_data': 0
    }

    def message_handler(message):
        events_received['messages'] += 1
        print(f"📩 Message: {message.type}")

    def connection_handler(state):
        events_received['connections'] += 1
        print(f"🔌 Connection: {state.name}")

    def error_handler(error):
        events_received['errors'] += 1
        print(f"❌ Error: {error.message}")

    def audio_data_handler(audio_data):
        events_received['audio_data'] += 1
        if events_received['audio_data'] % 100 == 0:  # Log every 100th
            print(f"🎤 Audio data chunks: {events_received['audio_data']}")

    # Register all handlers
    client.on_message(message_handler)
    client.on_connection_change(connection_handler)
    client.on_error(error_handler)
    client.on_audio_data(audio_data_handler)

    print("🧪 Testing all event handlers...")

    async with client:
        await client.stream_microphone(
            duration=10.0,
            auto_playback=False,
            verbose=False
        )

    # Report results
    print("\n📊 Event Handler Test Results:")
    for event_type, count in events_received.items():
        status = "✅" if count > 0 else "❌"
        print(f"   {status} {event_type}: {count}")

asyncio.run(test_event_handlers())
```

### 6. Validate All Controls Are Working

Run this comprehensive test to verify everything:

```bash
# Create a test script
cat > test_all_controls.py << 'EOF'
import asyncio
from vocals import VocalsClient

async def comprehensive_test():
    """Comprehensive test of all client controls"""
    print("🧪 Comprehensive Client Control Test")
    print("=" * 50)

    # Test 1: Default mode
    print("\n1️⃣ Testing Default Mode...")
    client1 = VocalsClient()
    async with client1:
        await client1.stream_microphone(duration=5.0, verbose=False)
    print("✅ Default mode test completed")

    # Test 2: Controlled mode
    print("\n2️⃣ Testing Controlled Mode...")
    client2 = VocalsClient(modes=['transcription', 'voice_assistant'])

    message_count = 0
    def counter(message):
        nonlocal message_count
        message_count += 1
        if message.type == "tts_audio":
            asyncio.create_task(client2.play_audio())

    client2.on_message(counter)
    async with client2:
        await client2.stream_microphone(duration=5.0, auto_playback=False, verbose=False)
    print(f"✅ Controlled mode test completed - {message_count} messages")

    # Test 3: All controls
    print("\n3️⃣ Testing Individual Controls...")
    client3 = VocalsClient()

    # Test properties
    print(f"   Connection state: {client3.connection_state.name}")
    print(f"   Is connected: {client3.is_connected}")
    print(f"   Recording state: {client3.recording_state.name}")
    print(f"   Is recording: {client3.is_recording}")
    print(f"   Playback state: {client3.playback_state.name}")
    print(f"   Is playing: {client3.is_playing}")
    print(f"   Queue length: {len(client3.audio_queue)}")
    print(f"   Current amplitude: {client3.current_amplitude}")

    await client3.disconnect()
    client3.cleanup()
    print("✅ All controls test completed")

    print("\n🎉 All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(comprehensive_test())
EOF

# Run the test
python test_all_controls.py
```

This comprehensive testing suite will validate that all your controls are working properly after our recent fixes!

## CLI Tools

The SDK includes powerful command-line tools for setup, testing, and debugging:

### Setup & Configuration

```bash
# Interactive setup wizard
vocals setup

# List available audio devices
vocals devices

# Test a specific audio device
vocals test-device 1 --duration 5

# Generate diagnostic report
vocals diagnose
```

### Development Tools

```bash
# Run all tests
vocals test

# Run a demo session
vocals demo --duration 30 --verbose

# Create project templates
vocals create-template voice_assistant
vocals create-template file_processor
vocals create-template conversation_tracker
vocals create-template advanced_voice_assistant
```

**Available Templates:**

- `voice_assistant`: Simple voice assistant (**Default Experience**)
- `file_processor`: Process audio files (**Default Experience**)
- `conversation_tracker`: Track conversations (**Controlled Experience**)
- `advanced_voice_assistant`: Full control voice assistant (**Controlled Experience**)

All templates use the modern **class-based API** with `VocalsClient`.

### Advanced Features

```bash
# Performance monitoring
vocals demo --duration 60 --stats

# Custom audio device
vocals demo --device 2

# Debug mode
VOCALS_DEBUG_LEVEL=DEBUG vocals demo
```

## Error Handling

The client provides comprehensive error handling:

```python
from vocals import VocalsClient, VocalsError

async def main():
    client = VocalsClient()

    try:
        async with client:
            await client.stream_microphone(duration=10.0)
    except VocalsError as e:
        print(f"Vocals client error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        # Manual cleanup if context manager fails
        await client.disconnect()
        client.cleanup()

# Alternative without context manager
async def main_manual():
    client = VocalsClient()

    try:
        await client.stream_microphone(duration=10.0)
    except VocalsError as e:
        print(f"Vocals client error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        await client.disconnect()
        client.cleanup()
```

## Troubleshooting

### Common Issues

1. **"API key not found"**

   - Set environment variable: `export VOCALS_DEV_API_KEY="your_key"`
   - Or create `.env` file with the key
   - Ensure the .env file is loaded (e.g., using python-dotenv if needed)

2. **"Connection failed"**

   - Check your internet connection
   - Verify API key is valid
   - Check WebSocket endpoint is accessible
   - Try increasing reconnect attempts in config

3. **"No audio input detected"**

   - Check microphone permissions
   - Verify microphone is working (use `vocals devices` to list devices)
   - Adjust `amplitude_threshold` parameter lower (e.g., 0.005)
   - Test with `vocals test-device <id>`

4. **Audio playback issues**

   - Ensure speakers/headphones are connected
   - Check system audio settings
   - Try different audio formats or sample rates in AudioConfig

5. **High latency**

   - Check network speed
   - Reduce buffer_size in AudioConfig
   - Ensure no other apps are using high bandwidth

6. **Dependency errors**
   - Run `pip install -r requirements.txt` again
   - For Linux: Ensure portaudio is installed
   - Try creating a fresh virtual environment

If issues persist, run `vocals diagnose` and share the output when reporting bugs.

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or for specific modules
logging.getLogger("vocals").setLevel(logging.DEBUG)
```

## Examples

Check out the included examples:

- [`examples/example_microphone_streaming.py`](examples/example_microphone_streaming.py) - Comprehensive microphone streaming examples
- [`examples/example_file_playback.py`](examples/example_file_playback.py) - Audio file playback examples
- [`examples/run_examples.sh`](examples/run_examples.sh) - Script to run examples with proper setup

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

For major changes, please open an issue first to discuss what you would like to change.

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details (feel free to create one if it doesn't exist).

## Support

For support, documentation, and updates:

- 📖 [Documentation](https://docs.vocals.dev)
- 🐛 [Issues](https://github.com/vocals/vocals-sdk-python/issues)
- 💬 [Support](mailto:support@vocals.dev)

## License

MIT License - see LICENSE file for details.
