[English](README.md) | [中文](README.zh-CN.md)

## Installation

1. Install package:

```sh

pip install hero-core hero-tools 

```

2. Quickly Start

```python
from hero import Hero, Model, Tool
from hero_tools import crewl_web, download_file


default_model = Model(
    model_name="deepseek",
    model_url="https://api.example.com/v1",
    model_api_key="api-key",
)

hero = Hero(
    name="hero",
    model=default_model,
)

tool = Tool()

@hero.tool("add")
def add_func(a, b):
    """
    <desc>Addition calculator</desc>
    <params>
        <a type="number">addend a</a>
        <b type="number">addend b</b>
    </params>
    <example>
        {
            "tool": "add",
            "params": {
                "a": 1, 
                "b": 2
            }
        }
    </example>
    """
    return a + b

hero.add_tool(crewl_web, download_file, add_func)

hero.run(question="some question")

```