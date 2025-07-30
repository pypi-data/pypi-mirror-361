from typing import AsyncGenerator, Awaitable, Callable
from llm import Client
from openai.types.chat import ChatCompletionUserMessageParam, ChatCompletionSystemMessageParam
import os
from logger import logger
from llm.client import Chunk
import re
from pathlib import Path


async def answer(working_dir: str, args: dict, on_shell: Callable[[str], Awaitable[None]], on_file: Callable[[str], Awaitable[None]], on_new_file: Callable[[str], Awaitable[None]]) -> AsyncGenerator[Chunk, None]:
    """
    stream the result
    """
    demand = args.get("demand", "")
    read_file = args.get("read_file", [])
    context = ""
    for file in read_file:
        with open(os.path.join(working_dir, file), "r") as f:
            context += f.read()
    
    with open(os.path.join(os.path.dirname(__file__), "code.xml"), "r") as f:
        code_prompt = f.read()
        code_prompt = code_prompt.replace("{{context}}", context)
        file_list = os.listdir(working_dir)
        file_list_str = "\n".join(file_list)
        code_prompt = code_prompt.replace("{{workspace_file_list}}", file_list_str)
        code_prompt = code_prompt.replace("{{environment}}", """
platform: Darwin
python: 3.12.4
node: 22.11.0
""")
    
    client = Client()
    current_code_block = None
    current_file: str | None = None
    current_content = ""


    async for chunk in client.stream(
        messages=[
            ChatCompletionSystemMessageParam(
                role="system",
                content=code_prompt
            ),
            ChatCompletionUserMessageParam(
                role="user",
                content=demand
            )
        ]
    ):
        chunk.tool = "write_code"
        current_content += chunk.choices[0].delta.content or ""

        shell_match = re.search(r'\[\[\[code\s+language="shell"\]\]\](.*?)\[\[\[/code\]\]\]', current_content, re.DOTALL)
        if shell_match:
            logger.info(f"shell_match: {shell_match.group(1).strip()}")
            await on_shell(shell_match.group(1).strip())
            current_content = current_content.replace(shell_match.group(0), "")

        code_start_match = re.search(r'\[\[\[code\s+language="([^"]+)"\s+filename="([^"]+)"\]\]\]', current_content)
        if code_start_match:
            current_file = code_start_match.group(2)
            current_code_block = True
            if current_file is not None:
                file_path = Path(working_dir) / current_file
                chunk.path = str(file_path)
                write_content = current_content
                write_content = write_content[code_start_match.end():]
                if "[[[/code]]]" in write_content:
                    write_content = write_content[:write_content.find("[[[/code]]]")]
                has_new_file = False
                if not file_path.exists():
                    has_new_file = True
                with open(file_path, "w") as f:
                    f.write(write_content)
                if has_new_file:
                    await on_new_file(str(file_path))
                await on_file(str(file_path))
        
        # 检测代码块结束
        if current_code_block and "[[[/code]]]" in current_content:
            current_code_block = None
            current_file = None
            # 保留 [[[/code]]] 后面的内容
            current_content = current_content[current_content.find("[[[/code]]]") + len("[[[/code]]]"):]
        
        yield chunk