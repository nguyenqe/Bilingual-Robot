import speech_recognition
from gtts import gTTS
from openai import OpenAI
import pygame
import re

client = OpenAI(
  api_key=""
)

robot_ear = speech_recognition.Recognizer()
robot = ""

def detect_language(text):
    """Simple language detection based on Vietnamese characters"""
    vietnamese_chars = re.compile(r'[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]')
    if vietnamese_chars.search(text.lower()):
        return "vi"
    return "en"

pygame.mixer.init()
while True:
    with speech_recognition.Microphone() as mic:
        print("Robot: Tôi đang nghe / I'm listening....")
        audio = robot_ear.listen(mic)

    print("Robot: ...")

    you = ""
    detected_lang = "en"  
    
    try:
        you = robot_ear.recognize_google(audio, language="vi-VN")
        detected_lang = "vi"
    except:
        try:
            you = robot_ear.recognize_google(audio, language="en-US")
            detected_lang = "en"
        except:
            you = ""

    if you and detect_language(you) != detected_lang:
        try:
            if detected_lang == "vi":
                you = robot_ear.recognize_google(audio, language="en-US")
                detected_lang = "en"
            else:
                you = robot_ear.recognize_google(audio, language="vi-VN")
                detected_lang = "vi"
        except:
            pass  

    print("You: " + you)
    
    try:
        if detected_lang == "vi":
            system_message = "Trả lời ngắn gọn dễ hiểu bằng tiếng Việt."
        else:
            system_message = "Respond briefly and clearly in English."
            
        completion = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages= [
                {"role": "system", "content": system_message},
                {"role": "user", "content": you}
                ],
                temperature= 0.7,
                max_tokens=100
        )

        robot = (completion.choices[0].message.content)
    except:
        if detected_lang == "vi":
            robot = "Tôi đang bận, vui lòng để lại lời nhắn"
        else:
            robot = "I'm busy right now, please leave a message"
        
    print("Robot: " + robot)

    if detected_lang == "vi":
        tts = gTTS(text=robot, lang='vi', slow=False)
        tts.save("voice.mp3")
    else:
        audio_response = client.audio.speech.create(
            model="tts-1",
            voice = "nova",
            input = robot
        )
        with open("voice.mp3", "wb") as file:
            file.write(audio_response.content)
    
    pygame.mixer.music.load("voice.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue