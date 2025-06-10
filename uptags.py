import os
import glob
import json
from pathlib import Path
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import threading # 导入 threading 模块用于线程锁

# 获取 Eagle 资源库路径
while True:
    eagle_library_path = input("请输入Eagle资源库路径: ").strip()
    if os.path.isdir(eagle_library_path):
        break
    else:
        print("路径无效，请重新输入")

images_dir = os.path.join(eagle_library_path, "images")
# 获取所有 JSON 文件路径
json_files = glob.glob(os.path.join(images_dir, "**", "*.json"), recursive=True)

# 获取当前脚本所在目录下的 uptags.csv
base_dir = Path(__file__).resolve().parent
csv_path = base_dir / "csv" / "uptags.csv"

# 加载更新标签对照表，构造映射字典
df = pd.read_csv(csv_path, encoding='utf-8-sig')  # 处理 BOM
df['old_right_tag_cn'] = df['old_right_tag_cn'].str.replace('_', ' ')
df['new_right_tag_cn'] = df['new_right_tag_cn'].str.replace('_', ' ')

tag_map = dict(zip(df['old_right_tag_cn'], df['new_right_tag_cn']))
print(f"共加载 {len(tag_map)} 条标签替换规则")
print("扫描中，等待……")
print(f"准备处理 {len(json_files)} 个 JSON 文件")

# 已更新文件计数器
updated_files_count = 0
# 用于线程安全地访问计数器的锁
count_lock = threading.Lock()

# 多线程处理 JSON 文件
def process_json(file_path):
    global updated_files_count # 声明使用全局变量
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        raw_tags = data.get('tags')
        updated = False
        
        # 确保 'tags' 键存在，否则跳过此文件
        if raw_tags is None:
            return

        if isinstance(raw_tags, str):
            # 分割字符串并去除空字符串，例如 "tag1,,tag2" 会变成 ["tag1", "tag2"]
            tags = [tag.strip() for tag in raw_tags.split(',') if tag.strip()]
            new_tags = []
            for tag in tags:
                new_tag = tag_map.get(tag, tag)
                if new_tag != tag:
                    updated = True
                new_tags.append(new_tag)
            if updated:
                data['tags'] = ','.join(new_tags)

        elif isinstance(raw_tags, list):
            new_tags = []
            for tag in raw_tags:
                # 确保标签是字符串类型，并去除首尾空格
                tag_str = str(tag).strip() if tag is not None else ""
                new_tag = tag_map.get(tag_str, tag_str)
                if new_tag != tag_str:
                    updated = True
                new_tags.append(new_tag)
            if updated:
                data['tags'] = new_tags

        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            # 使用锁确保在多线程环境下安全地更新计数器
            with count_lock:
                updated_files_count += 1
            print(f"已更新: {file_path}")

    except json.JSONDecodeError:
        print(f"处理失败: {file_path} 不是有效的 JSON 文件。")
    except Exception as e:
        print(f"处理失败: {file_path} 错误: {e}")

# 创建线程池并并发处理
with ThreadPoolExecutor(max_workers=8) as executor:
    executor.map(process_json, json_files)

print("---") # 分隔线
print(f"处理完成！共更新了 {updated_files_count} 个文件。") # 输出更新的文件总数