from glob import glob
from typing import Dict, List

from .paths import *


def read_characters_from_files(files: List[str], frecent: List[str], use_additional: bool) -> Dict[str, str]:
    all_characters: Dict[str, List[str]] = {}

    if frecent:
        for character in frecent:
            all_characters[character] = []

    for file in __resolve_all_filenames(files, use_additional):
        characters_from_file = __load_from_file(file)
        for line in characters_from_file:
            parsed_line = line.split(" ", 1)
            all_characters.setdefault(parsed_line[0], []).append(parsed_line[1]) if 1 < len(parsed_line) else ""

    return {character: ", ".join(descriptions) for character, descriptions in all_characters.items()}


def __resolve_all_filenames(file_names: List[str], use_additional: bool) -> List[Path]:
    resolved_file_names = []
    for file_name in file_names:
        resolved_file_names += __resolve_filename(file_name, use_additional)

    return resolved_file_names


def __resolve_filename(file_name: str, use_additional: bool) -> List[Path]:
    resolved_file_names = []

    for file in glob(file_name):
        resolved_file_names.append(Path(file))

    if resolved_file_names:
        return resolved_file_names

    for file in (Path(__file__).parent / "data").glob(file_name if "*" in file_name else file_name + "*"):
        resolved_file_names.append(file)
        resolved_file_names += __load_addtional_files(file, use_additional)

    if resolved_file_names:
        return resolved_file_names

    if file_name == "all":
        nested_file_names = [
            __resolve_filename(file.stem, use_additional) for file in (Path(__file__).parent / "data").glob("*.csv")
        ]
        resolved_file_names += [file_name for file_names in nested_file_names for file_name in file_names]
        return resolved_file_names

    raise FileNotFoundError(f"Couldn't find file {file_name!r}")


def __load_addtional_files(original_file: Path, use_additional: bool) -> List[Path]:
    additional_files = []
    custom_additional_file = custom_additional_files_location / f"{original_file.stem}.additional.csv"
    if custom_additional_file.is_file():
        additional_files.append(custom_additional_file)
    provided_additional_file = Path(__file__).parent / "data" / "additional" / f"{original_file.stem}.csv"
    if use_additional and provided_additional_file.is_file():
        additional_files.append(provided_additional_file)

    return additional_files


def __load_from_file(file: Path) -> List[str]:
    return file.read_text().strip("\n").split("\n")
