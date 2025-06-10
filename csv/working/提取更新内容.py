import pandas as pd

# 文件路径（请根据实际路径修改）
old_file = r'E:\GitHub\Eagle_AItagger_byWD1.4\csv\Tags-cn(ver1.0,2023).csv'
new_file = r'E:\GitHub\Eagle_AItagger_byWD1.4\csv\working\Tags-cn(ver2.0,2023).csv'
output_file = r'E:\GitHub\Eagle_AItagger_byWD1.4\csv\uptags.csv'

# 读取 CSV 文件（自动处理 BOM）
old_df = pd.read_csv(old_file, encoding='utf-8')
new_df = pd.read_csv(new_file, encoding='utf-8')

# 以 tag_id 为键合并两个 DataFrame
merged_df = pd.merge(
    old_df, new_df,
    on='tag_id',
    suffixes=('_old', '_new')
)

# 筛选 right_tag_cn 发生变化的行
changed = merged_df[merged_df['right_tag_cn_old'] != merged_df['right_tag_cn_new']]

# 选择并重命名需要的列
result = changed[[
    'tag_id',
    'name_new',
    'category_new',
    'count_new',
    'right_tag_cn_old',
    'right_tag_cn_new'
]].rename(columns={
    'name_new': 'name',
    'category_new': 'category',
    'count_new': 'count',
    'right_tag_cn_old': 'old_right_tag_cn',
    'right_tag_cn_new': 'new_right_tag_cn'
})

# 保存结果
result.to_csv(output_file, index=False, encoding='utf-8')

print(f'共发现 {len(result)} 条变更，已保存至 {output_file}')