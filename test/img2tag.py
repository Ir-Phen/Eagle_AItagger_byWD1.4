

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
        
    # 调用 进行图像预处理
        # dbimage.py 调整
    # 调用 进行图像标注
        # interrogators.py的interrogate()方法调用onnx模型
    # tag后处理
        # postprocess_tags()方法
    # 输出tag结果
        # dict[str, float]类型 


from PIL import Image

class WD14Tagger:
    def __init__(self, img_info_dataframe, tags_cn_path, model_dir, base_dir):
       self

    def ToLoad_model(model_dir):



        return
    # 将图像路径加载为PIL对象
    def image_PIL(id_image_path_list):
        image_objects = []
        for id, image_path in id_image_path_list:
            try:
                image = Image.open(image_path)
                image_objects.append((id,image_path, image))
                return image_objects
            except Exception as e:
                print(f"加载图像 {image_path} 时出错: {e}")
    
    @staticmethod
    def process_image():

        return
    
if __name__ == "__main__":
    id_image_path_list = [
        ['MA5LGO1IXFMWF', 'E:\\动画与设计资源库.library\\images\\MA5LGO1IXFMWF.info\\よるうよ_1913704956680720384.jpg'], 
        ['MA5LGWK64UFLI', 'E:\\动画与设计资源库.library\\images\\MA5LGWK64UFLI.info\\ぶんち_1917486659647700992.jpg'], 
        ['MA5LHO7JJ6X6T', 'E:\\动画与设计资源库.library\\images\\MA5LHO7JJ6X6T.info\\アシマ! Ashima_1915002612623282176.jpg']
    ]

    global_config = r'E:\GitHub\Eagle_AItagger_byWD1.4\test\config.ini'
    
    # 获取模型信息
    from Config import Config
    section = "Model"
    option = "model_name"
    model_name = Config.get_config_data(global_config, section, option, default = None)
    option = "model_path"
    model_path = Config.get_config_data(global_config, section, option, default = None)