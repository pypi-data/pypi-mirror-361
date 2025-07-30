from typing import List, Callable


class Hub:
    tools: List[Callable] = []

    def __init__(self):
        self.tools = []

    def register(self, tool):
        self.tools.append(tool)

    def get(self, tool_name):
        for tool in self.tools:
            if tool().get_name() == tool_name:
                return tool
        return None

    def get_all_tool_names(self):
        return [tool().get_name() for tool in self.tools]

    def get_prompts_by_tool_names(self, tool_names):
        prompts_text = ""
        for tool in self.tools:
            if tool().get_name() in tool_names:
                prompts_text += tool().get_prompt() + "\n"
        return prompts_text


hub = Hub()
