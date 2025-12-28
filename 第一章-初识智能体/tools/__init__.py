from .get_weather import get_weather
from .get_attraction import get_attraction

# 将工具函数组织成字典，方便通过名称调用
available_tools = {
    "get_weather": get_weather,
    "get_attraction": get_attraction
}

# 导出给外部使用
__all__ = ["available_tools", "get_weather", "get_attraction"]

