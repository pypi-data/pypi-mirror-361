# Vocals SDK Python

[![PyPI version](https://badge.fury.io/py/vocals.svg)](https://badge.fury.io/py/vocals)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub issues](https://img.shields.io/github/issues/hairetsucodes/vocals-sdk-python)](https://github.com/hairetsucodes/vocals-sdk-python/issues)

A Python SDK for voice processing and real-time audio communication with AI assistants. Stream microphone input or audio files to receive live transcription, AI responses, and text-to-speech audio.

## Features

- 🎤 **Real-time microphone streaming** with voice activity detection
- 📁 **Audio file playback** support (WAV format)
- ✨ **Live transcription** with partial and final results
- 🤖 **Streaming AI responses** with real-time text display
- 🔊 **Text-to-speech playback** with automatic audio queueing
- 📊 **Conversation tracking** and session statistics
- 🚀 **Easy setup** with minimal configuration required
- 🔄 **Auto-reconnection** and robust error handling

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

#### Microphone Streaming (Minimal Example)

```python
import asyncio
from vocals import create_vocals

async def main():
    # Create SDK instance
    sdk = create_vocals()

    # Stream microphone for 10 seconds
    await sdk["stream_microphone"](duration=10.0)

if __name__ == "__main__":
    asyncio.run(main())
```

#### Audio File Playback (Minimal Example)

```python
import asyncio
from vocals import create_vocals

async def main():
    # Create SDK instance
    sdk = create_vocals()

    # Stream audio file
    await sdk["stream_audio_file"]("path/to/your/audio.wav")

if __name__ == "__main__":
    asyncio.run(main())
```

## SDK Modes

The Vocals SDK supports two usage patterns:

### Default Experience (No Modes)

When you create the SDK without specifying modes, you get a full auto-contained experience:

```python
# Full experience with automatic handlers, playback, and beautiful console output
sdk = create_vocals()
```

**Features:**

- ✅ Automatic transcription display with partial updates
- ✅ Streaming AI response display in real-time
- ✅ Automatic TTS audio playback
- ✅ Speech interruption handling
- ✅ Beautiful console output with emojis
- ✅ Perfect for getting started quickly

### Controlled Experience (With Modes)

When you specify modes, the SDK becomes passive and you control everything:

```python
# Controlled experience - you handle all logic
sdk = create_vocals(modes=['transcription', 'voice_assistant'])
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
from vocals import create_vocals

async def main():
    # Create SDK with controlled experience
    sdk = create_vocals(modes=['transcription', 'voice_assistant'])

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
            asyncio.create_task(sdk["play_audio"]())

    # Register your handler
    sdk["on_message"](handle_messages)

    # Stream microphone
    await sdk["stream_microphone"](
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
    create_vocals,
    create_enhanced_message_handler,
    create_default_connection_handler,
    create_default_error_handler,
)

async def main():
    # Configure logging for cleaner output
    logging.getLogger("vocals").setLevel(logging.WARNING)

    # Create SDK with default full experience
    sdk = create_vocals()

    try:
        print("🎤 Starting microphone streaming...")
        print("Speak into your microphone!")

        # Stream microphone with enhanced features
        stats = await sdk["stream_microphone"](
            duration=30.0,            # Record for 30 seconds
            auto_connect=True,        # Auto-connect if needed
            auto_playback=True,       # Auto-play received audio
            verbose=False,            # SDK handles display automatically
            stats_tracking=True,      # Track session statistics
            amplitude_threshold=0.01, # Voice activity detection threshold
        )

        # Print session statistics
        print(f"\n📊 Session Statistics:")
        print(f"   • Transcriptions: {stats.get('transcriptions', 0)}")
        print(f"   • AI Responses: {stats.get('responses', 0)}")
        print(f"   • TTS Segments: {stats.get('tts_segments_received', 0)}")

    finally:
        # Disconnect and cleanup
        await sdk["disconnect"]()
        sdk["cleanup"]()

if __name__ == "__main__":
    asyncio.run(main())
```

### Conversation Tracking Example

```python
import asyncio
from vocals import (
    create_vocals,
    create_conversation_tracker,
    create_enhanced_message_handler,
)

async def main():
    # Create SDK with controlled experience for custom tracking
    sdk = create_vocals(modes=['transcription', 'voice_assistant'])
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
                asyncio.create_task(sdk["play_audio"]())

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
    sdk["on_message"](tracking_handler)

    try:
        # Stream microphone
        await sdk["stream_microphone"](
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

    finally:
        await sdk["disconnect"]()
        sdk["cleanup"]()

if __name__ == "__main__":
    asyncio.run(main())
```

### Infinite Streaming with Signal Handling

```python
import asyncio
import signal
from vocals import create_vocals

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

    # Create SDK
    sdk = create_vocals()

    # Create streaming task
    async def stream_task():
        await sdk["stream_microphone"](
            duration=0,  # 0 = infinite streaming
            auto_connect=True,
            auto_playback=True,
            verbose=False,
            stats_tracking=True,
        )

    # Run streaming and wait for shutdown
    streaming_task = asyncio.create_task(stream_task())
    shutdown_task = asyncio.create_task(shutdown_event.wait())

    try:
        print("🎤 Starting infinite streaming...")
        print("Press Ctrl+C to stop")

        # Wait for shutdown signal
        await shutdown_task

        # Stop recording gracefully
        await sdk["stop_recording"]()

    finally:
        # Cancel streaming task
        streaming_task.cancel()
        await sdk["disconnect"]()
        sdk["cleanup"]()

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

### Environment Variables

```bash
# Required: Your Vocals API key
export VOCALS_DEV_API_KEY="vdev_your_api_key_here"

```

### Audio Configuration

```python
from vocals import AudioConfig

# Create custom audio configuration
audio_config = AudioConfig(
    sample_rate=24000,    # Sample rate in Hz
    channels=1,           # Number of audio channels
    format="pcm_f32le",   # Audio format
    buffer_size=1024,     # Audio buffer size
)

# Use with SDK
sdk = create_vocals(audio_config=audio_config)
```

### SDK Configuration

```python
from vocals import get_default_config

# Get default configuration
config = get_default_config()

# Customize configuration
config.max_reconnect_attempts = 5
config.reconnect_delay = 2.0
config.auto_connect = True
config.token_refresh_buffer = 60.0

# Use with SDK
sdk = create_vocals(config=config)
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

- `create_vocals(config?, audio_config?, user_id?, modes?)` - Create SDK instance
- `get_default_config()` - Get default configuration
- `AudioConfig(...)` - Audio configuration class

#### `create_vocals()` Parameters

```python
create_vocals(
    config: Optional[VocalsConfig] = None,
    audio_config: Optional[AudioConfig] = None,
    user_id: Optional[str] = None,
    modes: List[str] = []  # Controls SDK behavior
)
```

**Parameters:**

- `config`: SDK configuration options (connection, logging, etc.)
- `audio_config`: Audio processing configuration (sample rate, channels, etc.)
- `user_id`: Optional user ID for token generation
- `modes`: List of modes to control SDK behavior

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
await sdk["stream_microphone"](
    duration: float = 30.0,           # Recording duration in seconds (0 for infinite)
    auto_connect: bool = True,        # Whether to automatically connect if not connected
    auto_playback: bool = True,       # Whether to automatically play received audio
    verbose: bool = True,             # Whether to log detailed progress
    stats_tracking: bool = True,      # Whether to track and return statistics
    amplitude_threshold: float = 0.01 # Minimum amplitude to consider as speech
)
```

**Important:** In **Controlled Experience** (with modes), TTS audio is always added to the queue, but `auto_playback=False` prevents automatic playback. You must manually call `sdk["play_audio"]()` to play queued audio.

#### `stream_audio_file()` Parameters

```python
await sdk["stream_audio_file"](
    file_path: str,                   # Path to the audio file to stream
    chunk_size: int = 1024,           # Size of each chunk to send
    verbose: bool = True,             # Whether to log detailed progress
    auto_connect: bool = True         # Whether to automatically connect if not connected
)
```

### Connection & Recording Methods

```python
await sdk["connect"]()                # Connect to WebSocket
await sdk["disconnect"]()             # Disconnect from WebSocket
await sdk["reconnect"]()              # Reconnect to WebSocket
await sdk["start_recording"]()        # Start recording
await sdk["stop_recording"]()         # Stop recording
```

### Audio Playback Methods

```python
await sdk["play_audio"]()             # Start/resume audio playback
await sdk["pause_audio"]()            # Pause audio playback
await sdk["stop_audio"]()             # Stop audio playback
await sdk["fade_out_audio"](duration) # Fade out audio over specified duration
sdk["clear_queue"]()                  # Clear the audio playback queue
sdk["add_to_queue"](segment)          # Add audio segment to queue
```

### Event Handlers

```python
sdk["on_message"](handler)            # Handle incoming messages
sdk["on_connection_change"](handler)  # Handle connection state changes
sdk["on_error"](handler)              # Handle errors
sdk["on_audio_data"](handler)         # Handle audio data
```

**Handler Functions:**

- `handler(message)` - Message handler receives WebSocket messages
- `handler(connection_state)` - Connection handler receives connection state changes
- `handler(error)` - Error handler receives error objects
- `handler(audio_data)` - Audio data handler receives real-time audio data

### Property Getters

```python
sdk["get_connection_state"]()         # Get current connection state
sdk["get_is_connected"]()             # Check if connected
sdk["get_is_connecting"]()            # Check if connecting
sdk["get_recording_state"]()          # Get current recording state
sdk["get_is_recording"]()             # Check if recording
sdk["get_playback_state"]()           # Get current playback state
sdk["get_is_playing"]()               # Check if playing audio
sdk["get_audio_queue"]()              # Get current audio queue
sdk["get_current_segment"]()          # Get currently playing segment
sdk["get_current_amplitude"]()        # Get current audio amplitude
sdk["get_token"]()                    # Get current token
sdk["get_token_expires_at"]()         # Get token expiration timestamp
```

### Utility Functions

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
- `auto_playback=False`: TTS audio is added to queue but requires manual `sdk["play_audio"]()` call

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
from vocals import create_vocals

async def test_default():
    """Test default experience with automatic handlers"""
    sdk = create_vocals()  # No modes = full automatic experience

    print("🎤 Testing default experience...")
    print("Speak and listen for AI responses...")

    # Test with automatic playback
    await sdk["stream_microphone"](
        duration=15.0,
        auto_playback=True,  # Should auto-play TTS
        verbose=False
    )

    await sdk["disconnect"]()
    sdk["cleanup"]()

asyncio.run(test_default())
```

### 3. Test Controlled Experience

```python
import asyncio
from vocals import create_vocals

async def test_controlled():
    """Test controlled experience with manual handlers"""
    sdk = create_vocals(modes=['transcription', 'voice_assistant'])

    # Track what we receive
    received_messages = []

    def test_handler(message):
        received_messages.append(message.type)
        print(f"✅ Received: {message.type}")

        # Test manual playback control
        if message.type == "tts_audio":
            print("🔊 Manually triggering playback...")
            asyncio.create_task(sdk["play_audio"]())

    # Register handler
    sdk["on_message"](test_handler)

    print("🎤 Testing controlled experience...")
    print("Should receive transcription and TTS messages...")

    # Test with manual playback control
    await sdk["stream_microphone"](
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

    await sdk["disconnect"]()
    sdk["cleanup"]()

asyncio.run(test_controlled())
```

### 4. Test Audio Playback Controls

```python
import asyncio
from vocals import create_vocals

async def test_playback_controls():
    """Test all audio playback controls"""
    sdk = create_vocals(modes=['transcription', 'voice_assistant'])

    # Test queue management
    print("🎵 Testing audio playback controls...")

    # Check initial state
    print(f"Initial queue size: {len(sdk['get_audio_queue']())}")
    print(f"Is playing: {sdk['get_is_playing']()}")

    def audio_handler(message):
        if message.type == "tts_audio":
            print(f"🎵 Audio received: {message.data.get('text', '')}")
            print(f"Queue size: {len(sdk['get_audio_queue']())}")

    sdk["on_message"](audio_handler)

    # Stream and collect audio
    await sdk["stream_microphone"](
        duration=10.0,
        auto_playback=False,  # Don't auto-play
        verbose=False
    )

    # Test manual controls
    queue_size = len(sdk["get_audio_queue"]())
    if queue_size > 0:
        print(f"✅ {queue_size} audio segments in queue")

        print("🎵 Testing play_audio()...")
        await sdk["play_audio"]()

        # Wait a moment then test pause
        await asyncio.sleep(1)
        print("⏸️ Testing pause_audio()...")
        await sdk["pause_audio"]()

        print("▶️ Testing play_audio() again...")
        await sdk["play_audio"]()

        # Test stop
        await asyncio.sleep(1)
        print("⏹️ Testing stop_audio()...")
        await sdk["stop_audio"]()

        print("🗑️ Testing clear_queue()...")
        sdk["clear_queue"]()
        print(f"Queue size after clear: {len(sdk['get_audio_queue']())}")

        print("✅ All playback controls working!")
    else:
        print("❌ No audio received to test playback controls")

    await sdk["disconnect"]()
    sdk["cleanup"]()

asyncio.run(test_playback_controls())
```

### 5. Test All Event Handlers

```python
import asyncio
from vocals import create_vocals

async def test_event_handlers():
    """Test all event handler types"""
    sdk = create_vocals(modes=['transcription', 'voice_assistant'])

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
    sdk["on_message"](message_handler)
    sdk["on_connection_change"](connection_handler)
    sdk["on_error"](error_handler)
    sdk["on_audio_data"](audio_data_handler)

    print("🧪 Testing all event handlers...")

    await sdk["stream_microphone"](
        duration=10.0,
        auto_playback=False,
        verbose=False
    )

    # Report results
    print("\n📊 Event Handler Test Results:")
    for event_type, count in events_received.items():
        status = "✅" if count > 0 else "❌"
        print(f"   {status} {event_type}: {count}")

    await sdk["disconnect"]()
    sdk["cleanup"]()

asyncio.run(test_event_handlers())
```

### 6. Validate All Controls Are Working

Run this comprehensive test to verify everything:

```bash
# Create a test script
cat > test_all_controls.py << 'EOF'
import asyncio
from vocals import create_vocals

async def comprehensive_test():
    """Comprehensive test of all SDK controls"""
    print("🧪 Comprehensive SDK Control Test")
    print("=" * 50)

    # Test 1: Default mode
    print("\n1️⃣ Testing Default Mode...")
    sdk1 = create_vocals()
    await sdk1["stream_microphone"](duration=5.0, verbose=False)
    await sdk1["disconnect"]()
    sdk1["cleanup"]()
    print("✅ Default mode test completed")

    # Test 2: Controlled mode
    print("\n2️⃣ Testing Controlled Mode...")
    sdk2 = create_vocals(modes=['transcription', 'voice_assistant'])

    message_count = 0
    def counter(message):
        nonlocal message_count
        message_count += 1
        if message.type == "tts_audio":
            asyncio.create_task(sdk2["play_audio"]())

    sdk2["on_message"](counter)
    await sdk2["stream_microphone"](duration=5.0, auto_playback=False, verbose=False)
    await sdk2["disconnect"]()
    sdk2["cleanup"]()
    print(f"✅ Controlled mode test completed - {message_count} messages")

    # Test 3: All controls
    print("\n3️⃣ Testing Individual Controls...")
    sdk3 = create_vocals()

    # Test getters
    print(f"   Connection state: {sdk3['get_connection_state']().name}")
    print(f"   Is connected: {sdk3['get_is_connected']()}")
    print(f"   Recording state: {sdk3['get_recording_state']().name}")
    print(f"   Is recording: {sdk3['get_is_recording']()}")
    print(f"   Playback state: {sdk3['get_playback_state']().name}")
    print(f"   Is playing: {sdk3['get_is_playing']()}")
    print(f"   Queue length: {len(sdk3['get_audio_queue']())}")
    print(f"   Current amplitude: {sdk3['get_current_amplitude']()}")

    await sdk3["disconnect"]()
    sdk3["cleanup"]()
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

The SDK provides comprehensive error handling:

```python
from vocals import create_vocals, VocalsError

async def main():
    try:
        sdk = create_vocals()
        await sdk["stream_microphone"](duration=10.0)
    except VocalsError as e:
        print(f"Vocals SDK error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if 'sdk' in locals():
            await sdk["disconnect"]()
            sdk["cleanup"]()
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
