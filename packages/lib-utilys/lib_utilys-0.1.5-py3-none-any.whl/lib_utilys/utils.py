import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def clean_special_characters(string):
        """Replaces special characters in a string with a hyphen."""
        special_chars = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]
        for char in special_chars:
            string = string.replace(char, "-")
        return string

def read_json(path: Path) -> dict:
    """Reads a JSON file and returns its content as a dictionary."""
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception:
        logger.exception("Failed to read JSON file at %s", path)
        return {}

    def write_json(path: Path, data: dict):
        """Writes data to a JSON file."""
        try:
            with open(path, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            logger.exception("Error writing JSON file at %s", path)