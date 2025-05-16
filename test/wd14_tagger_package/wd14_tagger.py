from wd14_tagger_package.interrogator import Interrogator

from PIL import Image
from pathlib import Path
from wd14_tagger_package.interrogators import interrogators

# 从全局配置文件获取参数配置

class ImageTagger:
    def __init__(self, model_name= None, threshold=0.5,device="gpu"):
        self.threshold = threshold #置信度，过滤标签
        self.device = device # 推理设备 
        self.load_model(model_name) # 模型名称

    def load_model(self, model_name):
        # 从config获取选择的模型，将模型加载到内存中。
        if model_name in interrogators.keys():
            self.model_name = model_name
            self.interrogator = interrogators[model_name]
            self.interrogator.use_cpu = self.device == "cpu"
        else:
            raise ValueError(f"Model {model_name} not available.")

    def change_model(self, new_model_name):
        # 改变加的模型
        print(f"Changing model from {self.model_name} to {new_model_name}")
        self.load_model(new_model_name)

    def image_interrogate(self, image_path: Path):
        # 对图像路径执行预测。
        im = Image.open(image_path)
        result = self.interrogator.interrogate(im, self.device)
        return self.interrogator.postprocess_tags(result[1], threshold=self.threshold)

def process_file(self, file_path):
    tags = self.image_interrogate(Path(file_path))
    print("\nDetected Tags:", ", ".join(tags.keys()))

if __name__ == "__main__":
    True