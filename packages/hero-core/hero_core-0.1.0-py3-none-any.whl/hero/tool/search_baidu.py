"""
search tool
"""
import aiohttp
from typing import Dict, List
import traceback
import tool
import time
from util import log, config, BceCredentials, sign

class BaiduSearch:
    def __init__(self):
        self.num_results = config.get("search_num_results")
        self.base_url = "http://aihc.bj.baidubce.com/v1/aisearch/search"
        self.ak=config.search("ak")
        self.sk=config.search("sk")
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

            credentials = BceCredentials(self.ak, self.sk)
            http_method = "GET"
            path = "/v1/aisearch/search"
            timestamp = time.time()
            time_struct = time.gmtime(timestamp)
            formatted_date = time.strftime('%Y-%m-%dT%H:%M:%SZ', time_struct)
            header_sign = {
                "host": "aihc.bj.baidubce.com",
                "x-bce-date": formatted_date
            }
            baidu_query=params.get("query")
            params_sign = {"query": baidu_query,
                "pn": 1,
                "num": self.num_results
            }
            signature = sign(credentials, http_method, path, header_sign, params_sign, int(timestamp), 1800, header_sign)
            log.debug(f"num_results: {self.num_results}")
            headers = {
                "Content-Type": "application/json",
                "Authorization": signature,
                "x-bce-date": formatted_date,
            }

            url = f"{self.base_url}?query={baidu_query}&pn=1&num={self.num_results}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        log.error(f"Search API error: {response.status}")
                        log.error(f"Search API error: {response.text}")
                        return {"status": "error", "message": "Search API error"}

                    result = await response.json()

                    message = "\n"
                    count = 0
                    for item in result.get("items", []):
                        message += f"## {item['title']}\n"
                        message += f"- url: {item['link']}\n"
                        if item.get("snippet"):
                            message += f"- snippet: {item['snippet']}\n\n"
                        count += 1

                    if count == 0:
                        return {"status": "error", "message": "No results found"}

                    return {"status": "success", "message": message}

        except Exception as e:
            log.error(f"Error in search: {e}")
            log.error(traceback.format_exc())

            return {"status": "error", "message": str(e)}
     
# 注册到 hub 中
if config.get("search") == "baidu_search":
    tool.hub.register(BaiduSearch)
