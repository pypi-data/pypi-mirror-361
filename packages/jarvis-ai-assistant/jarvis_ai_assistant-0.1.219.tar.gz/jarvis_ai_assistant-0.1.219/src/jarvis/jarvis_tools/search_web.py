# -*- coding: utf-8 -*-
"""A tool for searching the web."""
from typing import Any, Dict

import httpx
from bs4 import BeautifulSoup
from ddgs import DDGS

from jarvis.jarvis_agent import Agent
from jarvis.jarvis_platform.registry import PlatformRegistry
from jarvis.jarvis_utils.http import get as http_get
from jarvis.jarvis_utils.output import OutputType, PrettyOutput


class SearchWebTool:
    """A class to handle web searches."""

    name = "search_web"
    description = "搜索互联网上的信息"
    parameters = {
        "type": "object",
        "properties": {"query": {"type": "string", "description": "具体的问题"}},
    }

    def _search_with_ddgs(self, query: str, agent: Agent) -> Dict[str, Any]:
        # pylint: disable=too-many-locals, broad-except
        """Performs a web search, scrapes content, and summarizes the results."""
        try:
            PrettyOutput.print("▶️ 使用 DuckDuckGo 开始网页搜索...", OutputType.INFO)
            results = list(DDGS().text(query, max_results=5))

            if not results:
                return {
                    "stdout": "未找到搜索结果。",
                    "stderr": "未找到搜索结果。",
                    "success": False,
                }

            urls = [r["href"] for r in results]
            full_content = ""
            visited_urls = []

            for url in urls:
                try:
                    PrettyOutput.print(f"📄 正在抓取内容: {url}", OutputType.INFO)
                    response = http_get(url, timeout=10.0, follow_redirects=True)
                    soup = BeautifulSoup(response.text, "lxml")
                    body = soup.find("body")
                    if body:
                        full_content += body.get_text(" ", strip=True) + "\n\n"
                        visited_urls.append(url)
                except httpx.HTTPStatusError as e:
                    PrettyOutput.print(
                        f"⚠️ HTTP错误 {e.response.status_code} 访问 {url}",
                        OutputType.WARNING,
                    )
                except httpx.RequestError as e:
                    PrettyOutput.print(f"⚠️ 请求错误: {e}", OutputType.WARNING)

            if not full_content.strip():
                return {
                    "stdout": "无法从任何URL抓取有效内容。",
                    "stderr": "抓取内容失败。",
                    "success": False,
                }

            url_list_str = "\n".join(f"  - {u}" for u in visited_urls)
            PrettyOutput.print(
                f"🔍 已成功访问并处理以下URL:\n{url_list_str}", OutputType.INFO
            )

            PrettyOutput.print("🧠 正在总结内容...", OutputType.INFO)
            summary_prompt = f"请为查询“{query}”总结以下内容：\n\n{full_content}"

            if not agent.model:
                return {
                    "stdout": "",
                    "stderr": "用于总结的Agent模型未找到。",
                    "success": False,
                }

            platform_name = agent.model.platform_name()
            model_name = agent.model.name()

            model = PlatformRegistry().create_platform(platform_name)
            if not model:
                return {
                    "stdout": "",
                    "stderr": "无法创建用于总结的模型。",
                    "success": False,
                }

            model.set_model_name(model_name)
            model.set_suppress_output(False)
            summary = model.chat_until_success(summary_prompt)

            return {"stdout": summary, "stderr": "", "success": True}

        except Exception as e:
            PrettyOutput.print(f"❌ 网页搜索过程中发生错误: {e}", OutputType.ERROR)
            return {
                "stdout": "",
                "stderr": f"网页搜索过程中发生错误: {e}",
                "success": False,
            }

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the web search.

        If the agent's model supports a native web search, it uses it.
        Otherwise, it falls back to using DuckDuckGo Search and scraping pages.
        """
        query = args.get("query")
        agent = args.get("agent")

        if not query:
            return {"stdout": "", "stderr": "缺少查询参数。", "success": False}

        if not isinstance(agent, Agent) or not agent.model:
            return {
                "stdout": "",
                "stderr": "Agent或Agent模型未找到。",
                "success": False,
            }

        if agent.model.support_web():
            model = PlatformRegistry().create_platform(agent.model.platform_name())
            if not model:
                return {"stdout": "", "stderr": "无法创建模型。", "success": False}
            model.set_model_name(agent.model.name())
            model.set_web(True)
            model.set_suppress_output(False)
            return {
                "stdout": model.chat_until_success(query),
                "stderr": "",
                "success": True,
            }

        return self._search_with_ddgs(query, agent)

    @staticmethod
    def check() -> bool:
        """Check if the tool is available."""
        return True
