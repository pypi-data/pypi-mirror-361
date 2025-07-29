import argparse
import json
import httpx
from typing import Any
from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv(override=True)

# 初始化 MCP 服务器
mcp = FastMCP("WeatherServer")

# OpenWeather API 配置
OPENWEATHER_BASE_URL="http://api.openweathermap.org/data/2.5/weather"
# API_KEY 会从命令行参数获取
API_KEY=None 
USER_AGENT="weather-app/1.0"

async def fetch_weather(city:str)->dict[str,Any]|None:
    '''
    从 OpenWeather API获取天气信息。
    :param city:城市名称（需使用英文，如Beijing)
    :return:天气数据字典;若出错返回包含error信息的字典
    '''
    if not API_KEY:
        return {'error': 'OpenWeather API Key 未通过命令行参数配置'}

    params= {
        'q':city,
        'appid':API_KEY,
        'units':'metric',
        'lang':'zh_cn'
    }
    headers = {'User-Agent':USER_AGENT}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(OPENWEATHER_BASE_URL,params=params,headers=headers,timeout=30.0)
            response.raise_for_status()
            return response.json() # 返回字典类型
        except httpx.HTTPStatusError as e:
            return {'error':f'HTTP错误：{e.response.status_code}'}
        except Exception as e:
            return {'error':f'请求失败:{str(e)}'}

def format_weather(data:dict[str,Any]|str) -> str:
    '''
    将天气数据格式化为易读文本
    :param data:天气数据（可以是字典或JSON字符串）
    :return:格式化后的天气信息字符串
    '''
    if isinstance(data,str):
        try:
            data = json.loads(data)
        except Exception as e:
            return f"无法解析天气数据:{e}"
    
    if "error" in data:
        return f"! {data['error']} " # type:ignore
    
    city = data.get('name',"未知") # type:ignore
    country = data.get('sys',{}).get('country','未知') # type:ignore
    temp = data.get('main',{}).get('temp','N/A') # type:ignore
    humidity = data.get('main',{}).get('humidity','N/A') #type:ignore
    wind_speed = data.get('wind',{}).get('speed','N/A') # type:ignore
    weather_list = data.get('weather',[{}]) #type:ignore
    description = weather_list[0].get('description','未知')

    return (
        f"{city}，{country}\n"
        f"温度：{temp}摄氏度\n"
        f"湿度:{humidity}%\n"
        f"风速:{wind_speed}m/s\n"
        f"天气:{description}\n"
    )

@mcp.tool()
async def query_weather(city:str) -> str:
    '''
    输入指定城市的英文名称，返回今日天气查询结果。
    :param city:城市名称（需使用英文）
    :return:格式化后的天气信息
    '''
    data = await fetch_weather(city)
    return format_weather(data) #type:ignore

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="Weather Server using SSE")
    parser.add_argument("--api_key", type=str, required=True, help='你的OpenWeather API Key')
    args = parser.parse_args()
    
    # 将命令行传入的 api_key 赋值给全局变量
    global API_KEY
    API_KEY = args.api_key
    
    # 使用 sse 传输协议启动一个Web服务
    mcp.run(transport='sse')

if __name__=='__main__':
    main()