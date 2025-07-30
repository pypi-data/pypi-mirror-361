from util import log, config, function, Agent, stream
from typing import List

async def image_to_text(images: List[str], purpose: str, user_message: str, caller=None) -> str:
    """
    将图片转换为文本
    """
    watcher = Agent(
        name="watcher",
        api_url=config.model("watcher_model").base_url,
        api_key=config.model("watcher_model").api_key,
        model=config.model("watcher_model").model,
        prompt_path=config.prompt_dir() + "/watcher.md",
    )

    content = ""

    async for token in watcher.chat(
        message=f"View the image and return the text in strict accordance with the `purpose` and `user_message`.",
        images=images,
        caller=caller,
    ):
        if token.get("action") == "content_line":
            content += token.get("payload", {}).get("content")

        stream.push(
            component="message",
            action=token.get("action", ""),
            timestamp=function.timestamp(),
            payload=token.get("payload", {}),
        )

    return content