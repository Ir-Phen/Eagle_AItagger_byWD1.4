from PIL import Image
from pathlib import Path

class ImageTagger:
    def __init__(
        self, 
        model_name: str,
        model_path: str,  # 新增模型路径参数
        tags_path: str,   # 新增标签路径参数
        threshold=0.5,
        device="cpu"
    ):
        self.threshold = threshold
        self.device = device
        self.model_name = model_name
        self.model_path = Path(model_path)
        self.tags_path = Path(tags_path)
        self.interrogator = None  # 延迟初始化
        self.load_model()  # 直接加载模型

    def load_model(self):
        """根据模型类型创建对应的Interrogator实例"""
        from wd14_tagger_package.interrogator import WaifuDiffusionInterrogator, MLDanbooruInterrogator

        self.interrogator = WaifuDiffusionInterrogator(
            name=self.model_name,
            model_path=self.model_path,
            tags_path=self.tags_path
        )

        # 设置计算设备
        self.interrogator.use_cpu = (self.device == "cpu")
        self.interrogator.load()
        print(f"Successfully loaded {self.model_name}")

    def image_interrogate(self, image_path: Path):
        """执行图像标注"""
        if not self.interrogator:
            raise RuntimeError("Model not loaded")

        im = Image.open(image_path)
        _, tag_confidents = self.interrogator.interrogate(im, self.device)
        return self.interrogator.postprocess_tags(
            tag_confidents,
            threshold=self.threshold,
            replace_underscore=True
        )

    def unload(self):
        """显式卸载模型"""
        if self.interrogator:
            return self.interrogator.unload()
        return False