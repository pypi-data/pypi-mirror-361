#!/usr/bin/env python3
"""
Test script to verify that auto_playback=False works correctly
"""

import asyncio
import logging
from vocals import create_vocals

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_auto_playback_false():
    """Test that auto_playback=False prevents automatic playback"""

    # Create SDK with controlled experience (auto-connect now defaults to False)
    sdk = create_vocals(modes=["transcription", "voice_assistant"])

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

                # Check if playback was triggered automatically
                if sdk["get_is_playing"]():
                    playback_triggered = True
                    print("❌ PROBLEM: Playback was triggered automatically!")
                else:
                    print("✅ Good: No automatic playback triggered")
                    print("🎵 Manually starting playback...")
                    asyncio.create_task(sdk["play_audio"]())

    # Register message handler
    sdk["on_message"](handle_messages)

    try:
        print("🧪 Testing auto_playback=False")
        print("This should NOT trigger automatic playback")
        print("Speak into your microphone...")

        # Stream microphone with auto_playback=False
        await sdk["stream_microphone"](
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
        await sdk["disconnect"]()
        sdk["cleanup"]()


if __name__ == "__main__":
    asyncio.run(test_auto_playback_false())
