import csv

# 文件路径
role_csv = r"E:\GitHub\Eagle_AItagger_byWD1.4\csv\working\东方角色.csv"
tags_csv = r"E:\GitHub\Eagle_AItagger_byWD1.4\csv\working\Tags-cn(ver2.0,2023).csv"

# 读取东方角色的en_name
with open(role_csv, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    role_en_names = set(row["en_name"].strip() for row in reader if row["en_name"].strip())

# 读取Tags-cn的name
with open(tags_csv, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    tags_names = set(row["name"].strip() for row in reader if row["name"].strip())

# 差异
only_in_roles = role_en_names - tags_names
only_in_tags = tags_names - role_en_names

print("只在东方角色en_name中的项：")
for name in sorted(only_in_roles):
    print(name)