# Voice Agent Flow Documentation

A detailed breakdown of how the voice agent processes audio through multiple AI services.

## 🚀 Complete Runtime Execution Flow

Here's a step-by-step flow of how the code executes, sorted for learning the runtime flow of this Python voice agent program:

### ✅ 1. File Starts Executing

```python
if __name__ == "__main__":
    asyncio.run(main())
```

- Python checks if this is the main script and starts running it
- It runs the `main()` function asynchronously using `asyncio.run`

### ✅ 2. main() Function Begins

```python
async def main():
```

**Inside main():**

#### 🟢 a. Load Environment Variables

```python
load_dotenv()
```

#### 🟢 b. Check for API Key

```python
if not os.getenv("OPENAI_API_KEY"):
    # If missing, show error and stop
```

#### 🟢 c. Create an Agent

```python
agent = SimpleVoiceAgent(...)
```

This initializes:

- OpenAI connectors
- Audio recorder
- Audio player
- System prompt and conversation history

### ✅ 3. SimpleVoiceAgent **init**() Executes

```python
class SimpleVoiceAgent:
    def __init__(...):
```

**Loads:**

- `OpenAIChatCompletion`
- `OpenAIAudioToText`
- `OpenAITextToAudio`

**Creates:**

- `AudioRecorder`
- `AudioPlayer`

**Adds the system prompt to conversation history.**

### ✅ 4. Enter Conversation Loop

```python
await agent.conversation_loop()
```

**Inside conversation_loop():**

#### 🔁 LOOP BEGINS:

User sees:

```
Press Enter to start recording (or type 'exit' to quit):
```

### ✅ 5. If Enter is Pressed → Starts Recording

```python
user_input = await self.record_and_transcribe()
```

**Inside record_and_transcribe():**

#### 🟡 a. Record for 5 seconds

```python
self.recorder.record_audio(duration=5)
```

Uses `AudioRecorder.start_recording()` and reads audio chunks.

#### 🟡 b. Save audio to temp file

```python
self.recorder.save_audio(temp_filename)
```

#### 🟡 c. Transcribe via Whisper

```python
audio_content = AudioContent.from_audio_file(temp_filename)
text_content = await self.audio_to_text.get_text_content(audio_content)
```

### ✅ 6. Display & Process User Input

```python
response = await self.get_ai_response(user_input)
```

**Inside get_ai_response():**

- Adds user message to history
- Calls OpenAI GPT (`get_chat_message_content()`)
- Adds assistant reply to history

### ✅ 7. Text-to-Speech

```python
await self.speak_response(response)
```

**Inside speak_response():**

- Calls OpenAI TTS (`get_audio_content()`)
- Plays audio using `AudioPlayer.play_audio()`

### 🔁 8. Loop Repeats Until Exit

If user types or says "exit" → exits the loop.

### ✅ 9. Clean Up Resources

```python
agent.cleanup()
```

- Calls `self.recorder.cleanup()` → releases PyAudio mic
- Calls `self.player.cleanup()` → releases PyAudio speaker

---

## 🔄 FULL EXECUTION FLOW SUMMARY:

```
main() →
    load_dotenv() →
    create SimpleVoiceAgent →
        init chat/audio models + PyAudio →
        add system prompt to history
    →
    conversation_loop() →
        wait for user input →
        record_and_transcribe() →
            record audio →
            save .wav →
            transcribe to text
        →
        get_ai_response() →
            get GPT response
        →
        speak_response() →
            TTS → play response
        →
        repeat or exit →
    cleanup()
```

---

## 🎯 Individual Component Flows

### 🎙️ Step 1: Audio Recording (5 seconds)

**Function**: `self.recorder.record_audio(duration=5)`

When you press Enter:

- PyAudio opens the microphone
- It reads short chunks of data in a loop and stores them in `self.frames`
- After 5 seconds, the recording is stopped

**📍 Code:**

```python
for _ in range(0, int(self.sample_rate / self.chunk_size * duration)):
    data = self.stream.read(self.chunk_size)
    self.frames.append(data)
```

### 💾 Step 2: Audio Saved to Temporary File

**Function**: `self.recorder.save_audio(temp_filename)`

- It writes `self.frames` (list of audio chunks) to a `.wav` file
- Used for sending to OpenAI Whisper

### 🧠 Step 3: Speech Transcribed by Whisper (STT)

**Function**: `text_content = await self.audio_to_text.get_text_content(audio_content)`

- Converts `.wav` to `AudioContent` object
- Sends it to OpenAI Whisper model (`whisper-1`)
- Whisper returns the text you spoke

**📍 Code:**

```python
audio_content = AudioContent.from_audio_file(temp_filename)
text_content = await self.audio_to_text.get_text_content(audio_content)
```

**✅ Result**: Now we have your input as text (e.g., "What's the weather today?")

### 💬 Step 4: Text Sent to GPT (Chat Completion)

**Function**: `response = await self.chat_service.get_chat_message_content(...)`

- Your transcribed text is added to the conversation `ChatHistory`
- A chat completion request is sent to GPT (`gpt-4o-mini`)
- The model generates a response (e.g., "It's sunny and 28°C today.")
- Response is added to the chat history

**📍 Code:**

```python
self.history.add_user_message(user_input)
response = await self.chat_service.get_chat_message_content(...)
self.history.add_assistant_message(response.content)
```

**✅ Result**: Now we have the assistant's reply text.

### 🔊 Step 5: GPT Reply Sent to TTS (Text-to-Speech)

**Function**: `audio_content = await self.text_to_audio.get_audio_content(text, ...)`

- GPT response is sent to OpenAI TTS model (`tts-1`)
- TTS returns audio content (e.g., WAV data of the assistant saying: "It's sunny and 28°C today.")

**📍 Code:**

```python
audio_content = await self.text_to_audio.get_audio_content(
    text,
    OpenAITextToAudioExecutionSettings(response_format="wav")
)
```

**✅ Result**: We now have audio data ready to play.

### ▶️ Step 6: Audio Played Back to User

**Function**: `self.player.play_audio(audio_content.data)`

- Uses PyAudio to open a speaker stream
- Plays the audio data returned by TTS

**📍 Code:**

```python
stream.write(audio_data)
```

**✅ You now hear the assistant reply out loud.**

### 🔁 Step 7: Back to the Loop

Once playback is done, it goes back to waiting for the next Enter key press. You can:

- Speak again
- Say "exit" to quit

---

## 📊 Flow Summary

```mermaid
flowchart TD
    A[Press Enter] --> B[Record Audio 5s]
    B --> C[Save as WAV]
    C --> D[Whisper: Speech → Text]
    D --> E[ChatGPT: Text → Reply]
    E --> F[TTS: Reply → Audio]
    F --> G[Play Audio]
    G --> H[Wait for next interaction]
    H --> A

    style A fill:#e1f5fe
    style D fill:#f3e5f5
    style E fill:#e8f5e8
    style F fill:#fff3e0
```

## 🔧 Technical Details

### AI Models Used:

- **Whisper-1**: Speech-to-Text conversion
- **GPT-4o-mini**: Natural language processing and response generation
- **TTS-1**: Text-to-Speech conversion

### Audio Processing:

- **Sample Rate**: 16,000 Hz
- **Channels**: 1 (mono)
- **Format**: WAV
- **Duration**: 5 seconds per recording

### Error Handling:

- Temporary file cleanup after processing
- Graceful error messages for failed transcription
- Fallback to text output if audio playback fails

### Memory Management:

- **Chat History**: Stored in RAM using Semantic Kernel's ChatHistory
- **Audio Files**: Temporary WAV files (deleted after processing)
- **Session State**: In-memory only (lost on program restart)
