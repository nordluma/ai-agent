import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions.get_files_info import get_files_info, schema_get_files_info
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.run_python_file import run_python_file, schema_run_python_file
from functions.write_file import schema_write_file, write_file

SYSTEM_PROMPT = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)


def main():
    load_dotenv()

    verbose = "--verbose" in sys.argv
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    if not args:
        usage()

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    user_prompt = " ".join(args)
    if verbose:
        print(f"User prompt: {user_prompt}")

    messages = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]
    generate_content(client, messages, verbose)


def generate_content(client, messages, verbose):
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=SYSTEM_PROMPT
        ),
    )

    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    if not response.function_calls:
        return response.text

    fn_responses = []
    for fn_call_part in response.function_calls:
        fn_call_result = call_function(fn_call_part, verbose)
        if not fn_call_result.parts or not fn_call_result.parts[0].function_response:
            raise Exception("empty function call result")

        if verbose:
            print(f"-> {fn_call_result.parts[0].function_response.response}")
        fn_responses.append(fn_call_result.parts[0])

    if not fn_responses:
        raise Exception("no function responses generated")


def call_function(fn_call_part: types.FunctionCall, verbose=False):
    if verbose:
        print(f"Calling function: {fn_call_part.name}({fn_call_part.args})")
    else:
        print(f" - Calling function: {fn_call_part.name}")

    fn_map = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "run_python_file": run_python_file,
        "write_file": write_file,
    }

    fn_name = fn_call_part.name
    if fn_name not in fn_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=fn_name or "unknown",
                    response={"error": f"Unknown function: {fn_name}"},
                )
            ],
        )

    args = dict(fn_call_part.args or {})
    args["working_directory"] = "./calculator"
    fn_result = fn_map[fn_name](**args)
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=fn_name, response={"result": fn_result}
            )
        ],
    )


def usage():
    print("AI Code Assistant")
    print('\nUsage: uv run main.py "your prompt here" [--verbose]')
    print('Example: uv run main.py "How do I fix the calculator?"')
    sys.exit(1)


if __name__ == "__main__":
    main()
