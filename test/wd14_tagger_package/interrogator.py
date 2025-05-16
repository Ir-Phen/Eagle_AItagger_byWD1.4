import pandas as pd
from typing import Tuple, List, Dict
from PIL import Image
from pathlib import Path
import re
import numpy as np
import json

tag_escape_pattern = re.compile(r'([\\()])')

# 定义一个名为Interrogator的类，用于处理图像标签相关操作
class Interrogator:
    # 静态方法，用于对原始标签进行后处理
    @staticmethod
    def postprocess_tags(
        tags: Dict[str, float],          # 原始标签字典（标签:置信度）
        threshold=0.35,                  # 置信度阈值，默认0.35
        additional_tags: List[str] = [], # 强制添加的标签列表
        exclude_tags: List[str] = [],    # 需要排除的标签列表
        sort_by_alphabetical_order=False,# 是否按字母排序（默认按置信度降序）
        add_confident_as_weight=False,   # 是否将置信度作为后缀
        replace_underscore=True,        # 是否替换下划线为空格
        replace_underscore_excludes: List[str] = [], # 不替换下划线的标签
        escape_tag=False                 # 是否转义特殊字符
    ) -> Dict[str, float]:
        
        # 添加强制标签（置信度设为1.0，覆盖已存在标签）
        for t in additional_tags:
            tags[t] = 1.0

        # 标签过滤与排序处理
        tags = {
            t: c
            # 排序逻辑：按字母升序或置信度降序
            for t, c in sorted(
                tags.items(),
                key=lambda i: i[0 if sort_by_alphabetical_order else 1],
                reverse=not sort_by_alphabetical_order
            )
            # 过滤条件：置信度达标且不在排除列表
            if (
                c >= threshold
                and t not in exclude_tags
            )
        }

        # 标签格式转换
        new_tags = []
        for tag in list(tags):
            new_tag = tag

            # 下划线替换处理
            if replace_underscore and tag not in replace_underscore_excludes:
                new_tag = new_tag.replace('_', ' ')

            # 特殊字符转义处理（假设tag_escape_pattern已定义）
            if escape_tag:
                new_tag = tag_escape_pattern.sub(r'\\\1', new_tag)

            # 添加置信度后缀
            if add_confident_as_weight:
                new_tag = f'({new_tag}:{tags[tag]})'

            new_tags.append((new_tag, tags[tag]))  # 保存处理后的标签
        
        tags = dict(new_tags)  # 转换为字典
        return tags

    # 初始化方法，记录实例名称
    def __init__(self, name: str) -> None:
        self.name = name

    # 需子类实现的模型加载方法
    def load(self):
        raise NotImplementedError()

    # 模型卸载方法
    def unload(self) -> bool:
        unloaded = False
        # 删除模型对象
        if hasattr(self, 'model') and self.model is not None:
            del self.model
            unloaded = True
            print(f'Unloaded {self.name}')
        
        # 删除标签数据
        if hasattr(self, 'tags'):
            del self.tags
        
        return unloaded  # 返回卸载状态

    # 需子类实现的图像分析接口
    def interrogate(
        self,
        image: Image,  # 输入图像
        device: str    # 计算设备（如CPU/GPU）
    ) -> Tuple[
        Dict[str, float],  # 评分置信度字典
        Dict[str, float]   # 标签置信度字典
    ]:
        raise NotImplementedError()

# 本地化的
class WaifuDiffusionInterrogator(Interrogator):
    def __init__(
        self,
        name: str,
        model_path: str,  # 直接传入本地模型路径
        tags_path: str,   # 直接传入本地标签路径
        **kwargs
    ) -> None:
        super().__init__(name)
        self.model_path = Path(model_path)
        self.tags_path = Path(tags_path)
        self.kwargs = kwargs

    def load(self) -> None:
        from onnxruntime import InferenceSession

        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        if self.kwargs.get("use_cpu", True):
            providers.pop(0)

        self.model = InferenceSession(str(self.model_path), providers=providers)
        print(f'Loaded {self.name} model from {self.model_path}')

        self.tags = pd.read_csv(self.tags_path)

    def interrogate(self, image: Image.Image, device: str) -> Tuple[Dict[str, float], Dict[str, float]]:

    # 图像预处理（适配 HWC 输入）
        image = image.convert("RGB").resize((448, 448))
        image_np = np.array(image).astype(np.float32) / 255.0
        image_np = np.expand_dims(image_np, axis=0)  # 添加批次维度 (1, 448, 448, 3)

        # 运行模型推理
        input_name = self.model.get_inputs()[0].name
        output_name = self.model.get_outputs()[0].name
        confidences = self.model.run([output_name], {input_name: image_np})[0]

        # 解析标签（假设 CSV 包含 'name' 列）
        tags = {
            self.tags.iloc[i]['name']: float(confidences[0][i]) 
            for i in range(len(self.tags))
        }

        # 返回空评分字典和标签字典
        return {}, tags


# 本地化的
class MLDanbooruInterrogator(Interrogator):
    def __init__(
        self,
        name: str,
        model_path: str,  # 直接传入本地模型路径
        tags_path: str,    # 直接传入本地标签路径
        use_cpu=False,
        **kwargs
    ) -> None:
        super().__init__(name)
        self.model_path = Path(model_path)
        self.tags_path = Path(tags_path)
        self.kwargs = kwargs
        self.use_cpu = use_cpu

    def load(self) -> None:
        from onnxruntime import InferenceSession
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        if self.use_cpu:
            providers.pop(0)
        self.model = InferenceSession(str(self.model_path), providers=providers)
        print(f'Loaded {self.name} model from {self.model_path}')

        self.tags = pd.read_csv(self.tags_path)

    def interrogate(
        self,
        image: Image
    ) -> Tuple[
        Dict[str, float],  # rating confidents
        Dict[str, float]  # tag confidents
    ]:
        # init model
        if not hasattr(self, 'model') or self.model is None:
            self.load()

        # code for converting the image and running the model is taken from the link below
        # thanks, SmilingWolf!
        # https://huggingface.co/spaces/SmilingWolf/wd-v1-4-tags/blob/main/app.py

        # convert an image to fit the model
        _, height, _, _ = self.model.get_inputs()[0].shape

        # alpha to white
        image = image.convert('RGBA')
        new_image = Image.new('RGBA', image.size, 'WHITE')
        new_image.paste(image, mask=image)
        image = new_image.convert('RGB')
        image = np.asarray(image)

        # PIL RGB to OpenCV BGR
        image = image[:, :, ::-1]
        from wd14_tagger_package import dbimutils
        image = dbimutils.make_square(image, height)
        image = dbimutils.smart_resize(image, height)
        image = image.astype(np.float32)
        image = np.expand_dims(image, 0)

        # evaluate model
        input_name = self.model.get_inputs()[0].name
        label_name = self.model.get_outputs()[0].name
        confidents = self.model.run([label_name], {input_name: image})[0]

        tags = self.tags[:][['name']]
        tags['confidents'] = confidents[0]

        # first 4 items are for rating (general, sensitive, questionable, explicit)
        ratings = dict(tags[:4].values)

        # rest are regular tags
        tags = dict(tags[4:].values)

        return ratings, tags