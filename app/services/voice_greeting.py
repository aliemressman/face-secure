import pyttsx3

# Motoru bir kez oluştur ve hafızada tut
_engine = None

def init_tts():
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
        _engine.setProperty('rate', 160) # Konuşma Hızı
        _engine.setProperty('volume',1.0)
        
def say(text):
    init_tts()
    _engine.say(text)
    _engine.runAndWait()
    _engine.stop()