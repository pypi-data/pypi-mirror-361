from typing import Any, Dict, List
import traceback
from hero.util import log, function, stream, execute_shell
from hero.agent import Agent
import os
import re
import json


class Patch:
    def __init__(self, patcher: Agent, analyzer: Agent):
        self.name = "patch"
        self.prompt = """
<tool name="patch">
    <desc>Patch the original file with the patch file following the demand.</desc>
    <params>
        <demand type="string">The detailed requirement to modify the original file.</demand>
        <original_file type="string">The original file.</original_file>
        <reference_file_list type="list">Read some files as programming references.</reference_file_list>
    </params>
    <example>
        {
            "tool": "patch",
            "params": {
                "demand": "Modify the original file to increase the accuracy of the algorithm.",
                "original_file": "original_file.py",
                "reference_file_list": ["1.txt", "2.txt"],
            }
        }
    </example>
</tool>
        """
        self.patcher = patcher
        self.analyzer = analyzer
        self.run_count = 0
        self.hero_params = None

    def get_name(self):
        return self.name

    def get_prompt(self):
        return self.prompt

    async def invoke(
        self, params: Dict[str, Any], caller: Dict[str, str]
    ) -> Dict[str, Any]:
        dir = caller.get("dir")
        try:
            demand = params.get("demand")
            original_file = params.get("original_file", "")
            reference_file_list = params.get("reference_file_list", [])
            self.hero_params = params


            if not demand:
                raise ValueError("demand is required")

            result = await self.patch_run(
                demand, original_file, reference_file_list, caller
            )

            # 清理目录下的.orig和.rej文件
            if dir:
                clean_patch_file(dir)

            return result

        except Exception as e:
            log.error(f"Error: {str(e)}")
            log.error(traceback.format_exc())

            # 清理目录下的.orig和.rej文件
            if dir:
                clean_patch_file(dir)

            return {
                "status": "error",
                "message": f"Error: {str(e)}",
            }

    async def patch_run(
        self,
        demand: str,
        original_file: str,
        reference_file_list: List[str],
        caller: Dict[str, str],
    ) -> Dict[str, Any]:
        dir = caller.get("dir")
        if not dir:
            raise ValueError("dir is required")
        try:
            self.run_count += 1

            log.debug(f"patch run_count: {self.run_count}")

            patcher_caller = {
                "name": self.patcher.get_name(),
                "index": self.run_count,
                "dir": caller.get("dir"),
            }


            line_numbers = await self.analyzer_run(
                demand, original_file, reference_file_list, caller
            )

            original_file_content = f'<file name="{original_file}" with_line_number="true" format="line_number:line_text">\n'
            original_file_path = os.path.join(dir, original_file)
            original_file_content += function.file_to_text_with_line_number(
                original_file_path
            )
            original_file_content += "\n</file>\n"

            if line_numbers:
                original_file_content += "<modified_line_numbers>\n"
                original_file_content += json.dumps(line_numbers)
                original_file_content += "\n</modified_line_numbers>\n"

            reference_file_content = ""
            for file_name in reference_file_list:
                reference_file_content += (
                    f'<file name="{file_name}" with_line_number="false">\n'
                )
                reference_file_content += function.read_file(dir, file_name)
                reference_file_content += "\n</file>\n"

            is_output_file = False
            output_file_path = ""
            output_file_name = ""
            output_file_list = []

            async for token in self.patcher.chat(
                message=demand
                + "\n\n"
                + (
                    "Please fix the error of patch file, and regenerate the patch file in the `return_format`."
                    if self.run_count > 1
                    else "Please generate the patch file to modify the original file, and return the patch file in the `return_format`."
                ),
                params={
                    "original_file": original_file_content,
                    "demand": demand,
                    "reference_file": reference_file_content,
                },
                with_history=False,
            ):
                if token.get("action") == "content_line":
                    line = token.get("payload", {}).get("content")

                    # 处理代码文件
                    if re.search(r"<patch file=\"(.*?)\">", line):
                        if match := re.search(r"<patch file=\"(.*?)\">", line):
                            output_file_name = match.group(1)
                        else:
                            raise ValueError("patch file name is required")
                        output_file_path = os.path.join(dir, output_file_name)
                        output_file_list.append(output_file_name)

                        # 如果文件存在，则把现有文件改名
                        if os.path.exists(output_file_path):
                            # 获取当前时间
                            timestamp = function.timestamp()
                            # 改名
                            os.rename(
                                output_file_path,
                                os.path.join(
                                    dir, f"__{output_file_name}_{timestamp}.py"
                                ),
                            )

                        # 新建空文件
                        with open(output_file_path, "w", encoding="utf-8") as f:
                            f.write("")

                        # 设置标志位，后续将 line 写入文件
                        is_output_file = True

                        stream.push(
                            component="editor",
                            action="open_file",
                            timestamp=function.timestamp(),
                            payload={"file_name": output_file_name},
                        )

                        # 清空 line，特殊标志不输出，原始内容debug打印出来
                        line = None

                    elif "</patch>" in line:
                        stream.push(
                            component="editor",
                            action="close_file",
                            timestamp=function.timestamp(),
                            payload={"file_name": output_file_name},
                        )

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
                                payload={
                                    "file_name": output_file_name,
                                    "content": line,
                                },
                            )
                        else:
                            stream.push(
                                component="message",
                                action=token.get("action", ""),
                                timestamp=function.timestamp(),
                                payload={
                                    "name": self.get_name(),
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

            if len(output_file_list) == 0:
                return {
                    "status": "error",
                    "message": f"Patch file failed, there is no patch file generated, please try again.",
                }

            for file_name in output_file_list:
                file_path = os.path.join(dir, file_name)
                if not os.path.exists(file_path):
                    log.error(f"File {file_name} does not exist")
                    continue

                command = f"patch --batch --verbose {original_file} < {file_name}"

                stdout, stderr = await execute_shell(command, patcher_caller)

                if stderr or "failed at" in stdout:
                    # 还有错误继续修改

                    patch_file_content = function.file_to_text_with_line_number(
                        os.path.join(dir, file_name)
                    )

                    error_message = f"<demand>\n{demand}\n</demand>\n"
                    error_message += f'<patch_file file_name="{file_name}">\n{patch_file_content}\n</patch_file>\n'
                    error_message += (
                        f"<error_message>\n{stdout}" + f"\n" + f"{stderr}\n</error_message>\n"
                    )

                    return await self.patch_run(
                        original_file=original_file,
                        reference_file_list=reference_file_list,
                        demand=error_message,
                        caller=caller,
                    )

            return {
                "status": "success",
                "message": f"Patch file {original_file} modified successfully",
            }

        except Exception as e:
            log.error(f"Error: {str(e)}")
            log.error(traceback.format_exc())

            return {
                "status": "error",
                "message": f"Error: {str(e)}",
            }

    async def analyzer_run(
        self,
        demand: str,
        original_file: str,
        reference_file_list: List[str],
        caller: Dict[str, str],
    ):
        dir = caller.get("dir")
        if not dir:
            raise ValueError("dir is required")
        try:
            analyzer_caller = {
                "name": self.analyzer.get_name(),
                "index": self.run_count,
                "dir": caller.get("dir"),
            }

            original_file_path = os.path.join(dir, original_file)

            original_file_content = f'<file name="{original_file}" with_line_number="true" format="line_number:line_text">\n'
            original_file_content += function.file_to_text_with_line_number(
                original_file_path
            )
            original_file_content += "\n</file>\n"

            reference_file_content = ""
            for file_name in reference_file_list:
                reference_file_content += (
                    f'<file name="{file_name}" with_line_number="false">\n'
                )
                reference_file_content += function.read_file(dir, file_name)
                reference_file_content += "\n</file>\n"

            # 获取流式响应的返回
            json_content = ""
            json_processing = False
            content = ""

            async for token in self.analyzer.chat(
                message=demand
                + "\n\n"
                + "Please find the specific line number to be modified in the original file, and return the line numbers in the `line_numbers` field in the `return_format`.",
                params={
                    "original_file": original_file_content,
                    "demand": demand,
                    "reference_file": reference_file_content,
                },
                with_history=False,
            ):
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
                tool_dict = json.loads(json_content)
            else:
                tool_dict = function.extract_tool_response(content) or json.loads(
                    content.strip()
                )
            line_numbers = tool_dict.get("line_numbers")
            if line_numbers:
                log.debug(f"line_numbers: {line_numbers}")

            return line_numbers

        except Exception as e:
            log.error(f"Error: {str(e)}")
            log.error(traceback.format_exc())

            return None


def clean_patch_file(dir: str):
    for file in os.listdir(dir):
        if (
            file.endswith(".orig")
            or file.endswith(".rej")
            or file.endswith(".patch")
            or file.endswith(".patchf")
        ):
            os.remove(os.path.join(dir, file))