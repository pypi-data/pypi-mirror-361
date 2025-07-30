#!/usr/bin/env python3
"""
Advanced Voice Assistant Template - Custom Audio Processing
Full control over voice assistant behavior using controlled mode

This template demonstrates custom audio processing - how to process audio segments 
with your own function instead of using the built-in audio playback.
"""

import asyncio
import logging
from vocals import VocalsClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def advanced_voice_assistant():
    """Advanced voice assistant with full manual control and custom audio processing"""

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
            if text:
                # Only print the speaking message once per response
                if not conversation_state["speaking"]:
                    print(f"🔊 AI speaking: {text}")
                    conversation_state["speaking"] = True

                # OPTION 2: Process audio queue with custom handler (new approach)
                # Process each segment as it arrives
                def my_custom_audio_handler(segment):
                    print(f"🎵 Custom processing: {segment.text}")
                    # Here you can:
                    # - Save audio to file
                    # - Send to external audio player
                    # - Convert audio format
                    # - Analyze audio data
                    # - Or any other custom processing

                    # Example: Save to file
                    import base64

                    audio_data = base64.b64decode(segment.audio_data)
                    filename = f"audio_{segment.segment_id}.wav"
                    with open(filename, "wb") as f:
                        f.write(audio_data)
                    print(f"💾 Saved to: {filename}")

                # Process audio queue with custom handler
                processed_count = client.process_audio_queue(
                    my_custom_audio_handler, consume_all=True
                )
                print(f"✅ Processed {processed_count} audio segments")

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
        print("🎤 Advanced Voice Assistant Started - Custom Audio Processing")
        print("Full control mode - custom handlers active")
        print(
            "Features: live transcription, streaming responses, custom audio processing"
        )
        print("Audio segments will be saved to files instead of played")
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


async def context_manager_custom_audio_example():
    """Advanced voice assistant with custom audio processing using context manager"""

    # Custom state tracking for conversation flow
    conversation_state = {"listening": False, "processing": False, "speaking": False}

    def handle_messages(message):
        """Custom message handler with custom audio processing"""

        if message.type == "transcription" and message.data:
            text = message.data.get("text", "")
            is_partial = message.data.get("is_partial", False)

            if is_partial:
                print(f"\r🎤 Listening: {text}...", end="", flush=True)
                conversation_state["listening"] = True
            else:
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
        print("🎤 Advanced Voice Assistant Started (Context Manager + Custom Audio)")
        print("Connection and cleanup handled automatically!")
        print(
            "Features: live transcription, streaming responses, custom audio processing"
        )
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
                auto_playback=False,  # We'll handle audio processing manually
                verbose=False,
            )

            # Process any remaining audio in the queue using property access
            if client.audio_queue:
                print(
                    f"\n🎵 Processing {len(client.audio_queue)} remaining audio segments..."
                )

                def final_audio_handler(segment):
                    print(f"🎵 Final processing: {segment.text}")
                    import base64

                    audio_data = base64.b64decode(segment.audio_data)
                    filename = f"final_audio_{segment.segment_id}.wav"
                    with open(filename, "wb") as f:
                        f.write(audio_data)
                    print(f"💾 Saved final audio to: {filename}")

                processed_count = client.process_audio_queue(
                    final_audio_handler, consume_all=True
                )
                print(f"✅ Processed {processed_count} final audio segments")

        except KeyboardInterrupt:
            print("\n👋 Advanced voice assistant stopped")

    print("🔌 Disconnected automatically via context manager")


async def audio_queue_monitoring_demo():
    """Demonstrate real-time audio queue monitoring using properties"""

    client = VocalsClient(modes=["transcription", "voice_assistant"])

    try:
        print("🎤 Audio Queue Monitoring Demo")
        print("=" * 40)
        print("This demo shows real-time monitoring of the audio queue")
        print("using the new property-based access.")
        print()

        # Connect and start recording
        await client.connect()
        await client.start_recording()

        # Monitor the audio queue in real-time
        print("🎙️ Recording started. Monitoring audio queue...")
        print("Speak into your microphone to see queue changes!")

        # Custom handler to see when audio arrives
        def queue_monitor_handler(message):
            if message.type == "tts_audio" and message.data:
                text = message.data.get("text", "")
                print(f"🔊 New audio segment: {text}")
                print(f"📊 Queue length: {len(client.audio_queue)}")
                print(f"🎵 Current segment: {client.current_segment}")
                print(f"▶️ Is playing: {client.is_playing}")
                print()

        client.on_message(queue_monitor_handler)

        # Record for 20 seconds while monitoring
        for i in range(20):
            await asyncio.sleep(1)

            # Show current state every few seconds
            if i % 3 == 0:
                print(
                    f"⏰ Time: {i}s | Queue: {len(client.audio_queue)} | Playing: {client.is_playing}"
                )

        # Stop recording
        await client.stop_recording()
        print("🛑 Recording stopped")

        # Show final queue state
        print(f"📊 Final queue length: {len(client.audio_queue)}")
        if client.audio_queue:
            print("🎵 Processing remaining audio segments...")

            def final_processor(segment):
                print(f"  - {segment.text} (ID: {segment.segment_id})")

            processed = client.process_audio_queue(final_processor, consume_all=True)
            print(f"✅ Processed {processed} segments")

    finally:
        await client.disconnect()
        client.cleanup()


if __name__ == "__main__":
    print("Choose an advanced custom audio example:")
    print("1. Advanced voice assistant with custom audio processing")
    print("2. Context manager with custom audio processing")
    print("3. Audio queue monitoring demo")

    choice = input("Enter choice (1-3): ").strip()

    try:
        if choice == "1":
            asyncio.run(advanced_voice_assistant())
        elif choice == "2":
            asyncio.run(context_manager_custom_audio_example())
        elif choice == "3":
            asyncio.run(audio_queue_monitoring_demo())
        else:
            print("Invalid choice, running traditional advanced example")
            asyncio.run(advanced_voice_assistant())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Error: {e}")
        import sys

        sys.exit(1)
