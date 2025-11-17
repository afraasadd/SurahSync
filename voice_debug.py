"""
Debug voice recording and transcription
"""

import speech_recognition as sr
import time


def test_voice_debug():
    print("🎯 VOICE DEBUG TEST")
    print("=" * 50)

    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Test microphone list
    print("📞 Available microphones:")
    try:
        mics = sr.Microphone.list_microphone_names()
        for i, mic in enumerate(mics):
            print(f"  {i}: {mic}")
    except:
        print("  Could not list microphones")

    # Test recording
    print("\n🎤 Testing recording...")
    try:
        with sr.Microphone() as source:
            print("   Adjusting for noise...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print("   Speak now for 5 seconds...")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            print("   ✅ Recording successful!")

            # Test transcription
            print("\n🔄 Testing transcription...")
            try:
                text = recognizer.recognize_google(audio, language="ar-AR")
                print(f"   ✅ Transcribed: '{text}'")
                return text
            except sr.UnknownValueError:
                print("   ❌ Could not understand audio")
            except sr.RequestError as e:
                print(f"   ❌ API error: {e}")
                print("   💡 Check internet connection!")

    except sr.WaitTimeoutError:
        print("   ❌ No speech detected - speak louder!")
    except Exception as e:
        print(f"   ❌ Recording error: {e}")

    return None


if __name__ == "__main__":
    result = test_voice_debug()
    if result:
        print(f"\n🎉 SUCCESS: '{result}'")
    else:
        print("\n❌ Voice test failed")

    input("\nPress Enter to exit...")
