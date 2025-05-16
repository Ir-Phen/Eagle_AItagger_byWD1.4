from pathlib import Path
from wd14_tagger_package.wd14_tagger import ImageTagger
from wd14_tagger_package.interrogator import WaifuDiffusionInterrogator

# 配置模型路径（需要替换为实际路径）
MODEL_NAME = r'swinv2_v3'  # 选择要测试的模型名称
MODEL_PATH = r'E:\GitHub\Eagle_AItagger_byWD1.4\test\model\swinv2_v3.onnx'
TAGS_PATH = r'E:\GitHub\Eagle_AItagger_byWD1.4\test\csv\selected_tags.csv'
IMAGE_PATH = r'E:\动画与设计资源库.library\images\MAQGISQ1Z8PST.info\124086849_p0.png'

# 初始化标注器
tagger = ImageTagger(
    model_name=MODEL_NAME,
    model_path=MODEL_PATH,
    tags_path=TAGS_PATH,
    threshold=0.35,
    device="gpu"
)

# 执行标注
try:
    tags = tagger.image_interrogate(Path(IMAGE_PATH))
    print("\nDetected Tags:", ", ".join(tags.keys()))
except Exception as e:
    print(f"Tagging failed: {str(e)}")

# 显式释放资源
tagger.unload()