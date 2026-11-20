# -*- coding: utf-8 -*-
"""
rename_messages_key.py

功能：读取 JSONL 文件，将每一行中首次出现的键名 `"messages"`
依次重命名为 `"message1"`, `"message2"`, ...（计数器跨行累计），
结果写入新的文件。

说明：
- 采用纯字符串替换，不解析 JSON，因此可以跳过格式错误的行；
- 每一行只替换第一个匹配项，行内其余 `"messages"` 保持不变；
- 空行原样写出。
"""

import json  # noqa: F401  （原脚本保留的导入，当前逻辑未实际使用）
import os


def process_data(input_file_path, output_file_path):
    """
    读取文件，并将每一行中首次出现的 '"messages"' 键依次重命名为
    '"message1"', '"message2"', ...，然后将结果写入新的文件。

    :param input_file_path: 输入文件的路径
    :param output_file_path: 输出文件的路径
    """
    print(f"开始处理文件: {input_file_path}")

    try:
        with open(input_file_path, 'r', encoding='utf-8') as infile, \
                open(output_file_path, 'w', encoding='utf-8') as outfile:

            message_counter = 1
            for line in infile:
                # 跳过空行：原样写出
                if not line.strip():
                    outfile.write(line)
                    continue

                # 将 "messages" 替换为 "messageX"，只替换第一个匹配项
                # 这样做可以避免解析 JSON，从而忽略格式错误
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
    # 获取当前脚本所在的目录
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # 输入文件名为 '续写.jsonl'，位于脚本相同目录下
    input_file = os.path.join(current_directory, '续写.jsonl')

    # 输出文件名为 'processed_data.jsonl'，位于脚本相同目录下
    output_file = os.path.join(current_directory, 'processed_data.jsonl')
    # --- 配置结束 ---

    process_data(input_file, output_file)


if __name__ == "__main__":
    main()
#（注：内容由AI生成）
