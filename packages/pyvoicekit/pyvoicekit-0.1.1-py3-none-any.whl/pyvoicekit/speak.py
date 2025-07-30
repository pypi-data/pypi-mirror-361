import pyttsx3

def speak(text: str):
    """
    Convert text to speech.
    :param text: The text string to be spoken.
    """
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()