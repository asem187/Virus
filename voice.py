import os

try:
    import speech_recognition as sr
except ImportError:  # pragma: no cover - optional dependency
    sr = None

try:
    import pyttsx3
except ImportError:  # pragma: no cover - optional dependency
    pyttsx3 = None


def record_and_transcribe(timeout: int = 5) -> str:
    """Record from microphone and return recognized text using Whisper."""
    if sr is None:
        raise RuntimeError("speech_recognition is not installed")

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source, phrase_time_limit=timeout)
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is required")
        return recognizer.recognize_whisper_api(audio, api_key=api_key)
    except sr.UnknownValueError:
        return ""


def speak(text: str) -> None:
    """Speak ``text`` using pyttsx3 if available."""
    if pyttsx3 is None:
        return
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
