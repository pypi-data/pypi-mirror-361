import os
from typing import Any, Dict, List
import traceback
from util import log, config, function
import tool

class CheckImageFromFile:
    def __init__(self):
        self.name = "check_image_from_file"
        self.prompt = """
<tool name="check_image_from_file">
    <desc>View an image and use a large multimodal model capability to identify the image content.</desc>
    <params>
        <read_file_list type="list">Get the file name from context, can be one or more image files, must be image files(like .png, .jpg, .jpeg, .gif, .bmp, .webp, etc.)</read_file_list>
    </params>
    <example>
        {
            "tool": "check_image_from_file",
            "params": {
                "read_file_list": ["example.png", "example2.jpg"]
            }
        }
    </example>
</tool>
"""

    def get_name(self):
        return self.name
    
    def get_prompt(self):
        return self.prompt
    
    async def invoke(self, params: Dict[str, str], caller: Dict[str, str]) -> Dict[str, Any]:
        try:
            read_file_list = params.get("read_file_list")
            if not read_file_list:
                raise ValueError("Missing required parameter: read_file_list")
            
            read_file_path_list = []
            for read_file in read_file_list:
                read_file_path = os.path.join(caller.get("dir", ""), read_file)
                read_file_path_list.append(read_file_path)

            for read_file_path in read_file_path_list:
                if not os.path.exists(read_file_path):
                    raise ValueError(f"File not found: {read_file_path}")
            
            result_list = []
            for read_file_path in read_file_path_list:
                result = function.image_to_base64_url(read_file_path)
                if result.get("status") == "error":
                    raise ValueError(result.get("message"))
                base64_url = result.get("base64_url")
                result_list.append(base64_url)

            message = f"Image has been transferred to base64 data url, and add to the **context**."

            return {
                "status": "success",
                "message": message,
                "additional_images": result_list,
            }
        except Exception as e:
            log.error(f"Error checking image from file: {e}")
            log.error(traceback.format_exc())
            return {
                "status": "error",
                "message": str(e),
            }
        
tool.hub.register(CheckImageFromFile)
