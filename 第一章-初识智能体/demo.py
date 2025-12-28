import re
import os
from model import OpenAICompatibleClient
from tools import available_tools
from dotenv import load_dotenv

load_dotenv()

# --- 1. 配置LLM客户端 ---
# DeepSeek 配置
API_KEY = os.environ.get("DEEPSEEK_API_KEY")  # 从环境变量读取 DeepSeek API Key
BASE_URL = 'https://api.deepseek.com'  # DeepSeek API 地址
MODEL_ID = 'deepseek-chat'  # DeepSeek 推荐模型，性价比很高
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

llm = OpenAICompatibleClient(
    model=MODEL_ID,
    api_key=API_KEY,
    base_url=BASE_URL
)

# --- 系统提示词 ---
AGENT_SYSTEM_PROMPT = """你是一个智能旅行助手。你的任务是分析用户的请求，并使用可用工具一步步地解决问题。

# 可用工具:
- `get_weather(city="城市名", days="天数")`: 查询指定城市的天气信息
  - city: 城市名称（必填）
  - days: 查询未来第几天的天气，0=今天，1=明天，2=后天，...，最多6天（选填，默认为0）
  - 示例: get_weather(city="北京", days="0") - 查询北京今天的天气
  - 示例: get_weather(city="上海", days="7") - 查询上海一周后的天气
  
- `get_attraction(city="城市名", weather="天气描述")`: 根据城市和天气搜索推荐的旅游景点
  - city: 城市名称（必填）
  - weather: 天气描述（必填）

# 行动格式:
你的回答必须严格遵循以下格式。首先是你的思考过程，然后是你要执行的具体行动，每次回复只输出一对Thought-Action：
Thought: [这里是你的思考过程和下一步计划]
Action: [这里是你要调用的工具，格式为 function_name(arg_name="arg_value")]

# 任务完成:
当你收集到足够的信息，能够回答用户的最终问题时，你必须在`Action:`字段后使用 `finish(answer="...")` 来输出最终答案。

请开始吧！
"""

# --- 2. 获取用户输入 ---
print("=" * 60)
print("欢迎使用智能旅行助手！")
print("=" * 60)
print("示例: 请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。")
print("-" * 60)
user_prompt = input("请输入你的问题: ").strip()

if not user_prompt:
    print("错误: 输入不能为空！")
    exit(1)

prompt_history = [f"用户请求: {user_prompt}"]
print("\n" + "="*60)
print(f"开始处理您的请求...")
print("="*60 + "\n")

# --- 3. 运行主循环 ---
for i in range(5): # 设置最大循环次数
    print(f"--- 循环 {i+1} ---\n")
    
    # 3.1. 构建Prompt
    full_prompt = "\n".join(prompt_history)
    
    # 3.2. 调用LLM进行思考
    llm_output = llm.generate(full_prompt, system_prompt=AGENT_SYSTEM_PROMPT)
    # 模型可能会输出多余的Thought-Action，需要截断
    match = re.search(r'(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)', llm_output, re.DOTALL)
    if match:
        truncated = match.group(1).strip()
        if truncated != llm_output.strip():
            llm_output = truncated
            print("已截断多余的 Thought-Action 对")
    print(f"模型输出:\n{llm_output}\n")
    prompt_history.append(llm_output)
    
    # 3.3. 解析并执行行动
    action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
    if not action_match:
        print("解析错误:模型输出中未找到 Action。")
        break
    action_str = action_match.group(1).strip()

    if action_str.startswith("finish"):
        final_answer = re.search(r'finish\(answer="(.*)"\)', action_str).group(1)
        print(f"任务完成，最终答案: {final_answer}")
        break
    
    tool_name = re.search(r"(\w+)\(", action_str).group(1)
    args_str = re.search(r"\((.*)\)", action_str).group(1)
    kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))

    if tool_name in available_tools:
        observation = available_tools[tool_name](**kwargs)
    else:
        observation = f"错误:未定义的工具 '{tool_name}'"

    # 3.4. 记录观察结果
    observation_str = f"Observation: {observation}"
    print(f"{observation_str}\n" + "="*40)
    prompt_history.append(observation_str)
