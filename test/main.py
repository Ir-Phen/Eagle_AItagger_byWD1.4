from pathlib import Path
import json
import pandas

# 定义全局变量
def setup_global_var():
    global base_dir, model_path, TagsDic_path, global_config_path, img_input_list_path, requirements_path, img_info_csv_path
    base_dir = Path(__file__).resolve().parent # 获取当前文件的绝对路径
    model_path = base_dir / 'model' # 模型路径
    TagsDic_path = base_dir / 'csv' / 'Tags-cn(ver1.0,2023).csv' # tag字典路径
    global_config_path = base_dir / 'config.ini' # 全局配置文件路径
    img_input_list_path = base_dir / 'image_list.txt' # 图片路径列表文件路径
    requirements_path = base_dir / 'requirements.txt' # 依赖路径
    img_info_csv_path = base_dir / 'image_info.csv'  # 图像信息字典路径

# 从txt传入图像路径列表
def get_img_list_info(img_input_list_path):
    with img_input_list_path.open(mode = 'r', encoding='utf-8') as f:
        img_input_info = [Path(line.strip()).resolve() for line in f if line.strip()]
        img_input_json_path = [path.parent / 'metadata.json' for path in img_input_info]
        return img_input_json_path, img_input_info
    
# 读取图像json并创建一个数据库
def read_img_json_data(img_input_info, img_input_json_path):
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
    
    # 将 DataFrame 保存为 CSV 文件
    img_info_dataframe.to_csv(img_info_csv_path, index=False, encoding='utf-8')
    print(f"图像信息已保存到 {img_info_csv_path}")
    return img_info_dataframe

# 主函数
def main():
    # 配置全局参数
    setup_global_var()

    # 调用check_package.py检查依赖
    from check_package import check_package
    check_package(requirements_path)


    # 检查更新
    # from check_updata import VersionChecker
    # print("检查更新中")
    # VersionChecker.update_program()

    # 获取待处理图片路径
    img_list_info = get_img_list_info(img_input_list_path)
    print(f"图片路径列表：{img_list_info}")
    
    # 创建待处理图片的信息数据库
    img_input_json_path, img_input_info = get_img_list_info(img_input_list_path)
    img_info_dataframe = read_img_json_data(img_input_info, img_input_json_path)

    # 读取config初始化wd14配置
    from Config import Config
    config = Config(global_config_path)
    config.global_config = config.read_config(global_config_path)
    model_name = config.get_config_data("Model", "model_name")
    print(f'模型名称：{model_name}')
    model_path = config.get_config_data("Model", "model_path")
    print(f'模型路径：{model_path}')
    device = config.get_config_data("Model", "device")
    print(f'推理设备：{device}')
    threshold = float(config.get_config_data("Model", "threshold"))
    print(f'标签置信度：{threshold}')

    # 创建wd14实例
    from wd14_tagger_package.wd14_tagger import ImageTagger
    tagger = ImageTagger(
    model_name=model_name,
    threshold=threshold,
    device=device
    )
    
    # 处理每个图像并获取新标签
    print("\n开始处理图像标签...")
    for index, row in img_info_dataframe.iterrows():
        image_path = Path(row['image_path'])
        try:
            # 调用 WD14 处理图像
            tags = tagger.image_interrogate(image_path)
            # 将标签列表转换为字符串
            tag_list = list(tags.keys())
            img_info_dataframe.at[index, 'new_tags'] = ', '.join(tag_list)
            print(f"已处理：{image_path} -> 发现 {len(tag_list)} 个标签")
        except Exception as e:
            print(f"处理失败：{image_path} | 错误：{str(e)}")
    
     # 读取Tags-cn(ver1.0,2023).csv的数据
    tags_cn_df = pandas.read_csv(TagsDic_path, encoding='utf-8')
    # 创建一个字典用于快速查找标签对应的中文值
    tags_cn_dict = dict(zip(tags_cn_df['name'], tags_cn_df['right_tag_cn']))

    # 遍历img_info_dataframe的id, new_tags, json_path
    for index, row in img_info_dataframe.iterrows():
        new_tags = row['new_tags'].split(', ') if row['new_tags'] else []
        # 将new_tags中的标签转换成Tags-cn(ver1.0,2023).csv中对应的值
        new_tags_cn = [tags_cn_dict.get(tag, tag) for tag in new_tags]
        # 将转换后的new_tags写入img_info_dataframe对应的new_tags_cn
        img_info_dataframe.at[index, 'new_tags_cn'] = ', '.join(new_tags_cn)
        
    # 将new_tags_cn写入对应的JSON文件
    for index, row in img_info_dataframe.iterrows():
        json_path = row['json_path']
        new_tags_cn = row['new_tags_cn'].split(', ') if row['new_tags_cn'] else []
        try:
            # 读取现有的JSON文件内容
            with open(json_path, 'r', encoding='utf-8') as json_file:
                json_data = json.load(json_file)
            
            # 更新JSON文件中的tag键
            json_data['tag'] = new_tags_cn
            
            # 将更新后的内容写回JSON文件
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(json_data, json_file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"更新JSON文件 {json_path} 时出错: {e}")


if __name__ == "__main__":
    # 配置全局参数
    setup_global_var()

    # 获取待处理图片路径
    img_list_info = get_img_list_info(img_input_list_path)
    print(f"图片路径列表：{img_list_info}")
    
    # 创建待处理图片的信息数据库
    img_input_json_path, img_input_info = get_img_list_info(img_input_list_path)
    img_info_dataframe = read_img_json_data(img_input_info, img_input_json_path)
    
    # 读取config初始化wd14配置
    from Config import Config
    config = Config(global_config_path)
    config.global_config = config.read_config(global_config_path)
    model_name = config.get_config_data("Model", "model_name")
    print(f'模型名称：{model_name}')
    model_path = config.get_config_data("Model", "model_path")
    print(f'模型路径：{model_path}')
    device = config.get_config_data("Model", "device")
    print(f'推理设备：{device}')
    threshold = float(config.get_config_data("Model", "threshold"))
    print(f'标签置信度：{threshold}')

    # 创建wd14实例
    from wd14_tagger_package.wd14_tagger import ImageTagger
    tagger = ImageTagger(model_name=model_name, threshold=threshold, device=device)
    
    # # 处理每个图像并获取新标签
    # print("\n开始处理图像标签...")
    # for index, row in img_info_dataframe.iterrows():
    #     image_path = Path(row['image_path'])
    #     try:
    #         # 调用 WD14 处理图像
    #         tags = tagger.image_interrogate(image_path)
    #         # 将标签列表转换为字符串
    #         tag_list = list(tags.keys())
    #         img_info_dataframe.at[index, 'new_tags'] = ', '.join(tag_list)
    #         print(f"已处理：{image_path} -> 发现 {len(tag_list)} 个标签")
    #     except Exception as e:
    #         print(f"处理失败：{image_path} | 错误：{str(e)}")