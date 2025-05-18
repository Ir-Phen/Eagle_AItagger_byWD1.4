## 使用说明

1. 下载模型 (详见支持的模型列表) 到 *./model* ，将文件名改为模型的名称
    - 示例：./model/swinv2-v3

2. 从 *requirements.txt* 安装依赖，或运行 *check_package*

3. 从 Eagle 选择需要标注的图片，右键在菜单选择 **复制文件路径** (快捷键 **Ctrl+Alt+C** )

4. 将文件路径粘贴到 *iamge_list.txt* 文件内

    - 示例：
    
        ```
        E:\动画与设计资源库.library\images\MAQGISQ1ELX97.info\124956717_p0.png
        E:\动画与设计资源库.library\images\MAQGISQ1N6OHU.info\124719914_p0.png
        E:\动画与设计资源库.library\images\MAQGISQ1Z8PST.info\124086849_p0.png
        ```
5. 配置 *config.ini* 内模型键的参数

    - 示例：model_path = ./model/swinv2-v3.oonx

6. 如有需要，修改 *config.ini* 的其他参数配置

7. 运行 main.py


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

is_creat_image_info_csv：是否创建一个image_info.csv文件，保存的是处理图片的标签数据与索引

add_write_mode：标签的写入模式，默认True为追加写入，Fasle为覆盖写入

## 支持的模型列表

**仅支持wd类的模型，db类的不支持**

[convnext-v3](https://huggingface.co/SmilingWolf/wd-convnext-tagger-v3/tree/main) | [convnextv2-v2](https://huggingface.co/SmilingWolf/wd-v1-4-convnextv2-tagger-v2/tree/main) | [convnext-v2](https://huggingface.co/SmilingWolf/wd-v1-4-convnext-tagger-v2/tree/main) | [convnext](https://huggingface.co/SmilingWolf/wd-v1-4-convnext-tagger/tree/main)

[swinv2-v2](https://huggingface.co/SmilingWolf/wd-v1-4-swinv2-tagger-v2/tree/main) | [swinv2-v3](https://huggingface.co/SmilingWolf/wd-swinv2-tagger-v3/tree/main)

[vit-large-v3](https://huggingface.co/SmilingWolf/wd-vit-large-tagger-v3/tree/main) | [vit-v3](https://huggingface.co/SmilingWolf/wd-vit-tagger-v3/tree/main) | [vit-v2](https://huggingface.co/SmilingWolf/wd-v1-4-vit-tagger-v2/tree/main) | [vit](https://huggingface.co/SmilingWolf/wd-v1-4-vit-tagger/tree/main)

[moat-v2](https://huggingface.co/SmilingWolf/wd-v1-4-moat-tagger-v2/tree/main)

[eva02-large-v3](https://huggingface.co/SmilingWolf/wd-eva02-large-tagger-v3/tree/main)


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