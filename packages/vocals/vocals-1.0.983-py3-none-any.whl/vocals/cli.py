"""
Vocals SDK Command Line Interface

Provides convenient command-line tools for setup, testing, and demos.
"""

import asyncio
import sys
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

try:
    import click
except ImportError:
    print("Click is required for CLI functionality. Install with: pip install click")
    sys.exit(1)

from .config import VocalsConfig, get_default_config
from .audio_processor import AudioConfig
from .client import VocalsClient


@click.group()
def cli():
    """🎤 Vocals SDK Command Line Interface"""
    pass


@cli.command()
@click.option(
    "--duration", default=30, help="Recording duration in seconds (0 for infinite)"
)
@click.option("--verbose", is_flag=True, help="Enable verbose output")
@click.option("--stats", is_flag=True, default=True, help="Show session statistics")
@click.option("--device", type=int, help="Audio device ID to use")
@click.option(
    "--ui", is_flag=True, help="Launch web UI demo (installs Gradio if needed)"
)
def demo(duration, verbose, stats, device, ui):
    """Run a microphone streaming demo

    Use --ui flag to launch a web-based interface instead of the terminal demo.
    The web UI will automatically install Gradio if not already installed.
    """

    if ui:
        # Launch UI demo
        run_ui_demo()
        return

    async def run_demo():
        print("🎤 Vocals SDK Demo")
        print("=" * 50)

        # Configure logging
        if verbose:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.getLogger("vocals").setLevel(logging.WARNING)

        try:
            # Create SDK with pure default experience - fully self-contained
            client = (
                VocalsClient()
            )  # No modes, no config changes = full auto-contained experience

            # TODO: Override audio device if specified
            if device is not None:
                print(f"Using audio device ID: {device}")

            print(f"Starting microphone streaming for {duration}s...")
            print("Speak into your microphone!")
            print("Press Ctrl+C to stop early")

            # Stream microphone
            session_stats = await client.stream_microphone(
                duration=duration,
                auto_connect=True,
                auto_playback=True,
                verbose=False,  # SDK handles display automatically
                stats_tracking=stats,
            )

            # Show results
            if stats and session_stats:
                print("\n📊 Session Statistics:")
                print(f"   • Transcriptions: {session_stats.get('transcriptions', 0)}")
                print(f"   • AI Responses: {session_stats.get('responses', 0)}")
                print(
                    f"   • TTS Segments: {session_stats.get('tts_segments_received', 0)}"
                )

        except KeyboardInterrupt:
            print("\n👋 Demo stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            if "sdk" in locals():
                try:
                    await client.disconnect()
                    client.cleanup()
                except:
                    pass

    asyncio.run(run_demo())


@cli.command()
@click.option("--force", is_flag=True, help="Overwrite existing configuration")
def setup(force):
    """Interactive setup wizard"""

    print("🎤 Vocals SDK Setup Wizard")
    print("=" * 50)

    # Check if .env exists
    env_file = Path(".env")
    if env_file.exists() and not force:
        print("⚠️  .env file already exists. Use --force to overwrite.")
        if not click.confirm("Continue with existing configuration?"):
            return

    # API Key setup
    print("\n1. API Key Configuration")
    api_key = os.environ.get("VOCALS_DEV_API_KEY")
    if api_key:
        print(f"Current API key: {api_key[:10]}...")
        if not click.confirm("Keep current API key?"):
            api_key = None

    if not api_key:
        api_key = click.prompt("Enter your Vocals API key", hide_input=True)
        if not api_key.startswith("vdev_"):
            print("⚠️  API key should start with 'vdev_'")

    # WebSocket endpoint
    print("\n2. WebSocket Configuration")
    current_endpoint = os.environ.get(
        "VOCALS_WS_ENDPOINT", "ws://192.168.1.46:8000/v1/stream/conversation"
    )
    print(f"Current endpoint: {current_endpoint}")

    if click.confirm("Use custom WebSocket endpoint?"):
        endpoint = click.prompt("WebSocket endpoint", default=current_endpoint)
    else:
        endpoint = current_endpoint

    # Audio device selection
    print("\n3. Audio Device Selection")
    try:
        devices = list_audio_devices()
        if devices:
            print("Available audio devices:")
            for device in devices:
                print(
                    f"  {device['id']}: {device['name']} ({device['channels']} channels)"
                )

            device_id = click.prompt(
                "Select device ID (or press Enter for default)",
                type=int,
                default=None,
                show_default=False,
            )
        else:
            device_id = None
    except Exception as e:
        print(f"⚠️  Could not list audio devices: {e}")
        device_id = None

    # Write configuration
    env_content = f"""# Vocals SDK Configuration
VOCALS_DEV_API_KEY={api_key}
VOCALS_WS_ENDPOINT={endpoint}

# Connection settings (auto_connect defaults to False to prevent race conditions)
# VOCALS_AUTO_CONNECT=false
"""

    if device_id is not None:
        env_content += f"VOCALS_AUDIO_DEVICE_ID={device_id}\n"

    with open(".env", "w") as f:
        f.write(env_content)

    print("\n✅ Configuration saved to .env")
    print("You can now run: vocals demo")


@cli.command()
@click.option("--verbose", is_flag=True, help="Show detailed test output")
def test(verbose):
    """Run SDK functionality tests"""

    async def run_tests():
        print("🧪 Vocals SDK Tests")
        print("=" * 50)

        # Configure logging
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.getLogger("vocals").setLevel(logging.WARNING)

        tester = VocalsSDKTester()

        # Run tests
        print("Testing connection...")
        await tester.test_connection()

        print("Testing audio recording...")
        await tester.test_audio_recording()

        print("Testing configuration...")
        tester.test_configuration()

        print("Testing audio devices...")
        tester.test_audio_devices()

        # Show results
        tester.print_results()

    asyncio.run(run_tests())


@cli.command()
def devices():
    """List available audio devices"""

    print("🎧 Available Audio Devices")
    print("=" * 50)

    try:
        devices = list_audio_devices()
        if devices:
            for device in devices:
                print(f"ID {device['id']}: {device['name']}")
                print(f"  Input channels: {device['channels']}")
                print(f"  Sample rate: {device['sample_rate']}")
                print()
        else:
            print("No audio input devices found")
    except Exception as e:
        print(f"❌ Error listing devices: {e}")


@cli.command()
@click.argument("device_id", type=int)
@click.option("--duration", default=5, help="Test duration in seconds")
def test_device(device_id, duration):
    """Test a specific audio device"""

    print(f"🎤 Testing Audio Device {device_id}")
    print("=" * 50)

    try:
        print(f"Testing device for {duration} seconds...")
        print("Speak into your microphone!")
        print("Volume meter will show below:")

        test_audio_device(device_id, duration)

    except Exception as e:
        print(f"❌ Error testing device: {e}")


@cli.command()
@click.argument("template_name")
@click.option("--output", "-o", default=None, help="Output file name")
def create_template(template_name, output):
    """Create a template file for quick start

    Available templates:
    - voice_assistant: Simple voice assistant (default experience)
    - file_processor: Process audio files (default experience)
    - conversation_tracker: Track conversations (controlled experience)
    - advanced_voice_assistant: Full control voice assistant (controlled experience)
    """

    templates = get_available_templates()

    if template_name not in templates:
        print(f"❌ Template '{template_name}' not found")
        print(f"Available templates: {', '.join(templates.keys())}")
        return

    if output is None:
        output = f"{template_name}_example.py"

    if Path(output).exists():
        if not click.confirm(f"File {output} exists. Overwrite?"):
            return

    with open(output, "w") as f:
        f.write(templates[template_name])

    print(f"✅ Template created: {output}")


@cli.command()
@click.option(
    "--output", "-o", default="config_report.txt", help="Output file for report"
)
def diagnose(output):
    """Generate diagnostic report"""

    print("🔍 Generating Diagnostic Report")
    print("=" * 50)

    report = generate_diagnostic_report()

    with open(output, "w") as f:
        f.write(report)

    print(f"✅ Diagnostic report saved to: {output}")
    print("\nSummary:")
    print(report.split("\n")[:10])  # Show first 10 lines


# Helper functions
def run_ui_demo():
    """Run the Gradio UI demo"""
    print("🌐 Launching Vocals SDK Web UI Demo")
    print("=" * 50)

    # Check if Gradio is installed
    try:
        import gradio

        print("✅ Gradio is already installed")
    except ImportError:
        print("📦 Gradio not found, installing...")

        # Install Gradio
        import subprocess
        import sys

        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "gradio"])
            print("✅ Gradio installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Gradio: {e}")
            print("Please install Gradio manually: pip install gradio")
            return

    # Find the Gradio example file
    example_file = None
    possible_paths = [
        "examples/example_gradio_voice_assistant.py",
        "example_gradio_voice_assistant.py",
        Path(__file__).parent.parent / "examples" / "example_gradio_voice_assistant.py",
    ]

    for path in possible_paths:
        if Path(path).exists():
            example_file = Path(path)
            break

    if not example_file:
        print("❌ Gradio example file not found")
        print("Expected location: examples/example_gradio_voice_assistant.py")
        return

    print(f"📂 Found Gradio example: {example_file}")
    print("🚀 Launching web interface...")
    print("📱 Your browser should open automatically")
    print("🎤 Click 'Start Assistant' in the web interface to begin")
    print("Press Ctrl+C to stop the web server")

    # Launch the Gradio example
    try:
        import subprocess
        import sys

        # Run the Gradio example
        subprocess.run([sys.executable, str(example_file)], check=True)

    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching Gradio demo: {e}")
        print("You can run the demo manually:")
        print(f"python {example_file}")
    except KeyboardInterrupt:
        print("\n👋 Web UI demo stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def list_audio_devices():
    """List available audio devices"""
    try:
        import sounddevice as sd

        devices = sd.query_devices()
        result: List[Dict[str, Any]] = []

        for i, device in enumerate(devices):
            # sounddevice returns a DeviceList of dictionaries
            if isinstance(device, dict):
                max_input_channels = device.get("max_input_channels", 0)
                device_name = device.get("name", "Unknown")
                sample_rate = device.get("default_samplerate", 44100)
            else:
                # Fallback for unexpected types
                max_input_channels = 0
                device_name = str(device)
                sample_rate = 44100

            # Only include devices with input channels
            if max_input_channels > 0:
                result.append(
                    {
                        "id": i,
                        "name": str(device_name),
                        "channels": int(max_input_channels),
                        "sample_rate": float(sample_rate),
                    }
                )

        return result
    except ImportError:
        raise Exception("sounddevice not installed")
    except Exception as e:
        raise Exception(f"Error querying audio devices: {e}")


def test_audio_device(device_id: int, duration: int = 5):
    """Test audio device with visual feedback"""
    try:
        import sounddevice as sd
        import numpy as np
        import time

        print(f"Testing device {device_id} for {duration} seconds...")

        def callback(indata, frames, time, status):
            volume = np.sqrt(np.mean(indata**2))
            bar_length = int(volume * 50)
            bar = "█" * bar_length + "░" * (50 - bar_length)
            print(f"\rVolume: [{bar}] {volume:.3f}", end="", flush=True)

        with sd.InputStream(callback=callback, device=device_id, channels=1):
            time.sleep(duration)

        print("\n✅ Device test completed")

    except Exception as e:
        print(f"\n❌ Error testing device: {e}")


def get_available_templates():
    """Get available code templates"""
    return {
        "voice_assistant": '''#!/usr/bin/env python3
"""
Voice Assistant Template
A simple voice assistant using Vocals SDK
"""

import asyncio
import logging
from vocals import VocalsClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def voice_assistant():
    """Main voice assistant function"""
    
    # Create SDK instance with default full experience
    # No modes = full auto-contained experience with automatic playback
    client =VocalsClient()
    
    try:
        print("🎤 Voice Assistant Started")
        print("Speak into your microphone...")
        print("Press Ctrl+C to stop")
        
        # Stream microphone (30 seconds)
        await clientstream_microphone(
            duration=30,
            auto_connect=True,  # Connects automatically since auto_connect defaults to False
            auto_playback=True,  # AI responses play automatically
            verbose=False
        )
        
    except KeyboardInterrupt:
        print("\\n👋 Voice assistant stopped")
    finally:
        await clientdisconnect()
        clientcleanup()

if __name__ == "__main__":
    asyncio.run(voice_assistant())
''',
        "file_processor": '''#!/usr/bin/env python3
"""
Audio File Processor Template
Process audio files with Vocals SDK
"""

import asyncio
import sys
from pathlib import Path
from vocals import VocalsClient

async def process_audio_file(file_path: str):
    """Process an audio file and get AI responses"""
    
    # Check if file exists
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return
    
    # Create SDK instance with default full experience
    # No modes = full auto-contained experience with automatic playback
    client =VocalsClient()
    
    try:
        print(f"🎵 Processing file: {file_path}")
        
        # Stream audio file
        await clientstream_audio_file(
            file_path=file_path,
            verbose=False,
            auto_connect=True  # Connects automatically since auto_connect defaults to False
        )
        
        # Wait for TTS playback to complete (playback is automatic in default mode)
        print("⏳ Waiting for AI response playback...")
        while clientis_playing:
            await asyncio.sleep(0.1)
        
        print("✅ File processing completed")
        
    except Exception as e:
        print(f"❌ Error processing file: {e}")
    finally:
        await clientdisconnect()
        clientcleanup()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python file_processor.py <audio_file.wav>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    asyncio.run(process_audio_file(file_path))
''',
        "conversation_tracker": '''#!/usr/bin/env python3
"""
Conversation Tracker Template
Track and analyze conversation with AI
"""

import asyncio
from vocals import (
    VocalsClient,
    create_conversation_tracker,
)

async def conversation_session():
    """Run a conversation session with tracking"""
    
    # Create SDK with controlled experience for custom tracking
    # Using modes disables automatic handlers - we implement custom ones
    client =VocalsClient(modes=['transcription', 'voice_assistant'])
    tracker = create_conversation_tracker()
    
    # Custom tracking handler with manual playback control
    def track_conversation(message):
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
                # Manually start playback since auto_playback=False
                asyncio.create_task(clientplay_audio())
        
        # Track conversation for analysis
        if message.type == "transcription" and message.data:
            text = message.data.get("text", "")
            is_partial = message.data.get("is_partial", False)
            if text:
                tracker["add_transcription"](text, is_partial)
                
        elif message.type == "llm_response" and message.data:
            response = message.data.get("response", "")
            if response:
                tracker["add_response"](response)
    
    # Register our custom handler
    clienton_message(track_conversation)
    
    try:
        print("💬 Conversation Session Started")
        print("Have a conversation with the AI...")
        print("Press Ctrl+C to stop and see analysis")
        
        # Run conversation with manual playback control
        await clientstream_microphone(
            duration=60,  # 1 minute
            auto_connect=True,  # Connects automatically since auto_connect defaults to False
            auto_playback=False,  # We control playback manually via our handler
            verbose=False
        )
        
    except KeyboardInterrupt:
        print("\\n📊 Conversation Analysis:")
        
    finally:
        # Print conversation history
        tracker["print_conversation"]()
        
        # Print statistics
        stats = tracker["get_stats"]()
        print(f"\\n📈 Session Statistics:")
        print(f"   Duration: {stats['duration']:.1f} seconds")
        print(f"   Exchanges: {stats['transcriptions'] + stats['responses']}")
        
        await clientdisconnect()
        clientcleanup()

if __name__ == "__main__":
    asyncio.run(conversation_session())
''',
        "advanced_voice_assistant": '''#!/usr/bin/env python3
"""
Advanced Voice Assistant Template
Full control over voice assistant behavior using controlled mode

This template demonstrates two approaches for handling audio:
1. Built-in audio playback (default) - uses SDK's built-in audio player
2. Custom audio processing - process audio segments with your own function

To switch between approaches, comment/uncomment the relevant sections
in the tts_audio message handler.
"""

import asyncio
import logging
from vocals import VocalsClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def advanced_voice_assistant():
    """Advanced voice assistant with full manual control"""
    
    # Create SDK with specific modes for controlled experience
    # Using modes disables all automatic handlers - we have complete control
    # This prevents duplicate message processing that would occur with default handlers
    client =VocalsClient(modes=['transcription', 'voice_assistant'])
    
    # Custom state tracking for conversation flow
    conversation_state = {
        'listening': False,
        'processing': False,
        'speaking': False
    }
    
    def handle_messages(message):
        """Custom message handler with complete control over all behavior"""
        
        if message.type == "transcription" and message.data:
            text = message.data.get("text", "")
            is_partial = message.data.get("is_partial", False)
            
            if is_partial:
                # Show live transcription updates
                print(f"\\r🎤 Listening: {text}...", end="", flush=True)
                conversation_state['listening'] = True
            else:
                # Final transcription result
                print(f"\\n✅ You said: {text}")
                conversation_state['listening'] = False
                conversation_state['processing'] = True
                
        elif message.type == "llm_response_streaming" and message.data:
            token = message.data.get("token", "")
            is_complete = message.data.get("is_complete", False)
            
            if not conversation_state['processing']:
                print("\\n💭 AI Thinking: ", end="", flush=True)
                conversation_state['processing'] = True
                
            if token:
                print(token, end="", flush=True)
                
            if is_complete:
                print()  # New line
                conversation_state['processing'] = False
                
        elif message.type == "tts_audio" and message.data:
            text = message.data.get("text", "")
            if text:
                # Only print the speaking message once per response
                if not conversation_state['speaking']:
                    print(f"🔊 AI speaking: {text}")
                    conversation_state['speaking'] = True
                
                # OPTION 1: Use built-in audio playback (current approach)
                # Manually trigger playback since auto_playback=False
                asyncio.create_task(clientplay_audio())
                
                # OPTION 2: Process audio queue with custom handler (new approach)
                # Uncomment the lines below to use custom audio processing instead
                # def my_custom_audio_handler(segment):
                #     print(f"🎵 Custom processing: {segment.text}")
                #     # Here you can:
                #     # - Save audio to file
                #     # - Send to external audio player
                #     # - Convert audio format
                #     # - Analyze audio data
                #     # - Or any other custom processing
                #     
                #     # Example: Save to file
                #     # import base64
                #     # audio_data = base64.b64decode(segment.audio_data)
                #     # filename = f"audio_{segment.segment_id}.wav"
                #     # with open(filename, 'wb') as f:
                #     #     f.write(audio_data)
                #     # print(f"💾 Saved to: {filename}")
                # 
                # # Process audio queue with custom handler
                # processed_count = clientprocess_audio_queue(
                #     my_custom_audio_handler, 
                #     consume_all=True
                # )
                # print(f"✅ Processed {processed_count} audio segments")
                
        elif message.type == "speech_interruption":
            print("\\n🛑 Speech interrupted")
            conversation_state['speaking'] = False
    
    # Register our custom message handler
    clienton_message(handle_messages)
    
    # Custom connection handler
    def handle_connection(state):
        if state.name == "CONNECTED":
            print("✅ Connected to voice assistant")
        elif state.name == "DISCONNECTED":
            print("❌ Disconnected from voice assistant")
    
    clienton_connection_change(handle_connection)
    
    try:
        print("🎤 Advanced Voice Assistant Started")
        print("Full control mode - custom handlers active")
        print("Features: live transcription, streaming responses, manual playback")
        print("Speak into your microphone...")
        print("Press Ctrl+C to stop")
        
        # Stream microphone with complete manual control
        await clientstream_microphone(
            duration=0,  # Infinite recording
            auto_connect=True,  # Connects automatically since auto_connect defaults to False
            auto_playback=False,  # We have complete manual control over playback
            verbose=False
        )
        
    except KeyboardInterrupt:
        print("\\n👋 Advanced voice assistant stopped")
    finally:
        await clientdisconnect()
        clientcleanup()

if __name__ == "__main__":
    asyncio.run(advanced_voice_assistant())
''',
        "gradio_demo": '''#!/usr/bin/env python3
"""
Gradio Demo Template
A simple demo using Gradio to interact with the Vocals SDK
"""
#!/usr/bin/env python3
"""
Advanced Voice Assistant with Gradio Interface
Real-time voice assistant with web interface using Gradio

This interface provides:
- Real-time audio streaming
- Live transcription updates
- Streaming AI responses
- Visual status indicators
- Manual control over all voice assistant behavior
"""

import asyncio
import logging
import threading
import time
from typing import Optional, Generator, Union
from concurrent.futures import TimeoutError
import gradio as gr
from vocals import VocalsClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GradioVoiceAssistant:
    """Advanced voice assistant with Gradio web interface"""

    def __init__(self):
        self.sdk: Optional[VocalsClient] = None
        self.conversation_state = {
            "listening": False,
            "processing": False,
            "speaking": False,
            "connected": False,
        }
        self.current_transcription = ""
        self.current_response = ""
        self.conversation_log = []  # Store conversation history
        self.status_message = "Ready to start"
        self.audio_queue = []
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.stop_event: Optional[asyncio.Event] = None

    async def initialize_sdk(self):
        """Initialize the voice assistant SDK"""
        if self.sdk is None:
            self.sdk = VocalsClient(modes=["transcription", "voice_assistant"])

            # Register message handler
            self.sdk.on_message(self.handle_messages)

            # Register connection handler
            self.sdk.on_connection_change(self.handle_connection)

    def handle_messages(self, message):
        """Handle all voice assistant messages"""
        # Skip processing if not running
        if not self.running:
            logger.debug("Skipping message processing - assistant not running")
            return

        if message.type == "transcription" and message.data:
            text = message.data.get("text", "")
            is_partial = message.data.get("is_partial", False)

            if is_partial:
                self.current_transcription = f"🎤 Listening: {text}..."
                self.conversation_state["listening"] = True
            else:
                # Clear the current response when we get a new complete transcription
                self.current_response = ""

                self.current_transcription = f"✅ You said: {text}"
                self.conversation_state["listening"] = False
                self.conversation_state["processing"] = True

                # Add user message to conversation log
                if text.strip():
                    self.conversation_log.append(
                        {
                            "type": "user",
                            "message": text,
                            "timestamp": time.strftime("%H:%M:%S"),
                        }
                    )

        elif message.type == "llm_response_streaming" and message.data:
            token = message.data.get("token", "")
            is_complete = message.data.get("is_complete", False)

            if not self.conversation_state["processing"]:
                self.current_response = "💭 AI Thinking: "
                self.conversation_state["processing"] = True

            if token:
                self.current_response += token

            if is_complete:
                self.conversation_state["processing"] = False

                # Add AI response to conversation log (remove the "💭 AI Thinking: " part)
                clean_response = self.current_response.replace("💭 AI Thinking: ", "")
                if clean_response.strip():
                    self.conversation_log.append(
                        {
                            "type": "assistant",
                            "message": clean_response,
                            "timestamp": time.strftime("%H:%M:%S"),
                        }
                    )

        elif message.type == "tts_audio" and message.data:
            text = message.data.get("text", "")
            if text:
                if not self.conversation_state["speaking"]:
                    self.status_message = f"🔊 AI speaking"
                    self.conversation_state["speaking"] = True

                # Use built-in audio playback - only if we're still running
                if self.sdk and self.running:
                    try:
                        # Check if we have a valid event loop
                        if self.loop and not self.loop.is_closed():
                            asyncio.run_coroutine_threadsafe(
                                self.sdk.play_audio(), self.loop
                            )
                        else:
                            logger.warning(
                                "Cannot play audio: event loop not available"
                            )
                    except Exception as e:
                        logger.error(f"Error playing audio: {e}")

        elif message.type == "speech_interruption":
            self.status_message = "🛑 Speech interrupted"
            self.conversation_state["speaking"] = False

    def handle_connection(self, state):
        """Handle connection state changes"""
        if state.name == "CONNECTED":
            self.status_message = "✅ Connected to voice assistant"
            self.conversation_state["connected"] = True
        elif state.name == "DISCONNECTED":
            self.status_message = "❌ Disconnected from voice assistant"
            self.conversation_state["connected"] = False

    async def start_streaming(self):
        """Start the voice assistant streaming"""
        if not self.running:
            self.running = True
            self.stop_event = asyncio.Event()
            await self.initialize_sdk()

            try:
                if self.sdk:
                    logger.info("Starting microphone streaming...")
                    # Start streaming with proper cleanup handling
                    streaming_task = asyncio.create_task(
                        self.sdk.stream_microphone(
                            duration=0,  # Infinite recording
                            auto_connect=True,
                            auto_playback=False,  # Manual control
                            verbose=False,
                        )
                    )

                    # Wait for either completion or stop signal
                    done, pending = await asyncio.wait(
                        [streaming_task, asyncio.create_task(self.stop_event.wait())],
                        return_when=asyncio.FIRST_COMPLETED,
                    )

                    # Cancel any remaining tasks
                    for task in pending:
                        logger.info(f"Cancelling pending task: {task}")
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            logger.info("Task cancelled successfully")
                            pass
                        except Exception as e:
                            logger.error(f"Error while cancelling task: {e}")

                    # Check if streaming task completed with an error
                    if streaming_task in done:
                        try:
                            result = streaming_task.result()
                            logger.info(f"Streaming task completed: {result}")
                        except Exception as e:
                            logger.error(f"Streaming task failed: {e}")

            except Exception as e:
                logger.error(f"Error in streaming: {e}")
                self.status_message = f"❌ Error: {str(e)}"
                self.running = False
            finally:
                logger.info("start_streaming finished")

    async def stop_streaming(self):
        """Stop the voice assistant streaming"""
        if self.running:
            logger.info("Initiating stop_streaming...")
            self.running = False

            # Signal stop event if it exists
            if self.stop_event:
                self.stop_event.set()

            # Clean up SDK with proper sequencing
            if self.sdk:
                try:
                    logger.info("Disconnecting SDK...")
                    await self.sdk.disconnect()

                    # Give a moment for any pending operations to complete
                    await asyncio.sleep(0.5)

                    logger.info("Cleaning up SDK...")
                    self.sdk.cleanup()

                except Exception as e:
                    logger.error(f"Error during SDK cleanup: {e}")
                finally:
                    self.sdk = None

            # Wait a bit more for any remaining operations to finish
            await asyncio.sleep(0.2)

            self.status_message = "👋 Voice assistant stopped"
            logger.info("stop_streaming completed")

    def get_status(self) -> tuple:
        """Get current status for Gradio updates"""
        # Format conversation log for display
        conversation_text = ""
        for entry in self.conversation_log[-10:]:  # Show last 10 entries
            if entry["type"] == "user":
                conversation_text += (
                    f"[{entry['timestamp']}] 👤 You: {entry['message']}\n\n"
                )
            else:
                conversation_text += (
                    f"[{entry['timestamp']}] 🤖 AI: {entry['message']}\n\n"
                )

        return (
            self.current_transcription,
            self.current_response,
            conversation_text,
            self.status_message,
            self.conversation_state["connected"],
        )

    def clear_conversation(self):
        """Clear the conversation log"""
        self.conversation_log = []
        self.current_transcription = ""
        self.current_response = ""


# Global instance
assistant = GradioVoiceAssistant()


def start_assistant():
    """Start the voice assistant in a separate thread"""

    def run_async():
        # Create and set the event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        assistant.loop = loop

        try:
            loop.run_until_complete(assistant.start_streaming())
        except Exception as e:
            logger.error(f"Error in async run: {e}")
        finally:
            # Wait a bit for any pending operations to complete
            try:
                # Give time for any remaining operations to finish
                remaining_tasks = [
                    task for task in asyncio.all_tasks(loop) if not task.done()
                ]
                if remaining_tasks:
                    logger.info(
                        f"Waiting for {len(remaining_tasks)} remaining tasks to complete..."
                    )
                    # Wait for remaining tasks with a timeout
                    loop.run_until_complete(
                        asyncio.wait_for(
                            asyncio.gather(*remaining_tasks, return_exceptions=True),
                            timeout=2.0,
                        )
                    )
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning(f"Some tasks didn't complete cleanly: {e}")
                # Cancel any remaining tasks
                for task in asyncio.all_tasks(loop):
                    if not task.done():
                        task.cancel()

            # Clean up the loop
            try:
                loop.close()
            except Exception as e:
                logger.error(f"Error closing loop: {e}")
            finally:
                assistant.loop = None

    if not assistant.running:
        assistant.thread = threading.Thread(target=run_async, daemon=True)
        assistant.thread.start()
        return "🚀 Starting voice assistant...", True
    else:
        return "⚠️ Assistant already running", assistant.conversation_state["connected"]


def stop_assistant():
    """Stop the voice assistant"""
    if assistant.running:
        logger.info("Stopping voice assistant...")

        # Use the original event loop if it exists and is running
        if (
            assistant.loop
            and not assistant.loop.is_closed()
            and assistant.loop.is_running()
        ):
            logger.info("Using original event loop for graceful shutdown")
            try:
                # Schedule the stop_streaming coroutine on the original loop
                future = asyncio.run_coroutine_threadsafe(
                    assistant.stop_streaming(), assistant.loop
                )

                # Wait for the coroutine to complete
                future.result(timeout=10.0)  # Increased timeout

                logger.info("Graceful shutdown completed")

            except (TimeoutError, Exception) as e:
                logger.error(f"Error during graceful stop: {e}")
                # Fall through to fallback cleanup
        else:
            logger.info("Event loop not available, using fallback cleanup")

        # Wait for the thread to complete
        if assistant.thread and assistant.thread.is_alive():
            logger.info("Waiting for thread to complete...")
            assistant.thread.join(timeout=10.0)  # Increased timeout
            if assistant.thread.is_alive():
                logger.warning("Thread did not complete within timeout")

        # Always ensure cleanup happens (either first time or after graceful stop fails)
        if assistant.running:
            logger.info("Performing fallback cleanup")
            # Fallback: force stop if loop is not available or graceful stop failed
            assistant.running = False
            if assistant.sdk:
                try:
                    assistant.sdk.cleanup()
                except Exception as e:
                    logger.error(f"Error during fallback cleanup: {e}")
                finally:
                    assistant.sdk = None
            assistant.status_message = "🛑 Voice assistant stopped"

        return "🛑 Voice assistant stopped", False
    else:
        return "⚠️ Assistant not running", False


def clear_conversation():
    """Clear the conversation log"""
    assistant.clear_conversation()
    return "", "", "🧹 Conversation cleared"


def get_real_time_updates() -> Generator[tuple, None, None]:
    """Generator for real-time updates"""
    while True:
        if assistant.running:
            transcription, response, conversation_log, status, connected = (
                assistant.get_status()
            )
            yield transcription, response, conversation_log, status, connected
        else:
            yield "", "", "", "Ready to start", False
        time.sleep(0.1)  # Update every 100ms


def create_interface():
    """Create the Gradio interface"""
    with gr.Blocks(
        title="Advanced Voice Assistant",
        css="""
        .status-connected { color: green; font-weight: bold; }
        .status-disconnected { color: red; font-weight: bold; }
        .transcription-box { border: 2px solid #4CAF50; }
        .response-box { border: 2px solid #2196F3; }
        .conversation-log { border: 2px solid #9C27B0; background-color: #f8f9fa; }
        """,
    ) as interface:

        gr.Markdown(
            """
        # 🎤 Advanced Voice Assistant
        
        Real-time voice assistant with complete manual control over transcription, 
        AI responses, and audio playback.
        
        **Features:**
        - ✅ Real-time transcription with response clearing
        - 🤖 Streaming AI responses  
        - 📜 Back-and-forth conversation log
        - 🔊 Manual audio playback control
        - 🎯 Full conversation state tracking
        """
        )

        with gr.Row():
            with gr.Column(scale=1):
                start_btn = gr.Button(
                    "🚀 Start Assistant", variant="primary", size="lg"
                )
                stop_btn = gr.Button(
                    "🛑 Stop Assistant", variant="secondary", size="lg"
                )
                clear_btn = gr.Button(
                    "🧹 Clear Conversation", variant="secondary", size="lg"
                )

            with gr.Column(scale=2):
                status_display = gr.Textbox(
                    label="Status",
                    value="Ready to start",
                    interactive=False,
                    elem_classes=["status-disconnected"],
                )

        with gr.Row():
            with gr.Column():
                transcription_display = gr.Textbox(
                    label="🎤 Live Transcription",
                    placeholder="Your speech will appear here...",
                    lines=3,
                    interactive=False,
                    elem_classes=["transcription-box"],
                )

            with gr.Column():
                response_display = gr.Textbox(
                    label="🤖 AI Response",
                    placeholder="AI responses will appear here...",
                    lines=3,
                    interactive=False,
                    elem_classes=["response-box"],
                )

        with gr.Row():
            conversation_log_display = gr.Textbox(
                label="💬 Conversation Log",
                placeholder="Your conversation history will appear here...",
                lines=10,
                interactive=False,
                elem_classes=["conversation-log"],
            )

        gr.Markdown(
            """
        ### 📋 Instructions:
        1. Click **Start Assistant** to begin
        2. **Speak into your microphone** - you'll see live transcription
        3. **Wait for AI response** - responses stream in real-time
        4. **Listen to AI speech** - audio plays automatically
        5. **View conversation log** - see your back-and-forth conversation
        6. Click **Clear Conversation** to reset the log
        7. Click **Stop Assistant** when done
        
        ### 🔧 Technical Details:
        - Uses VocalsClient with manual control modes
        - Real-time updates every 100ms
        - Complete control over transcription, LLM, and TTS
        - Supports speech interruption detection
        - Response clears automatically when new transcription starts
        - Conversation log shows last 10 exchanges with timestamps
        """
        )

        # Event handlers
        start_btn.click(fn=start_assistant, outputs=[status_display, gr.State()])

        stop_btn.click(fn=stop_assistant, outputs=[status_display, gr.State()])

        clear_btn.click(
            fn=clear_conversation,
            outputs=[
                transcription_display,
                response_display,
                status_display,
            ],
        )

        # Real-time updates using a timer approach
        def update_interface():
            if assistant.running:
                transcription, response, conversation_log, status, connected = (
                    assistant.get_status()
                )
                return transcription, response, conversation_log, status
            else:
                return "", "", "", "Ready to start"

        # Create a timer-based update mechanism
        timer = gr.Timer(0.1)  # Update every 100ms
        timer.tick(
            fn=update_interface,
            outputs=[
                transcription_display,
                response_display,
                conversation_log_display,
                status_display,
            ],
        )

    return interface


if __name__ == "__main__":
    # Create and launch the interface
    interface = create_interface()

    print("🌐 Launching Gradio Voice Assistant Interface...")
    print("📱 The interface will open in your browser")
    print("🎤 Click 'Start Assistant' to begin voice interaction")

    interface.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,  # Default Gradio port
        share=False,  # Set to True for public sharing
        debug=True,  # Enable debug mode
        show_error=True,  # Show errors in interface
        inbrowser=True,  # Auto-open browser
    )
        ''',
    }


def generate_diagnostic_report():
    """Generate a diagnostic report"""
    import platform
    import sys

    report = f"""Vocals SDK Diagnostic Report
Generated: {__import__('datetime').datetime.now()}

System Information:
- Platform: {platform.platform()}
- Python Version: {sys.version}
- Python Path: {sys.executable}

Environment Variables:
- VOCALS_DEV_API_KEY: {'SET' if os.environ.get('VOCALS_DEV_API_KEY') else 'NOT SET'}
- VOCALS_WS_ENDPOINT: {os.environ.get('VOCALS_WS_ENDPOINT', 'NOT SET')}

Dependencies:
"""

    # Check dependencies
    deps_to_check = [
        "sounddevice",
        "numpy",
        "websockets",
        "aiohttp",
        "PyJWT",
        "python-dotenv",
        "click",
    ]

    for dep in deps_to_check:
        try:
            __import__(dep)
            report += f"- {dep}: ✅ Installed\n"
        except ImportError:
            report += f"- {dep}: ❌ Missing\n"

    # Check audio devices
    report += "\nAudio Devices:\n"
    try:
        devices = list_audio_devices()
        for device in devices:
            report += (
                f"- {device['id']}: {device['name']} ({device['channels']} channels)\n"
            )
    except Exception as e:
        report += f"- Error: {e}\n"

    return report


class VocalsSDKTester:
    """Test framework for SDK functionality"""

    def __init__(self):
        self.results = []

    async def test_connection(self):
        """Test WebSocket connection"""
        try:
            from .client import VocalsClient

            client = VocalsClient()
            await client.connect()
            connected = client.is_connected
            await client.disconnect()

            self.results.append(
                ("WebSocket Connection", "✅ PASS" if connected else "❌ FAIL")
            )
            return connected
        except Exception as e:
            self.results.append(("WebSocket Connection", f"❌ ERROR: {e}"))
            return False

    async def test_audio_recording(self):
        """Test audio recording functionality"""
        try:
            from .client import VocalsClient

            client = VocalsClient()
            await client.start_recording()
            await asyncio.sleep(0.5)
            recording = client.is_recording
            await client.stop_recording()

            self.results.append(
                ("Audio Recording", "✅ PASS" if recording else "❌ FAIL")
            )
            return recording
        except Exception as e:
            self.results.append(("Audio Recording", f"❌ ERROR: {e}"))
            return False

    def test_configuration(self):
        """Test configuration"""
        try:
            issues = validate_config()
            if not issues:
                self.results.append(("Configuration", "✅ PASS"))
                return True
            else:
                self.results.append(
                    ("Configuration", f"❌ ISSUES: {', '.join(issues)}")
                )
                return False
        except Exception as e:
            self.results.append(("Configuration", f"❌ ERROR: {e}"))
            return False

    def test_audio_devices(self):
        """Test audio device availability"""
        try:
            devices = list_audio_devices()
            if devices:
                self.results.append(
                    ("Audio Devices", f"✅ {len(devices)} devices found")
                )
                return True
            else:
                self.results.append(("Audio Devices", "❌ No input devices found"))
                return False
        except Exception as e:
            self.results.append(("Audio Devices", f"❌ ERROR: {e}"))
            return False

    def print_results(self):
        """Print test results"""
        print("\n🧪 Test Results:")
        print("=" * 50)
        for test, result in self.results:
            print(f"{test}: {result}")


def validate_config() -> List[str]:
    """Validate configuration and return issues"""
    issues = []

    # Check API key
    api_key = os.environ.get("VOCALS_DEV_API_KEY")
    if not api_key:
        issues.append("VOCALS_DEV_API_KEY not set")
    elif not api_key.startswith("vdev_"):
        issues.append("Invalid API key format")

    # Check audio system
    try:
        import sounddevice as sd

        sd.query_devices()
    except ImportError:
        issues.append("sounddevice not installed")
    except Exception as e:
        issues.append(f"Audio system error: {e}")

    # Check WebSocket endpoint
    endpoint = os.environ.get("VOCALS_WS_ENDPOINT")
    if endpoint and not endpoint.startswith("ws"):
        issues.append("Invalid WebSocket endpoint format")

    return issues


if __name__ == "__main__":
    cli()
