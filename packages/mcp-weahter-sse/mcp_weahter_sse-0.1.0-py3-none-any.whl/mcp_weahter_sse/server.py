# -*- coding: utf-8 -*-
# @Time：2025/7/8 3:05 下午
# @Author: zhangna
import json
import httpx
import argparse
from typing import Any
from json import JSONDecodeError
from mcp.server.fastmcp import FastMCP

# 初始化 MCP 服务器
mcp = FastMCP("WeatherServer")
# 高德地图天气  获取天气
WEATHER_API_BASE = "https://restapi.amap.com/v3/weather/weatherInfo"
API_KEY = "0e18bca53a0ae7474cbcdbdaf95665f2"

async def get_weather(city: str) -> dict[str, Any] | None:
    """
    从 高德地图天气  API 获取天气信息。
    :param city: 城市名称（如 北京）
    :return: 天气数据字典；若出错返回包含 error 信息的字典
    """
    params = {
        "city": city,
        "key": API_KEY,
        "extensions": "base", # base:实时 all:预报

    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(WEATHER_API_BASE, params=params)
            response.raise_for_status()
            data = response.json()  # 返回字典类型
            # 验证JSON完整性
            if not isinstance(data, dict) or "lives" not in data:
                raise ValueError("Invalid API response format")
            return data
        except (JSONDecodeError, ValueError) as e:
            return {"error": f"数据格式错误: {str(e)}"}
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP 错误: {e.response.status_code}"}
        except Exception as e:
            return {"error": f"请求失败: {str(e)}"}

def format_weather(data: dict[str, Any] | str) -> str:
    """
    将天气数据格式化为易读文本。
    :param data: 天气数据（可以是字典或 JSON 字符串）
    :return: 格式化后的天气信息字符串
    """
    # 如果传入的是字符串，则先转换为字典
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception as e:
            return f"无法解析天气数据: {e}"
            # 如果数据中包含错误信息，直接返回错误提示
    if "error" in data:
        return f"{data['error']}"
    wetather_info = data['lives'][0]
    # 提取数据时做容错处理
    province = wetather_info.get("province", "未知")
    city = wetather_info.get("city", "未知")
    weather = wetather_info.get("weather", "未知")
    temp = wetather_info.get("temperature", "N/A")
    humidity = wetather_info.get("humidity", "N/A")
    winddirection = wetather_info.get("winddirection", "N/A")
    wind_speed = wetather_info.get("windpower", "N/A")
    return (
        f"城市：{province}，{city}\n"
        f"天气: {weather}\n"
        f"温度: {temp}°C\n"
        f"湿度: {humidity}%\n"
        f"风向: {winddirection}风\n"
        f"风速: {wind_speed} m/s\n")


@mcp.tool()
async def query_weather(city: str) -> str:
    """
    输入指定城市的名称，返回今日天气查询结果。
    :param city: 城市名称（如"北京"）
    :return: 格式化后的天气信息字符串
    """
    data = await get_weather(city)
    return format_weather(data)

def main():
    parser = argparse.ArgumentParser(description="Weather Server")
    parser.add_argument("--api_key", type=str, required=True, help="你的高德地图 API Key")
    args = parser.parse_args()
    global API_KEY
    API_KEY = args.api_key
    mcp.run(transport='sse')

if __name__ == "__main__":
    main()