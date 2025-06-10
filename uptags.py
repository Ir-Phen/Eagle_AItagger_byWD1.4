import os
import glob
import json
from pathlib import Path
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import threading

# 获取 Eagle 资源库路径
while True:
    eagle_library_path = input("请输入Eagle资源库路径: ").strip()
    if os.path.isdir(eagle_library_path):
        break
    else:
        print("路径无效，请重新输入")

images_dir = os.path.join(eagle_library_path, "images")
json_files = glob.glob(os.path.join(images_dir, "**", "*.json"), recursive=True)

# 获取当前脚本所在目录下的 uptags.csv
base_dir = Path(__file__).resolve().parent
csv_path = base_dir / "csv" / "uptags.csv"

# 加载标签映射
df = pd.read_csv(csv_path, encoding='utf-8-sig')
df['old_right_tag_cn'] = df['old_right_tag_cn'].str.replace('_', ' ')
df['new_right_tag_cn'] = df['new_right_tag_cn'].str.replace('_', ' ')
tag_map = dict(zip(df['old_right_tag_cn'], df['new_right_tag_cn']))

print(f"共加载 {len(tag_map)} 条标签替换规则")
print("扫描中，等待……")
print(f"准备处理 {len(json_files)} 个 JSON 文件")

updated_files_count = 0
count_lock = threading.Lock()

def process_json(file_path):
    global updated_files_count
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        raw_tags = data.get('tags')
        updated = False
        new_tags = None

        if isinstance(raw_tags, str):
            tags = [tag.strip() for tag in raw_tags.split(',') if tag.strip()]
            new_tags = [tag_map.get(tag, tag) for tag in tags]
            if new_tags != tags:
                updated = True
                data['tags'] = ','.join(new_tags)

        elif isinstance(raw_tags, list):
            tags = [str(tag).strip() if tag is not None else "" for tag in raw_tags]
            new_tags = [tag_map.get(tag, tag) for tag in tags]
            if new_tags != tags:
                updated = True
                data['tags'] = new_tags

        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            with count_lock:
                updated_files_count += 1
            print(f"已更新: {file_path}")

    except json.JSONDecodeError:
        print(f"处理失败: {file_path} 不是有效的 JSON 文件。")
    except Exception as e:
        print(f"处理失败: {file_path} 错误: {e}")

with ThreadPoolExecutor(max_workers=8) as executor:
    executor.map(process_json, json_files)

print("---")
print(f"处理完成！共更新了 {updated_files_count} 个文件。")
