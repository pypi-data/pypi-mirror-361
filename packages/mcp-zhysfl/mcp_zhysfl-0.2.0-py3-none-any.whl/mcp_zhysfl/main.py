from pathlib import Path
from pprint import pprint
from tkinter import PROJECTING

import graphrag
import pandas as pd

import graphrag.api as api
from graphrag.config.load_config import load_config
from graphrag.index.typing.pipeline_run_result import PipelineRunResult

PROJECT_DIRECTORY='./graphrag'

graphrag_config = load_config(Path(PROJECT_DIRECTORY))

async def index():
    index_result:list[PipelineRunResult] = await api.build_index(config=graphrag_config)

    for workflow_result in index_result:
        status = f"error\n{workflow_result.errors}" if workflow_result.errors else "success"
        print(f"Workflow Name:{workflow_result.workflow}\tStatus:{status}")
async def query(query = "请帮我对比下ID3和C4.5决策树算法优劣势。并用中文进行回答。"):
    entities = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/entities.parquet")
    communities = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/communities.parquet")
    community_reports = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/community_reports.parquet")
    response, context = await api.global_search(
        config=graphrag_config,
        entities=entities,
        communities=communities,
        community_reports=community_reports,
        community_level=2,
        dynamic_community_selection=False,
        response_type="Multiple Paragraphs",
        query=query,
    )
#     在这里，我们调用 `global_search` 方法，使用已加载的索引数据进行查询。  
# - `community_level=2`：设定社群层级为 2 级。  
# - `dynamic_community_selection=False`：禁用动态社群选择。  
# - `response_type="Multiple Paragraphs"`：设置返回的查询结果为多段落格式。  
# - `query=query`：查询问题为 **"请帮我对比下ID3和C4.5决策树算法优劣势。并用中文进行回答。"**。
    print(response)
    pprint(context)

async def rag_ML(query: str) -> str:
    """
    输入机器学习领域相关问题，获得问题答案。
    :param query: 机器学习领域的相关问题
    :return: query问题对应的答案
    """
    PROJECT_DIRECTORY = "/root/autodl-tmp/MCP/mcp-graphrag/graphrag"
    graphrag_config = load_config(Path(PROJECT_DIRECTORY))
    
    # 加载实体
    entities = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/entities.parquet")
    # 加载社区
    communities = pd.read_parquet(f"{PROJECT_DIRECTORY}/output/communities.parquet")
    # 加载社区报告
    community_reports = pd.read_parquet(
        f"{PROJECT_DIRECTORY}/output/community_reports.parquet"
    )
    # 进行全局搜索
    response, context = await api.global_search(
        config=graphrag_config,
        entities=entities,
        communities=communities,
        community_reports=community_reports,
        community_level=2,
        dynamic_community_selection=False,
        response_type="Multiple Paragraphs",
        query=query,
    )
    
    return response #type:ignore

