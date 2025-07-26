#!/usr/bin/env python3
"""
Voice Agent using Semantic Kernel and OpenAI
A complete voice interaction system with speech-to-text, AI chat, and text-to-speech
"""

import os
import asyncio
import logging
import tempfile
from typing import Optional

import pyaudio
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAIAudioToText,
    OpenAITextToAudio,
    OpenAITextToAudioExecutionSettings,
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.contents import AudioContent, ChatHistory

# Set up logging for debugging and info
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------
# Audio Recorder Class
# ----------------------
class AudioRecorder:
    """Handles audio recording using PyAudio"""
    def __init__(self, sample_rate=16000, channels=1, chunk_size=1024):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.audio = pyaudio.PyAudio()
        self.frames = []
        self.stream = None

    def start_recording(self):
        """Start the audio stream and begin recording"""
        self.frames = []
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
        )
        logger.info("Recording started...")

    def stop_recording(self):
        """Stop the audio stream and finish recording"""
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        logger.info("Recording stopped.")

    def save_audio(self, filename):
        """Save the recorded audio frames to a WAV file"""
        import wave
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        logger.info(f"Audio saved to {filename}")

    def record_audio(self, duration=5):
        """Record audio for a fixed duration (in seconds)"""
        self.start_recording()
        for _ in range(0, int(self.sample_rate / self.chunk_size * duration)):
            data = self.stream.read(self.chunk_size)
            self.frames.append(data)
        self.stop_recording()

    def cleanup(self):
        """Release PyAudio resources"""
        self.audio.terminate()

# ----------------------
# Audio Player Class
# ----------------------
class AudioPlayer:
    """Handles audio playback using PyAudio"""
    def __init__(self):
        self.audio = pyaudio.PyAudio()

    def play_audio(self, audio_data, sample_rate=24000):
        """Play audio data through the default output device"""
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            output=True
        )
        stream.write(audio_data)
        stream.stop_stream()
        stream.close()

    def cleanup(self):
        """Release PyAudio resources"""
        self.audio.terminate()

# ----------------------
# Simple Voice Agent Class
# ----------------------
class SimpleVoiceAgent:
    """
    Main voice agent class that manages:
    - Audio recording
    - Speech-to-text (OpenAI Whisper)
    - AI chat (OpenAI GPT)
    - Text-to-speech (OpenAI TTS)
    - Conversation history
    """
    def __init__(self, system_prompt: str = "You are a helpful voice assistant."):
        # Initialize OpenAI connectors via Semantic Kernel
        self.chat_service = OpenAIChatCompletion(ai_model_id="gpt-4o-mini")
        self.audio_to_text = OpenAIAudioToText(ai_model_id="whisper-1")
        self.text_to_audio = OpenAITextToAudio(ai_model_id="tts-1")
        self.history = ChatHistory()
        self.system_prompt = system_prompt
        self.recorder = AudioRecorder()
        self.player = AudioPlayer()
        # Add system prompt to conversation history
        self.history.add_system_message(self.system_prompt)

    async def record_and_transcribe(self) -> Optional[str]:
        """
        Record audio from the microphone and transcribe it to text using OpenAI Whisper.
        Returns the transcribed text, or None if transcription fails.
        """
        try:
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_filename = temp_file.name
            print("Recording for 5 seconds... Speak now!")
            # Record audio for 5 seconds
            self.recorder.record_audio(duration=5)
            # Save the recorded audio to the temp file
            self.recorder.save_audio(temp_filename)
            # Convert audio to text using OpenAI Whisper
            audio_content = AudioContent.from_audio_file(temp_filename)
            text_content = await self.audio_to_text.get_text_content(audio_content)
            # Clean up the temp file
            os.unlink(temp_filename)
            return text_content.text
        except Exception as e:
            logger.error(f"Error recording/transcribing: {e}")
            return None

    async def get_ai_response(self, user_input: str) -> str:
        """
        Get an AI-generated response for the user's input using OpenAI GPT.
        Maintains conversation history for context.
        """
        try:
            # Add user message to conversation history
            self.history.add_user_message(user_input)
            # Get AI response from OpenAI GPT
            response = await self.chat_service.get_chat_message_content(
                chat_history=self.history,
                settings=OpenAIChatPromptExecutionSettings(
                    max_tokens=2000,
                    temperature=0.7,
                    top_p=0.8,
                ),
            )
            # Add assistant response to history
            self.history.add_assistant_message(response.content)
            return response.content
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return "I'm sorry, I encountered an error processing your request."

    async def speak_response(self, text: str):
        """
        Convert the AI's text response to speech and play it using OpenAI TTS.
        """
        try:
            # Convert text to audio using OpenAI TTS
            audio_content = await self.text_to_audio.get_audio_content(
                text, 
                OpenAITextToAudioExecutionSettings(response_format="wav")
            )
            # Play the audio response
            self.player.play_audio(audio_content.data)
        except Exception as e:
            logger.error(f"Error converting text to speech: {e}")
            print(f"Assistant: {text}")

    async def conversation_loop(self):
        """
        Main conversation loop:
        - Waits for user to press Enter or type 'exit'
        - Records and transcribes audio
        - Gets AI response
        - Speaks the response
        - Exits on 'exit' command
        """
        print("Simple Voice Agent Started!")
        print("Instructions:")
        print("- Press Enter to start recording (speak for 5 seconds)")
        print("- Type 'exit' and press Enter to quit")
        print("- The agent will respond with voice")
        print()
        while True:
            try:
                # Wait for user to press Enter or type exit
                user_choice = input("Press Enter to start recording (or type 'exit' to quit): ")
                # Check for exit command in text input
                if user_choice.lower().strip() == "exit":
                    print("Goodbye!")
                    break
                # Record and transcribe user input
                user_input = await self.record_and_transcribe()
                if not user_input:
                    print("Could not transcribe audio. Please try again.")
                    continue
                print(f"You said: {user_input}")
                # Check for exit command in transcribed audio
                if "exit" in user_input.lower():
                    print("Goodbye!")
                    break
                # Get AI response
                response = await self.get_ai_response(user_input)
                print(f"Assistant: {response}")
                # Speak the response
                await self.speak_response(response)
                print()
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error in conversation loop: {e}")
                print("An error occurred. Please try again.")

    def cleanup(self):
        """Release all resources used by the agent"""
        self.recorder.cleanup()
        self.player.cleanup()

# ----------------------
# Main Entry Point
# ----------------------
async def main():
    """
    Main function:
    - Sets OpenAI API key if not already set
    - Creates the voice agent
    - Starts the conversation loop
    - Cleans up resources on exit
    """
    # Set OpenAI API key if not already set
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "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"
        print("OpenAI API key set automatically.")
    # Create voice agent with a system prompt
    agent = SimpleVoiceAgent(
        system_prompt="You are a helpful voice assistant. Keep your responses concise and natural for voice interaction."
    )
    try:
        # Start the main conversation loop
        await agent.conversation_loop()
    finally:
        # Clean up resources on exit
        agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 