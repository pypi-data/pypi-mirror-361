import os
from dotenv import load_dotenv
import google.generativeai as genai
import time as T

load_dotenv()

def T1() :
 # User Inputs
 x = input("Enter the text to translate: ")
 t = input("Enter the target language (e.g., French, Hindi): ")

 # Configure Gemini API key
 genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  

 # Initialize the model
 model = genai.GenerativeModel("gemini-1.5-flash")

 # Generate translation
 response = model.generate_content(
     f"You are a translation agent. Translate this to {t}: '{x}'"
 )

 T.sleep(2)

 # Output the translation
 print("\nTranslated Text:")
 print(response.text)
def T2() :
 # User Inputs
 x = input("Enter the text to Indetify: ")

 # Configure Gemini API key
 genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  

 # Initialize the model
 model = genai.GenerativeModel("gemini-1.5-flash")

 # Generate translation
 response = model.generate_content(
     f"You are a Language agent. Identify the language in this Text '{x}'"
 )

 T.sleep(2)

 # Output the Recognisation
 print(response.text)
def T3() :
 # User Inputs
 x = input("Enter the text to Understand: ")

 # Configure Gemini API key
 genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  

 # Initialize the model
 model = genai.GenerativeModel("gemini-1.5-flash")

 # Generate translation
 response = model.generate_content(
     f"You are a translation agent. and Explain breifly the Builder of {x} sentence, Phases, Clauses, Helping verb, verb, idiom, and many more if any. "
 )

 T.sleep(2)

 # Output the translation
 print("\nTranslated Text:")
 print(response.text)

def T4() :
 k = 1
 while k == 1 :
  # User Inputs
  x = input("Enter: ")

  # Configure Gemini API key
  genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
  # Exit
  if x == "exit":
   print("Exiting. . .")
   T.sleep(1)
   k = 0
  # Initialize the model
  model = genai.GenerativeModel("gemini-1.5-flash")

  # Generate translation
  response = model.generate_content(
      f"You are a translator ChatBot and A Guide. You're name is Pablo, Respond to this: {x}"
  )

  T.sleep(2)

  # Output the translation
  print(response.text)
