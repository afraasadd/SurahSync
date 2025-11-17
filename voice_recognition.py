"""
Enhanced Voice Recognition with Better Debugging
"""

import speech_recognition as sr
import threading
import time


class VoiceRecorder:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.is_recording = False
        self.current_audio = None

        print("🔊 Initializing microphone...")
        try:
            self.microphone = sr.Microphone()
            print("✅ Microphone found")
        except Exception as e:
            print(f"❌ Microphone error: {e}")
            self.microphone = None
            return

        print("🎚️ Calibrating for ambient noise...")
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=3)
            print("✅ Microphone calibrated")
        except Exception as e:
            print(f"❌ Calibration failed: {e}")

    def record_audio(self, duration=10):
        """Record audio from microphone with enhanced error handling"""
        if not self.microphone:
            print("❌ No microphone available")
            return None

        try:
            print(f"🎤 Recording for {duration} seconds...")
            print("💡 SPEAK CLEARLY IN ARABIC NOW!")

            with self.microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=20,
                    phrase_time_limit=duration
                )

            print("✅ Recording complete!")
            self.current_audio = audio
            return audio

        except sr.WaitTimeoutError:
            print("❌ No speech detected within timeout")
            print("💡 Tips: Speak louder and clearer")
            return None
        except Exception as e:
            print(f"❌ Recording error: {e}")
            return None

    def transcribe_audio(self, audio):
        """Transcribe Arabic audio to text with multiple fallbacks"""
        if audio is None:
            print("❌ No audio to transcribe")
            return ""

        print("🔄 Transcribing Arabic speech...")

        # Try Google Speech Recognition first
        try:
            text = self.recognizer.recognize_google(audio, language="ar-AR")
            if text and text.strip():
                print(f"✅ Transcribed: '{text}'")
                return text.strip()
            else:
                print("❌ Empty transcription received")
                return ""

        except sr.UnknownValueError:
            print("❌ Google could not understand the Arabic speech")
            print("💡 Possible reasons:")
            print("   - Background noise too loud")
            print("   - Speech too fast/unclear")
            print("   - Microphone quality issues")
            return ""

        except sr.RequestError as e:
            print(f"❌ Google API error: {e}")
            print("💡 Check your internet connection!")
            return ""

        except Exception as e:
            print(f"❌ Unexpected transcription error: {e}")
            return ""

    def quick_record_and_transcribe(self, duration=12):
        """Quick record and transcribe with detailed logging"""
        print(f"\n{'=' * 50}")
        print("🎯 STARTING VOICE RECOGNITION")
        print(f"{'=' * 50}")

        audio = self.record_audio(duration)
        if audio:
            result = self.transcribe_audio(audio)
            print(f"{'=' * 50}")
            print(f"📝 FINAL RESULT: '{result}'")
            print(f"{'=' * 50}")
            return result
        else:
            print("❌ No audio recorded")
            return ""

    def test_microphone(self):
        """Test if microphone is working"""
        if not self.microphone:
            return False, "No microphone detected"

        try:
            with self.microphone as source:
                print("Testing microphone... say something!")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
                return True, "Microphone working"
        except:
            return False, "Microphone not responding"


# Test function
def test_voice_system():
    """Comprehensive voice system test"""
    print("🔊 COMPREHENSIVE VOICE SYSTEM TEST")
    recorder = VoiceRecorder()

    # Test microphone
    mic_ok, mic_msg = recorder.test_microphone()
    print(f"Microphone: {mic_msg}")

    if mic_ok:
        # Test recording and transcription
        text = recorder.quick_record_and_transcribe(duration=8)
        return text
    else:
        print("❌ Cannot proceed - microphone issues")
        return None


if __name__ == "__main__":
    result = test_voice_system()
    if result:
        print(f"🎉 Test successful: '{result}'")
    else:
        print("❌ Voice system test failed")