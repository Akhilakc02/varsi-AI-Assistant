from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import time
import mtranslate as mt

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en-IN")  # Default to English India

# HTML content for Web Speech API
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript + " ";
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
        }
    </script>
</body>
</html>'''

# Inject language into the HTML
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Save the HTML file
os.makedirs("Data", exist_ok=True)
with open("Data/Voice.html", "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# File path
current_dir = os.getcwd()
Link = f"{current_dir}/Data/Voice.html"

# Chrome options
chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")  # Headless mode (no window)
chrome_options.add_argument("user-agent=Mozilla/5.0")

# Create driver using webdriver-manager (no path issues)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Temp folder setup
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding='utf-8') as file:
        file.write(Status)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you"]

    if any(word + " " in new_query for word in question_words):
        new_query = new_query.rstrip(".?!") + "?"
    else:
        new_query = new_query.rstrip(".?!") + "."

    return new_query.capitalize()

def UniversalTranslator(Text):
    try:
        translated = mt.translate(Text, "en", "auto")
        return translated if translated else Text
    except Exception:
        return Text

def SpeechRecognition():
    driver.get("file:///" + Link)
    driver.find_element(By.ID, "start").click()

    while True:
        try:
            Text = driver.find_element(By.ID, "output").text
            if Text:
                driver.find_element(By.ID, "end").click()
                if "exit" in Text.lower() or "stop" in Text.lower():
                    return "Exit"
                if InputLanguage.lower().startswith("en"):
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))
        except Exception:
            pass
        time.sleep(0.5)

# Run loop
if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        if Text.lower() == "exit":
            print("Speech recognition exited.")
            break
        print("User said:", Text)
