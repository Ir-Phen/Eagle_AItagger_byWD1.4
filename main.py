from pathlib import Path
import json
import pandas
import configparser
from Tagger import on_interrogate
from check_updata import on_check_update

# 从txt传入图像路径列表
def get_img_list_info(img_input_list_path):
    with img_input_list_path.open(mode = 'r', encoding='utf-8') as f:
        img_input_info = [Path(line.strip()).resolve() for line in f if line.strip()]
        img_input_json_path = [path.parent / 'metadata.json' for path in img_input_info]
        return img_input_json_path, img_input_info
    
# 读取图像json并创建一个数据库
def read_img_json_data(img_input_info, img_input_json_path,config_data):
    # 创建一个空的 DataFrame 并定义列名
    img_info_dataframe = pandas.DataFrame(columns=['id', 'name', 'annotation', 'old_tags', 'new_tags', 'new_tags_cn', 'image_path', 'json_path'])
    
    # 遍历图像路径和对应的 JSON 路径
    for img_path, json_path in zip(img_input_info, img_input_json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as json_file:
                img_json_data = json.load(json_file)
                # 提取所需字段
                img_id = img_json_data.get('id', '')
                img_name = img_json_data.get('name', '')
                annotations = img_json_data.get('annotations', '')
                old_tags = img_json_data.get('tag', '')
                
                # 将数据追加到 DataFrame
                img_info_dataframe = pandas.concat([img_info_dataframe, pandas.DataFrame([{
                    'id': img_id,
                    'name': img_name,
                    'annotation': annotations,
                    'old_tags': old_tags,
                    'new_tags': '',
                    'new_tags_cn': '',
                    'image_path': str(img_path),
                    'json_path': str(json_path)
                }])], ignore_index=True)
        except Exception as e:
            print(f"读取JSON文件 {json_path} 时出错: {e}")
    
    return img_info_dataframe

# 主函数
def main():
    base_dir = Path(__file__).resolve().parent # 获取当前文件的绝对路径

    # 读取config
    global_config_path = base_dir / 'config.ini' # 全局配置文件路径
    config_data = {}
    config_data = configparser.ConfigParser()
    config_data.read(global_config_path, encoding='utf-8')

    # 更新代码版本
    print("检查更新中")
    on_check_update(config_data, global_config_path)

    # 获取待处理图片路径
    img_input_list_path = base_dir / 'image_list.txt' # 图片路径列表文件路径
    img_list_info = get_img_list_info(img_input_list_path)
    print(f"识别到的图片数量：{len(img_list_info[1])}")
    
    # 创建待处理图片的信息数据库
    img_input_json_path, img_input_info = get_img_list_info(img_input_list_path)
    img_info_dataframe = read_img_json_data(img_input_info, img_input_json_path, config_data)
    
    # 初始化wd14配置，读取 Model 键的值，转换成绝对路径
    model_path = config_data.get('Model', 'model_path')
    tags_path = config_data.get('Model', 'tags_path')
    if model_path:
        model_path = (base_dir / model_path).resolve()
    if tags_path:
        tags_path = (base_dir / tags_path).resolve()
    config_data.set('Model', 'model_path', str(model_path) if model_path else '')
    config_data.set('Model', 'tags_path', str(tags_path) if tags_path else '')

    # 创建wd14实例
    
    tagger = on_interrogate(config_data)
    
    # 处理每个图像并获取新标签
    print("\n开始处理图像标签...")
    for index, row in img_info_dataframe.iterrows():
        image_path = Path(row['image_path'])
        try:
            # 调用 WD14 处理图像
            tags = tagger.process_single_image(image_path)
            # 将标签列表转换为字符串
            tag_list = list(tags.keys())
            use_chinese_name = config_data.get('Tag', 'use_chinese_name')
            if use_chinese_name is True:
                img_info_dataframe.at[index, 'new_tags_cn'] = ', '.join(tag_list)
            else:
                img_info_dataframe.at[index, 'new_tags'] = ', '.join(tag_list)
            print(f"已处理：{image_path} -> 发现 {len(tag_list)} 个标签")
        except Exception as e:
            print(f"处理失败：{image_path} | 错误：{str(e)}")
    # 释放内存
    if hasattr(tagger, 'unload') and callable(tagger.unload):
        tagger.unload()
        print("模型已卸载")

    # 根据 use_chinese_name 的值将标签写入对应的 JSON 文件
    for index, row in img_info_dataframe.iterrows():
        json_path = row['json_path']
        if use_chinese_name is True:
            new_tags = row['new_tags_cn'].split(', ') if row['new_tags_cn'] else []
        else:
            new_tags = row['new_tags'].split(', ') if row['new_tags'] else []
        try:
            # 读取现有的JSON文件内容
            with open(json_path, 'r', encoding='utf-8') as json_file:
                json_data = json.load(json_file)
            # 更新JSON文件中的tag键
            json_data['tags'] = new_tags
            # 判断是否覆盖还是追加
            add_write_mode = config_data.get('Json', 'add_write_mode')
            if 'tags' in json_data and isinstance(json_data['tags'], list):
                if add_write_mode is True:
                    json_data['tags'] = list(set(json_data['tags'] + new_tags))
                else:
                    json_data['tags'] = new_tags
            else:
                json_data['tags'] = new_tags
        
            # 将更新后的内容写回JSON文件
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, ensure_ascii=False)
        except Exception as e:
            print(f"更新JSON文件 {json_path} 时出错: {e}")

    # 检查未成功标记的图片
    failed_images = []
    for index, row in img_info_dataframe.iterrows():
        use_chinese_name = config_data.get('Tag', 'use_chinese_name')
        tags_col = 'new_tags_cn' if use_chinese_name is True else 'new_tags'
        if not row[tags_col]:
            failed_images.append(row['image_path'])
    success_count = len(img_info_dataframe) - len(failed_images)
    total_count = len(img_info_dataframe)
    print(f'标记成功：{success_count}/{total_count}')
    if failed_images:
        print('未成功标记的图片路径：')
        for path in failed_images:
            print(path)
    else:
        print('所有图像已标注完成')

    # 将 DataFrame 保存为 CSV 文件
    is_creat_image_info_csv = config_data.getboolean('Json', 'is_creat_image_info_csv')
    if is_creat_image_info_csv is True:
        processed_csv_path = base_dir / 'image_info.csv'
        img_info_dataframe.to_csv(processed_csv_path, index=False, encoding='utf-8')
        print(f"\n处理后的数据已保存到 {processed_csv_path}")


if __name__ == "__main__":
    main()