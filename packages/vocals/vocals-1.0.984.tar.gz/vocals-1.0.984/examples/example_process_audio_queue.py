#!/usr/bin/env python3
"""
Example demonstrating how to use process_audio_queue to handle audio segments with custom processing.

This example shows how to grab audio from the queue and send it to your own processing function
instead of using the built-in audio playback.
"""

import asyncio
import logging
import sys
import os
import base64
import wave
import io

# Add the parent directory to the path so we can import vocals
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vocals import VocalsClient
from vocals.types import TTSAudioSegment


def my_custom_audio_handler(segment: TTSAudioSegment):
    """
    Custom audio processing function.

    This function receives audio segments from the queue and can process them however you like.
    Examples: save to file, send to external player, convert format, etc.
    """
    print(f"📢 Processing audio segment: '{segment.text}'")
    print(f"   Segment ID: {segment.segment_id}")
    print(f"   Duration: {segment.duration_seconds:.2f}s")
    print(f"   Sample Rate: {segment.sample_rate} Hz")
    print(f"   Format: {segment.format}")

    # Example 1: Save to file
    try:
        # Decode base64 audio data
        audio_data = base64.b64decode(segment.audio_data)

        # Save to WAV file
        filename = f"audio_segment_{segment.segment_id}_{segment.sentence_number}.wav"
        with open(filename, "wb") as f:
            f.write(audio_data)
        print(f"   💾 Saved to: {filename}")

    except Exception as e:
        print(f"   ❌ Error saving audio: {e}")

    # Example 2: Audio analysis
    try:
        # Parse WAV data to get audio samples
        with io.BytesIO(audio_data) as wav_io:
            with wave.open(wav_io, "rb") as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())

                # Simple analysis - just count samples
                sample_count = len(frames) // wav_file.getsampwidth()
                print(f"   📊 Audio contains {sample_count} samples")

    except Exception as e:
        print(f"   ❌ Error analyzing audio: {e}")

    print()


async def main():
    """Main example function"""
    print("🎵 Custom Audio Processing Example")
    print("=" * 50)
    print()

    # Create vocals client instance
    client = VocalsClient()

    try:
        # Connect to the service
        print("🔗 Connecting to Vocals service...")
        await client.connect()

        # Send a test message to generate some audio
        print("📤 Sending test message to generate audio...")
        from vocals.types import WebSocketMessage

        test_message = WebSocketMessage(
            event="message",
            data={
                "text": "Hello! This is a test message to generate some audio segments."
            },
        )
        await client.send_message(test_message)

        # Wait for audio to be generated and added to queue
        print("⏳ Waiting for audio to be generated...")
        await asyncio.sleep(5)

        # Check if we have audio in the queue using the new property
        audio_queue = client.audio_queue
        print(f"📄 Audio queue contains {len(audio_queue)} segments")

        if audio_queue:
            print("\n🎯 Processing audio segments with custom handler...")
            print("-" * 50)

            # Process all audio segments in the queue
            processed_count = client.process_audio_queue(
                my_custom_audio_handler, consume_all=True
            )

            print(f"✅ Successfully processed {processed_count} audio segments")

            # Check queue again - should be empty now
            audio_queue_after = client.audio_queue
            print(f"📄 Audio queue now contains {len(audio_queue_after)} segments")

        else:
            print(
                "❌ No audio segments were generated. Check your connection and API key."
            )

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        # Disconnect
        print("\n🔌 Disconnecting...")
        await client.disconnect()


async def context_manager_example():
    """Example using the new async context manager"""
    print("🎵 Custom Audio Processing with Context Manager")
    print("=" * 50)
    print()

    # Use the new async context manager
    async with VocalsClient() as client:
        print("🔗 Connected automatically via context manager")

        # Send a test message to generate some audio
        print("📤 Sending test message to generate audio...")
        from vocals.types import WebSocketMessage

        test_message = WebSocketMessage(
            event="message",
            data={"text": "This is a test using the new context manager approach!"},
        )
        await client.send_message(test_message)

        # Wait for audio to be generated
        print("⏳ Waiting for audio to be generated...")
        await asyncio.sleep(5)

        # Process audio segments using property access
        if client.audio_queue:
            print(f"\n🎯 Processing {len(client.audio_queue)} audio segments...")
            print("-" * 50)

            # Process one segment at a time
            while client.audio_queue:
                processed_count = client.process_audio_queue(
                    my_custom_audio_handler, consume_all=False
                )
                if processed_count == 0:
                    break
                print(
                    f"✅ Processed {processed_count} segment. {len(client.audio_queue)} remaining."
                )

        else:
            print("❌ No audio segments were generated.")

    print("🔌 Disconnected automatically via context manager")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    print("Choose an example:")
    print("1. Basic custom audio processing")
    print("2. Context manager example")

    choice = input("Enter choice (1-2): ").strip()

    if choice == "1":
        asyncio.run(main())
    elif choice == "2":
        asyncio.run(context_manager_example())
    else:
        print("Invalid choice, running basic example")
        asyncio.run(main())
