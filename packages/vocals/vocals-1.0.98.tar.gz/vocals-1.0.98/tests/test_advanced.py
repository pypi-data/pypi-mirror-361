#!/usr/bin/env python3
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

    # Create SDK client with specific modes for controlled experience
    # Using modes disables all automatic handlers - we have complete control
    # This prevents duplicate message processing that would occur with default handlers
    client = VocalsClient(modes=["transcription", "voice_assistant"])

    # Custom state tracking for conversation flow
    conversation_state = {"listening": False, "processing": False, "speaking": False}

    def handle_messages(message):
        """Custom message handler with complete control over all behavior"""

        if message.type == "transcription" and message.data:
            text = message.data.get("text", "")
            is_partial = message.data.get("is_partial", False)

            if is_partial:
                # Show live transcription updates
                print(f"\r🎤 Listening: {text}...", end="", flush=True)
                conversation_state["listening"] = True
            else:
                # Final transcription result
                print(f"\n✅ You said: {text}")
                conversation_state["listening"] = False
                conversation_state["processing"] = True

        elif message.type == "llm_response_streaming" and message.data:
            token = message.data.get("token", "")
            is_complete = message.data.get("is_complete", False)

            if not conversation_state["processing"]:
                print("\n💭 AI Thinking: ", end="", flush=True)
                conversation_state["processing"] = True

            if token:
                print(token, end="", flush=True)

            if is_complete:
                print()  # New line
                conversation_state["processing"] = False

        elif message.type == "tts_audio" and message.data:
            text = message.data.get("text", "")
            if text and not conversation_state["speaking"]:
                print(f"🔊 AI speaking: {text}")
                conversation_state["speaking"] = True

                # OPTION 1: Use built-in audio playback (current approach)
                # Manually trigger playback since auto_playback=False
                asyncio.create_task(client.play_audio())

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
                #     pass
                #
                # # Process audio queue with custom handler
                # processed_count = client.process_audio_queue(
                #     my_custom_audio_handler,
                #     consume_all=True
                # )
                # print(f"✅ Processed {processed_count} audio segments")

        elif message.type == "speech_interruption":
            print("\n🛑 Speech interrupted")
            conversation_state["speaking"] = False

    # Register our custom message handler
    client.on_message(handle_messages)

    # Custom connection handler
    def handle_connection(state):
        if state.name == "CONNECTED":
            print("✅ Connected to voice assistant")
        elif state.name == "DISCONNECTED":
            print("❌ Disconnected from voice assistant")

    client.on_connection_change(handle_connection)

    try:
        print("🎤 Advanced Voice Assistant Started")
        print("Full control mode - custom handlers active")
        print("Features: live transcription, streaming responses, manual playback")
        print("Speak into your microphone...")
        print("Press Ctrl+C to stop")

        # Stream microphone with complete manual control
        await client.stream_microphone(
            duration=0,  # Infinite recording
            auto_connect=True,  # Connects automatically since auto_connect defaults to False
            auto_playback=False,  # We have complete manual control over playback
            verbose=False,
        )

    except KeyboardInterrupt:
        print("\n👋 Advanced voice assistant stopped")
    finally:
        await client.disconnect()
        client.cleanup()


async def context_manager_advanced_example():
    """Advanced voice assistant using the new async context manager"""

    # Custom state tracking for conversation flow
    conversation_state = {"listening": False, "processing": False, "speaking": False}

    def handle_messages(message):
        """Custom message handler with complete control over all behavior"""

        if message.type == "transcription" and message.data:
            text = message.data.get("text", "")
            is_partial = message.data.get("is_partial", False)

            if is_partial:
                # Show live transcription updates
                print(f"\r🎤 Listening: {text}...", end="", flush=True)
                conversation_state["listening"] = True
            else:
                # Final transcription result
                print(f"\n✅ You said: {text}")
                conversation_state["listening"] = False
                conversation_state["processing"] = True

        elif message.type == "llm_response_streaming" and message.data:
            token = message.data.get("token", "")
            is_complete = message.data.get("is_complete", False)

            if not conversation_state["processing"]:
                print("\n💭 AI Thinking: ", end="", flush=True)
                conversation_state["processing"] = True

            if token:
                print(token, end="", flush=True)

            if is_complete:
                print()  # New line
                conversation_state["processing"] = False

        elif message.type == "tts_audio" and message.data:
            text = message.data.get("text", "")
            if text and not conversation_state["speaking"]:
                print(f"🔊 AI speaking: {text}")
                conversation_state["speaking"] = True

        elif message.type == "speech_interruption":
            print("\n🛑 Speech interrupted")
            conversation_state["speaking"] = False

    # Use the new async context manager with controlled mode
    async with VocalsClient(modes=["transcription", "voice_assistant"]) as client:
        print("🎤 Advanced Voice Assistant Started (Context Manager)")
        print("Connection and cleanup handled automatically!")
        print("Features: live transcription, streaming responses")
        print("Speak into your microphone...")
        print("Press Ctrl+C to stop")

        # Register our custom message handler
        client.on_message(handle_messages)

        # Custom connection handler
        def handle_connection(state):
            if state.name == "CONNECTED":
                print("✅ Connected to voice assistant")
            elif state.name == "DISCONNECTED":
                print("❌ Disconnected from voice assistant")

        client.on_connection_change(handle_connection)

        try:
            # Stream microphone with complete manual control
            await client.stream_microphone(
                duration=30,  # 30 seconds for demo
                auto_connect=False,  # Already connected by context manager
                auto_playback=True,  # Let SDK handle playback
                verbose=False,
            )

        except KeyboardInterrupt:
            print("\n👋 Advanced voice assistant stopped")

    print("🔌 Disconnected automatically via context manager")


async def property_access_demo():
    """Demonstrate the new property-based access"""

    client = VocalsClient(modes=["transcription", "voice_assistant"])

    try:
        print("🎤 Property Access Demo")
        print("=" * 40)

        # Show initial state using properties
        print(f"Initial connection state: {client.connection_state}")
        print(f"Is connected: {client.is_connected}")
        print(f"Is recording: {client.is_recording}")
        print(f"Audio queue length: {len(client.audio_queue)}")

        # Connect and show updated state
        await client.connect()
        print(f"After connect - Is connected: {client.is_connected}")
        print(f"Connection state: {client.connection_state}")

        # Start recording and show recording state
        await client.start_recording()
        print(f"After start recording - Is recording: {client.is_recording}")
        print(f"Recording state: {client.recording_state}")

        # Show live amplitude for a few seconds
        print("\nLive amplitude monitoring:")
        for i in range(10):
            amplitude = client.current_amplitude
            print(f"🔊 Amplitude: {amplitude:.4f}")
            await asyncio.sleep(0.5)

        # Stop recording
        await client.stop_recording()
        print(f"After stop recording - Is recording: {client.is_recording}")
        print(f"Recording state: {client.recording_state}")

        # Show final audio queue
        print(f"Final audio queue length: {len(client.audio_queue)}")

    finally:
        await client.disconnect()
        client.cleanup()


if __name__ == "__main__":
    print("Choose an advanced example:")
    print("1. Advanced voice assistant (traditional)")
    print("2. Advanced voice assistant (context manager)")
    print("3. Property access demo")

    choice = input("Enter choice (1-3): ").strip()

    try:
        if choice == "1":
            asyncio.run(advanced_voice_assistant())
        elif choice == "2":
            asyncio.run(context_manager_advanced_example())
        elif choice == "3":
            asyncio.run(property_access_demo())
        else:
            print("Invalid choice, running traditional advanced example")
            asyncio.run(advanced_voice_assistant())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Error: {e}")
        import sys

        sys.exit(1)
