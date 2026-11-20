import os
import json
import concurrent.futures
from volcenginesdkarkruntime import Ark

# 1. API配置
API_KEY = os.environ.get("VOLC_API_KEY", "")
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
ENDPOINT_ID = ""
# 注意：根据SDK的使用方式，模型ID通常就是Endpoint ID
MODEL = ENDPOINT_ID

# 2. 并发配置
MAX_WORKERS = 25  # 设置并发线程数

# 3. 文件路径配置
INPUT_FILE = 'processed_回复.jsonl'
OUTPUT_FILE = 'logical_issues_found.jsonl'

# 4. Prompt 定义
SYSTEM_PROMPT = """
我会向你提供一段对话数据和它的编号。编号在对话数据之前。如message1、message2、message3...以此类推。

请你严格按照以下要求处理每段对话：
1. **核心判断规则**：重点审查每一条message中`role`字段值为`assistant`的回复内容，判断其是否存在特定逻辑问题。此处的“逻辑问题”特指两种情况：① 该`assistant`回复与前文（即该条`assistant`消息之前的所有`user`消息、及更早的对话上下文）完全无关联；② 该`assistant`回复表达模糊、语义不明，无法与前文形成连贯对话。只要满足任一情况，即判定为存在逻辑问题。
2. **输出格式**：如果判定某条`assistant`回复存在上述逻辑问题，需将该条数据按以下格式生成一个结果。如果有多条回复存在问题，请为每一条都生成一个独立的结果，并用换行符分隔。如果所有`assistant`回复都没有逻辑问题，则不输出任何内容。

**结果输出格式**：
{"role": "assistant", "content": "[原assistant回复内容]", "tag": "逻辑问题", "number": "你收到的对话编号"}

## 输出示例
{"role": "assistant", "content": "起高高了", "tag": "逻辑问题", "number": "message14"}
"""

def call_llm(session_content: str, session_number: int):
    """
    调用豆包大模型API来分析单条对话数据。

    :param session_content: 包含对话内容的单行文本。
    :param session_number: 对话的编号。
    :return: API返回的分析结果，如果无逻辑问题则为空字符串。
    """
    try:
        client = Ark(base_url=BASE_URL, api_key=API_KEY)
        dialogue_id = f"message{session_number}"
        
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{dialogue_id}\n{session_content}"}
            ]
        )
        
        result = completion.choices[0].message.content
        # 打印API的原始输出，方便调试
        print(f"API response for {dialogue_id}: {result}")
        return result
    except Exception as e:
        print(f"Error processing message {session_number}: {e}")
        return ""

def process_line_wrapper(line_info):
    """
    用于并发处理的包装函数。
    """
    line_number, line_content = line_info
    return call_llm(line_content, line_number)

def main():
    """
    主函数，读取文件、并发处理并写入结果。
    """
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as infile, \
             open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile, \
             concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            
            lines_with_numbers = [(i, line) for i, line in enumerate(infile, 1)]
            
            future_to_line = {executor.submit(process_line_wrapper, line_info): line_info for line_info in lines_with_numbers}
            
            for future in concurrent.futures.as_completed(future_to_line):
                line_info = future_to_line[future]
                try:
                    result = future.result()
                    if result and result.strip():
                        # API可能返回多个由换行符分隔的JSON对象
                        results = result.strip().split('\n')
                        for res_line in results:
                            if res_line.strip():
                                # 验证是否是合法的JSON，避免写入错误格式
                                try:
                                    json.loads(res_line)
                                    outfile.write(res_line + '\n')
                                except json.JSONDecodeError:
                                    print(f"Warning: API returned non-JSON string for line {line_info[0]}: {res_line}")
                except Exception as exc:
                    print(f'Line {line_info[0]} generated an exception: {exc}')

        print(f"Processing complete. Results saved to {OUTPUT_FILE}")

    except FileNotFoundError:
        print(f"Error: Input file '{INPUT_FILE}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()