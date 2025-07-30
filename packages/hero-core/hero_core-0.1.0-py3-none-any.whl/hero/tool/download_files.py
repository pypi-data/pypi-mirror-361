from typing import Dict
import traceback
from hero.util import log, function

DOWNLOAD_TIMEOUT = 60000


class DownloadFiles:
    def __init__(self):
        self.name = "download_files"
        self.prompt = """
<tool name="download_files">
    <desc>Download files from the internet</desc>
    <params>
        <url_list type="list">The url list to download, don't generate the url by yourself, just select from the **context**</url_list>
    </params>
    <example>
        {
            "tool": "download_files",
            "params": {
                "url_list":  ["https://example1.com/file1.pdf", "https://example2.com/file2.txt"]
            }
        }
    </example>
</tool>
"""

    def get_name(self):
        return self.name

    def get_prompt(self):
        return self.prompt

    async def invoke(
        self, params: Dict[str, str], caller: Dict[str, str]
    ) -> Dict[str, str]:
        try:
            url_list = params.get("url_list")

            if not url_list:
                raise ValueError("url_list is required")

            message = ""

            for index, url in enumerate(url_list):
                file_path = function.download_file(url, caller.get("dir", ""))

                if file_path:
                    message += f"- download {url} success, save to {file_path}\n\n"
                else:
                    message += f"- download {url} failed, content is empty\n\n"

            return {
                "status": "success",
                "message": message
            }
        except Exception as e:
            log.error(f"下载文件失败: {str(e)}")
            log.error(traceback.format_exc())
            return {
                "status": "error",
                "message": str(e)
            }
