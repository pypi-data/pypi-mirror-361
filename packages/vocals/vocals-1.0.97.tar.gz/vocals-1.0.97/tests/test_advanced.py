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
from vocals import create_vocals

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def advanced_voice_assistant():
    """Advanced voice assistant with full manual control"""

    # Create SDK with specific modes for controlled experience
    # Using modes disables all automatic handlers - we have complete control
    # This prevents duplicate message processing that would occur with default handlers
    sdk = create_vocals(modes=["transcription", "voice_assistant"])

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
                asyncio.create_task(sdk["play_audio"]())

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
                # processed_count = sdk["process_audio_queue"](
                #     my_custom_audio_handler,
                #     consume_all=True
                # )
                # print(f"✅ Processed {processed_count} audio segments")

        elif message.type == "speech_interruption":
            print("\n🛑 Speech interrupted")
            conversation_state["speaking"] = False

    # Register our custom message handler
    sdk["on_message"](handle_messages)

    # Custom connection handler
    def handle_connection(state):
        if state.name == "CONNECTED":
            print("✅ Connected to voice assistant")
        elif state.name == "DISCONNECTED":
            print("❌ Disconnected from voice assistant")

    sdk["on_connection_change"](handle_connection)

    try:
        print("🎤 Advanced Voice Assistant Started")
        print("Full control mode - custom handlers active")
        print("Features: live transcription, streaming responses, manual playback")
        print("Speak into your microphone...")
        print("Press Ctrl+C to stop")

        # Stream microphone with complete manual control
        await sdk["stream_microphone"](
            duration=0,  # Infinite recording
            auto_connect=True,  # Connects automatically since auto_connect defaults to False
            auto_playback=False,  # We have complete manual control over playback
            verbose=False,
        )

    except KeyboardInterrupt:
        print("\n👋 Advanced voice assistant stopped")
    finally:
        await sdk["disconnect"]()
        sdk["cleanup"]()


if __name__ == "__main__":
    asyncio.run(advanced_voice_assistant())
