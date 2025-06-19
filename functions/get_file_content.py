import os

MAX_CHARS = 10_000


def get_file_content(working_directory, file_path):
    abs_working_dir = os.path.abspath(working_directory)
    file_path = os.path.abspath(os.path.join(working_directory, file_path))
    if not file_path.startswith(abs_working_dir):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(file_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        with open(file_path, "r") as f:
            file_content = f.read(MAX_CHARS)

            if len(file_content) >= MAX_CHARS:
                return (
                    file_content
                    + f"... File {file_path} truncated at {MAX_CHARS} characters"
                )
            return file_content
    except Exception as e:
        return f"Error reading file content: {e}"
