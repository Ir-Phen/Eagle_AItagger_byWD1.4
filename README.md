- [✓] 本体逻辑

- [✓] 集成wd14

- [ ] 小功能完善

- [ ] 集成到eagle插件，通过本地接口将数据传递给py

## config配置

[Version] --> 显然是版本信息，**别动这个**👊😡🫵

version：版本号

update_notes：版本信息

</br>

[Model] --> 模型信息

两个路径都只接受相对路径，别改成绝对路径。

model_path：推理使用的模型，详见支持的模型列表

tags_path：推理使用的字典

</br>

[Tag] --> 标签处理方式

**threshold**：过滤推理标签的置信度阈值，**范围\[0-1\]，默认0.5**

replace_underscore：是否将标签名中的下划线替换为空格

underscore_excludes：不替换下划线的标签

escape_tags：是否转义特殊字符（如括号和反斜杠）

**use_chinese_name**：是否使用标签的中文名称

additional_tags：强制添加的标签

exclude_tags：强制排除的标签，默认排除1girl类

sort_alphabetically：是否按字母顺序排序（默认按置信度降序）

</br>

[Json] --> 写入Eagle的配置

add_write_mode：标签的写入模式，默认True为追加写入，Fasle为覆盖写入

## 支持的模型列表

**仅支持wd类的模型，db类的不支持**

convnext-v3

convnextv2-v2

swinv2-v2

swinv2-v3：推荐，默认配置。

vit-v2

vit-v3

vit-large-tagger-v3

wd14-moat-v2

eva02-large-tagger-v3

## tag数据集

汉化部分：[NGA阿巧](https://ngabbs.com/read.php?tid=33869519)

    ./csv/人名tag.xlsx

    ./csv/中文化danbooru-tag对照表-词性对AI用优化版-Editor阿巧.xlsx

**未汉化：5630条**

    ./csv/untranslated_tags.csv

原始数据集：Danbooru2023

    ./csv/selected_tags.csv

## Eagel集成方案

**JavaScript**

```
eagle.onSelectionChanged(async (items) => {
    const selectedData = items.map(item => ({
        path: item.path,
        metadata: item.metadata
    }));
    // 将数据写入临时文件（如JSON）
    const fs = require('fs');
    fs.writeFileSync('/tmp/eagle_selected.json', JSON.stringify(selectedData));
});
```
**Python**

```
def get_eagle_selection():
    try:
        with open('/tmp/eagle_selected.json', 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return []
while True:
    selected_items = get_eagle_selection()
    if selected_items:
        print("当前选中项：", selected_items)
        break
    time.sleep(1)
```