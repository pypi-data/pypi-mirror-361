#!/usr/bin/env python3
"""
Test script to verify that auto_playback=False works correctly using the new class-based API
"""

import asyncio
import logging
from vocals import VocalsClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_auto_playback_false():
    """Test that auto_playback=False prevents automatic playback"""

    # Create SDK client with controlled experience
    client = VocalsClient(modes=["transcription", "voice_assistant"])

    # Flag to track if playback was triggered automatically
    playback_triggered = False

    def handle_messages(message):
        """Custom message handler that tracks playback"""
        nonlocal playback_triggered

        if message.type == "transcription" and message.data:
            text = message.data.get("text", "")
            is_partial = message.data.get("is_partial", False)
            if not is_partial and text:
                print(f"🎤 You said: {text}")

        elif message.type == "llm_response" and message.data:
            response = message.data.get("response", "")
            if response:
                print(f"🤖 AI: {response}")

        elif message.type == "tts_audio" and message.data:
            text = message.data.get("text", "")
            if text:
                print(f"🔊 TTS received: {text}")

                # Check if playback was triggered automatically using property access
                if client.is_playing:
                    playback_triggered = True
                    print("❌ PROBLEM: Playback was triggered automatically!")
                else:
                    print("✅ Good: No automatic playback triggered")
                    print("🎵 Manually starting playback...")
                    asyncio.create_task(client.play_audio())

    # Register message handler
    client.on_message(handle_messages)

    try:
        print("🧪 Testing auto_playback=False with Class-Based API")
        print("This should NOT trigger automatic playback")
        print("Speak into your microphone...")

        # Stream microphone with auto_playback=False
        await client.stream_microphone(
            duration=10,  # 10 seconds
            auto_connect=True,
            auto_playback=False,  # This should prevent automatic playback
            verbose=False,
        )

        if not playback_triggered:
            print("✅ Test PASSED: No automatic playback detected")
        else:
            print("❌ Test FAILED: Automatic playback was triggered")

    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    finally:
        await client.disconnect()
        client.cleanup()


async def test_auto_playback_true():
    """Test that auto_playback=True enables automatic playback"""

    # Create SDK client with controlled experience
    client = VocalsClient(modes=["transcription", "voice_assistant"])

    # Flag to track if playback was triggered automatically
    playback_triggered = False

    def handle_messages(message):
        """Custom message handler that tracks playback"""
        nonlocal playback_triggered

        if message.type == "transcription" and message.data:
            text = message.data.get("text", "")
            is_partial = message.data.get("is_partial", False)
            if not is_partial and text:
                print(f"🎤 You said: {text}")

        elif message.type == "llm_response" and message.data:
            response = message.data.get("response", "")
            if response:
                print(f"🤖 AI: {response}")

        elif message.type == "tts_audio" and message.data:
            text = message.data.get("text", "")
            if text:
                print(f"🔊 TTS received: {text}")

                # Give it a moment for auto-playback to trigger
                asyncio.create_task(check_playback_after_delay())

    async def check_playback_after_delay():
        """Check if playback started after a short delay"""
        nonlocal playback_triggered
        await asyncio.sleep(0.5)  # Wait 500ms
        if client.is_playing:
            playback_triggered = True
            print("✅ Good: Automatic playback was triggered")
        else:
            print("❌ PROBLEM: Automatic playback was NOT triggered")

    # Register message handler
    client.on_message(handle_messages)

    try:
        print("🧪 Testing auto_playback=True with Class-Based API")
        print("This SHOULD trigger automatic playback")
        print("Speak into your microphone...")

        # Stream microphone with auto_playback=True
        await client.stream_microphone(
            duration=10,  # 10 seconds
            auto_connect=True,
            auto_playback=True,  # This should enable automatic playback
            verbose=False,
        )

        if playback_triggered:
            print("✅ Test PASSED: Automatic playback was triggered")
        else:
            print("❌ Test FAILED: Automatic playback was NOT triggered")

    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    finally:
        await client.disconnect()
        client.cleanup()


async def test_property_access():
    """Test the new property-based access for playback state"""

    client = VocalsClient()

    try:
        print("🧪 Testing Property Access for Playback State")
        print("=" * 50)

        # Test initial state
        print(f"Initial playback state: {client.playback_state}")
        print(f"Initial is_playing: {client.is_playing}")
        print(f"Initial audio queue length: {len(client.audio_queue)}")

        # Connect and test connection properties
        await client.connect()
        print(f"After connect - Connection state: {client.connection_state}")
        print(f"After connect - Is connected: {client.is_connected}")

        # Test recording properties
        await client.start_recording()
        print(f"After start recording - Recording state: {client.recording_state}")
        print(f"After start recording - Is recording: {client.is_recording}")

        # Monitor for a few seconds
        print("\nMonitoring properties for 5 seconds...")
        for i in range(5):
            await asyncio.sleep(1)
            print(
                f"  Time {i+1}s: Recording={client.is_recording}, "
                f"Playing={client.is_playing}, Queue={len(client.audio_queue)}"
            )

        # Stop recording
        await client.stop_recording()
        print(f"After stop recording - Recording state: {client.recording_state}")
        print(f"After stop recording - Is recording: {client.is_recording}")

        # Test final state
        print(f"Final playback state: {client.playback_state}")
        print(f"Final is_playing: {client.is_playing}")
        print(f"Final audio queue length: {len(client.audio_queue)}")

        print("✅ Property access test completed successfully")

    except Exception as e:
        print(f"❌ Property access test failed: {e}")
    finally:
        await client.disconnect()
        client.cleanup()


async def context_manager_test():
    """Test auto_playback with the new context manager"""

    print("🧪 Testing auto_playback with Context Manager")
    print("=" * 50)

    # Test with auto_playback=False
    async with VocalsClient(modes=["transcription", "voice_assistant"]) as client:
        print("🔇 Testing auto_playback=False in context manager")

        def handle_messages(message):
            if message.type == "tts_audio" and message.data:
                text = message.data.get("text", "")
                if text:
                    print(f"🔊 TTS received: {text}")
                    if client.is_playing:
                        print("❌ Automatic playback detected (should not happen)")
                    else:
                        print("✅ No automatic playback (correct)")

        client.on_message(handle_messages)

        try:
            await client.stream_microphone(
                duration=5,
                auto_connect=False,  # Already connected by context manager
                auto_playback=False,
                verbose=False,
            )
        except KeyboardInterrupt:
            print("Test interrupted")

    print("🔌 Context manager automatically handled disconnect")
    print("✅ Context manager test completed")


if __name__ == "__main__":
    print("Choose a test:")
    print("1. Test auto_playback=False")
    print("2. Test auto_playback=True")
    print("3. Test property access")
    print("4. Test context manager")

    choice = input("Enter choice (1-4): ").strip()

    try:
        if choice == "1":
            asyncio.run(test_auto_playback_false())
        elif choice == "2":
            asyncio.run(test_auto_playback_true())
        elif choice == "3":
            asyncio.run(test_property_access())
        elif choice == "4":
            asyncio.run(context_manager_test())
        else:
            print("Invalid choice, running auto_playback=False test")
            asyncio.run(test_auto_playback_false())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Error: {e}")
        import sys

        sys.exit(1)
