from typing import Dict
import traceback
from hero.util import log, function, stream
from hero.agent import Agent


class ReflectAndBrainstorm:
    def __init__(self, agent: Agent):
        self.name = "reflect_and_brainstorm"
        self.prompt = """
<tool name="reflect_and_brainstorm">
    <desc>Analyze the current situation and difficulties, reflect on the past, and brainstorm the improvements or big changes. The make a new plan.</desc>
    <params>
        <reasoning type="string">The reasoning.</reasoning>
    </params>
    <example>
        {
            "tool": "reflect_and_brainstorm",
            "params": {
                "reasoning": "The reasoning.",
            }
        }
    </example>
</tool>
"""
        self.agent = agent

    def get_name(self):
        return self.name

    def get_prompt(self):
        return self.prompt

    async def invoke(
        self, params: Dict[str, str], caller: Dict[str, str]
    ) -> Dict[str, str]:
        try:
            task_execute_history = function.read_file(
                caller.get("log_dir"), "__Hero_tasks.md"
            )

            user_message = str(function.read_user_message(caller))

            current_brainstorm = function.read_file(
                caller.get("log_dir"), "__brainstorm.md"
            )

            content = ""

            # 使用模型提取关键信息
            async for token in self.agent.chat(
                message=user_message
                + "\nPlease reflect on the past and brainstorm the improvements or big changes.",
                params={
                    "task_execute_history": task_execute_history,
                    "current_brainstorm": current_brainstorm,
                },
            ):
                stream.push(
                    component="message",
                    action=token.get("action", ""),
                    timestamp=function.timestamp(),
                    payload=token.get("payload", {}),
                )

                if token.get("action") == "content_line":
                    content += token.get("payload", {}).get("content", "")

            function.write_file(caller.get("log_dir"), "__brainstorm.md", content)

            return {
                "status": "success",
                "message": f"Brainstorm completed. Added to context.",
            }

        except Exception as e:
            log.error(f"reflect_and_brainstorm error: {e}")
            log.error(traceback.format_exc())
            return {
                "status": "error",
                "message": str(e),
            }