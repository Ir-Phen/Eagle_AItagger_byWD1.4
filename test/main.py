from pathlib import Path
import json
import os
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

# 获取模型列表
def build_model_list():
    model_list = []
    # 遍历model_path下的所有文件查找onnx
    for file in model_path.glob('*.onnx'):
        model_name = file.stem
        onnx_model_path = model_path / f"{model_name}.onnx"
        model_list.append([model_name, onnx_model_path])
    print(f'模型列表：{model_list}')
    return model_list

# 获取硬件参数

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

# 读取config初始化wd14配置

# 将img_list_info传入wd14
class WD14Tagger:
    
    def a():
        tag_wd14_export = []
        wd14_export = [id,r'new_tag']
        return wd14_export

# 将tag写入csv
def new_tag_into_csv(wd14_export):
    return
# 翻译tag
# 将csv的值迁移到json，为anno添加已AI生成标签（配置可选）
# 清除imgcsv的数据（配置可选）

# 主函数
def main():
    # 配置全局参数
    setup_global_var()

    # 调用check_package.py检查依赖
    from check_package import check_package
    package_checker = check_package() # 创建check_package实例
    fastest_source = package_checker.test_source_speed(package_checker.sources) # 测试源速度
    package_checker.set_pip_source(fastest_source) # 设置pip源
    requirements = package_checker.read_requirements(package_checker.requirements_path) # 读取requirements.txt文件
    package_checker.check_and_install_dependencies(requirements) # 检查并安装依赖项

    # 检查更新
    from updata import VersionChecker
    VersionChecker.update_program()

    # 运行硬件检查,自动配置config
        # 如果config中硬件信息为空,运行check_hardware

    # 生成模型列表 over
    build_model_list()
    os.environ["MODEL_LIST"] = json.dumps(build_model_list()) # 将模型列表转换为JSON字符串并存储在环境变量中
    
    # 获取待处理图片路径
    img_list_info = get_img_list_info(img_input_list_path)
    print(f"图片路径列表：{img_list_info}")
    
    # 创建待处理图片的信息数据库
    img_input_json_path, img_input_info = get_img_list_info(img_input_list_path)
    read_img_json_data(img_input_info, img_input_json_path) 

if __name__ == "__main__":
    # main()

    # 配置全局变量
    setup_global_var()

    # 使用img_input_list_path，打印返回的列表
    img_input_json_path, img_input_info = get_img_list_info(img_input_list_path)
    img_info_dataframe = read_img_json_data(img_input_info, img_input_json_path)  # 新增调用
    
    '''
    WD14处理模块
    '''
    # 接受imgcsv的数据
    id_image_path_list = img_info_dataframe[['id', 'image_path']].values.tolist()
    print(f"调试{id_image_path_list}")


'''
    # 将图片路径加载为PIL对象
    from img2tag import WD14Tagger
    image_objects = WD14Tagger.image_PIL(id_image_path_list)

    # 使用WD14Tagger处理图像对象并生成新标签
    new_tag_fromWD14 = []
    for image_path, image in image_objects:
        try:
            # 假设WD14Tagger有一个方法process_image返回新标签
            new_tags = WD14Tagger.process_image(image)
            new_tag_fromWD14.append((image_path, new_tags))
        except Exception as e:
            print(f"处理图像 {image_path} 时出错: {e}")

    # 将新标签写入 DataFrame
    for image_path, new_tags in new_tag_fromWD14:
        # 找到对应的行并更新 new_tags 列
        img_info_dataframe.loc[img_info_dataframe['image_path'] == image_path, 'new_tags'] = ', '.join(new_tags)

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
            '''