from pathlib import Path
import json
import pandas
import configparser
from Tagger import on_interrogate
from check_updata import on_check_update
from concurrent.futures import ThreadPoolExecutor

# 从txt传入图像路径列表
def get_img_list_info(img_input_list_path):
    with img_input_list_path.open(mode = 'r', encoding='utf-8') as f:
        img_input_info = [Path(line.strip()).resolve() for line in f if line.strip()]
        img_input_json_path = [path.parent / 'metadata.json' for path in img_input_info]
        return img_input_json_path, img_input_info
    
# 读取图像json
def _process_single_json(img_path, json_path):
    """
    处理单个图像路径和JSON路径，提取所需信息并返回一个字典。
    这个函数将被多线程调用。
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as json_file:
            img_json_data = json.load(json_file)

            img_id = img_json_data.get('id', '')
            img_name = img_json_data.get('name', '')
            annotations = img_json_data.get('annotation', '')
            old_tags = img_json_data.get('tags', '')

            return {
                'id': img_id,
                'name': img_name,
                'annotation': annotations,
                'old_tags': old_tags,
                'new_tags': '',
                'new_tags_cn': '',
                'image_path': str(img_path),
                'json_path': str(json_path)
            }
    except Exception as e:
        print(f"读取JSON文件 {json_path} 时出错: {e}")
        return None # 返回None表示处理失败
    
# 多线程读取图像json并创建一个数据库
def read_img_json_data_threaded(img_input_info, img_input_json_path, config_data, max_workers=8):
    img_info_list = []
    
    # 使用 ThreadPoolExecutor 进行多线程处理
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(_process_single_json, img_input_info, img_input_json_path)
        for result in results:
            if result is not None:
                img_info_list.append(result)
    
    # 将所有结果合并到一个 DataFrame 中
    img_info_dataframe = pandas.DataFrame(img_info_list, columns=[
        'id', 'name', 'annotation', 'old_tags', 'new_tags', 'new_tags_cn', 'image_path', 'json_path'
    ])
    
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
    img_info_dataframe = read_img_json_data_threaded(img_input_info, img_input_json_path, config_data)
    
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
    
    # 处理每个图像并获取新标签，同时写入JSON文件
    print("\n开始处理图像标签...")
    failed_images = []
    for index, row in img_info_dataframe.iterrows():
        image_path = Path(row['image_path'])
        json_path = Path(row['json_path'])
        try:
            # 调用 WD14 处理图像
            tags = tagger.process_single_image(image_path)
            tag_list = list(tags.keys())
            
            # 更新DataFrame中的标签信息
            use_chinese_name = config_data.get('Tag', 'use_chinese_name')
            if use_chinese_name is True:
                img_info_dataframe.at[index, 'new_tags_cn'] = ', '.join(tag_list)
            else:
                img_info_dataframe.at[index, 'new_tags'] = ', '.join(tag_list)
            print(f"已处理：{image_path} -> 发现 {len(tag_list)} 个标签")
        
            # 读取并更新JSON文件
            with open(json_path, 'r', encoding='utf-8') as json_file:
                json_data = json.load(json_file)
            
            # 合并或覆盖标签
            add_write_mode = config_data.getboolean('Json', 'add_write_mode')
            existing_tags = json_data.get('tags', [])

            if add_write_mode is True:
                combined_tags = list(set(existing_tags + tag_list))
            else:
                combined_tags = tag_list
            
            json_data['tags'] = combined_tags
            
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, ensure_ascii=False)
        
            # 记录空标签为失败
            if not tag_list:
                failed_images.append(str(image_path))

        except Exception as e:
            print(f"处理失败：{image_path} | 错误：{str(e)}")
            failed_images.append(str(image_path))

    # 释放内存
    if hasattr(tagger, 'unload') and callable(tagger.unload):
        tagger.unload()
        print("模型已卸载")

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
    # main()
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
    img_info_dataframe = read_img_json_data_threaded(img_input_info, img_input_json_path, config_data)
    
    # # 初始化wd14配置，读取 Model 键的值，转换成绝对路径
    # model_path = config_data.get('Model', 'model_path')
    # tags_path = config_data.get('Model', 'tags_path')
    # if model_path:
    #     model_path = (base_dir / model_path).resolve()
    # if tags_path:
    #     tags_path = (base_dir / tags_path).resolve()
    # config_data.set('Model', 'model_path', str(model_path) if model_path else '')
    # config_data.set('Model', 'tags_path', str(tags_path) if tags_path else '')

    # # 创建wd14实例
    # tagger = on_interrogate(config_data)
    
    # # 处理每个图像并获取新标签，同时写入JSON文件
    # print("\n开始处理图像标签...")
    # failed_images = []
    # for index, row in img_info_dataframe.iterrows():
    #     image_path = Path(row['image_path'])
    #     json_path = Path(row['json_path'])
    #     try:
    #         # 调用 WD14 处理图像
    #         tags = tagger.process_single_image(image_path)
    #         tag_list = list(tags.keys())
            
    #         # 更新DataFrame中的标签信息
    #         use_chinese_name = config_data.get('Tag', 'use_chinese_name')
    #         if use_chinese_name is True:
    #             img_info_dataframe.at[index, 'new_tags_cn'] = ', '.join(tag_list)
    #         else:
    #             img_info_dataframe.at[index, 'new_tags'] = ', '.join(tag_list)
    #         print(f"已处理：{image_path} -> 发现 {len(tag_list)} 个标签")
        
    #         # 读取并更新JSON文件
    #         with open(json_path, 'r', encoding='utf-8') as json_file:
    #             json_data = json.load(json_file)
            
    #         # 合并或覆盖标签
    #         add_write_mode = config_data.getboolean('Json', 'add_write_mode')
    #         existing_tags = json_data.get('tags', [])

    #         if add_write_mode is True:
    #             combined_tags = list(set(existing_tags + tag_list))
    #         else:
    #             combined_tags = tag_list
            
    #         json_data['tags'] = combined_tags
            
    #         with open(json_path, 'w', encoding='utf-8') as json_file:
    #             json.dump(json_data, json_file, ensure_ascii=False)
        
    #         # 记录空标签为失败
    #         if not tag_list:
    #             failed_images.append(str(image_path))

    #     except Exception as e:
    #         print(f"处理失败：{image_path} | 错误：{str(e)}")
    #         failed_images.append(str(image_path))

    # # 释放内存
    # if hasattr(tagger, 'unload') and callable(tagger.unload):
    #     tagger.unload()
    #     print("模型已卸载")

    # success_count = len(img_info_dataframe) - len(failed_images)
    # total_count = len(img_info_dataframe)
    # print(f'标记成功：{success_count}/{total_count}')
    # if failed_images:
    #     print('未成功标记的图片路径：')
    #     for path in failed_images:
    #         print(path)
    # else:
    #     print('所有图像已标注完成')

    # 将 DataFrame 保存为 CSV 文件
    is_creat_image_info_csv = config_data.getboolean('Json', 'is_creat_image_info_csv')
    is_creat_image_info_csv = True # 强制创建CSV文件
    if is_creat_image_info_csv is True:
        processed_csv_path = base_dir / 'image_info.csv'
        img_info_dataframe.to_csv(processed_csv_path, index=False, encoding='utf-8')
        print(f"\n处理后的数据已保存到 {processed_csv_path}")