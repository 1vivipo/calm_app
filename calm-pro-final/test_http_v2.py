"""测试讯飞Spark X HTTP API - 使用OpenAI兼容格式"""
import requests
import json

# 从截图获取的配置
API_KEY = "f4808f28dd32ee67fab04630a60996f6"
API_SECRET = "NWQzZjM1ZDJhZjkzYjl4OWI4YjdjZGQ2"

# HTTP接口（从截图）
url = "https://spark-api-open.xf-yun.com/x2/chat/completions"

print("=" * 60)
print("测试讯飞Spark X HTTP API（OpenAI兼容格式）")
print("=" * 60)

# 方式1：直接用APIKey作为Authorization
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "x2",
    "messages": [
        {"role": "user", "content": "你好"}
    ]
}

print("\n方式1：Bearer Token...")
try:
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    print(f"状态码: {resp.status_code}")
    print(f"响应: {resp.text}")
except Exception as e:
    print(f"错误: {e}")

# 方式2：直接用APIKey（无Bearer）
print("\n方式2：直接API Key...")
headers2 = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}
try:
    resp = requests.post(url, headers=headers2, json=data, timeout=30)
    print(f"状态码: {resp.status_code}")
    print(f"响应: {resp.text}")
except Exception as e:
    print(f"错误: {e}")

# 方式3：试试v2端点
url_v2 = "https://spark-api-open.xf-yun.com/v2/chat/completions"
print("\n方式3：v2端点 + Bearer Token...")
try:
    resp = requests.post(url_v2, headers=headers, json={"model": "x1.5", "messages": [{"role": "user", "content": "你好"}]}, timeout=30)
    print(f"状态码: {resp.status_code}")
    print(f"响应: {resp.text}")
except Exception as e:
    print(f"错误: {e}")
