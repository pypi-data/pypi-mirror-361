from typing import Dict
import traceback
from hero.util import log, function, stream
from hero.agent import Agent
import os
import re


class FinalAnswer:
    def __init__(self, agent: Agent):
        self.name = "final_answer"
        self.prompt = """
<tool name="final_answer">
    <desc>If you believe that you have sufficient and accurate information to answer the user's question, please invoke the `final_answer` tool to provide an accurate response in a friendly format.</desc>
    <params>
        <answer type="string">The final answer</answer>
        <read_file_list type="list">The file contains the information that is most relevant to the user's question, Do not generate filenames yourself, the file name must be in the **workspace_file_list** context. only support **TEXT FILES** like: txt, json, csv, md, py, js, html, etc.(Can be empty)</read_file_list>
        <file_format type="string">only choose from: markdown, html, text</file_format>
    </params>
    <example>
        {
            "tool": "final_answer",
            "params": {
                "answer": "The final answer", "read_file_list": ["example.txt", "example.md"], "file_format": "markdown"
            }
        }
    </example>
</tool>
"""
        self.answer = agent

    def get_name(self):
        return self.name

    def get_prompt(self):
        return self.prompt

    async def invoke(
        self, params: Dict[str, str], caller: Dict[str, str]
    ):
        try:
            answer = params.get("answer")
            read_file_list = params.get("read_file_list")
            file_format = params.get("file_format")
            dir = caller.get("dir", "")

            if not answer:
                raise ValueError("Missing required parameter: answer")

            if not read_file_list:
                read_file_list = []

            if not file_format:
                file_format = "markdown"

            if file_format not in ["markdown", "html", "text"]:
                raise ValueError(
                    "Invalid output format, only choose from: markdown, html, text"
                )

            # 读取文件作为 context
            related_files = ""
            for file in read_file_list:
                file_path = os.path.join(dir, file)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {file}")

                related_files += f'<related_file name="{file}">\n'
                with open(file_path, "r", encoding="utf-8") as f:
                    related_files += f.read() + "\n"
                related_files += f"</related_file>\n\n"

            # 读取用户消息
            user_messages = function.read_user_message(caller)
            for message in user_messages:
                self.answer.add_message("user", message)

            is_output_file = False
            output_file_path = ""
            output_file_name = ""
            output_file_list = []

            # 调用 answer 生成回答
            async for token in self.answer.chat(
                message="Please output the content strictly in accordance with the user's requirements.",
                params={
                    "answer": answer,
                    "related_files": related_files,
                    "file_format": file_format,
                },
            ):
                if token.get("action") == "content_line":
                    line = token.get("payload", {}).get("content")

                    # 如果 line 包含 [[[output format="xx" file="xx.yy"]]]，用正则表达式提取文件名
                    match = re.search(
                        r"\[\[\[output format=\"(.*?)\" file=\"(.*?)\"\]\]\]", line
                    )
                    if match:
                        # 提取文件名
                        file_name = match.group(2)
                        output_file_list.append(
                            os.path.join(caller.get("dir", ""), file_name)
                        )
                        output_file_name = file_name
                        output_file_path = os.path.join(caller.get("dir", ""), file_name)

                        # 新建空文件
                        with open(output_file_path, "w", encoding="utf-8") as f:
                            f.write("")

                        # 设置标志位，后续将 line 写入文件
                        is_output_file = True

                        stream.push(
                            component="editor",
                            action="open_file",
                            timestamp=function.timestamp(),
                            payload={"path": output_file_name},
                        )

                        # 清空 line，特殊标志不输出，原始内容debug打印出来
                        line = None

                    # 如果 part 包含 [[[/output]]]，则设置标志位，停止写入文件
                    elif "[[[/output]]]" in line:
                        stream.push(
                            component="editor",
                            action="close_file",
                            timestamp=function.timestamp(),
                            payload={"path": output_file_name},
                        )

                        # 如果 pre_content 包含 [[[output format="xx" file="xx.yy"]]]，则用正则表达式提取文件名
                        is_output_file = False
                        output_file_name = ""
                        output_file_path = ""
                        line = None

                    if not line == None:
                        if is_output_file:
                            with open(output_file_path, "a", encoding="utf-8") as f:
                                f.write(line)

                            stream.push(
                                component="editor",
                                action="append_file",
                                timestamp=function.timestamp(),
                                payload={"path": output_file_name,
                                         "content": line},
                            )
                        else:
                            stream.push(
                                component="message",
                                action=token.get("action", ""),
                                timestamp=function.timestamp(),
                                payload={
                                    "name": self.name,
                                    "content": line,
                                    "reasoning_content": "",
                                },
                            )
                else:
                    stream.push(
                        component="message",
                        action=token.get("action", ""),
                        timestamp=function.timestamp(),
                        payload=token.get("payload", {}),
                    )

            
            log.info(f"output_file_list: {output_file_list}")

            function.write_ans(caller, output_file_list)

            return {
                "status": "success",
                "message": f"Final answer has been saved to the file: {output_file_list}\n",
                "output_file_list": output_file_list,
            }
        except Exception as e:
            log.error(f"Error in {self.name}: {e}")
            log.error(traceback.format_exc())
            return {
                "status": "error",
                "message": str(e),
            }
