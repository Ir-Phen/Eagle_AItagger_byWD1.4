import re
from pathlib import Path
from typing import Dict, Tuple
from PIL import Image, UnidentifiedImageError
import pandas as pd
import numpy as np
from onnxruntime import InferenceSession
import cv2

# 图像预处理类
class DBIMUtils:
    """图像预处理类"""
    @staticmethod
    def fill_transparent(image: Image.Image, color='WHITE'):
        image = image.convert('RGBA')
        new_image = Image.new('RGBA', image.size, color)
        new_image.paste(image, mask=image)
        image = new_image.convert('RGB')
        return image

    @staticmethod
    def resize(pic: Image.Image, size: int, keep_ratio=True) -> Image.Image:
        if not keep_ratio:
            target_size = (size, size)
        else:
            min_edge = min(pic.size)
            target_size = (
                int(pic.size[0] / min_edge * size),
                int(pic.size[1] / min_edge * size),
            )

        target_size = (target_size[0] & ~3, target_size[1] & ~3)

        return pic.resize(target_size, resample=Image.Resampling.LANCZOS)

    @staticmethod
    def smart_imread(img, flag=cv2.IMREAD_UNCHANGED):
        if img.endswith(".gif"):
            img = Image.open(img)
            img = img.convert("RGB")
            img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        else:
            img = cv2.imread(img, flag)
        return img

    @staticmethod
    def smart_24bit(img):
        if img.dtype is np.dtype(np.uint16):
            img = (img / 257).astype(np.uint8)

        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif img.shape[2] == 4:
            trans_mask = img[:, :, 3] == 0
            img[trans_mask] = [255, 255, 255, 255]
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    @staticmethod
    def make_square(img, target_size):
        old_size = img.shape[:2]
        desired_size = max(old_size)
        desired_size = max(desired_size, target_size)

        delta_w = desired_size - old_size[1]
        delta_h = desired_size - old_size[0]
        top, bottom = delta_h // 2, delta_h - (delta_h // 2)
        left, right = delta_w // 2, delta_w - (delta_w // 2)

        color = [255, 255, 255]
        new_im = cv2.copyMakeBorder(
            img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color
        )
        return new_im

    @staticmethod
    def smart_resize(img, size):
        # Assumes the image has already gone through make_square
        if img.shape[0] > size:
            img = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)
        elif img.shape[0] < size:
            img = cv2.resize(img, (size, size), interpolation=cv2.INTER_CUBIC)
        return img

# 核心模块
class WaifuDiffusionInterrogator:
    """WD14模型实现"""
    def __init__(self, model_path: Path, tags_path: Path, use_chinese_name: bool, config_data: dict):
        self.name = "WD14-Tagger"
        self.model_path = model_path
        self.tags_path = tags_path
        self.use_chinese_name = use_chinese_name
        self.config_data = config_data
        self.model = None
        self.tags = None

    def load(self):
        """加载模型和标签"""
        
        self.model = InferenceSession(
            str(self.model_path),
            providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
        )
        self.tags = pd.read_csv(self.tags_path)
        print(f"Loaded {self.name} from {self.model_path}")

    def unload(self):
        """通用卸载逻辑"""
        if self.model is not None:
            del self.model
            self.model = None
            print(f"Unloaded {self.name} model")
        return True

    def interrogate(self, image: Image.Image) -> Tuple[Dict, Dict]:
        """执行图像分析"""
        target_size = self.model.get_inputs()[0].shape[1]
        processed = self._preprocess_image(image, target_size)

        # 模型推理
        input_name = self.model.get_inputs()[0].name
        output_name = self.model.get_outputs()[0].name
        confs = self.model.run([output_name], {input_name: processed})[0][0]  # 确保输出维度正确

        # 验证标签列和置信度对齐
        tag_col = 'right_tag_cn' if self.use_chinese_name else 'name'
        
        # 确保标签数量与confs长度匹配
        total_tags = len(self.tags)
        if len(confs) != total_tags:
            raise ValueError(f"模型输出置信度数量({len(confs)})与标签数量({total_tags})不匹配")

        # 分割评分和普通标签
        ratings = dict(zip(self.tags.head(4)[tag_col], confs[:4]))
        tags = dict(zip(self.tags[4:][tag_col], confs[4:]))

        return ratings, tags

    def _preprocess_image(self, image: Image.Image, target_size: int) -> np.ndarray:
        """图像预处理标准化"""
        # 透明通道
        image = DBIMUtils.fill_transparent(image, color='WHITE')
        # 格式转换和尺寸调整
        arr = np.array(image)[:, :, ::-1]  # PIL RGB to OpenCV BGR
        arr = DBIMUtils.make_square(arr, target_size)
        arr = DBIMUtils.smart_resize(arr, target_size)
        return np.expand_dims(arr.astype(np.float32), 0)

# 标签生成服务
class TaggerService:
    """标签生成服务，合并了标签后处理逻辑"""

    def __init__(self, config_data: dict):
        print("config_data:", config_data)
        self.config_data = config_data
        self.interrogator = None
        # 合并后的标签处理逻辑参数
        self.model_path = Path(self.config_data.get('Model', 'model_path', fallback=None))
        self.tags_path = Path(self.config_data.get('Model', 'tags_path', fallback=None))

        self.additional_tags =self.config_data.get('Tag', 'additional_tags', fallback='')
        self.additional_tags = [tag.strip() for tag in self.additional_tags.split(',') if tag.strip()]
        print(self.additional_tags)

        self.exclude_tags_str = self.config_data.get('Tag', 'exclude_tags', fallback='')
        self.exclude_tags = [tag.strip() for tag in self.exclude_tags_str.split(',') if tag.strip()]
        print(self.exclude_tags)

        self.threshold = self.config_data.getfloat('Tag', 'threshold', fallback=0.5)
        self.replace_underscore = self.config_data.getboolean('Tag', 'replace_underscore', fallback=True)
        
        self.underscore_excludes = self.config_data.get('Tag', 'underscore_excludes', fallback='')
        self.underscore_excludes = [tag.strip() for tag in self.underscore_excludes.split(',') if tag.strip()]

        self.sort_alphabetically = self.config_data.getboolean('Tag', 'sort_alphabetically', fallback=False)
        self.escape_tags = self.config_data.getboolean('Tag', 'escape_tags', fallback=False)
        self.use_chinese_name = self.config_data.getboolean('Tag', 'use_chinese_name', fallback=False)
        self.TAG_ESCAPE_PATTERN = re.compile(r'([\\()])')  # 保留正则模式

    def initialize_model(self):
        """模型初始化"""
        self.interrogator = WaifuDiffusionInterrogator(self.model_path, self.tags_path, self.use_chinese_name, self.config_data)
        self.interrogator.load()

    def process_single_image(self, image_path: Path) -> Dict:
        """处理单张图像，集成标签处理逻辑"""
        try:
            with Image.open(image_path) as img:
                _, raw_tags = self.interrogator.interrogate(img)
                return self.process_tags(raw_tags)  # 直接调用合并后的处理方法
        except (IOError, UnidentifiedImageError) as e:
            print(f"Error processing {image_path}: {str(e)}")
            return {}

    def process_tags(self, raw_tags: Dict[str, float]) -> Dict[str, float]:
        """合并的标签处理方法"""
        # 强制标签处理（添加必备标签）
        tags = raw_tags.copy()  # 避免修改原始字典

        if not self.additional_tags:
            pass
        else:
            tags.update({tag: 1.0 for tag in self.additional_tags if tag not in tags})

        # 过滤和排序标签
        filtered = {tag: conf for tag, conf in tags.items() if conf >= self.threshold}

        if not self.exclude_tags:
            pass
        else:
            filtered = {tag: conf for tag, conf in filtered.items() if tag not in self.exclude_tags}
        
        # 过滤非法字符
        illegal_chars = {'[', ']', ',', '(', ')', '\\'}
        removed_tags = []  # 记录被移除的标签
        valid_tags = {}    # 保留的有效标签
        for tag, conf in filtered.items():
            if len(tag) == 1 and tag in illegal_chars:
                removed_tags.append(tag)
            else:
                valid_tags[tag] = conf
        # 打印被移除的标签（调试用）
        if removed_tags:
            print(f"已过滤无效单字符标签: {', '.join(removed_tags)}")
        filtered = valid_tags

        # 在排序处理中使用三元操作简化if逻辑
        sorted_tags = sorted(filtered.items(), key=lambda x: (-x[1], x[0]) if not self.sort_alphabetically else x[0])

        processed = []
        for tag, conf in sorted_tags:
            new_tag = tag

            # 下划线处理逻辑保持一致
            if self.replace_underscore:
                if tag not in self.underscore_excludes:
                    new_tag = new_tag.replace('_', ' ')

            # 转义处理逻辑保持一致
            if self.escape_tags:
                new_tag = self.TAG_ESCAPE_PATTERN.sub(r'\\\1', new_tag)

            processed.append((new_tag, conf))

        return dict(processed)

# 接口适配模块
def setup_tagger_service(config_data: dict) -> TaggerService:
    """工厂方法创建服务"""
    service = TaggerService(config_data)
    service.initialize_model()
    return service

# 主入口适配
def on_interrogate(config_data: dict) -> TaggerService:
    """主入口函数"""
    return setup_tagger_service(config_data)

if __name__ == "__main__":
    raise
    # import configparser
    # config_data = configparser.ConfigParser()
    # config_data.read(r'E:\GitHub\Eagle_AItagger_byWD1.4\config.ini', encoding='utf-8')
    # image_path = r'E:\动画与设计资源库.library\images\M1MIJT7FF1FWF.info\119370624_p0.webp'

    # tagger = setup_tagger_service(config_data)
    # print("标签过滤阈值:", tagger.threshold)
    # try:
    #     tags = tagger.process_single_image(Path(image_path))
    #     print("\nDetected Tags:", ", ".join(tags.keys()))
    # except Exception as e:
    #     print(f"Tagging failed: {str(e)}")