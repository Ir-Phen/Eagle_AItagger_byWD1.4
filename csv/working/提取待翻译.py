import pandas as pd
import re

# 读取CSV文件
df = pd.read_csv(r'E:\GitHub\Eagle_AItagger_byWD1.4\csv\working\untranslated_tags.csv.csv')  # 替换为实际文件名

# 定义正则表达式模式
pattern = r'_\((.*?)\)$'

# 提取匹配的行并添加game列
matched_rows = []
for _, row in df.iterrows():
    match = re.search(pattern, row['name'])
    if match:
        # 复制当前行
        new_row = row.copy()
        # 添加game列
        new_row['game'] = match.group(1)
        matched_rows.append(new_row)

# 创建包含匹配项的新DataFrame
result_df = pd.DataFrame(matched_rows)

# 按照game列的值排序（升序）
result_df = result_df.sort_values(by='game')

# 保存结果到新CSV文件
result_df.to_csv(r'E:\GitHub\Eagle_AItagger_byWD1.4\csv\working\toTranslation.csv', index=False)

print(f"处理完成！匹配到 {len(result_df)} 条记录")