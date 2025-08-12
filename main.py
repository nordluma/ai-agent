import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions.get_files_info import schema_get_files_info

SYSTEM_PROMPT = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
    ]
)

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
    config=types.GenerateContentConfig(
        tools=[available_functions], system_instruction=SYSTEM_PROMPT
    ),
)

if response.function_calls:
    for function_call_part in response.function_calls:
        print(
            f"Calling function: {function_call_part.name}({function_call_part.args})",
        )
else:
    print(response.text)

if verbose_output:
    print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
    print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
