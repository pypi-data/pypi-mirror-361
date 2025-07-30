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
