# type: ignore
import os
from pathlib import Path

output_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "output")
)


def save_to_file(
    file_content: str,
    file_name: str,
    folder_name: str | None = None,
    absolute_folder_path: str | None = None,
) -> str:
    global output_folder
    if Path(file_name).suffix == "":
        file_name += ".txt"

    if folder_name is not None and absolute_folder_path is not None:
        raise AttributeError

    if folder_name is not None:
        file_folder = f"{output_folder}/{folder_name}"

    elif absolute_folder_path is not None:
        file_folder = f"{absolute_folder_path}"

    else:
        file_folder = f"{output_folder}"

    if not os.path.exists(file_folder):
        os.makedirs(file_folder)

    file_path: Path = Path(f"{file_folder}/{file_name}")

    with open(file_path, "w") as f:  # mypy crashes on this line, i don't know why
        f.write(file_content)

    f.close()

    return str(file_path)
