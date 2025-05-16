from pathlib import Path
from wd14_tagger_package.wd14_tagger import ImageTagger
from wd14_tagger_package.interrogator import WaifuDiffusionInterrogator
from wd14_tagger_package.interrogators import interrogators

# 配置模型路径（需要替换为实际路径）
MODEL_NAME = "swinv2_v3"  # 选择要测试的模型名称
MODEL_PATH = "E:\GitHub\Eagle_AItagger_byWD1.4\test\model\swinv2_v3.onnx"
TAGS_PATH = "E:\GitHub\Eagle_AItagger_byWD1.4\test\csv\selected_tags.csv"
IMAGE_PATH = "E:\动画与设计资源库.library\images\MAQGISQ2TXC7F.info\アシマ! Ashima_1915002612623282176.jpg"

# 注册模型到interrogators字典
interrogators[MODEL_NAME] = WaifuDiffusionInterrogator(
    name=MODEL_NAME,
    model_path=MODEL_PATH,  # 本地模型路径
    tags_path=TAGS_PATH     # 本地标签路径
)
# 初始化图片标记器
tagger = ImageTagger(
    model_name=MODEL_NAME,
    threshold=0.35,  # 置信度阈值
    device="gpu"     # 使用cpu或gpu
)

# 执行图片标记
try:
    tags = tagger.image_interrogate(Path(IMAGE_PATH))
    print("\n检测到的标签:")
    print(", ".join(tags.keys()))
except Exception as e:
    print(f"标记失败: {str(e)}")

# 可选：清理模型（释放显存）
tagger.interrogator.unload()