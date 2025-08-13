import os

from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes content to a file within the working directory. Creates the file if it doesn't exist.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to write, relative to the working directory",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Content to write to the file",
            ),
        },
        required=["file_path", "content"],
    ),
)


def write_file(working_directory, file_path, content):
    abs_working_dir = os.path.abspath(working_directory)
    file_path = os.path.abspath(os.path.join(working_directory, file_path))
    if not file_path.startswith(abs_working_dir):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

    target_dir = os.path.dirname(file_path)
    try:
        if not os.path.exists(target_dir):
            print(f"creating dir: {target_dir}")
            os.makedirs(target_dir)
        with open(file_path, "w") as f:
            f.write(content)
    except Exception as e:
        return f"Error writing to file: {e}"

    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
