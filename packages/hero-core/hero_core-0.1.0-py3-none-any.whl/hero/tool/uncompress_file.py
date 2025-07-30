import os
from typing import Any, Dict
import zipfile
import tarfile
import gzip
import shutil
import traceback
import tool
from util import log

class UncompressFile:
    def __init__(self):
        self.name = "uncompress_file"
        self.prompt = """
<tool name="uncompress_file">
    <desc>Uncompress a file</desc>
    <params>
        <read_file_list type="list">The file list to uncompress</read_file_list>
    </params>
    <example>
        {
            "tool": "uncompress_file",
            "params": {
                "read_file_list": ["example.zip", "example.tar", "example.gz"]
            }
        }
    </example>
</tool>
"""

    def get_name(self):
        return self.name

    def get_prompt(self):
        return self.prompt

    async def invoke(self, params: dict, caller: Dict[str, str]) -> Dict[str, Any]:
        try:
            file_list = params.get("read_file_list")
            if not file_list:
                raise ValueError("Missing required parameter: read_file_list")
            
            dir = caller.get("dir")

            uncompressed_files = []
            uncompressed_files_message = ""

            for file in file_list:
                file_path = os.path.join(dir or "", file)
                if file_path.endswith(".zip"):
                    with zipfile.ZipFile(file_path, "r") as zip_ref:
                        zip_ref.extractall(dir or "")
                        files = zip_ref.namelist()
                        uncompressed_files.extend(files)
                elif file_path.endswith(".tar"):
                    with tarfile.open(file_path, "r") as tar_ref:
                        tar_ref.extractall(dir or "")
                        files = tar_ref.getnames()
                        uncompressed_files.extend(files)
                elif file_path.endswith(".gz"):
                    with gzip.open(file_path, "rb") as f:
                        shutil.copyfileobj(f, open(dir or "", "wb"))
                        files = [file_path]
                        uncompressed_files.extend(files)
                else:
                    # 如果文件类型不支持，则返回False
                    raise ValueError(f"Unsupported file type: {file}")
                
                for file in uncompressed_files:
                    uncompressed_files_message += f"- {file}\n"

            # 返回解压后的文件列表
            return {
                "status": "success",
                "message": f"Uncompressed file: \n{uncompressed_files_message}",
            }
            
        except Exception as e:
            log.error(f"{self.name} error: {e}")
            log.error(traceback.format_exc())

            return {
                "status": "error",
                "message": f"{e}",
            }

# 注册到 hub 中
tool.hub.register(UncompressFile)