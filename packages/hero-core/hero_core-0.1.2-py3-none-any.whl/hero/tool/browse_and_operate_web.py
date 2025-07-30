from typing import Dict
import traceback
from hero.agent import Agent
import os
import re
from hero.util import function, stream, log, Browser
import asyncio
import json



class BrowseAndOperateWeb:
    def __init__(self, agent: Agent):
        self.name = "browse_and_operate_web"
        self.prompt = """
<tool name="browse_and_operate_web">
    <desc>Can open a browser, visit a webpage, and read its content. Based on the user's question and goal, it can perform actions on the webpage to obtain the desired key information and write it to the task history and an independent file.</desc>
    <params>
        <url type="string">Get from *context, must be one webpage link</url>
        <purpose type="string">The purpose of browsing and operating this webpage, related to the **user message**</purpose>
        <write_file type="string">Write the obtained key information to a .md file</write_file>
    </params>
    <example>
        {
            "tool": "browse_and_operate_web",
            "params": {
                "url": "https://www.baidfunction.com", "purpose": "Get the latest news", "write_file": "latest_news.md"
            }
        }
    </example>
</tool>
"""
        self.browser = Browser()
        self.agent = agent
        self.run_count = 0
        self.params = None
        self.error_count = 0
        self.notes = []
        self.web_content_limit = 20000

    def custom(self, web_content_limit: int | None = None):
        if web_content_limit is not None:
            self.web_content_limit = web_content_limit

    def get_name(self):
        return self.name

    def get_prompt(self):
        return self.prompt

    async def invoke(
        self, params: Dict[str, str], caller: Dict[str, str]
    ) -> Dict[str, str]:
        try:
            url = params.get("url")
            purpose = params.get("purpose")
            write_file = params.get("write_file")
            self.params = params
            if not url:
                raise ValueError("url is required")

            if not purpose:
                raise ValueError("purpose is required")

            if not write_file:
                raise ValueError("write_file is required")

            await self.browser.start()
            result = await self.browser.open_url(url)
            if result.get("status") == "error":
                return result

            result = await self.browser_run(
                purpose, write_file, images=[], caller=caller
            )

            return result
        except Exception as e:
            log.error(f"BROWSE AND OPERATE WEB ERROR: {e}")
            log.error(traceback.format_exc())

            return {
                "status": "error",
                "message": str(e),
            }
        finally:
            await self.browser.close()

    async def browser_run(self, purpose, write_file, images=[], caller: Dict[str, str] = {}):

        browser_caller = {
            "name": self.agent.get_name(),
            "index": self.run_count,
            "dir": caller.get("dir", ""),
            "log_dir": caller.get("log_dir", ""),
        }

        # 获取当前页面url
        current_url = await self.browser.get_current_page_url()
        content_type = await self.browser.get_content_type()

        additional_images = []

        try:
            self.run_count += 1
            log.info(f"BROWSER RUN COUNT: {self.run_count}")

            # 等待页面加载完成
            log.info("WAIT FOR DOM CONTENT LOADED")
            await self.browser.wait_for_domcontentloaded()

            log.info(f"CONTENT TYPE: {content_type}")

            if "wikipedia.org/w/" in current_url:
                return {
                    "status": "error",
                    "message": "Do not visit the wikipedia `Revision history` (https://en.wikipedia.org/w/) page, use the `program` tool and handle it through programming."
                    + get_notes(self.notes),
                }

            if not "text/html" in content_type:
                # 退出browser
                message = f"The webpage is a downloadable file, please use `download_files` tool to get the information.\nURL: {current_url}"

                with open(
                    os.path.join(caller.get("dir", ""), write_file), "w", encoding="utf-8"
                ) as f:
                    f.write(message)

                return {
                    "status": "error",
                    "message": message,
                }

            # 准备上下文内容
            purpose_content = f"<purpose>{purpose}</purpose>"
            user_message = function.read_user_message(caller)
            log.debug(f"USER MESSAGE: {user_message}")

            web_content = await self.browser.get_content()
            log.info(f"WEB CONTENT LENGTH: {len(web_content)}")
            function.write_file(
                caller.get("log_dir"),
                f"__task_{caller.get('index')}_web_content_{self.run_count}.html",
                web_content,
            )

            # log.info(f"HTML ELEMENTS LENGTH: {len(html_elements)}")
            # function.write_file(caller.get("dir"), f"__task_{caller.get('index')}_html_elements_{self.run_count}.html", html_elements)

            if len(web_content) > self.web_content_limit:

                file_name = f"web_content_index_{caller.get('index')}.html"

                function.write_file(caller.get(
                    "dir"), f"{file_name}", web_content)

                return {
                    "status": "error",
                    "message": f"The webpage content is too long, and the content has been saved to the file: {file_name}, please use `extract_key_info_from_file` tool to get the key information."
                    + get_notes(self.notes),
                }

            # 获取浏览器的页面列表
            page_list = await self.browser.get_page_list()
            current_page_index = await self.browser.get_current_page_index()
            current_page_url = await self.browser.get_current_page_url()

            log.debug(f"PAGE LIST: {page_list}")
            log.debug(f"CURRENT PAGE INDEX: {current_page_index}")
            log.debug(f"CURRENT PAGE URL: {current_page_url}")

            text_of_images = ""

            # 处理图片
            if self.agent.model.is_multimodal:
                log.info("MULTIMODAL MODE")
                if len(images) > 0:
                    web_content = ""
                    log.debug("CHECK IMAGE, NOT READ WEB CONTENT")
                else:
                    screenshot = await self.browser.screenshot()
                    if screenshot:
                        images.append(f"data:image/jpeg;base64,{screenshot}")
                        log.info("PASS WEB SCREENSHOT")
                    else:
                        log.error("SCREENSHOT FAILED")

            # 获取浏览器工具
            tools = self.browser.get_prompts()

            # 获取任务执行历史
            task_execute_history = function.read_task_execute_history(
                browser_caller)

            # 获取工作目录下的文件列表
            workspace_file_list = function.list_files_recursive(
                caller.get("dir", ""))

            # 临时变量
            json_content = ""
            json_processing = False
            content = ""

            # 获取流式响应的返回
            async for token in self.agent.chat(
                message=purpose_content
                + "\n"
                + "Please give me the next task in `json` following the `return_format`.",
                params={
                    "tools": tools,
                    "web_content": web_content,
                    "page_list": page_list,
                    "current_page_index": current_page_index,
                    "current_page_url": current_page_url,
                    "task_execute_history": task_execute_history,
                    "user_message": user_message,
                    "text_of_images": text_of_images,
                    "workspace_file_list": workspace_file_list,
                },
                images=images,
                with_history=False,
            ):
                # 获取json内容
                if token.get("action") == "content_line":
                    # 获取完整的大模型响应内容
                    line = token.get("payload", {}).get("content")
                    content += line

                    # 处理json内容
                    if re.search(r"^```json$", line):
                        json_processing = True
                        line = None
                        stream.push(
                            component="message",
                            action="json_start",
                            timestamp=function.timestamp(),
                            payload=token.get("payload", {}),
                        )
                    elif re.search(r"^```$", line):
                        json_processing = False
                        line = None
                        stream.push(
                            component="message",
                            action="json_end",
                            timestamp=function.timestamp(),
                            payload=token.get("payload", {}),
                        )

                    if not line == None:
                        if json_processing:
                            json_content += line
                            stream.push(
                                component="message",
                                action="json_line",
                                timestamp=function.timestamp(),
                                payload=token.get("payload", {}),
                            )
                        else:
                            # 处理非json内容
                            stream.push(
                                component="message",
                                action="content_line",
                                timestamp=function.timestamp(),
                                payload=token.get("payload", {}),
                            )
                else:
                    # 其他消息直接广播
                    stream.push(
                        component="message",
                        action=token.get("action", ""),
                        timestamp=function.timestamp(),
                        payload=token.get("payload", {}),
                    )

            # 从json中提取工具名称和参数
            if json_content:
                tool_list = json.loads(json_content.strip())
            else:
                tool_list = function.extract_tool_response(content) or json.loads(
                    content.strip()
                )

            log.debug(f"TOOL LIST: {tool_list}")

            if tool_list:
                for tool_dict in tool_list:
                    tool_name = tool_dict.get("tool")
                    tool_params = tool_dict.get("params")
                    log.info(f"EXECUTE TOOL: {tool_name}, {tool_params}")

                    if not tool_name or not tool_params:
                        raise ValueError("NO TOOL NAME OR TOOL PARAMS")

                    # 开始执行工具
                    stream.push(
                        component="message",
                        action="execute_tool_start",
                        timestamp=function.timestamp(),
                        payload={
                            "tool_name": tool_name,
                            "params": tool_params,
                        },
                    )

                    # 执行工具
                    result = await getattr(self.browser, tool_name)(tool_params)
                    log.info(f"EXECUTE STATUS: {result.get('status')}")
                    log.info(f"EXECUTE MESSAGE: {result.get('message')}")

                    if (
                        result.get("status") == "success"
                        or result.get("status") == "finished"
                        or result.get("status") == "interrupt"
                    ):
                        # 工具执行结束
                        stream.push(
                            component="message",
                            action="tool_end",
                            timestamp=function.timestamp(),
                            payload=result,
                        )

                        function.write_task_execute_history(
                            tool=tool_name,
                            params=tool_params,
                            status="success",
                            message=result.get("message") +
                            f"\nURL: {current_url}",
                            caller=browser_caller,
                        )

                        # 处理图片
                        if tool_name == "check_image_by_selector":
                            additional_images.append(
                                f"data:image/jpeg;base64,{result.get('image_base64')}"
                            )

                        # 处理 note
                        if tool_name == "write_a_note":
                            note = f"<note url=\"{current_url}\">\n{result.get('message')}\n</note>\n\n"
                            function.append_file(
                                caller.get("dir"), result.get(
                                    "write_file"), note
                            )
                            self.notes.append(note)
                            stream.push(
                                component="editor",
                                action="open_file",
                                timestamp=function.timestamp(),
                                payload={
                                    "path": result.get("write_file"),
                                    "content": result.get("message")
                                },
                            )

                        # 写入结果文件
                        if tool_name == "purpose_completed_and_stop":
                            log.debug(
                                f"PURPOSE COMPLETED AND STOP, WRITE FILE: {write_file}"
                            )
                            function.write_file(
                                caller.get("dir"), write_file, result.get(
                                    "message")
                            )
                            message = (
                                result.get("message")
                                + f"\nURL: {current_url}"
                                + get_notes(self.notes)
                            )

                            return {
                                "status": result.get("status"),
                                "message": message,
                            }

                        if tool_name in [
                            "search_and_stop",
                            "write_code_and_stop",
                            "download_file_and_stop",
                        ]:
                            log.debug(f"{tool_name}")
                            message = (
                                result.get("message")
                                + f"\nURL: {current_url}"
                                + get_notes(self.notes)
                            )
                            return {
                                "status": result.get("status"),
                                "message": message,
                            }
                    else:
                        log.error(
                            f"EXECUTE TOOL FAILED: {result.get('message')}")
                        self.error_count += 1
                        function.write_task_execute_history(
                            tool=tool_name,
                            params=tool_params,
                            status="error",
                            message=result.get("message") +
                            f"\nURL: {current_url}",
                            caller=browser_caller,
                        )

                        if self.error_count > 10:
                            log.error("ERROR COUNT EXCEEDED 10, BREAK")
                            return {
                                "status": "error",
                                "message": "ERROR COUNT EXCEEDED 10, You should try another way to get the information."
                                + get_notes(self.notes),
                            }

                        # 如果工具执行失败，跳过后续工具执行
                        break

                    # 每执行一个工具，暂停5秒
                    await asyncio.sleep(5)
            else:
                log.error("NO TOOL NAME OR TOOL PARAMS")

            # 继续执行
            return await self.browser_run(
                purpose, write_file, additional_images, caller
            )

        except Exception as e:
            log.error(f"BROWSER RUN ERROR: {e}")
            log.error(traceback.format_exc())

            # 如果大模型返回的消息长度超过限制，则记录失败，退出browser
            if str(e) == "messages length is too long":
                message = (
                    f"The webpage content is too long, please use `crawl_web` tool to get the information.\nURL: {current_url}"
                    + get_notes(self.notes)
                )

                return {
                    "status": "error",
                    "message": message,
                }

            # 记录失败记录，继续执行
            function.write_task_execute_history(
                tool="browse_and_operate_web",
                params={
                    "url": current_url,
                    "purpose": purpose,
                    "write_file": write_file,
                },
                status="error",
                message=str(e) + f"\nURL: {current_url}",
                caller=browser_caller,
            )
            return await self.browser_run(
                purpose, write_file, additional_images, caller
            )
        finally:
            await self.browser.close()


def get_notes(notes):
    if len(notes) > 0:
        notes_text = ""
        for note in notes:
            notes_text += note + "\n"
        return f"\n\n## NOTES:\n{notes_text}\n"
    else:
        return ""
