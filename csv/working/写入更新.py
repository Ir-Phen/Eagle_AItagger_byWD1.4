import pandas as pd
import os

# 定义文件路径
file1 = r"E:\GitHub\Eagle_AItagger_byWD1.4\csv\working\翻译中.csv"
file2 = r"E:\GitHub\Eagle_AItagger_byWD1.4\csv\working\Tags-cn(ver2.0,2023).csv"
file3 = r"E:\GitHub\Eagle_AItagger_byWD1.4\csv\working\untranslated_tags.csv.csv"

# 读取CSV文件
df1 = pd.read_csv(file1)    # 仅包含 tag_id 和 right_tag_cn
df2 = pd.read_csv(file2)    # Tags-cn
df3 = pd.read_csv(file3)    # untranslated_tags

# 任务1：更新 Tags-cn 的 right_tag_cn 列（只用 tag_id 作为键）
update_dict = df1.set_index('tag_id')['right_tag_cn'].to_dict()

# 更新 df2 的 right_tag_cn（如果 tag_id 匹配，就替换）
df2['right_tag_cn'] = df2.apply(
    lambda row: update_dict.get(row['tag_id'], row['right_tag_cn']),
    axis=1
)

# 保存更新后的 Tags-cn 文件（覆盖原文件）
df2.to_csv(file2, index=False)

# 任务2：删除 untranslated_tags 中 tag_id 匹配的行（不再使用 name）
matched_tag_ids = set(df1['tag_id'])

# 过滤：保留 tag_id 不在 matched_tag_ids 中的行
df3_filtered = df3[~df3['tag_id'].isin(matched_tag_ids)].copy()

# 保存处理后的 untranslated_tags 文件（覆盖原文件）
df3_filtered.to_csv(file3, index=False)

# 输出结果
print("操作完成！")
print(f"更新 Tags-cn 记录数: {len(df2)}")
print(f"清理后 untranslated_tags 记录数: {len(df3_filtered)} (原始: {len(df3)})")
