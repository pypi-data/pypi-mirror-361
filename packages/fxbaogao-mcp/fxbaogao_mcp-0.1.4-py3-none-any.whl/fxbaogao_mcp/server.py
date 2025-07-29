import json
import os
from typing import Optional, List, Union

import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP


class Settings:
    """应用配置"""

    # API 配置
    BASE_URL: str = os.getenv("BASE_URL", "https://api.fxbaogao.com")

    # HTTP 客户端配置
    HTTP_TIMEOUT: float = float(os.getenv("HTTP_TIMEOUT", "30.0"))


settings = Settings()

app = FastMCP("FxbaogaoMcp")
client = httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT)


@app.tool(
    name="search_reports",
    description="""搜索研究报告工具。支持按关键词、作者、机构名称等条件搜索研报。
        参数说明：
        - keywords: 搜索关键词，支持中英文
        - authors: 作者姓名列表，如 ["张三", "李四"]  
        - org_names: 机构名称列表，如 ["中信证券", "华泰证券"]
        - start_time: 开始时间，毫秒级时间戳，如 1640995200000 (2022-01-01 00:00:00)
        - end_time: 结束时间，毫秒级时间戳，且支持以下格式：
          * 毫秒级时间戳，如 1672531199000 (2022-12-31 23:59:59)  
          * 相对时间字符串：
            - "last3day": 最近3天
            - "last7day": 最近1周  
            - "last1mon": 最近1个月
            - "last3mon": 最近3个月
            - "last1year": 最近1年
        - page_size: 返回数量，默认10，最大100

        使用示例：
        - 搜索关键词: search_reports(keywords="人工智能")
        - 按机构搜索: search_reports(org_names=["中信证券"])  
        - 获取特定报告详情: search_reports(doc_ids=[12345, 67890])
        - 时间范围搜索: search_reports(keywords="新能源", end_time="last1mon")
        - 时间范围搜索: search_reports(keywords="新能源", start_time=1748707200000, end_time=1749398399999)
"""
)
async def search_reports(
        keywords: Optional[str] = None,
        authors: Optional[List[str]] = None,
        org_names: Optional[List[str]] = None,
        start_time: Optional[int] = None,
        end_time: Optional[Union[int, str]] = None,
        page_size: int = 10) -> str:
    """搜索研报"""
    try:
        print(f"搜索研报请求: keywords={keywords}, authors={authors}")

        # 构建搜索请求
        search_request = {
            "keywords": keywords,
            "authors": authors or [],
            "orgNames": org_names or [],
            "paragraphSize": 3,
            "startTime": start_time,
            "endTime": end_time,
            "pageSize": page_size,
            "pageNum": 1
        }

        # 调用搜索接口
        response = await client.post(
            f"{settings.BASE_URL}/mofoun/report/searchReport/searchNoAuth",
            json=search_request
        )

        response.raise_for_status()

        result = response.json()

        # 为每个报告添加 reportUrl 字段
        if result.get("code") == 0 and result.get("data") and result["data"].get("dataList"):
            for report in result["data"]["dataList"]:
                if "docId" in report:
                    report["reportUrl"] = f"https://www.fxbaogao.com/view?id={report['docId']}"

        print(f"搜索成功，返回 {len(result.get('data', {}).get('dataList', []))} 条记录")

        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        print(f"搜索研报失败: {e}")
        raise


@app.tool(
    name="get_report_content",
    description="""
    根据 docId (报告id) 获取研报正文内容和总结

    Args:
        doc_id (int): 研报文档ID，从搜索研报接口返回的docId字段获取

    Usage:
        # 首先通过搜索接口获取docId
        search_result = await search_reports("某个关键词")
        doc_id = search_result["data"]['dataList'][0]["docId"]  # 获取第一个结果的docId

        # 然后获取该研报的详细内容
        content = await get_report_content(doc_id)
    """
)
async def get_report_content(doc_id: int) -> str:
    print(f"获取研报正文请求: doc_id={doc_id}")

    response = await client.get(
        f"https://www.fxbaogao.com/detail/{doc_id}",
        headers={"AUTH-KEY": ""}
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    # 提取 AI 智能摘要部分 <li>
    summary_items = soup.select("div ul li")
    summary_text = [li.get_text(strip=True) for li in summary_items]

    # 提取正文 <p>
    paragraphs = soup.select("div p")
    paragraph_text = [p.get_text(strip=True) for p in paragraphs]

    # 构造 JSON 格式结果
    result = {
        "summary": summary_text,
        "content": paragraph_text
    }

    return json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    app.run(transport="stdio")
