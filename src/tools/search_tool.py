"""
平静AI助手工具集 - 联网搜索工具
"""
from langchain.tools import tool
from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context


@tool
def web_search(query: str) -> str:
    """
    联网搜索工具。获取实时信息、新闻、最新数据。
    
    参数:
        query: 搜索关键词
    """
    try:
        ctx = new_context(method="web_search")
        client = SearchClient(ctx=ctx)
        response = client.web_search_with_summary(query=query, count=5)
        
        result_parts = []
        if response.summary:
            result_parts.append(f"📋 摘要:\n{response.summary}\n")
        
        if response.web_items:
            result_parts.append("🔗 相关链接:")
            for i, item in enumerate(response.web_items[:5], 1):
                result_parts.append(f"\n{i}. {item.title}")
                result_parts.append(f"   来源: {item.site_name}")
                result_parts.append(f"   链接: {item.url}")
        
        return "\n".join(result_parts) if result_parts else "未找到相关结果"
    except Exception as e:
        return f"搜索出错: {str(e)}"


# 可用工具列表
AVAILABLE_TOOLS = [web_search]
