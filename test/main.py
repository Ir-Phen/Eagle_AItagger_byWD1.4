from configparser import ConfigParser
import json
import os
from pathlib import Path
import csv

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

# 配置文件类
class Config:
    # 读取配置文件
    @staticmethod
    def read_config(global_config_path):
        global_config = ConfigParser()
        global_config.read(global_config_path, encoding="utf-8")
        return global_config

    # 从配置文件中获取参数
    @staticmethod
    def get_config_param(global_config, section, option, default=None):
        try:
            if global_config.has_option(section, option):
                return global_config.get(section, option)
            else:
                return default
        except Exception as e:
            print(f"读取配置参数 [{section}] {option} 时出错: {e}")
            return default

    # 配置config.ini的参数
    @staticmethod
    def config_ini(global_config):
        global_config = Config.read_config(global_config_path)

        # 从get_config_param函数获取model类的参数model_name
        model_name = Config.get_config_param(global_config, "Model", "model_name", "None")
        # 从get_config_param函数获取model类的参数model_path
        model_path = Config.get_config_param(global_config, "Model", "model_path", "None")
        print(f"模型名称: {model_name}")
        print(f"模型路径: {model_path}")
        # 其他参数可以类似获取

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
        with img_info_csv_path.open(mode='w', encoding='utf-8', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            # 写入CSV文件的表头
            csv_writer.writerow(['id', 'name', 'annotation', 'old_tags', 'new_tags', 'new_tags_cn', 'image_path', 'json_path'])
        for img_path, json_path in zip(img_input_info, img_input_json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as json_file:
                    img_json_data = json.load(json_file)
                    # 提取所需字段
                    img_id = img_json_data.get('id', '')
                    img_name = img_json_data.get('name', '')
                    annotations = img_json_data.get('annotations', '')
                    old_tags = img_json_data.get('tag', '')
                # 写入CSV文件
                with img_info_csv_path.open(mode='a', encoding='utf-8', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow([img_id, img_name, annotations, old_tags, '', '', img_path, json_path])
            except Exception as e:
                print(f"读取JSON文件 {json_path} 时出错: {e}")
        print(f"图像信息已保存到 {img_info_csv_path}")

# 读取config初始化wd14配置

# 将img_list_info传入wd14
    # 更改selected.csv是否能直接生成中文tag？
class WD14Tagger:
    # 接受imgcsv的数据
    def a():
        return
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
    
    # 读取配置文件 over
    global_app_config = Config.read_config(global_config_path)
    print(f'全局配置文件：{global_app_config}')
    
    img_list_info = get_img_list_info(img_input_list_path)
    print(f"图片路径列表：{img_list_info}")
    
    # 新增调用
    img_input_json_path, img_input_info = get_img_list_info(img_input_list_path)
    read_img_json_data(img_input_info, img_input_json_path) 

    
    # interrogators.py：预定义可用模型实例。
    # image.py：未直接使用（代码中未调用resize_image）。
    # dbimutils.py：提供图像预处理工具函数。
    # interrogator.py：实现模型加载、推理和后处理逻辑。
    # 将依次读取图像路径，转化为PIL图像对象
    '''
    ### **关键变量**
1. **`image: Image.Image`**
    - 输入图像对象（PLPIL格式），通过`Image.open`加载。
2. **`model_name`**
    - 模型名称（如`wd14-convnextv2.v1`），决定使用的预训练模型。
3. **`threshold`**
    - 置信度阈值（默认`0.35`），过滤低置信度标签。
4. **`device`**
    - 设备类型（`"cpu"`或`"cuda"`），控制模型推理的计算设备。
5. **`interrogator`**
    - 模型实例（如`WaifuDiffusionInterrogator`或`MLDanbooruInterrogator`），负责推理和标签生成。
6. **`tags`**
    - 模型输出的原始标签置信度字典（`Dict[str, float]`），包含所有标签及其置信度。
7. **`confidents`**
    - 模型推理输出的置信度数组（`numpy.ndarray`），包含所有标签的原始预测值。
### **关键函数**
1. **`ImageTagger.img_interrogate()`**
    - 入口函数：接收图像路径，调用模型推理和后处理。
    - 流程：
        - `Image.open`加载图像 → `interrogator.interrogate()`推理 → `postprocess_tags()`后处理。
2. **`Interrogator.interrogate()`**
    - 模型推理核心逻辑（分两类实现）：
        - **`WaifuDiffusionInterrogator`**：
            - 使用`dbimutils.make_square`和`dbimutils.smart_resize`调整图像尺寸。
            - 调用ONNX模型推理，输出`ratings`和`tags`。
        - **`MLDanbooruInterrogator`**：
            - 使用`dbimutils.fill_transparent`和`dbimutils.resize`预处理图像。
            - 调用ONNX模型推理，输出`tags`。
3. **`dbimutils`工具函数**
    - `fill_transparent()`：填充透明背景为白色。
    - `make_square()`：将图像填充为正方形。
    - `smart_resize()`：按目标尺寸缩放图像。
    - `smart_24bit()`：将图像统一为24位BGR格式。
4. **`Interrogator.postprocess_tags()`**
    - 标签后处理逻辑：
        - 按阈值过滤低置信度标签。
        - 按字母顺序或置信度排序。
        - 替换下划线、添加置信度权重、转义特殊字符等。
5. **模型加载函数**
    - `WaifuDiffusionInterrogator.load()`：从HuggingFace Hub下载并加载ONNX模型。
    - `MLDanbooruInterrogator.load()`：加载JSON标签文件及模型。
    '''
        # image.py 的 Image.open()方法,将路径加载为PIL对象
    # 调用 进行图像预处理
        # dbimage.py 调整
    # 调用 进行图像标注
        # interrogators.py的interrogate()方法调用onnx模型
    # tag后处理
        # postprocess_tags()方法
    # 输出tag结果
        # dict[str, float]类型 
    # 生成csv文件

    # 翻译tag

    # tag迁移到metadata.json




if __name__ == "__main__":
    # main()
    # 配置全局变量
    setup_global_var()
    # 使用img_input_list_path，打印返回的列表
    img_input_json_path, img_input_info = get_img_list_info(img_input_list_path)
    read_img_json_data(img_input_info, img_input_json_path)  # 新增调用
    