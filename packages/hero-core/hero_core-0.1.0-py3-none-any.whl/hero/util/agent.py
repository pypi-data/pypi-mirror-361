import aiohttp
import json
from typing import Optional, Dict, Any, Callable, AsyncGenerator, List
import os

from util import log, config

MODEL_CONTEXT_LIMIT = config.get("model_context_limit")
MAX_TOKENS = config.get("max_tokens")
AGENT_TIMEOUT = config.get("agent_timeout")


class Usage:
    """
    使用情况
    """
    def __init__(
        self,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        reasoning_tokens: int = 0,
        content_tokens: int = 0,
        prompt_cache_hit_tokens: int = 0,
        prompt_cache_miss_tokens: int = 0,
    ):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens
        self.reasoning_tokens = reasoning_tokens
        self.content_tokens = content_tokens
        self.prompt_cache_hit_tokens = prompt_cache_hit_tokens
        self.prompt_cache_miss_tokens = prompt_cache_miss_tokens

    def to_dict(self) -> Dict[str, int]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "reasoning_tokens": self.reasoning_tokens,
            "content_tokens": self.content_tokens,
            "prompt_cache_hit_tokens": self.prompt_cache_hit_tokens,
            "prompt_cache_miss_tokens": self.prompt_cache_miss_tokens,
        }


class Agent:
    """
    代理
    """
    def __init__(
        self,
        name: str,
        api_url: str,
        api_key: str,
        model: str,
        prompt_path: str,
    ):
        self.name = name
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.prompt_path = prompt_path
        self.messages: List[Dict[str, Any]] = []
        self.index = 0

    async def _load_prompt(self) -> str:
        """
        加载提示
        """
        try:
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            log.error(f"Error loading prompt from {self.prompt_path}: {e}")
            raise e

    def _replace_prompt_params(
        self, prompt: str, params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        替换提示参数
        """
        if not params:
            return prompt

        result = prompt
        for key, value in params.items():
            if value is not None:
                placeholder = f"{{{{{key}}}}}"
                result = result.replace(placeholder, str(value))
        return result

    def clear_history(self) -> None:
        """
        清除历史
        """
        self.messages = []

    def get_message_history(self) -> List[Dict[str, Any]]:
        """
        获取消息历史
        """
        return self.messages

    def write_message_history(self, file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            for message in self.messages:
                f.write(f"{message['role']}: {message['content']}\n")

    def add_message(self, role: str, content: str) -> None:
        """
        添加消息
        """
        self.messages.append({"role": role, "content": content})

    def get_name(self) -> str:
        """
        获取名称
        """
        return self.name

    async def chat(
        self,
        message: str,
        on_token: Callable[[Dict[str, Any]], None] = None,
        params: Optional[Dict[str, Any]] = None,
        with_history: bool = True,
        images: Optional[List[str]] = [],
        audio: Optional[List[str]] = [],
        index: Optional[int] = None,
        caller: Optional[Dict[str, str]] = {},
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        聊天
        """
        try:
            # 加载并处理系统提示词
            # 如果请求中设置语言为中文，则尝试加载中文系统提示词
            if caller is not None and caller.get("language") == "zh-CN":
                parts = self.prompt_path.split(os.sep)
                # 过滤掉空字符串
                parts = [part for part in parts if part]
                # 返回最后一层目录
                last_dir = parts[-2] if len(parts) > 1 else parts[-1]
                if last_dir != 'zh': # 如果最后一层目录不是 'zh'，则修改 self.prompt_path 为 'zh' 目录下的同名文件
                    self.prompt_path = os.path.join(
                        os.path.dirname(self.prompt_path),
                        'zh',
                        os.path.basename(self.prompt_path)
                    )

            system_prompt = await self._load_prompt()
            system_prompt = self._replace_prompt_params(system_prompt, params)

            log.debug(f"{self.name} | Messages Length: {len(self.messages)}")

            images_str_length = len(json.dumps(images, ensure_ascii=False))

            if len(images) > 0:
                user_message = {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": message},
                        *[
                            {
                                "type": "image_url",
                                "image_url": {"url": image},
                            }
                            for image in images
                        ],
                    ],
                }
                log.debug(f"{self.name} | Images Str Length: {images_str_length}")
            else:
                user_message = {
                    "role": "user",
                    "content": message,
                }

            if with_history:
                messages: List[Dict[str, Any]] = [
                    {"role": "user", "content": system_prompt},
                    *[msg for msg in self.messages],
                    user_message,
                ]
                self.messages.append({"role": "user", "content": message})
            else:
                messages: List[Dict[str, Any]] = [
                    {"role": "user", "content": system_prompt},
                    user_message,
                ]

            messages_length = len(json.dumps(messages, ensure_ascii=False))

            log.debug(f"{self.name} | Messages Bytes: {messages_length}")
            log.debug(
                f"{self.name} | Messages without images: {messages_length - images_str_length}"
            )

            # 把 messages 写入文件，用于 debug
            messages_content = ""
            for message_item in messages:
                messages_content += f"# {message_item['role']}: \n{message_item['content']}\n\n"
            
            # MODEL_CONTEXT_LIMIT 默认值为 60000
            if messages_length - images_str_length > int(MODEL_CONTEXT_LIMIT or 60000):
                log.error("messages length is too long")
                raise Exception("messages length is too long")

            max_tokens = MAX_TOKENS
            if "claude-3-7" in self.model:
                max_tokens = 60000

            # 构建请求体
            request_body = {
                "model": self.model,
                "messages": messages,
                "stream": True,
                "max_tokens": max_tokens,
                "stream_options": {
                    "include_reasoning": True,
                    "include_usage": True,
                },
                # "temperature": 0.6,
            }

            if "Qwen3" in self.model:
                request_body["chat_template_kwargs"] = {"enable_thinking": False}

            # if "o4-mini" in self.model:
            #     request_body["reasoning"] = {"effort": "low"}

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }

            if index:
                self.index = index
            else:
                self.index += 1

            yield {
                "action": "message_start",
                "payload": {
                    "name": self.name,
                    "index": self.index,
                },
            }

            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=AGENT_TIMEOUT)
            ) as session:
                async with session.post(
                    self.api_url + "/chat/completions",
                    headers=headers,
                    json=request_body,
                ) as response:
                    if not response.ok:
                        error_text = await response.text()
                        log.error(f"API Error Response: {error_text}")
                        raise Exception(
                            f"API request failed with status {response.status}: {error_text}"
                        )

                    content_cache = ""
                    reasoning_content_cache = ""
                    reasoning_content_progressing = False
                    content_progressing = False
                    line_index = 0

                    async for line in response.content:
                        if line:
                            line = line.decode("utf-8").strip()
                            # print(line)
                            if line.startswith("data: "):
                                data = line[6:]
                                # 如果 data 为 "[DONE]"，则说明流式响应结束
                                if data == "[DONE]":
                                    break

                                try:
                                    parsed = json.loads(data)
                                    content = ""
                                    reasoning_content = ""

                                    if parsed.get("choices") and parsed["choices"][0]:
                                        delta = parsed["choices"][0].get("delta", {})
                                        content = delta.get("content", "")
                                        reasoning_content = delta.get(
                                            "reasoning_content", ""
                                        )
                                        finish_reason = parsed["choices"][0].get(
                                            "finish_reason", ""
                                        )

                                        # 按行输出content，只有content按行输出，reasoning_content内没有需要格式化的内容，所以不需要按行输出
                                        content_list = content_cache.split("\n")
                                        content_list_len = len(content_list)

                                        # 至少要有两行，第一行内容才是完整的
                                        if content_list_len > 1:

                                            while line_index < content_list_len - 1:

                                                # 消息结束时，再处理最后一行，确保最后一行的内容是完整的
                                                if line_index == content_list_len - 1:
                                                    break

                                                # split时会移除换行符，所以这里要加回去
                                                line = content_list[line_index] + "\n"

                                                yield {
                                                    "action": "content_line",
                                                    "payload": {
                                                        "name": self.name,
                                                        "content": line,
                                                    },
                                                }

                                                line_index += 1

                                        # 如果发现 finish_reason 为 stop，则说明 content 已经结束
                                        if finish_reason == "stop":

                                            # 发出 content_end 事件
                                            if content_progressing:
                                                content_progressing = False

                                                # 输出最后一行
                                                yield {
                                                    "action": "content_line",
                                                    "payload": {
                                                        "name": self.name,
                                                        "content": content_list[
                                                            line_index
                                                        ]
                                                        + "\n",
                                                    },
                                                }

                                                yield {
                                                    "action": "progress_update",
                                                    "payload": {
                                                        "name": self.name,
                                                        "content": "content_end",
                                                    },
                                                }

                                        # 如果 content 不为空，则记录 content 完整文本
                                        if content:
                                            # 记录 content 完整文本
                                            content_cache += content
                                            # 发出 content_start 事件
                                            if not content_progressing:
                                                content_progressing = True
                                                yield {
                                                    "action": "progress_update",
                                                    "payload": {
                                                        "name": self.name,
                                                        "content": "content_start",
                                                    },
                                                }
                                            # 发出 think_end 事件
                                            if reasoning_content_progressing:
                                                reasoning_content_progressing = False
                                                yield {
                                                    "action": "progress_update",
                                                    "payload": {
                                                        "name": self.name,
                                                        "content": "think_end",
                                                    },
                                                }

                                        # 如果 reasoning_content 不为空，则记录 reasoning_content 完整文本
                                        if reasoning_content:
                                            # 记录 reasoning_content 完整文本
                                            reasoning_content_cache += reasoning_content
                                            # 发出 think_start 事件
                                            if not reasoning_content_progressing:
                                                reasoning_content_progressing = True
                                                yield {
                                                    "action": "progress_update",
                                                    "payload": {
                                                        "name": self.name,
                                                        "content": "think_start",
                                                    },
                                                }

                                            yield {
                                                "action": "reasoning_content_token",
                                                "payload": {
                                                    "name": self.name,
                                                    "reasoning_content": reasoning_content,
                                                },
                                            }

                                    # 如果 parsed 中包含 usage 字段，则计算 usage
                                    if parsed.get("usage"):

                                        usage = Usage()
                                        usage_data = parsed["usage"]

                                        if "prompt_tokens" in usage_data:
                                            usage.prompt_tokens = usage_data[
                                                "prompt_tokens"
                                            ]
                                        if "completion_tokens" in usage_data:
                                            usage.completion_tokens = usage_data[
                                                "completion_tokens"
                                            ]
                                        if "total_tokens" in usage_data:
                                            usage.total_tokens = usage_data[
                                                "total_tokens"
                                            ]

                                        if "completion_tokens_details" in usage_data:
                                            details = usage_data[
                                                "completion_tokens_details"
                                            ]
                                            if "reasoning_tokens" in details:
                                                usage.reasoning_tokens = details[
                                                    "reasoning_tokens"
                                                ]
                                            if "content_tokens" in details:
                                                usage.content_tokens = details[
                                                    "content_tokens"
                                                ]

                                        if "prompt_cache_hit_tokens" in usage_data:
                                            usage.prompt_cache_hit_tokens = usage_data[
                                                "prompt_cache_hit_tokens"
                                            ]
                                        if "prompt_cache_miss_tokens" in usage_data:
                                            usage.prompt_cache_miss_tokens = usage_data[
                                                "prompt_cache_miss_tokens"
                                            ]

                                        yield {
                                            "action": "usage",
                                            "payload": {
                                                "name": self.name,
                                                "usage": usage.to_dict(),
                                            },
                                        }

                                except json.JSONDecodeError as e:
                                    log.error(f"Error parsing chunk: {e}")
                                    log.error(f"Raw chunk: {line}")

                    # 添加完整的助手回复到消息历史
                    self.messages.append(
                        {"role": "assistant", "content": content_cache}
                    )
                    yield {
                        "action": "message_completed",
                        "payload": {
                            "name": self.name,
                            "content": content_cache,
                            "reasoning_content": reasoning_content_cache,
                        },
                    }

            # 接收完流式响应后，结束
            yield {
                "action": "message_end",
                "payload": {
                    "name": self.name,
                    "index": self.index,
                },
            }

        except Exception as e:
            log.error(f"Error in chat: {e}")
            raise e
