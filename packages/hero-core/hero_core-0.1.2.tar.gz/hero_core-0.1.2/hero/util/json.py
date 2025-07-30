"""
    json util
"""
import json
import re
from typing import Any

def parse_json(json_string: str) -> Any:
    """
    parse json string
    """
    json_pattern = r'(\{[\s\S]*\}|\[[\s\S]*\])'
    match = re.search(json_pattern, json_string)
    
    if match:
        json_content = match.group(1)
        return json.loads(json_content)
    else:
        # if no match, try to parse the string as json
        return json.loads(json_string)