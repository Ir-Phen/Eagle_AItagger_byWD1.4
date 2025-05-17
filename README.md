- [✓] 本体逻辑
- [✓] 集成wd14
- [ ] 小功能完善
    - [ ] 版本更新
    - [ ] 依赖检查
    - [ ] 
- [ ] 集成到eagle插件，通过本地接口将数据传递给py

## tag数据集
汉化部分：[NGA阿巧](https://ngabbs.com/read.php?tid=33869519)

- ./csv/人名tag.xlsx
- ./csv/中文化danbooru-tag对照表-词性对AI用优化版-Editor阿巧.xlsx

**未汉化：5630条**

- ./csv/untranslated_tags.csv

原始数据集：Danbooru2023

- ./csv/selected_tags.csv

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