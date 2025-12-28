import requests
import json
from datetime import datetime, timedelta


def get_weather(city: str, days: str = "0") -> str:
    """
    通过调用 wttr.in API 查询天气信息。
    
    参数:
        city: 城市名称
        days: 查询未来第几天的天气 (0=今天, 1=明天, 2=后天, ..., 最多6天)
    
    如果 wttr.in 不可用，使用备用方案返回模拟数据。
    """
    try:
        days_int = int(days)
        if days_int < 0 or days_int > 6:
            return "错误: 天气预报仅支持查询今天到未来6天的天气"
    except ValueError:
        return f"错误: 无效的天数参数 '{days}'，请使用0-6之间的数字"
    
    # API端点，我们请求JSON格式的数据
    url = f"https://wttr.in/{city}?format=j1"
    
    try:
        # 发起网络请求，添加超时和更宽松的 SSL 验证
        response = requests.get(url, timeout=10, verify=True)
        # 检查响应状态码是否为200 (成功)
        response.raise_for_status() 
        # 解析返回的JSON数据
        data = response.json()
        
        # 获取日期描述
        date_desc = get_date_description(days_int)
        
        if days_int == 0:
            # 查询当前天气
            current_condition = data['current_condition'][0]
            weather_desc = current_condition['weatherDesc'][0]['value']
            temp_c = current_condition['temp_C']
            return f"{city}{date_desc}天气: {weather_desc}，气温{temp_c}°C"
        else:
            # 查询未来天气
            if days_int <= len(data.get('weather', [])):
                forecast = data['weather'][days_int - 1]  # 索引从0开始，但第0个是今天
                weather_desc = forecast['hourly'][4]['weatherDesc'][0]['value']  # 取中午的天气
                max_temp = forecast['maxtempC']
                min_temp = forecast['mintempC']
                avg_temp = forecast['avgtempC']
                return f"{city}{date_desc}天气预报: {weather_desc}，最高{max_temp}°C，最低{min_temp}°C，平均{avg_temp}°C"
            else:
                return f"抱歉，无法获取{city}{date_desc}的天气预报"
        
    except requests.exceptions.RequestException as e:
        # 网络错误时使用备用方案
        print(f"⚠️  天气API暂时不可用，使用模拟数据: {e}")
        return get_weather_fallback(city, days_int)
    except (KeyError, IndexError) as e:
        # 处理数据解析错误
        return f"错误: 解析天气数据失败，可能是城市名称无效 - {e}"


def get_date_description(days: int) -> str:
    """
    根据天数返回日期描述
    """
    target_date = datetime.now() + timedelta(days=days)
    date_str = target_date.strftime("%m月%d日")
    
    if days == 0:
        return f"今天({date_str})"
    elif days == 1:
        return f"明天({date_str})"
    elif days == 2:
        return f"后天({date_str})"
    elif days == 7:
        return f"一周后({date_str})"
    else:
        return f"未来第{days}天({date_str})"


def get_weather_fallback(city: str, days: int = 0) -> str:
    """
    备用天气查询方案 - 返回模拟的天气数据
    """
    # 简单的城市天气模拟数据
    weather_templates = {
        "北京": [
            {"weather": "晴天", "temp": "15", "max": "20", "min": "10"},
            {"weather": "多云", "temp": "16", "max": "21", "min": "11"},
            {"weather": "晴天", "temp": "17", "max": "22", "min": "12"},
            {"weather": "小雨", "temp": "14", "max": "18", "min": "10"},
        ],
        "上海": [
            {"weather": "多云", "temp": "18", "max": "22", "min": "15"},
            {"weather": "阴天", "temp": "19", "max": "23", "min": "16"},
            {"weather": "小雨", "temp": "17", "max": "21", "min": "14"},
            {"weather": "多云", "temp": "18", "max": "22", "min": "15"},
        ],
        "广州": [
            {"weather": "阴天", "temp": "22", "max": "26", "min": "19"},
            {"weather": "多云", "temp": "23", "max": "27", "min": "20"},
            {"weather": "晴天", "temp": "24", "max": "28", "min": "21"},
            {"weather": "小雨", "temp": "21", "max": "25", "min": "18"},
        ],
    }
    
    date_desc = get_date_description(days)
    
    # 获取城市的天气模板，如果没有就用默认值
    city_weather = weather_templates.get(city, [
        {"weather": "晴天", "temp": "20", "max": "24", "min": "16"},
        {"weather": "多云", "temp": "21", "max": "25", "min": "17"},
        {"weather": "晴天", "temp": "22", "max": "26", "min": "18"},
        {"weather": "小雨", "temp": "19", "max": "23", "min": "15"},
    ])
    
    # 循环使用天气模板
    data = city_weather[days % len(city_weather)]
    
    if days == 0:
        return f"{city}{date_desc}天气: {data['weather']}，气温{data['temp']}°C（模拟数据）"
    else:
        return f"{city}{date_desc}天气预报: {data['weather']}，最高{data['max']}°C，最低{data['min']}°C（模拟数据）"


