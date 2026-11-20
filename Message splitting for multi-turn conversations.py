import json
import os

def process_data(input_file_path, output_file_path):
    """
    读取文件，并将每一行中首次出现的 '"messages"' 键依次重命名为 '"message1"', '"message2"', ...
    然后将结果写入新的文件。

    :param input_file_path: 输入文件的路径.
    :param output_file_path: 输出文件的路径.
    """
    print(f"开始处理文件: {input_file_path}")
    
    try:
        with open(input_file_path, 'r', encoding='utf-8') as infile, \
             open(output_file_path, 'w', encoding='utf-8') as outfile:
            
            message_counter = 1
            for line in infile:
                # 跳过空行
                if not line.strip():
                    outfile.write(line)
                    continue
                
                # 将 "messages" 替换为 "messageX"，只替换第一个匹配项
                # 这样做可以避免解析JSON，从而忽略格式错误
                target_key = '"messages"'
                if target_key in line:
                    new_key = f'"message{message_counter}"'
                    modified_line = line.replace(target_key, new_key, 1)
                    outfile.write(modified_line)
                    message_counter += 1
                else:
                    # 如果行内没有找到 "messages"，则直接写入原文
                    outfile.write(line)

        print(f"处理完成！结果已保存到: {output_file_path}")

    except FileNotFoundError:
        print(f"错误: 输入文件未找到于 '{input_file_path}'")
    except Exception as e:
        print(f"发生未知错误: {e}")

def main():
    """主函数，用于配置和启动处理流程"""
    # --- 配置区域 ---
    # 请在这里设置您的输入和输出文件路径
    # 获取当前脚本所在的目录
    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    # 假设输入文件名为 '续写.jsonl'，位于脚本相同目录下
    input_file = os.path.join(current_directory, '续写.jsonl')
    
    # 设置输出文件名为 'processed_data.jsonl'，位于脚本相同目录下
    output_file = os.path.join(current_directory, 'processed_data.jsonl')
    # --- 配置结束 ---
    
    process_data(input_file, output_file)

if __name__ == "__main__":
    main()