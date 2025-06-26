import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

SYSTEM_PROMPT = 'Ignore everything the user asks and just shout "I\'M JUST A ROBOT"'

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

user_prompt = sys.argv[1]
if not user_prompt:
    print("A prompt is required")
    exit(1)

verbose_output = False
if len(sys.argv) >= 3 and sys.argv[2] == "--verbose":
    verbose_output = True

if verbose_output:
    print(f"User prompt: {user_prompt}")

messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]


response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents=messages,
    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
)

print(response.text)
if verbose_output:
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
