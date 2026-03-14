from __future__ import annotations

from typing import Any


SEED_SITES: list[dict[str, Any]] = [
    {
        "name": "ChatGPT",
        "url": "https://chat.openai.com",
        "logo": "C",
        "description": "OpenAI conversational AI assistant.",
        "level1": "AI Tools",
        "level2": "Text Generation",
        "level3": "Chat Assistants",
        "tags": ["GPT", "Assistant"],
        "isRecommended": True,
        "sortOrder": 10,
        "status": "approved",
    },
    {
        "name": "Claude",
        "url": "https://claude.ai",
        "logo": "C",
        "description": "Long-context AI assistant for writing and analysis.",
        "level1": "AI Tools",
        "level2": "Text Generation",
        "level3": "Chat Assistants",
        "tags": ["Anthropic", "Writing"],
        "sortOrder": 9,
        "status": "approved",
    },
    {
        "name": "Midjourney",
        "url": "https://midjourney.com",
        "logo": "M",
        "description": "Image generation platform for creative workflows.",
        "level1": "AI Tools",
        "level2": "Image Generation",
        "level3": "Creative",
        "tags": ["Image", "Art"],
        "sortOrder": 8,
        "status": "approved",
    },
    {
        "name": "Cursor",
        "url": "https://cursor.com",
        "logo": "C",
        "description": "AI-first code editor for engineering teams.",
        "level1": "AI Tools",
        "level2": "Developer Tools",
        "level3": "Editors",
        "tags": ["IDE", "Coding"],
        "isRecommended": True,
        "sortOrder": 10,
        "status": "approved",
    },
    {
        "name": "Hugging Face",
        "url": "https://huggingface.co",
        "logo": "H",
        "description": "Open platform for models, datasets, and demos.",
        "level1": "AI Resources",
        "level2": "Platforms",
        "level3": "Model Hub",
        "tags": ["Models", "Community"],
        "sortOrder": 7,
        "status": "approved",
    },
]


SEED_ARTICLES: list[dict[str, Any]] = [
    {
        "name": "导航站文章展示兼容示例",
        "url": "https://example.com/articles/navigation-content-demo",
        "logo": "文",
        "description": "一篇用于验证富文本、Markdown 与纯文本兼容展示的模拟文章。",
        "level1": "站内文章",
        "level2": "产品更新",
        "level3": "演示内容",
        "tags": ["Demo", "Article"],
        "isRecommended": True,
        "sortOrder": 20,
        "status": "approved",
        "contentFormat": "markdown",
        "content": "# 导航站文章展示兼容示例\n\n这篇文章用于验证三类内容展示能力：\n\n- Markdown 文章\n- 富文本 HTML 文章\n- 纯文本说明\n\n## 当前改造点\n\n1. 后台编辑器升级为更完整的组件。\n2. 前台详情页支持文章阅读，而不是只跳转站点。\n3. 数据层将文章与导航链接拆分存储。\n\n> 这是一条示例引用，用于检查样式。\n\n```ts\nconst contentType = 'article'\nconst format = 'markdown'\n```\n\n你现在看到的就是插入到数据库中的模拟文章内容。\n",
    }
]
