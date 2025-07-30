from playwright.async_api import async_playwright, TimeoutError
from typing import List, Dict
import asyncio
from bs4 import BeautifulSoup, Comment
import re
import base64
from urllib.parse import urljoin
import traceback
from hero.util import log, function
import random
from tqdm import tqdm
import os

class Browser:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.pages = []  # 存储所有打开的页面
        self.current_page_index = 0  # 当前页面的索引
        self.context = None
        self.timeout = 10000
        self.start_page = ""
        self.prompt = self.load_prompts("browser_prompt.txt")
        self.interactive_elements = [
            "a",  # 链接
            "button",  # 按钮
            "input",  # 输入框
            "select",  # 下拉框
            "textarea",  # 文本区域
            "img",  # 图片
            "[role='button']",  # 具有按钮角色的元素
            "[onclick]",  # 具有点击事件的元素
            "[href]",  # 具有链接的元素
        ]

    def custom(self, timeout: int | None = None):
        if timeout is not None:
            self.timeout = timeout

    def load_prompts(self, file_name: str) -> List[str]:
        """
        加载 browser_prompt.txt 文件，并返回一个列表
        """
        # 获取当前文件的目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, file_name)

        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip().split('\n\n')

    def get_prompts(self):
        content = ""
        for prompt in self.prompt:
            content += prompt
        return content

    async def start(self):
        """启动浏览器"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        page = await self.context.new_page()
        # 设置页面超时
        page.set_default_timeout(self.timeout)
        self.pages.append(page)
        self.current_page_index = 0

    @property
    def page(self):
        """获取当前页面"""
        if not self.pages:
            return None
        return self.pages[self.current_page_index]

    async def get_page_list(self):
        """获取所有页面"""
        content = ""
        for page in self.pages:
            content += f"- page {self.pages.index(page)}: {page.url}\n"
        return content

    async def get_current_page_index(self):
        """获取当前页面索引"""
        return self.current_page_index

    async def get_current_page_url(self):
        """获取当前页面URL"""
        return self.pages[self.current_page_index].url

    async def get_content_type(self):
        """获取当前页面内容类型"""
        try:
            response = await self.pages[self.current_page_index].evaluate(
                """() => {
                return document.contentType || '';
            }"""
            )
            return response
        except Exception as e:
            log.error(f"get_content_type error: {e}")
            return "text/html"  # 默认返回 text/html

    async def switch_to_page(self, index: int) -> bool:
        """切换到指定索引的页面

        Args:
            index: 要切换到的页面索引

        Returns:
            bool: 是否切换成功
        """
        if 0 <= index < len(self.pages):
            self.current_page_index = index
            return True
        return False

    async def open_url(self, url: str) -> Dict[str, str]:
        """
        打开指定URL并等待页面加载完成
        返回页面HTML内容
        """
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            if not self.page:
                return {
                    "status": "error",
                    "message": "Browser not initialized",
                }
            try:
                # 等待页面加载完成
                await self.page.goto(url)
                self.start_page = url

                current_url = await self.get_current_page_url()
                content_type = await self.get_content_type()
                log.info(f"CONTENT TYPE: {content_type}")

                if not "text/html" in content_type:
                    # 退出browser
                    message = f"The webpage is a downloadable file, please use `download_files` tool to get the information.\nURL: {current_url}"

                    return {
                        "status": "error",
                        "message": message,
                    }

                # 等待页面稳定
                await self.page.wait_for_load_state("domcontentloaded")
                # await self.page.wait_for_load_state("networkidle")

                # 检查页面是否还在加载
                is_loading = await self.page.evaluate(
                    """() => {
                    return document.readyState !== 'complete';
                }"""
                )

                if is_loading:
                    # 如果页面还在加载，等待一段时间
                    await asyncio.sleep(2)

                # 尝试获取页面内容
                try:
                    content = await self.page.content()
                    await self.click_cookie_button()
                    if content:
                        return {
                            "status": "success",
                            "message": "Open URL successfully",
                        }
                except Exception as e:
                    log.debug(f"获取页面内容失败，等待页面加载完成: {e}")
                    # 如果获取内容失败，等待页面加载完成
                    await self.page.wait_for_load_state("networkidle")
                    await asyncio.sleep(1)
                    if attempt < max_retries - 1:
                        continue
                    raise e

            except TimeoutError:
                if attempt < max_retries - 1:
                    log.debug(f"页面加载超时，尝试重试 ({attempt + 1}/{max_retries})")
                    await asyncio.sleep(retry_delay)
                    continue
                # 如果超时，尝试获取当前页面内容
                content = await self.page.content()
                if content:
                    return {
                        "status": "success",
                        "message": "Open URL successfully",
                        "content": content,
                    }
            except Exception as e:
                log.error(f"open_url error: {e}")
                log.error(traceback.format_exc())
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    continue
                return {
                    "status": "error",
                    "message": "Open URL failed. Please use the `download_files` tool to download the file.",
                }
        return {
            "status": "error",
            "message": "Open URL failed. Please use the `download_files` tool to download the file.",
        }

    async def wait_for_domcontentloaded(self):
        if not self.page:
            return {
                "status": "error",
                "message": "Browser not initialized",
            }
        await self.page.wait_for_load_state("domcontentloaded")

    async def go_to_start_page(self, params: Dict[str, str]):
        try:
            if self.start_page and self.page:
                await self.page.goto(
                    self.start_page, wait_until="domcontentloaded", timeout=self.timeout
                )
            else:
                return {
                    "status": "error",
                    "message": "Start page not set",
                }
            return {
                "status": "success",
                "message": "Go to start page successfully",
            }
        except Exception as e:
            log.error(f"go_to_start_page error: {e}")
            log.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"Go to start page error: {e}",
            }

    async def go_back(self, params: Dict[str, str]):
        if not self.page:
            return {
                "status": "error",
                "message": "Browser not initialized",
            }
        try:
            await self.page.go_back()
            return {
                "status": "success",
                "message": "Go back successfully",
            }
        except Exception as e:
            log.error(f"go_back error: {e}")
            log.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"Go back error: {e}",
            }

    async def click_cookie_button(self):
        """点击cookie按钮"""
        if not self.page:
            return {
                "status": "error",
                "message": "Browser not initialized",
            }
        try:
            buttons = await self.page.query_selector_all("button")
            for button in buttons:
                if "cookie" in await button.evaluate(
                    "(el) => el.innerText.toLowerCase()"
                ):
                    log.debug(
                        f"click cookie button: {await button.evaluate('(el) => el.outerHTML')}"
                    )

                    # 1. 尝试使用 JavaScript 点击
                    try:
                        await button.evaluate("(el) => el.click()")
                        log.debug("使用 JavaScript 点击成功")
                        return {
                            "status": "success",
                            "message": "Click cookie button successfully with JavaScript",
                        }
                    except Exception as e:
                        log.debug(f"JavaScript 点击失败: {e}")

                    # 2. 尝试使用鼠标点击
                    try:
                        box = await button.bounding_box()
                        if box:
                            await self.page.mouse.click(
                                box["x"] + box["width"] / 2,
                                box["y"] + box["height"] / 2,
                            )
                            log.debug("使用鼠标点击成功")
                            return {
                                "status": "success",
                                "message": "Click cookie button successfully with mouse",
                            }
                    except Exception as e:
                        log.debug(f"鼠标点击失败: {e}")

                    # 3. 尝试使用原生点击
                    try:
                        await button.click()
                        log.debug("使用原生点击成功")
                        return {
                            "status": "success",
                            "message": "Click cookie button successfully with native click",
                        }
                    except Exception as e:
                        log.debug(f"原生点击失败: {e}")
                        continue

        except Exception as e:
            log.error(f"click_cookie_button error: {e}")
            log.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"Click cookie button error: {e}",
            }

    async def get_content(self) -> str:
        """
        获取页面内容，不修改原始页面
        使用 BeautifulSoup 处理 HTML 并提取文本内容
        """

        html = await self.get_content_with_unique_selectors()
        html = BeautifulSoup(html, "html.parser")
        log.debug(f"html pretty")
        html.prettify()

        log.debug(f"remove html comment")
        # 移除 HTML 注释
        for comment in html.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        log.debug(f"remove tags")
        # 需要保留 script 标签，因为可能包含有效信息
        for script in html(["style", "meta", "link", "path", "noscript"]):
            script.decompose()

        log.debug(f"remove tags without data-hid")
        # 移除所有不带 data-hid 属性的标签，保留script标签
        for tag in html.find_all(True):
            if not tag.get("data-hid"): # type: ignore
                tag.unwrap() # type: ignore

        html_text = str(html)

        # 去除所有空行和重复行
        log.debug(f"remove empty lines and duplicate lines")
        html_text = function.clean_overlength_lines(html_text)
        html_text = re.sub(r"\n\s*\n", "\n", html_text)
        lines = html_text.split("\n")
        seen = set()
        unique_lines = []
        for line in lines:
            line = line.strip()
            if line and line not in seen:
                seen.add(line)
                unique_lines.append(line)
        html_text = "\n".join(unique_lines)

        return html_text

    async def refresh_page(self, params: Dict[str, str]):
        """刷新页面"""
        if not self.page:
            return {
                "status": "error",
                "message": "Browser not initialized",
            }
        try:
            await self.page.reload(wait_until="domcontentloaded", timeout=self.timeout)
            return {
                "status": "success",
                "message": "Refresh page successfully",
            }
        except Exception as e:
            log.error(f"refresh_page error: {e}")
            log.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"Refresh page error: {e}",
            }

    async def get_image_base64_from_screenshot(self, img_selector):
        if not self.page:
            return None
        try:
            img_element = self.page.locator(img_selector).first
            screenshot_bytes = await img_element.screenshot()
            return base64.b64encode(screenshot_bytes).decode("utf-8")
        except Exception as e:
            log.error(f"获取图片base64编码时出错: {e}")
            log.error(traceback.format_exc())
            return None

    async def click_button_by_selector(
        self, params: Dict[str, str], retries: int = 3
    ) -> Dict:
        """点击指定元素，带有重试机制
        返回包含状态和原因的字典
        """

        if not self.page:
            return {
                "status": "error",
                "message": "Browser page not initialized",
            }

        selector = params.get("selector")
        outer_html = params.get("outer_html")

        if not selector:
            raise ValueError("Must provide a selector")
        if not outer_html:
            raise ValueError("Must provide the outer_html")

        for attempt in range(retries):
            try:
                log.debug(f"尝试点击元素: {selector}")

                if not self.context:
                    return {
                        "status": "error",
                        "message": "Browser context not initialized",
                    }

                # 监听新页面的打开
                new_page_promise = asyncio.create_task(
                    self.context.wait_for_event("page")
                )

                # 尝试定位元素
                locator = None
                try:
                    if selector.startswith("text="):
                        # 使用文本定位时，尝试更精确的匹配
                        locator = self.page.locator(selector).first
                    elif selector.startswith("xpath="):
                        # 使用XPath时，确保只匹配第一个元素
                        locator = self.page.locator(selector).first
                    elif ":contains(" in selector:
                        # 处理包含特定文本的链接
                        text = selector.split(":contains('")[1].split("')")[0]
                        locator = self.page.locator(f"text={text}").first
                    else:
                        # 尝试CSS选择器，使用更精确的选择器
                        locator = self.page.locator(selector).first

                    # 检查元素是否存在
                    count = await locator.count()
                    if count == 0:
                        # 如果是 a 标签
                        if selector.startswith("a["):
                            message = f"Element does not exist, **Use `go_to_url` to handle the `a` tag.**"
                            raise ValueError(message)
                        else:
                            raise ValueError(
                                f"Element does not exist, **Don't use this selector: `{selector}` again.**"
                            )
                except Exception as e:
                    log.debug(f"尝试选择器 {selector} 失败: {e}")
                    continue

                if not locator:
                    raise ValueError("Cannot find a valid selector")


                # 检查元素是否在DOM中
                is_in_dom = await locator.evaluate("el => el.isConnected")
                if not is_in_dom:
                    raise ValueError(f"Element {selector} is not in DOM")

                # 尝试使用JavaScript滚动到元素位置
                try:
                    await self.page.evaluate(
                        """
                        (selector) => {
                            const element = document.querySelector(selector);
                            if (element) {
                                element.scrollIntoView({ behavior: 'instant', block: 'center' });
                            }
                        }
                    """,
                        selector,
                    )
                    await asyncio.sleep(0.5)
                except Exception as e:
                    log.debug(f"JavaScript滚动失败: {e}")

                # 获取元素位置
                box = await locator.bounding_box()
                if not box:
                    # 如果无法获取元素位置，尝试使用JavaScript点击
                    try:
                        await self.page.evaluate(
                            """
                            (selector) => {
                                const element = document.querySelector(selector);
                                if (element) {
                                    element.click();
                                }
                            }
                        """,
                            selector,
                        )
                        log.debug("使用JavaScript点击成功")
                    except Exception as e:
                        log.debug(f"JavaScript点击失败: {e}")
                        raise ValueError(f"Element {selector} is not clickable")
                else:
                    log.debug(
                        f"元素位置: x={box['x']}, y={box['y']}, width={box['width']}, height={box['height']}"
                    )

                    # 检查元素是否在视口内
                    viewport_size = self.page.viewport_size
                    is_in_viewport = (
                        box["x"] >= 0
                        and box["y"] >= 0
                        and box["x"] + box["width"] <= viewport_size["width"]
                        and box["y"] + box["height"] <= viewport_size["height"]
                    )

                    if not is_in_viewport:
                        # 如果元素不在视口内，尝试使用JavaScript滚动
                        try:
                            await self.page.evaluate(
                                """
                                (selector) => {
                                    const element = document.querySelector(selector);
                                    if (element) {
                                        const rect = element.getBoundingClientRect();
                                        window.scrollTo({
                                            top: window.scrollY + rect.top - window.innerHeight/2,
                                            behavior: 'instant'
                                        });
                                    }
                                }
                            """,
                                selector,
                            )
                            await asyncio.sleep(0.5)
                        except Exception as e:
                            log.debug(f"JavaScript滚动到视口失败: {e}")

                    # 尝试使用JavaScript点击
                    try:
                        await self.page.evaluate(
                            """
                            (selector) => {
                                const element = document.querySelector(selector);
                                if (element) {
                                    element.click();
                                }
                            }
                        """,
                            selector,
                        )
                        log.debug("使用JavaScript点击成功")
                    except Exception as e:
                        log.debug(f"JavaScript点击失败，尝试使用鼠标点击: {e}")
                        # 如果JavaScript点击失败，尝试使用鼠标点击
                        await self.page.mouse.click(
                            box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
                        )

                log.debug(f"点击元素 {selector} 成功")

                # 检查是否打开了新页面
                try:
                    new_page = await asyncio.wait_for(new_page_promise, timeout=2.0)
                    if new_page:
                        log.debug("检测到新页面打开，添加到页面列表")
                        # 将新页面添加到页面列表
                        self.pages.append(new_page)
                        # 切换到新页面
                        self.current_page_index = len(self.pages) - 1
                        # 等待新页面加载完成
                        await self.page.wait_for_load_state("networkidle")
                        await self.page.wait_for_load_state("domcontentloaded")
                except asyncio.TimeoutError:
                    # 没有新页面打开，继续使用当前页面
                    pass

                return {
                    "status": "success",
                    "message": "Click successfully",
                }

            except Exception as e:
                log.error(f"点击元素 {selector} 失败，等待1秒后重试: {e}")
                log.error(traceback.format_exc())
                if attempt == retries - 1:
                    return {
                        "status": "error",
                        "message": f"Click failed: {str(e)}",
                    }
                await asyncio.sleep(1)

        return {
            "status": "error",
            "message": f"Click failed: Element does not exist, **Don't use this selector: `{selector}` again.**",
        }

    async def input_text_by_selector(
        self, params: Dict[str, str], retries: int = 3
    ) -> Dict:
        """在指定输入框中输入文本，带有重试机制
        返回包含状态和原因的字典
        """

        if not self.page:
            return {
                "status": "error",
                "message": "Browser page not initialized",
            }

        selector = params.get("selector")
        text = params.get("text")
        outer_html = params.get("outer_html")
        if not selector:
            raise ValueError("Must provide a selector")
        if not text:
            raise ValueError("Must provide the text to input")
        if not outer_html:
            raise ValueError("Must provide the outer_html")

        for attempt in range(retries):
            try:
                log.debug(f"尝试在元素 {selector} 中输入文本: {text}")

                # 尝试定位元素
                locator = None
                try:
                    if selector.startswith("text="):
                        locator = self.page.locator(selector)
                    elif selector.startswith("xpath="):
                        locator = self.page.locator(selector)
                    else:
                        # 尝试CSS选择器
                        locator = self.page.locator(selector)

                    # 检查元素是否存在
                    count = await locator.count()
                    if count == 0:
                        raise ValueError(
                            f"Element does not exist, **Don't use this selector: `{selector}` again.**"
                        )
                except Exception as e:
                    log.debug(f"尝试选择器 {selector} 失败: {e}")
                    continue

                if not locator:
                    raise ValueError("Cannot find a valid selector")

                # 等待元素可见
                await locator.wait_for(state="visible", timeout=self.timeout)

                # 检查元素是否在视口内
                is_in_viewport = await locator.is_visible()
                if not is_in_viewport:
                    log.debug("元素不在视口内，尝试滚动到元素位置")
                    await locator.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)

                # 确保元素可编辑
                is_enabled = await locator.is_enabled()
                if not is_enabled:
                    raise ValueError(f"Element {selector} is not editable")

                # 清空输入框
                await locator.fill("", timeout=self.timeout)
                await asyncio.sleep(0.1)

                # 模拟真实输入
                for char in text:
                    await locator.type(char, delay=50)
                    await asyncio.sleep(0.05)

                log.debug(f"在元素 {selector} 中输入文本 {text} 成功")
                return {
                    "status": "success",
                    "message": "Input successfully",
                }

            except Exception as e:
                log.error(f"在元素 {selector} 中输入文本失败，等待1秒后重试: {e}")
                log.error(traceback.format_exc())
                if attempt == retries - 1:
                    return {
                        "status": "error",
                        "message": f"Input failed: {str(e)}",
                    }
                await asyncio.sleep(1)

        return {
            "status": "error",
            "message": f"Input failed: Element does not exist, **Don't use this selector: `{selector}` again.**",
        }

    async def go_to_url(self, params: Dict[str, str]):
        """打开指定URL"""
        if not self.page:
            return {
                "status": "error",
                "message": "Browser page not initialized",
            }
        try:
            url = params.get("url")
            if not url:
                raise ValueError("Must provide a url")
            log.debug(f"pre url: {url}")
            url = urljoin(self.page.url, url)
            log.debug(f"url: {url}")
            content = await self.open_url(url)
            if content:
                return content
            else:
                return {
                    "status": "error",
                    "message": "Open URL failed",
                }
        except Exception as e:
            log.debug(f"打开URL时出错: {e}")
            return {
                "status": "error",
                "message": f"Open URL error: {str(e)}",
            }

    async def scroll_to_bottom(
        self, params: Dict[str, str], max_retries: int = 5, scroll_delay: float = 0.5
    ):
        """滚动到页面底部

        Args:
            max_retries: 最大重试次数
            scroll_delay: 每次滚动后的等待时间（秒）
        """
        if not self.page:
            return {
                "status": "error",
                "message": "Browser page not initialized",
            }
        try:
            for attempt in range(max_retries):
                # 获取当前滚动位置和页面高度
                current_scroll = await self.page.evaluate("window.scrollY")
                page_height = await self.page.evaluate("document.body.scrollHeight")

                # 如果已经到达底部，退出循环
                if current_scroll + self.page.viewport_size["height"] >= page_height:
                    log.debug("已到达页面底部")
                    break

                # 滚动到页面底部
                await self.page.evaluate(
                    "window.scrollTo(0, document.body.scrollHeight)"
                )

                # 等待一段时间，让页面内容加载
                await asyncio.sleep(scroll_delay)

                # 检查页面高度是否发生变化
                new_page_height = await self.page.evaluate("document.body.scrollHeight")
                if new_page_height == page_height:
                    log.debug("页面高度未变化，可能已到达底部")
                    break

                log.debug(f"第 {attempt + 1} 次滚动，当前高度: {new_page_height}")

                log.debug("滚动到底部完成")

            return {
                "status": "success",
                "message": "Scroll to bottom successfully",
            }

        except Exception as e:
            log.debug(f"滚动到底部时出错: {e}")
            log.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"Scroll to bottom error: {str(e)}",
            }

    async def close(self):
        """关闭浏览器"""
        for page in self.pages:
            try:
                await page.close()
            except Exception:
                pass
        self.pages = []
        self.current_page_index = 0

        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def get_content_with_unique_selectors(self) -> str:
        """
        为页面上的所有可交互元素添加唯一标识符
        返回处理后的HTML内容
        """

        if not self.page:
            return ""

        interactive_elements = [
            "a",  # 链接
            "button",  # 按钮
            "input",  # 输入框
            "select",  # 下拉框
            "textarea",  # 文本区域
            "img",  # 图片
            "[role='button']",  # 具有按钮角色的元素
            "[onclick]",  # 具有点击事件的元素
            "[href]:not(a)",  # 具有链接的元素
            "[jsaction]",  # 具有 jsaction 属性的元素 for google maps
        ]

        element_counter = 0
        count = 0

        seen = set()

        for element_type in tqdm(interactive_elements, desc="处理HTML元素"):
            elements = await self.page.query_selector_all(element_type)

            for element in tqdm(elements, desc=f"处理{element_type}元素"):
                try:
                    # # 检查元素是否可见和可操作
                    # is_visible = await element.evaluate("""
                    #     (el) => {
                    #         const style = window.getComputedStyle(el);
                    #         return (
                    #             style.display !== 'none' &&
                    #             style.visibility !== 'hidden' &&
                    #             style.opacity !== '0' &&
                    #             !el.hidden &&
                    #             el.offsetWidth > 0 &&
                    #             el.offsetHeight > 0
                    #         );
                    #     }
                    # """)

                    # if not is_visible:
                    #     continue

                    # # 检查元素是否被其他元素遮挡
                    # is_covered = await element.evaluate("""
                    #     (el) => {
                    #         const rect = el.getBoundingClientRect();
                    #         const centerX = rect.left + rect.width / 2;
                    #         const centerY = rect.top + rect.height / 2;
                    #         const topElement = document.elementFromPoint(centerX, centerY);
                    #         return topElement !== el && !el.contains(topElement);
                    #     }
                    # """)

                    # if is_covered:
                    #     continue

                    # 对于 a 标签，检查 href 是否以 # 开头
                    if str(element) not in seen:
                        seen.add(str(element))
                        if await element.evaluate(
                            "(el) => el.tagName.toLowerCase() === 'a'"
                        ):
                            href = await element.get_attribute("href")
                            if href and href.startswith("#"):
                                continue

                        # 对于已经有 data-hid 属性，跳过
                        if await element.get_attribute("data-hid"):
                            continue

                        tag_name = await element.evaluate(
                            "(el) => el.tagName.toLowerCase()"
                        )

                        # 以 5-10 的整数随机生成一个 unique_id
                        element_counter += random.randint(5, 10)
                        count += 1
                        unique_id = f"{tag_name}-{element_counter}"

                        await element.evaluate(
                            f"(el) => el.setAttribute('data-hid', '{unique_id}')"
                        )

                        # if await element.evaluate(
                        #     "(el) => el.tagName.toLowerCase() === 'img'"
                        # ) and not await element.get_attribute("alt"):
                        #     await element.evaluate(
                        #         f"(el) => el.setAttribute('alt', 'image-{unique_id}')"
                        #     )

                        # if await element.evaluate(
                        #     "(el) => el.tagName.toLowerCase() === 'a'"
                        # ) and not await element.get_attribute("href"):
                        #     await element.evaluate("(el) => el.setAttribute('href', '#')")

                        # if await element.evaluate(
                        #     "(el) => el.tagName.toLowerCase() === 'input'"
                        # ) and not await element.get_attribute("type"):
                        #     await element.evaluate("(el) => el.setAttribute('type', 'text')")

                except Exception as e:
                    log.debug(f"处理元素时出错: {e}")
                    continue

        log.debug(f"处理 {count} 个元素")
        # 用evaluate获取html
        html = ""
        useful_elements = []
        # 需要去重
        elements = await self.page.query_selector_all(":not(:has(*))")
        for element in elements:
            outer_html = await element.evaluate("(el) => el.outerHTML")
            # outer_html = str(element)
            # print(outer_html)
            if outer_html not in useful_elements:
                useful_elements.append(outer_html)
                # print(outer_html)

        for outer_html in useful_elements:
            html += outer_html + "\n\n"

        # with open("html.html", "w", encoding="utf-8") as f:
        #     f.write(html)

        return html

    async def select_option_by_selector(
        self, params: Dict[str, str], retries: int = 3
    ) -> Dict:
        if not self.page:
            return {
                "status": "error",
                "message": "Browser page not initialized",
            }
        """选择或设置选项值，支持下拉框、单选框和复选框

        Args:
            selector: 元素选择器
            value: 对于下拉框和单选框，指定要选择的值
            checked: 对于复选框，指定是否选中（True/False）
            retries: 重试次数

        Returns:
            Dict: 包含操作结果的字典
        """
        selector = params.get("selector")
        value = params.get("value")
        checked = params.get("checked")
        outer_html = params.get("outer_html")

        if not selector:
            raise ValueError("Must provide a selector")
        if not outer_html:
            raise ValueError("Must provide the outer_html")

        if value is None and checked is None:
            raise ValueError("Must provide value or checked parameter")

        for attempt in range(retries):
            try:
                log.debug(f"尝试选择元素: {selector}")

                # 尝试定位元素
                locator = None
                try:
                    if selector.startswith("text="):
                        locator = self.page.locator(selector)
                    elif selector.startswith("xpath="):
                        locator = self.page.locator(selector)
                    else:
                        locator = self.page.locator(selector)

                    # 检查元素是否存在
                    count = await locator.count()
                    if count == 0:
                        raise ValueError(
                            f"Element does not exist, **Don't use this selector: `{selector}` again.**"
                        )
                except Exception as e:
                    log.debug(f"尝试选择器 {selector} 失败: {e}")
                    continue

                if not locator:
                    raise ValueError("Cannot find a valid selector")

                # 等待元素可见
                await locator.wait_for(state="visible", timeout=self.timeout)

                # 检查元素是否在视口内
                is_in_viewport = await locator.is_visible()
                if not is_in_viewport:
                    log.debug("元素不在视口内，尝试滚动到元素位置")
                    await locator.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)

                # 确保元素可交互
                is_enabled = await locator.is_enabled()
                if not is_enabled:
                    raise ValueError(f"Element {selector} is not interactive")

                # 获取元素类型
                element_type = await locator.evaluate("el => el.tagName.toLowerCase()")
                input_type = await locator.evaluate(
                    "el => el.type ? el.type.toLowerCase() : ''"
                )

                # 根据元素类型执行不同的操作
                if element_type == "select":
                    # 处理下拉框
                    if value is None:
                        raise ValueError("Dropdown must provide value parameter")
                    await locator.select_option(value=value)
                    log.debug(f"选择下拉框选项: {value}")
                elif element_type == "input":
                    if input_type == "radio":
                        # 处理单选框
                        if value is None:
                            raise ValueError(
                                "Radio button must provide value parameter"
                            )
                        await locator.evaluate(
                            f"el => el.value === '{value}' && el.click()"
                        )
                        log.debug(f"选择单选框: {value}")
                    elif input_type == "checkbox":
                        # 处理复选框
                        if checked is None:
                            raise ValueError("Checkbox must provide checked parameter")
                        current_checked = await locator.is_checked()
                        if current_checked != checked:
                            await locator.click()
                        log.debug(f"设置复选框状态: {checked}")
                    else:
                        raise ValueError(f"Unsupported input type: {input_type}")
                else:
                    raise ValueError(f"Unsupported element type: {element_type}")

                return {
                    "status": "success",
                    "message": "Operation successful",
                }

            except Exception as e:
                log.debug(f"选择元素 {selector} 失败，等待1秒后重试: {e}")
                log.error(traceback.format_exc())
                if attempt == retries - 1:
                    return {
                        "status": "error",
                        "message": f"Select failed: {str(e)}",
                    }
                await asyncio.sleep(1)

        return {
            "status": "error",
            "message": f"Select failed: Element does not exist, **Don't use this selector: `{selector}` again.**",
        }

    async def screenshot(self):
        """
        截取页面截图
        """
        if not self.page:
            return {
                "status": "error",
                "message": "Browser page not initialized",
            }
        try:
            image = await self.page.screenshot(full_page=True)
            base64_image = base64.b64encode(image).decode("utf-8")
            return base64_image
        except Exception as e:
            log.debug(f"截图失败: {e}")
            return None

    async def check_image_by_selector(self, params: Dict[str, str]) -> Dict[str, str]:
        """
        检查指定元素是否存在

        Args:
            selector: 元素选择器

        Returns:
            Dict[str, str]: 包含状态和原因的字典
        """
        try:
            selector = params.get("selector")
            if not selector:
                raise ValueError("Must provide a selector")

            image_base64 = await self.get_image_base64_from_screenshot(selector)
            if not image_base64:
                raise ValueError("Cannot get image base64")

            return {
                "status": "success",
                "message": "Image has been transferred to base64, please check the image carefully.",
                "image_base64": image_base64,
            }
        except Exception as e:
            log.debug(f"检查图片时出错: {e}")
            log.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"Check image failed: {str(e)}",
            }

    async def search_and_stop(self, params: Dict[str, str]) -> Dict[str, str]:
        """
        搜索指定URL并停止

        Args:
            url: 要搜索的URL
        """
        try:
            query = params.get("query")
            reason = params.get("reason")
            if not query:
                raise ValueError("Must provide a query")
            if not reason:
                raise ValueError("Must provide a reason")

            return {
                "status": "interrupt",
                "message": f"## Reason: \n {reason}\n\n## Query: \n {query}\n",
            }
        except Exception as e:
            log.debug(f"搜索并停止时出错: {e}")
            log.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"Search and stop failed: {str(e)}",
            }

    async def write_code_to_reach_purpose_and_stop(
        self, params: Dict[str, str]
    ) -> Dict[str, str]:
        """
        写代码达到目的并停止

        Args:
            params: 包含目的和原因的参数
        """
        try:
            demand = params.get("demand")
            reason = params.get("reason")
            if not demand:
                raise ValueError("Must provide a demand")
            if not reason:
                raise ValueError("Must provide a reason")

            return {
                "status": "interrupt",
                "message": f"## Reason: \n {reason}\n\n## Demand: \n {demand}\n",
            }
        except Exception as e:
            log.debug(f"写代码达到目的并停止时出错: {e}")
            log.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"Write code to reach purpose and stop failed: {str(e)}",
            }

    async def purpose_completed_and_stop(self, params: Dict[str, str]) -> Dict[str, str]:
        """
        达到目的并停止

        Args:
            params: 包含目的和原因的参数
        """
        try:
            answer = params.get("answer")
            reason = params.get("reason")
            if not answer:
                raise ValueError("Must provide a answer")
            if not reason:
                raise ValueError("Must provide a reason")

            return {
                "status": "finished",
                "message": f"## Reason: \n {reason}\n\n## Answer: \n {answer}\n",
            }
        except Exception as e:
            log.debug(f"达到目的并停止时出错: {e}")
            log.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"Purpose completed and stop failed: {str(e)}",
            }

    async def write_a_note(self, params: Dict[str, str]) -> Dict[str, str]:
        """
        写一个笔记

        Args:
            params: 包含笔记内容的参数
        """
        try:
            write_file = params.get("write_file")
            note = params.get("note")
            if not write_file:
                raise ValueError("Must provide a write_file")
            if not note:
                raise ValueError("Must provide a note")

            return {
                "status": "success",
                "message": note,
                "write_file": write_file,
            }
        except Exception as e:
            log.debug(f"写一个笔记时出错: {e}")
            log.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"Write a note failed: {str(e)}",
            }

    async def download_file_and_stop(self, params: Dict[str, str]) -> Dict[str, str]:
        """
        下载文件并停止

        Args:
            params: 包含文件URL的参数
        """
        try:
            url = params.get("url")
            reason = params.get("reason")
            if not url:
                raise ValueError("Must provide a url")
            if not reason:
                raise ValueError("Must provide a reason")

            return {
                "status": "interrupt",
                "message": f"## Reason: \n {reason}\n\n## URL: \n {url}\n",
            }
        except Exception as e:
            log.debug(f"下载文件时出错: {e}")
            log.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"Download file failed: {str(e)}",
            }

        """
        聚焦元素

        Args:
            selector: 元素选择器
        """
        try:
            self.page.focus(selector)
            return {
                "status": "success",
                "message": f"Focus on element by selector: {selector}",
            }
        except Exception as e:
            log.debug(f"聚焦元素时出错: {e}")
            log.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"Focus on element by selector failed: {str(e)}",
            }

    async def request_for_human_assistance(self, params: Dict[str, str]) -> Dict[str, str]:
        """
        请求人类助手

        Args:
            params: 包含原因的参数
        """
        try:
            reason = params.get("reason")
            if not reason:
                raise ValueError("Must provide a reason")

            message = input(
                f"When finish the operation, You can [ Press Enter to Continue ] OR [ Leave Some Message to Browser ] : "
            )

            message = message.strip()

            return {
                "status": "success",
                "message": message,
            }
        except Exception as e:
            log.debug(f"请求人类助手时出错: {e}")
            log.error(traceback.format_exc())
            return {
                "status": "error",
                "message": f"Request for human assistance failed: {str(e)}",
            }
