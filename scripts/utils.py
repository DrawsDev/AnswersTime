import os
import sys
import json

def asset_path(relative_path: str) -> str:
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS + f"\{relative_path}"
    return os.path.join(relative_path)

def get_files_from(path: str) -> list:
    for _full_path, _sub_files, files in os.walk(path):
        return files
    return []

def read_json(file_path: str) -> dict:
    if not file_path.endswith(".json"):
        return {}
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def set_character(string: str, character: str, position: int) -> str:
    if character == "":
        return string[:position] + string[position + 1:]
    else:
        return string[:position + 1] + character + string[position + 1:]
