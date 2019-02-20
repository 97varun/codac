import speech_recognition as sr
import sys

d_correct = {
    'declare a variable of type integer and name x': 'int x;'
}

d_wrong = {
    'declare a variable x': 'Type missing'
}

# obtain audio from the microphone
r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    sys.stdout.flush()
    audio = r.listen(source)

# recognize speech using Google Speech Recognition
try:
    # for testing purposes, we're just using the default API key
    # to use another API key, use
    # `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
    # instead of `r.recognize_google(audio)`
    text = r.recognize_google(audio)
    if text in d_correct:
        print(d_correct[text])
    elif text in d_wrong:
        # do text to speech here
        import win32com.client as wincl
        speak = wincl.Dispatch("SAPI.SpVoice")
        speak.Speak("Type missing")
    sys.stdout.flush()
except sr.UnknownValueError:
    print("Google could not understand audio")
except sr.RequestError as e:
    print("Could not request results from GSR {0}".format(e))
