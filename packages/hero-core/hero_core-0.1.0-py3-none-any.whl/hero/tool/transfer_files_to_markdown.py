from typing import Any, Dict, List
import traceback
from util import log, config, function, agent, stream
import tool
import os
import re

class TransferFilesToMarkdown:
    def __init__(self):
        self.name = "transfer_files_to_markdown"
        self.prompt = """
<tool name="transfer_files_to_markdown">
    <desc>Convert non-text files (.pdf, .docx, .pptx, .xlsx, etc.) to markdown format and write them to an independent file.</desc>
    <params>
        <read_file_list type="list">The files to transfer to markdown format.</read_file_list>
    </params>
    <example>
        {
            "tool": "transfer_files_to_markdown",
            "params": {
                "read_file_list": ["file1.pdf", "file2.xlsx"]
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
            
            markdown_content = ""
            md_file_list = []
            
            for file in read_file_list:
                file_path = os.path.join(caller.get("dir") or "", file)

                if file.endswith(".pdf"):
                    markdown_content += function.transfer_pdf_to_markdown(file_path)
                elif file.endswith(".docx"):
                    markdown_content += function.transfer_docx_to_markdown(file_path)
                elif file.endswith(".pptx"):
                    markdown_content += function.transfer_pptx_to_markdown(file_path)
                elif file.endswith(".xlsx"):
                    markdown_content += function.transfer_xlsx_to_markdown(file_path)
                else:
                    raise ValueError(f"Unsupported file type: {file}")
                    
                md_file_name = os.path.splitext(file)[0] + ".md"
                md_file_path = os.path.join(caller.get("dir") or "", md_file_name)
                with open(md_file_path, "w", encoding="utf-8") as f:
                    f.write(markdown_content)

                md_file_list.append(md_file_name)

            message = f"Converted files: {', '.join(md_file_list)}"

            return {
                "status": "success",
                "message": message,
                "md_file_list": md_file_list,
            }
        except Exception as e:
            log.error(f"Error transferring files to markdown: {e}")
            log.error(traceback.format_exc())
            return {
                "status": "error",
                "message": str(e),
            }

tool.hub.register(TransferFilesToMarkdown)