import os
import glob
import json
from pathlib import Path
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

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
print(f"准备处理 {len(json_files)} 个 JSON 文件")

# 多线程处理 JSON 文件
def process_json(file_path):
    print(f"正在处理: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        raw_tags = data.get('tags')
        updated = False
        if isinstance(raw_tags, str):
            tags = [tag.strip() for tag in raw_tags.split(',')]
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
                new_tag = tag_map.get(tag, tag)
                if new_tag != tag:
                    updated = True
                new_tags.append(new_tag)
            if updated:
                data['tags'] = new_tags

        if updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"已更新: {file_path}")

    except Exception as e:
        print(f"处理失败: {file_path} 错误: {e}")

# 创建线程池并并发处理
with ThreadPoolExecutor(max_workers=8) as executor:
    executor.map(process_json, json_files)

print("处理完成")
