import os
from dotenv import load_dotenv
import google.generativeai as genai
import time as T

# Load environment variables from .env file
load_dotenv()
a = os.getenv("GOOGLE_API_KEY")

def ConAi():
    """Configure API Key if not already set"""
    global a
    if not a:
        a = input("Enter API Key: ")

def T1(x="", t=""):
    """Translate text to target language"""

    # User Inputs
    if not x.strip():
        x = input("Enter the text to translate: ")
    if not t.strip():
        t = input("Enter the target language (e.g., French, Hindi): ")

    genai.configure(api_key=a)
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(
        f"You are a translation agent. Translate this to {t}: '{x}'"
    )
    T.sleep(2)
    print("\nTranslated Text:")
    print(response.text)

def T2(x=""):
    """Identify language of a given text"""
    if not x.strip():
        x = input("Enter the text to identify: ")

    genai.configure(api_key=a)
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(
        f"You are a language agent. Identify the language in this text: '{x}'"
    )
    T.sleep(2)
    print(response.text)

def T3(x=""):
    """Understand and explain the grammar structure of a sentence"""
    

    if not x.strip():
        x = input("Enter the text to understand: ")

    genai.configure(api_key=a)
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(
        f"You are a grammar expert. Explain the builder of the sentence '{x}' including phrases, clauses, helping verbs, idioms, etc."
    )
    T.sleep(2)
    print("\nExplanation:")
    print(response.text)

def T4():
    """Interactive chatbot named Pablo"""
    
    while True:
        x = input("Enter: ")
        if x.strip().lower() == "exit":
            print("Exiting...")
            T.sleep(1)
            break

        genai.configure(api_key=a)
        model = genai.GenerativeModel("gemini-1.5-flash")

        response = model.generate_content(
            f"You are a translator ChatBot and a guide. Your name is Pablo. Respond to this: {x}"
        )
        T.sleep(2)
        print(response.text)
import inspect

import inspect
import textwrap

def GameSafe(func):
    """
    Returns the code inside a function (only the body), as a string.
    """
    try:
        source = inspect.getsource(func)  
        lines = source.splitlines()       
        body_lines = lines[1:]            
        dedented = textwrap.dedent('\n'.join(body_lines))  
        return dedented
    except Exception as e:
        return f"# Error fetching code: {e}"
