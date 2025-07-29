import asyncio
from pkgutil import resolve_name
from zoneinfo import available_timezones
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack
import os
from openai import OpenAI
from dotenv import load_dotenv
from openai.types.responses import response, response_output_item
from pydantic.type_adapter import R
from typing import Optional
load_dotenv(override=True)

import json
import sys

class MCPClient:
    def __init__(self) -> None:
        '''初始化 MCP 客户端'''
        self.session:Optional[ClientSession]= None
        self.exit_stack = AsyncExitStack()
        self.api_key=os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("× 未找到API Key,请在 .env文件中设置")
        self.model = os.getenv("MODEL") or 'deepseek-chat'
        self.base_url = os.getenv("DEEPSEEK_BASE_URL")
        self.client = OpenAI(api_key=self.api_key,base_url=self.base_url)


    async def connect_to_server(self,server_script_path:str):
        '''连接到MCP服务器并列出可用工具'''
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError('服务器脚本必须是 .py 或 .js 文件')
        
        command = 'python' if is_python else 'node'
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        # 启动MCP服务器并建立通信
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio,self.write=stdio_transport
        self.session=await self.exit_stack.enter_async_context(ClientSession(self.stdio,self.write))

        await self.session.initialize()

        # 列出MCP服务器上的工具
        response=await self.session.list_tools()
        tools = response.tools
        print('\n已连接到服务器，支持以下工具:',[tool.name for tool in tools])


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
        '''运行交互式聊天循环'''
        print("\nMCP 客户端已启动！输入 'quit' 退出")

        while True:
            try:
                query = input('\n你:').strip()
                if query.lower() == 'quit':
                    break
                
                response = await self.process_query(query) # 发送用户输入给LLM

                print(f"\nDS:{response}")
            except Exception as e:
                print(f"\n发生错误：{str(e)}")
    
    async def cleanup(self):
        '''清理资源'''
        print("\n正在关闭连接...")
        await self.exit_stack.aclose()
        print("连接已关闭。")

async def main():
    if len(sys.argv) < 2:
        print("用法: python client.py <path_to_server_script>")
        sys.exit(1)
    
    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    except ValueError as e:
        print(f"初始化错误: {e}")
    except KeyboardInterrupt:
        print("\n检测到中断，正在退出...")
    finally:
        await client.cleanup()

    
if __name__=='__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # 这个捕获是为了在 asyncio.run(main()) 启动之前被中断的情况
        pass