import asyncio
from contextlib import AsyncExitStack
import os
from dotenv import load_dotenv
from openai import OpenAI
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters, ClientSession
import json
import sys
from typing import Optional

load_dotenv(override=True)  # 加载 .env 文件中的环境变量

class MCPClient:
    def __init__(self):
        """初始化 MCP 客户端"""

        self.exit_stack = AsyncExitStack()
        self.openai_api_key = os.getenv("DEEPSEEK_API_KEY") # 读取 OpenAI API Key
        self.base_url = os.getenv("DEEPSEEK_BASE_URL") # 读取 BASE YRL
        self.model = 'deepseek-chat'
        if not self.openai_api_key:
            raise ValueError("❌ 未找到 OpenAI API Key，请在 .env 文件中设置OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.openai_api_key, base_url=self.base_url)
        self.session: Optional[ClientSession] = None

    async def transform_json(self, json2_data):
        """
        将Claude Function calling参数格式转换为OpenAI Function calling参数格式，多余字
        段会被直接删除。
        :param json2_data: 一个可被解释为列表的 Python 对象（或已解析的 JSON 数据）
        :return: 转换后的新列表
        """
        result = []

        for item in json2_data:
            # 确保有 "type" 和 "function" 两个关键字段
            if not isinstance(item, dict) or "type" not in item or "function" not in item:
                continue
            
            old_func = item["function"]
            # 确保 function 下有我们需要的关键子字段
            if not isinstance(old_func, dict) or "name" not in old_func or "description" not in old_func:
                continue
            # 处理新 function 字段
            new_func = {
            "name": old_func["name"],
            "description": old_func["description"],
            "parameters": {}
            }
            # 读取 input_schema 并转成 parameters
            if "input_schema" in old_func and isinstance(old_func["input_schema"], dict):
                old_schema = old_func["input_schema"]
                # 新的 parameters 保留 type, properties, required 这三个字段
                new_func["parameters"]["type"] = old_schema.get("type", "object")
                new_func["parameters"]["properties"] =old_schema.get("properties", {})
                new_func["parameters"]["required"] = old_schema.get("required",[])
                
                new_item = {
                "type": item["type"],
                "function": new_func
                }

            result.append(new_item)
            
            return result

    async def connect_to_server(self, server_script_path: str):
        """连接到 MCP 服务器并列出可用工具"""
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("服务器脚本必须是 .py 或 .js 文件")
    
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
            )
        # 启动 MCP 服务器并建立通信
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        print(f"DEBUG: 已建立通信，stdio: {self.stdio}, write: {self.write}")
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        print(f"DEBUG: 开始创建 session")
        await self.session.initialize()
        print(f"DEBUG: 已初始化 session")

        # 列出 MCP 服务器上的工具
        response = await self.session.list_tools()
        tools = response.tools
        print("\n已连接到服务器，支持以下工具:", [tool.name for tool in tools])
    async def process_query(self,query:str) -> str:
        '''使用大模型处理查询并调用可用的MCP工具(function calling)，支持多次调用'''
        messages=[
            {'role':'system','content':'你是一个智能助手，帮助用户回答问题。'},
            {'role':'user','content':query}
        ]

        response = await self.session.list_tools() # type:ignore

        available_tools=[
            {
                'type':'function',
                'function':{
                    'name':tool.name,
                    'description':tool.description,
                    'input_schema':tool.inputSchema
                }
            }for tool in response.tools
        ]

        # 初次调用大模型
        response = self.client.chat.completions.create(
            model=self.model, # type:ignore
            messages=messages,# type:ignore
            tools=available_tools, # type:ignore
            tool_choice="auto" # 让模型自动选择是否调用工具
        )
        
        response_message = response.choices[0].message

        # 核心改动：使用 while 循环处理多次工具调用
        # 只要模型的回复中包含 tool_calls，就一直循环
        while response_message.tool_calls:
            # 将模型的回复（包含工具调用请求）添加到消息历史中
            messages.append(response_message.model_dump())

            # 遍历并执行模型请求的所有工具调用
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name 
                tool_args = json.loads(tool_call.function.arguments)
                
                print(f"\n[Calling tool {tool_name} with args {tool_args}]\n")

                # 通过MCP session执行工具
                result = await self.session.call_tool(tool_name, tool_args) #type:ignore
                
                # 将工具执行结果添加到消息历史中，以便模型进行下一步决策
                messages.append({
                    "role": "tool",
                    "content": result.content[0].text, #type:ignore
                    "tool_call_id": tool_call.id,
                })
            
            # 再次调用大模型，并附带上所有工具调用的结果
            response = self.client.chat.completions.create(
                model=self.model,# type:ignore
                messages=messages,# type:ignore
                tools=available_tools,# type:ignore
                tool_choice="auto" # 继续让模型自动决策
            )
            response_message = response.choices[0].message
        
        # 当模型不再返回工具调用时，`response_message.content` 将包含最终的自然语言回复
        if response_message.content:
             return response_message.content #type:ignore
        
        return "抱歉，无法获取有效的回复内容。" # 添加一个备用回复

    async def chat_loop(self):
        """运行交互式聊天循环"""
        print("\n🤖 MCP 客户端已启动！输入 'quit' 退出")
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break
                response = await self.process_query(query)
                print(f"\n🤖 OpenAI: {response}")
            except Exception as e:
                print(f"\n⚠️ 发生错误: {str(e)}")

    async def cleanup(self):
        """清理资源"""
        await self.exit_stack.aclose()



async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <server_script_path>")
        sys.exit(1)

    client = MCPClient()
    
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())