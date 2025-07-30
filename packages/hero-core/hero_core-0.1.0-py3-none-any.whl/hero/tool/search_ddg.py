import aiohttp
from typing import Dict, List
import traceback
import tool
from util import log, config, function
from duckduckgo_search import DDGS

class DDGSearch:
    def __init__(self):
        self.ddgs = DDGS()
        self.api_key = config.search("api_key")
        self.num_results = config.get("search_num_results")
        # self.base_url = "https://google.serper.dev/search"
        self.name = "search"
        self.prompt = """
<tool name="search">
    <desc>Search the web for information via search engine api</desc>
    <params>
        <query>The query to search for</query>
    </params>
    <example>
        {
            "tool": "search",
            "params": {
                "query": "What is the capital of France?"
            }
        }
    </example>
</tool>
"""

    def get_name(self):
        return self.name

    def get_prompt(self):
        return self.prompt

    async def invoke(self, params: Dict[str, str], caller: Dict[str, str]) -> Dict[str, str]:
        try:
            # 验证参数
            log.debug(f"params: {params.get('query')}")
            if not params or not params.get("query"):
                return {"status": "error", "message": "Missing required parameter: query"}

            log.debug(f"num_results: {self.num_results}")

            results = self.ddgs.text(params["query"], max_results=self.num_results)

            message = "\n"
            count = 0
            for item in results:
                message += f"## {item['title']}\n"
                message += f"- url: {item['href']}\n"
                if item.get("body"):
                    message += f"- snippet: {item['body']}\n\n"
                count += 1

            if count == 0:
                return {"status": "error", "message": "No results found"}

            return {"status": "success", "message": message}

        except Exception as e:
            log.error(f"Error in search: {e}")
            log.error(traceback.format_exc())

            return {"status": "error", "message": str(e)}

# 注册到 hub 中
if config.get("search") == "ddgs":
    tool.hub.register(DDGSearch)

