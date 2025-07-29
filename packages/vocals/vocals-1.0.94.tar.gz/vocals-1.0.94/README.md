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
- [Advanced Usage](#advanced-usage)
- [Configuration](#configuration)
- [API Reference](#api-reference)
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

## API Reference

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
    modes: List[str] = []  # New parameter for controlling SDK behavior
)
```

**Modes:**

- `[]` (empty list): **Default Experience** - Full auto-contained behavior with automatic handlers
- `['transcription']`: **Controlled** - Only transcription-related internal processing
- `['voice_assistant']`: **Controlled** - Only AI response handling and speech interruption
- `['transcription', 'voice_assistant']`: **Controlled** - Both features, but no automatic handlers

### SDK Methods

- `await sdk["stream_microphone"](**options)` - Stream microphone input
- `await sdk["stream_audio_file"](file_path, **options)` - Stream audio file
- `await sdk["connect"]()` - Connect to WebSocket
- `await sdk["disconnect"]()` - Disconnect from WebSocket
- `await sdk["start_recording"]()` - Start recording
- `await sdk["stop_recording"]()` - Stop recording
- `await sdk["play_audio"]()` - Start/resume audio playback
- `await sdk["pause_audio"]()` - Pause audio playback
- `await sdk["stop_audio"]()` - Stop audio playback
- `sdk["cleanup"]()` - Cleanup resources

### Event Handlers

- `sdk["on_message"](handler)` - Handle incoming messages
- `sdk["on_connection_change"](handler)` - Handle connection state changes
- `sdk["on_error"](handler)` - Handle errors
- `sdk["on_audio_data"](handler)` - Handle audio data

**Note:** In **Default Experience** (no modes), enhanced message handlers are automatically attached. In **Controlled Experience** (with modes), you must attach your own handlers.

### Utility Functions

- `create_enhanced_message_handler(**options)` - Enhanced message display (for controlled experience)
- `create_conversation_tracker()` - Track conversation history
- `create_microphone_stats_tracker()` - Track microphone session statistics
- `create_default_connection_handler()` - Default connection handler
- `create_default_error_handler()` - Default error handler

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
