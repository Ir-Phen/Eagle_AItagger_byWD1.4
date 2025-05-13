from configparser import ConfigParser
import json
import os
from pathlib import Path
import sys

# 定义全局变量
def setup_global_var():
    global base_dir, model_path, wd14_path, Transfer_path, global_config_path, image_input_list_path
    base_dir = Path(__file__).resolve().parent
    model_path = base_dir / 'model'
    wd14_path = base_dir / 'wd14_tagger_api'
    Transfer_path = base_dir / 'csv' / 'Tags-cn(ver1.0,2023).csv'
    global_config_path = base_dir / 'config.ini'
    sys.path.append(str(wd14_path))  # 添加wd1.4路径
    image_input_list_path = base_dir / 'image_list.txt'

# 更新程序
def update_program():
    import updata
    updata.update_program()

# 读取配置文件
def read_config(global_config_path):
    global_config = ConfigParser()
    global_config.read(global_config_path, encoding="utf-8")
    return global_config

# 检查model_path下的sw_jax_cv_config.json文件
# 读取model_name的值，获取同级onxx模型文件
# 建构列表[model_name, onnx_model_path]
def build_model_list():
    model_list = []
    for subdir in os.listdir(model_path):
        subdir_full = os.path.join(model_path, subdir)
        if os.path.isdir(subdir_full):
            model_config_path = os.path.join(subdir_full, 'sw_jax_cv_config.json')
            # 检查配置文件是否存在
            if os.path.isfile(model_config_path):
                try:
                    # 读取JSON配置文件
                    with open(model_config_path, 'r') as f:
                        model_config = json.load(f)
                        model_name = model_config.get('model_name')
                        if model_name:
                            # 查找所有ONNX文件
                            onnx_files = [
                                f for f in os.listdir(subdir_full)
                                if f.lower().endswith('.onnx') 
                                and os.path.isfile(os.path.join(subdir_full, f))
                            ]
                            # 为每个ONNX文件添加条目
                            for onnx_file in onnx_files:
                                onnx_path = os.path.join(subdir_full, onnx_file)
                                model_list.append([model_name, onnx_path])
                except Exception as e:
                    print(f"处理配置文件 {model_config_path} 时出错: {e}")
    print(f'模型列表：{model_list}')
    return model_list

# def从"依赖检查.py"检测运行环境

    # else# 配置wd1.4运行环境 

# def获取硬件参数
    # 检查gpu
        # 检查显存
        # 检查型号
    # 检查cpu
        # 检查核心数、线程数
    # 检查内存容量

# def配置服务器参数
    # 是否汉化tag
# 从txt传入生产路径列表
# 解析路径
    #图片类
    # 传入wd1.4
    # 生成标注提示文件
    # 配置多线程池，从完成列表生产新图片路径
    # 从新图片路径打开txt与metajson
    # 对比tag，差异度新增
    # 删除临时文件

# 主函数
def main():
    # 配置全局参数
    setup_global_var()
    '''
    # 检查更新
    update_program()

    # 运行依赖检查
    # 运行硬件检查

    # 生成模型列表 over
    build_model_list()
    os.environ["MODEL_LIST"] = json.dumps(build_model_list()) # 将模型列表转换为JSON字符串并存储在环境变量中
    
    # 读取配置文件 over
    global_app_config = read_config(global_config_path)
    print(f'全局配置文件：{global_app_config}')
    
    # 启动wd1.4服务
    # 获取服务器配置
    from start_wd14 import start_server
    start_server(global_app_config) 
    print(f"正在启动服务器，请稍候...")
    '''
    # 获取图片路径列表
    with image_input_list_path.open(mode = 'r', encoding='utf-8') as f:
        img_input_list = f.read().splitlines()
        img_input_json_path = [os.path.join(os.path.dirname(path), 'metadata.json') for path in img_input_list]

    # 传入参数到wd1.4
    from wd14_tagger_api import send_to_server  # 假设wd1.4服务器有一个send_to_server函数

    for img_path in img_input_list:
        try:
            # 将图片路径传入wd1.4服务器
            response = send_to_server(img_path)
            print(f"图片 {img_path} 已成功传入服务器，响应: {response}")
        except Exception as e:
            print(f"传入图片 {img_path} 时出错: {e}")
    # 加载img2tag.py

if __name__ == "__main__":
    main()