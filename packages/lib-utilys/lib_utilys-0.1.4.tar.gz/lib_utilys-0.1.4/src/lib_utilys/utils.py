import json
import logging

logger = logging.getLogger(__name__)

def clean_special_characters(string):
        """Replaces special characters in a string with a hyphen."""
        special_chars = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]
        for char in special_chars:
            string = string.replace(char, "-")
        return string

def read_json(path: str) -> dict:
    """Reads a JSON file and returns its content as a dictionary."""
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception:
        logger.exception("Failed to read JSON file at %s", path)
        return {}