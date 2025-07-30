from typing import Dict
import traceback
from hero.util import log, function
from hero.util.shell import execute_shell
import re

class ExecuteShell:
    def __init__(self):
        self.name = "execute_shell"
        self.prompt = """
<tool name="execute_shell">
    <desc>Execute shell commands to complete tasks.</desc>
    <params>
        <command_list type="list">The shell command list to execute.</command_list>
    </params>
    <example>
        {
            "tool": "execute_shell",
            "params": {
                "command_list": ["python main.py", "python test.py"]
            }
        }
</tool>
"""

    def get_name(self):
        return self.name

    def get_prompt(self):
        return self.prompt

    async def invoke(
        self, params: Dict[str, str], caller: Dict[str, str]
    ) -> Dict[str, str]:
        command_list = params.get("command_list", [])
        if not command_list:
            return {"status": "error", "message": "No command list provided."}

        dir = caller.get("dir", "")
        message_list = []

        for command in command_list:
            try:
                # 执行命令
                command = re.sub(r"#.*\n?", "", command).strip()
                if not command:
                    continue

                stdout, stderr = await execute_shell(command, caller)

                message = f'<shell command="{command}">\n\n'
                message += f"## Stdout:\n\n"
                message += f"{function.get_head_and_tail_n_chars(stdout)}\n\n"
                message += f"## Stderr:\n\n"
                message += f"{function.get_head_and_tail_n_chars(stderr)}\n\n"
                message += f"</shell>\n\n"

                message_list.append(message)

                if stderr:
                    return {
                        "status": "error",
                        "message": "\n\n".join(message_list),
                    }

            except Exception as e:
                log.error(f"Error: {str(e)}")
                log.error(traceback.format_exc())
                message_list.append(f"<error>\n\n{str(e)}\n\n</error>\n\n")
                return {
                    "status": "error",
                    "message": "\n\n".join(message_list),
                }

        return {
            "status": "success",
            "message": "\n\n".join(message_list),
        }
