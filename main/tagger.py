import re
from pathlib import Path
from typing import Dict, Tuple
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener
import pandas as pd
import onnxruntime as ort

# 注册 HEIC/HEIF 格式支持
register_heif_opener()
from .image_utils import ImageUtils  # 导入预处理工具
from .unified_config import GPU_PROVIDERS


class WaifuDiffusionInterrogator:
    """WD14模型实现"""

    def __init__(self, config):
        self.config = config
        self.model = None
        self.tags = None

    def load(self):
        """加载模型和标签"""
        available = ort.get_available_providers()
        backend = self.config.model.backend
        if backend == "auto":
            backend = next(
                (name for name, provider in GPU_PROVIDERS.items() if provider in available),
                None,
            )
        provider = GPU_PROVIDERS.get(backend)
        if provider not in available:
            raise RuntimeError(
                f"当前 Python 环境无法使用 backend={self.config.model.backend}。"
                "请安装所选后端的依赖：DirectML 使用 requirements.txt，"
                "CUDA 使用 requirements-cuda.txt。"
            )

        device_id = self.config.model.device_id
        options = ort.SessionOptions()
        if backend == "directml":
            options.enable_mem_pattern = False
            options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        elif hasattr(ort, "preload_dlls"):
            ort.preload_dlls()
        session = ort.InferenceSession(
            str(self.config.model.model_path),
            sess_options=options,
            providers=[(provider, {"device_id": device_id})],
        )
        if session.get_providers()[0] != provider:
            raise RuntimeError(
                f"{provider} 初始化失败 (device_id={device_id})，"
                "请检查显卡驱动、推理依赖和设备编号。"
            )
        session.disable_fallback()
        self.tags = pd.read_csv(self.config.model.tags_path)
        self.model = session
        print(f"从{self.config.model.model_path}加载模型，推理后端: {provider} (device_id={device_id})")

    def unload(self):
        """卸载模型"""
        if self.model is not None:
            del self.model
            self.model = None
            print("卸载模型")
        return True

    def interrogate(self, image: Image.Image) -> Tuple[Dict, Dict]:
        """执行图像分析"""
        target_size = self.model.get_inputs()[0].shape[1]
        processed = ImageUtils.preprocess_image(image, target_size)

        # 模型推理
        input_name = self.model.get_inputs()[0].name
        output_name = self.model.get_outputs()[0].name
        confs = self.model.run([output_name], {input_name: processed})[0][0]

        # 验证标签列和置信度对齐
        tag_col = "right_tag_cn" if self.config.tag.use_chinese_name else "name"

        total_tags = len(self.tags)
        if len(confs) != total_tags:
            raise ValueError(
                f"模型输出置信度数量({len(confs)})与标签数量({total_tags})不匹配"
            )

        # 分割评分和普通标签
        ratings = dict(zip(self.tags.head(4)[tag_col], confs[:4]))
        tags = dict(zip(self.tags[4:][tag_col], confs[4:]))

        return ratings, tags


class TaggerService:
    """标签生成服务"""

    def __init__(self, config):
        self.config = config
        self.interrogator = WaifuDiffusionInterrogator(config)
        self.interrogator.load()
        self.TAG_ESCAPE_PATTERN = re.compile(r"([\\()])")

    def process_single_image(self, image_path: Path) -> Dict[str, float]:
        """处理单张图像，返回处理后的标签"""
        try:
            with Image.open(image_path) as img:
                _, raw_tags = self.interrogator.interrogate(img)
                return self.process_tags(raw_tags)
        except (IOError, UnidentifiedImageError) as e:
            print(f"处理图片时出错 {image_path}: {str(e)}")
        return {}

    def process_tags(self, raw_tags: Dict[str, float]) -> Dict[str, float]:
        """处理标签"""
        tags = raw_tags.copy()

        if self.config.tag.additional_tags:
            tags.update(
                {tag: 1.0 for tag in self.config.tag.additional_tags if tag not in tags}
            )

        filtered = {
            tag: conf for tag, conf in tags.items() if conf >= self.config.tag.threshold
        }

        if self.config.tag.exclude_tags:
            filtered = {
                tag: conf
                for tag, conf in filtered.items()
                if tag not in self.config.tag.exclude_tags
            }

        # 过滤非法字符
        illegal_chars = {"[", "]", ",", "(", ")", "\\"}
        valid_tags = {
            tag: conf
            for tag, conf in filtered.items()
            if not (len(tag) == 1 and tag in illegal_chars)
        }

        # 排序
        sorted_tags = sorted(
            valid_tags.items(),
            key=lambda x: (
                (-x[1], x[0]) if not self.config.tag.sort_alphabetically else x[0]
            ),
        )

        processed = []
        for tag, conf in sorted_tags:
            new_tag = tag
            if self.config.tag.replace_underscore:
                if tag not in self.config.tag.underscore_excludes:
                    new_tag = new_tag.replace("_", " ")
            if self.config.tag.escape_tags:
                new_tag = self.TAG_ESCAPE_PATTERN.sub(r"\\\1", new_tag)
            processed.append((new_tag, conf))

        return dict(processed)

    def unload(self):
        self.interrogator.unload()
