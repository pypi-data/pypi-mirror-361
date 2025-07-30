"""
Main Vocals SDK client using class-based composition pattern for better Python developer experience.
"""

import asyncio
import logging
from typing import Optional, List, Callable, Dict, Any, Tuple

from .config import VocalsConfig, get_default_config
from .types import (
    ConnectionState,
    RecordingState,
    PlaybackState,
    VocalsError,
    VocalsSDKException,
    TTSAudioSegment,
    WebSocketMessage,
    WebSocketResponse,
    MessageHandler,
    ConnectionHandler,
    ErrorHandler,
    AudioDataHandler,
)
from .websocket_client import create_websocket_client
from .audio_processor import create_audio_processor, AudioConfig

logger = logging.getLogger(__name__)


class VocalsClient:
    """
    Vocals SDK client for voice processing and real-time audio communication.

    This class provides the same functionality as the functional VocalsClient approach
    but uses a class-based structure for better Python developer experience.

    Args:
        config: Configuration options for the SDK
        audio_config: Audio processing configuration
        user_id: Optional user ID for token generation
        modes: List of modes to control SDK behavior (e.g., ['transcription', 'voice_assistant'])
               - Default (empty list): Full auto-contained experience with handlers, playback, and logging
               - 'transcription': Enables transcription-related internal processing only
               - 'voice_assistant': Enables AI response handling and speech interruption only
               Note: When modes are specified, SDK becomes passive - users must attach their own handlers.

    Example:
        # Basic usage
        client = VocalsClient()
        await client.connect()
        await client.stream_microphone(duration=30.0)

        # With custom configuration
        config = VocalsConfig(debug_level="DEBUG")
        client = VocalsClient(config=config)

        # Context manager usage
        async with VocalsClient() as client:
            await client.stream_microphone(duration=30.0)
    """

    def __init__(
        self,
        config: Optional[VocalsConfig] = None,
        audio_config: Optional[AudioConfig] = None,
        user_id: Optional[str] = None,
        modes: List[str] = [],
    ):
        """Initialize the Vocals client."""
        # Initialize configurations
        self.config = config or get_default_config()
        self.audio_config = audio_config or AudioConfig()
        self.modes = modes

        # Setup logging based on configuration
        self.config.setup_logging()

        # Create components using composition
        self.websocket_client = create_websocket_client(self.config, user_id)
        self.audio_processor = create_audio_processor(self.audio_config)

        # Store event loop reference for audio callback thread
        self._event_loop = None
        # Flag to track if microphone streaming is active (to avoid duplicate TTS processing)
        self._microphone_streaming_active = False

        # Set up event handlers between components
        self._setup_internal_handlers()

        # Auto-attach enhanced handler ONLY when no modes are specified (default experience)
        if not modes:  # Empty list means default full experience
            self._setup_default_handlers()

        # Auto-connect if configured
        if self.config.auto_connect:
            asyncio.create_task(self.connect())

    def _setup_internal_handlers(self) -> None:
        """Set up internal event handlers between components."""
        self.websocket_client["add_message_handler"](self._handle_websocket_message)
        self.audio_processor["add_audio_data_handler"](self._handle_audio_data)
        self.websocket_client["add_error_handler"](self._handle_error)
        self.audio_processor["add_error_handler"](self._handle_error)

    def _setup_default_handlers(self) -> None:
        """Set up default handlers for full experience mode."""
        from .utils import create_enhanced_message_handler

        enhanced_handler = create_enhanced_message_handler(
            verbose=(self.config.debug_level == "DEBUG"),
            show_transcription=True,
            show_responses=True,
            show_streaming=True,
            show_detection=True,
        )
        self.websocket_client["add_message_handler"](enhanced_handler)

    def _handle_websocket_message(self, message: WebSocketResponse) -> None:
        """Handle incoming WebSocket messages."""
        try:
            # Handle TTS audio messages (skip if microphone streaming is handling it)
            if (
                message.type == "tts_audio"
                and message.data
                and (
                    not self._microphone_streaming_active or not self.modes
                )  # Always handle in default mode
            ):
                # Convert to TTSAudioSegment
                segment_data = message.data
                segment = TTSAudioSegment(
                    text=segment_data.get("text", ""),
                    audio_data=segment_data.get("audio_data", ""),
                    sample_rate=segment_data.get("sample_rate", 24000),
                    segment_id=segment_data.get("segment_id", ""),
                    sentence_number=segment_data.get("sentence_number", 0),
                    generation_time_ms=segment_data.get("generation_time_ms", 0),
                    format=segment_data.get("format", "wav"),
                    duration_seconds=segment_data.get("duration_seconds", 0.0),
                )

                # Add to audio queue
                self.audio_processor["add_to_queue"](segment)

                # Auto-start playback if not already playing (default experience only)
                # In controlled mode, the audio processor's auto_playback setting will handle this
                if not self.modes and not self.audio_processor["get_is_playing"]():
                    asyncio.create_task(self.audio_processor["play_audio"]())

            # Handle speech interruption messages
            elif message.type == "speech_interruption":
                # Handle speech interruption for default experience or voice_assistant mode
                if not self.modes or "voice_assistant" in self.modes:
                    # Fade out current audio and clear queue for new speech
                    asyncio.create_task(self._handle_speech_interruption())

        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")

    async def _handle_speech_interruption(self) -> None:
        """Handle speech interruption events."""
        try:
            # Fade out current audio
            await self.audio_processor["fade_out_audio"](0.3)

            # Clear the queue
            self.audio_processor["clear_queue"]()

        except Exception as e:
            logger.error(f"Error handling speech interruption: {e}")

    def _handle_audio_data(self, audio_data: List[float]) -> None:
        """Handle audio data from processor."""
        # Send audio data to WebSocket if connected and recording
        if (
            self.websocket_client["get_is_connected"]()
            and self.audio_processor["get_recording_state"]()
            == RecordingState.RECORDING
        ):
            message = WebSocketMessage(
                event="media",
                data=audio_data,
                format=self.audio_config.format,
                sample_rate=self.audio_config.sample_rate,
            )

            # Schedule the coroutine in the main event loop since we're in a callback thread
            if self._event_loop:
                try:
                    future = asyncio.run_coroutine_threadsafe(
                        self.websocket_client["send_message"](message), self._event_loop
                    )

                    # Add a callback to handle any errors
                    def handle_send_result(fut):
                        try:
                            fut.result()  # This will raise any exceptions
                        except Exception as e:
                            logger.error(f"Error sending audio data: {e}")

                    future.add_done_callback(handle_send_result)
                except Exception as e:
                    logger.error(f"Error scheduling audio data send: {e}")
            else:
                logger.warning("No event loop available for audio data sending")

    def _handle_error(self, error: VocalsError) -> None:
        """Handle errors from components."""
        logger.error(f"SDK Error: {error.message} ({error.code})")
        # Additional error handling can be added here

    # Connection methods
    async def connect(self) -> None:
        """Connect to the WebSocket server."""
        await self.websocket_client["connect"]()

    async def disconnect(self) -> None:
        """Disconnect from the WebSocket server."""
        await self.websocket_client["disconnect"]()
        self.audio_processor["cleanup"]()

    async def reconnect(self) -> None:
        """Reconnect to the WebSocket server."""
        await self.disconnect()
        await self.connect()

    # Voice recording methods
    async def start_recording(self) -> None:
        """Start voice recording."""
        # Capture the event loop for audio callback thread
        try:
            self._event_loop = asyncio.get_running_loop()
        except RuntimeError:
            logger.warning("No event loop running when starting recording")

        # Ensure we're connected
        if not self.websocket_client["get_is_connected"]():
            await self.connect()

        # Send start event
        start_message = WebSocketMessage(event="start")
        await self.websocket_client["send_message"](start_message)

        # Start audio recording
        await self.audio_processor["start_recording"]()

        # Send settings event with sample rate
        settings_message = WebSocketMessage(
            event="settings", data={"sampleRate": self.audio_config.sample_rate}
        )
        await self.websocket_client["send_message"](settings_message)

    async def stop_recording(self) -> None:
        """Stop voice recording."""
        # Stop audio recording
        await self.audio_processor["stop_recording"]()

        # Send stop event
        stop_message = WebSocketMessage(event="stop")
        await self.websocket_client["send_message"](stop_message)

    # Audio playback methods
    async def play_audio(self) -> None:
        """Start or resume audio playback."""
        await self.audio_processor["play_audio"]()

    async def pause_audio(self) -> None:
        """Pause audio playback."""
        await self.audio_processor["pause_audio"]()

    async def stop_audio(self) -> None:
        """Stop audio playback."""
        await self.audio_processor["stop_audio"]()

    async def fade_out_audio(self, duration: float = 0.5) -> None:
        """Fade out current audio over specified duration."""
        await self.audio_processor["fade_out_audio"](duration)

    def clear_queue(self) -> None:
        """Clear the audio playback queue."""
        self.audio_processor["clear_queue"]()

    def add_to_queue(self, segment: TTSAudioSegment) -> None:
        """Add an audio segment to the playback queue."""
        self.audio_processor["add_to_queue"](segment)

    def process_audio_queue(
        self, callback: Callable[[TTSAudioSegment], None], consume_all: bool = False
    ) -> int:
        """
        Process audio segments from the queue by sending them to a user-provided callback function.

        This allows users to handle audio segments themselves instead of using the built-in playback.

        Args:
            callback: Function to call with each audio segment. Should accept a TTSAudioSegment.
            consume_all: If True, processes all segments in the queue. If False, processes only the next segment.

        Returns:
            Number of segments processed

        Example:
            def my_audio_handler(segment: TTSAudioSegment):
                # Custom audio processing
                print(f"Received audio: {segment.text}")
                # Send to custom player, save to file, etc.

            count = client.process_audio_queue(my_audio_handler, consume_all=True)
            print(f"Processed {count} audio segments")
        """
        return self.audio_processor["process_queue"](callback, consume_all)

    # Messaging methods
    async def send_message(self, message: WebSocketMessage) -> None:
        """Send a message to the WebSocket server."""
        await self.websocket_client["send_message"](message)

    # High-level audio file streaming
    async def stream_audio_file(
        self,
        file_path: str,
        chunk_size: int = 1024,
        verbose: bool = True,
        auto_connect: bool = True,
    ) -> None:
        """
        High-level method to stream an audio file to the WebSocket server.

        This method handles the entire flow:
        1. Loads the audio file
        2. Connects to WebSocket if not connected
        3. Sends start and settings messages
        4. Streams audio in chunks
        5. Sends stop message
        6. Handles any received audio playback

        Args:
            file_path: Path to the audio file to stream
            chunk_size: Size of each chunk to send
            verbose: Whether to log detailed progress
            auto_connect: Whether to automatically connect if not connected

        Raises:
            VocalsSDKException: If there's an error streaming the file
        """
        try:
            from .utils import load_audio_file, send_audio_in_chunks

            if verbose:
                logger.info(f"🎵 Starting to stream audio file: {file_path}")

            # Load audio file
            audio_data = load_audio_file(file_path)
            if not audio_data:
                raise VocalsSDKException(
                    "AUDIO_LOAD_ERROR", f"Failed to load audio file: {file_path}"
                )

            if verbose:
                logger.info(f"✅ Loaded {len(audio_data)} audio samples")

            # Connect if not connected
            if auto_connect and not self.websocket_client["get_is_connected"]():
                if verbose:
                    logger.info("Connecting to WebSocket...")
                await self.connect()
                # Give it a moment to establish connection
                await asyncio.sleep(1)

            # Verify connection
            if not self.websocket_client["get_is_connected"]():
                raise VocalsSDKException(
                    "CONNECTION_ERROR", "Not connected to WebSocket server"
                )

            # Send start message
            if verbose:
                logger.info("Sending start message...")
            start_message = WebSocketMessage(event="start")
            await self.websocket_client["send_message"](start_message)

            # Send settings message
            if verbose:
                logger.info("Sending settings message...")
            settings_message = WebSocketMessage(
                event="settings", data={"sampleRate": self.audio_config.sample_rate}
            )
            await self.websocket_client["send_message"](settings_message)

            # Stream audio in chunks
            if verbose:
                logger.info("Starting audio chunk streaming...")
            await send_audio_in_chunks(
                self.websocket_client["send_message"],
                audio_data,
                chunk_size=chunk_size,
                sample_rate=self.audio_config.sample_rate,
                verbose=verbose,
            )

            # Send stop message
            if verbose:
                logger.info("Sending stop message...")
            stop_message = WebSocketMessage(event="stop")
            await self.websocket_client["send_message"](stop_message)

            # Wait for any final responses
            if verbose:
                logger.info("Waiting for responses...")
            await asyncio.sleep(2)

            # Check for any audio in queue and play it
            audio_queue = self.audio_processor["get_audio_queue"]()
            if audio_queue:
                if verbose:
                    logger.info(f"Playing {len(audio_queue)} audio segments...")
                await self.audio_processor["play_audio"]()

                # Wait for playback to complete
                while self.audio_processor["get_is_playing"]():
                    await asyncio.sleep(0.1)

                if verbose:
                    logger.info("✅ Playback completed")

            if verbose:
                logger.info("🎉 Audio file streaming completed successfully")

        except Exception as e:
            error_msg = f"Error streaming audio file: {e}"
            logger.error(error_msg)
            raise VocalsSDKException("AUDIO_STREAM_ERROR", error_msg)

    # High-level microphone streaming
    async def stream_microphone(
        self,
        duration: float = 30.0,
        auto_connect: bool = True,
        auto_playback: bool = True,
        verbose: bool = True,
        stats_tracking: bool = True,
        amplitude_threshold: float = 0.01,
    ) -> Optional[dict]:
        """
        High-level method to stream from microphone for a specified duration.

        This method handles the entire microphone streaming flow:
        1. Connects to WebSocket if not connected
        2. Sets up optimized handlers for microphone streaming
        3. Starts recording for the specified duration
        4. Automatically plays back received audio
        5. Tracks statistics and provides session summary

        Args:
            duration: Recording duration in seconds (0 for infinite)
            auto_connect: Whether to automatically connect if not connected
            auto_playback: Whether to automatically play received audio
            verbose: Whether to log detailed progress
            stats_tracking: Whether to track and return statistics
            amplitude_threshold: Minimum amplitude to consider as speech

        Returns:
            Optional dictionary with session statistics if stats_tracking is True

        Raises:
            VocalsSDKException: If there's an error during streaming
        """
        try:
            from .utils import (
                create_microphone_stats_tracker,
                create_microphone_message_handler,
                create_microphone_connection_handler,
                create_microphone_audio_data_handler,
            )

            # Set flag to prevent default handler from processing TTS messages
            self._microphone_streaming_active = True

            # Set auto_playback flag on audio processor
            self.audio_processor["set_auto_playback"](auto_playback)

            if verbose:
                logger.info(f"🎤 Starting microphone streaming for {duration}s...")

            # Initialize statistics tracker
            stats_tracker = None
            if stats_tracking:
                stats_tracker = create_microphone_stats_tracker(verbose)

            # Connect if not connected
            if auto_connect and not self.websocket_client["get_is_connected"]():
                # Wait a bit for any existing connection attempts to complete
                if self.websocket_client["get_is_connecting"]():
                    if verbose:
                        logger.info("Waiting for existing connection attempt...")
                    # Wait up to 3 seconds for connection to complete
                    for _ in range(30):  # 30 * 0.1 = 3 seconds
                        await asyncio.sleep(0.1)
                        if self.websocket_client["get_is_connected"]():
                            break
                        if not self.websocket_client["get_is_connecting"]():
                            break  # Connection attempt failed

                # Only connect if still not connected
                if not self.websocket_client["get_is_connected"]():
                    if verbose:
                        logger.info("Connecting to WebSocket...")
                    await self.connect()
                    # Give it a moment to establish connection
                    await asyncio.sleep(1)

            # Verify connection
            if not self.websocket_client["get_is_connected"]():
                raise VocalsSDKException(
                    "CONNECTION_ERROR", "Not connected to WebSocket server"
                )

            # Set up optimized handlers
            # Only add microphone message handler if we're in controlled mode
            # In default mode, the enhanced handler is already attached
            message_handler = None
            if self.modes:  # Only in controlled mode
                # Use a simplified handler for stats only, disable text display to avoid duplication
                # with custom user handlers
                # Always pass audio_processor to ensure TTS audio is added to queue
                # auto_playback only controls whether playback starts automatically
                message_handler = create_microphone_message_handler(
                    stats_tracker,
                    verbose,
                    audio_processor=self.audio_processor,  # Always pass audio_processor
                    show_text=False,  # Disable built-in text display in controlled mode
                    show_streaming=False,  # Disable built-in streaming display
                )
            elif stats_tracking:  # Default mode with stats tracking
                # Add stats tracking handler for default mode
                def stats_handler(message):
                    if stats_tracker:  # Null check
                        if message.type == "transcription" and message.data:
                            stats_tracker["update"]("transcriptions")
                        elif message.type == "llm_response" and message.data:
                            stats_tracker["update"]("responses")
                        elif message.type == "tts_audio" and message.data:
                            stats_tracker["update"]("tts_segments_received")

                message_handler = stats_handler

            connection_handler = create_microphone_connection_handler(
                stats_tracker, verbose
            )
            audio_data_handler = create_microphone_audio_data_handler(
                amplitude_threshold, verbose
            )

            # Register microphone-specific handlers (they'll handle TTS display)
            remove_message_handler = None
            if message_handler:  # Only if we created one
                remove_message_handler = self.websocket_client["add_message_handler"](
                    message_handler
                )
            remove_connection_handler = self.websocket_client["add_connection_handler"](
                connection_handler
            )
            remove_audio_handler = self.audio_processor["add_audio_data_handler"](
                audio_data_handler
            )

            # Start playback monitoring if enabled
            playback_monitor_task = None
            if auto_playback:

                async def monitor_playback():
                    try:
                        while True:
                            # Check if there's audio in queue and we're not playing
                            audio_queue = self.audio_processor["get_audio_queue"]()
                            is_playing = self.audio_processor["get_is_playing"]()

                            if audio_queue and not is_playing:
                                if verbose:
                                    logger.info(
                                        f"🎶 Auto-playing {len(audio_queue)} queued audio segments"
                                    )
                                await self.audio_processor["play_audio"]()

                            await asyncio.sleep(0.1)  # Check every 100ms

                    except asyncio.CancelledError:
                        if verbose:
                            logger.debug("Playback monitor cancelled")
                        raise
                    except Exception as e:
                        logger.error(f"Error in playback monitor: {e}")
                        raise

                playback_monitor_task = asyncio.create_task(monitor_playback())

            try:
                # Start recording
                if verbose:
                    logger.info("🎙️ Starting recording session...")
                await self.start_recording()

                # Record for specified duration
                if duration > 0:
                    start_time = asyncio.get_event_loop().time()
                    while (asyncio.get_event_loop().time() - start_time) < duration:
                        # Show recording status
                        if verbose:
                            recording_state = self.audio_processor[
                                "get_recording_state"
                            ]()
                            amplitude = self.audio_processor["get_current_amplitude"]()

                            if (
                                recording_state.name == "RECORDING"
                                and amplitude > amplitude_threshold
                            ):
                                logger.debug(
                                    f"🎤 Recording... amplitude: {amplitude:.4f}"
                                )

                        await asyncio.sleep(0.5)

                        # Update recording time stats
                        if stats_tracker:
                            stats_tracker["update"]("recording_time", duration)

                else:
                    # Infinite recording - wait for external stop
                    if verbose:
                        logger.info(
                            "🎙️ Recording indefinitely... (use stop_recording() to stop)"
                        )
                    while (
                        self.audio_processor["get_recording_state"]().name
                        == "RECORDING"
                    ):
                        await asyncio.sleep(0.5)

                # Stop recording
                if verbose:
                    logger.info("🛑 Stopping recording session...")
                await self.stop_recording()

                # Wait for any final responses
                if verbose:
                    logger.info("Waiting for final responses...")
                await asyncio.sleep(2)

                # Wait for playback to complete if auto_playback is enabled
                if auto_playback:
                    while self.audio_processor["get_is_playing"]():
                        if verbose:
                            current_segment = self.audio_processor[
                                "get_current_segment"
                            ]()
                            if current_segment:
                                logger.debug(f"🎵 Playing: {current_segment.text}")
                        await asyncio.sleep(0.1)

                    if verbose:
                        logger.info("✅ Playback completed")

                # Print final statistics
                if stats_tracker and verbose:
                    stats_tracker["print"]()

                if verbose:
                    logger.info("🎉 Microphone streaming completed successfully")

                return stats_tracker["stats"] if stats_tracker else None

            finally:
                # Cancel playback monitor
                if playback_monitor_task:
                    playback_monitor_task.cancel()
                    try:
                        await playback_monitor_task
                    except asyncio.CancelledError:
                        pass

                # Cleanup handlers
                if remove_message_handler:
                    remove_message_handler()
                remove_connection_handler()
                remove_audio_handler()

        except Exception as e:
            error_msg = f"Error during microphone streaming: {e}"
            logger.error(error_msg)
            raise VocalsSDKException("MICROPHONE_STREAM_ERROR", error_msg)
        finally:
            # Reset flag to allow default handler to process TTS messages again
            self._microphone_streaming_active = False
            # Reset auto_playback to default
            self.audio_processor["set_auto_playback"](True)

    # Event handler registration methods
    def on_message(self, handler: MessageHandler) -> Callable[[], None]:
        """Register a message handler."""
        return self.websocket_client["add_message_handler"](handler)

    def on_connection_change(self, handler: ConnectionHandler) -> Callable[[], None]:
        """Register a connection state change handler."""
        return self.websocket_client["add_connection_handler"](handler)

    def on_error(self, handler: ErrorHandler) -> Callable[[], None]:
        """Register an error handler."""
        return self.websocket_client["add_error_handler"](handler)

    def on_audio_data(self, handler: AudioDataHandler) -> Callable[[], None]:
        """Register an audio data handler."""
        return self.audio_processor["add_audio_data_handler"](handler)

    # Properties (using @property for better Python idioms)
    @property
    def connection_state(self) -> ConnectionState:
        """Get the current connection state."""
        return self.websocket_client["get_connection_state"]()

    @property
    def is_connected(self) -> bool:
        """Check if connected to the WebSocket server."""
        return self.websocket_client["get_is_connected"]()

    @property
    def is_connecting(self) -> bool:
        """Check if connecting or reconnecting to the WebSocket server."""
        return self.websocket_client["get_is_connecting"]()

    @property
    def recording_state(self) -> RecordingState:
        """Get the current recording state."""
        return self.audio_processor["get_recording_state"]()

    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self.audio_processor["get_is_recording"]()

    @property
    def playback_state(self) -> PlaybackState:
        """Get the current playback state."""
        return self.audio_processor["get_playback_state"]()

    @property
    def is_playing(self) -> bool:
        """Check if currently playing audio."""
        return self.audio_processor["get_is_playing"]()

    @property
    def audio_queue(self) -> List[TTSAudioSegment]:
        """Get the current audio queue."""
        return self.audio_processor["get_audio_queue"]()

    @property
    def current_segment(self) -> Optional[TTSAudioSegment]:
        """Get the currently playing audio segment."""
        return self.audio_processor["get_current_segment"]()

    @property
    def current_amplitude(self) -> float:
        """Get the current audio amplitude for visualization."""
        return self.audio_processor["get_current_amplitude"]()

    @property
    def token(self) -> Optional[str]:
        """Get the current token."""
        token_info = self.websocket_client["get_token_info"]()
        return token_info[0]

    @property
    def token_expires_at(self) -> Optional[float]:
        """Get the token expiration timestamp."""
        token_info = self.websocket_client["get_token_info"]()
        return token_info[1]

    def set_user_id(self, user_id: str) -> None:
        """Set user ID for token generation."""
        self.websocket_client["set_user_id"](user_id)

    # Context manager support
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

    # Cleanup
    def cleanup(self) -> None:
        """Clean up resources."""
        self.audio_processor["cleanup"]()
        # WebSocket client cleanup is handled by disconnect
