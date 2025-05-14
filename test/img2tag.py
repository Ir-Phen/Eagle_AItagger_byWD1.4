import json
from pathlib import Path
from wd14_tagger_package import ImageTagger
from configparser import ConfigParser

# 假设已经定义了全局变量 base_dir, wd14_path, Transfer_path, global_config_path, img_input_list_path

base_dir = Path(__file__).resolve().parent
wd14_path = base_dir / 'wd14_tagger_api'
Transfer_path = base_dir / 'csv' / 'Tags-cn(ver1.0,2023).csv'
global_config_path = base_dir / 'config.ini'
img_input_list_path = base_dir / 'image_list.txt'

def process_images_with_wd14_tagger():
    """
    使用 wd14_tagger 包处理图片并生成标签。
    """
    # 读取配置文件
    global_config = ConfigParser()
    global_config.read(global_config_path, encoding="utf-8")

    # 从配置文件中获取模型名称和设备信息，这里假设配置文件中有相应的配置项
    model_name = global_config.get('wd14_tagger', 'model_name', fallback='wd14-convnextv2.v1')
    device = global_config.get('wd14_tagger', 'device', fallback='cpu')
    threshold = global_config.getfloat('wd14_tagger', 'threshold', fallback=0.35)

    # 初始化标签生成器
    tagger = ImageTagger(model_name=model_name, threshold=threshold, device=device)
    print(f"初始化标签生成器成功，使用模型：{model_name}，设备：{device}，阈值：{threshold}")

    # 获取图片路径列表
    try:
        with img_input_list_path.open(mode='r', encoding='utf-8') as f:
            img_input_list = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"图片列表文件 {img_input_list_path} 未找到")
        return
    except Exception as e:
        print(f"读取图片列表文件时出错：{e}")
        return

    # 处理每张图片并生成标签
    for img_path in img_input_list:
        img_path = Path(img_path)
        if not img_path.is_file():
            print(f"图片文件 {img_path} 不存在，跳过")
            continue

        try:
            # 对图片进行标签生成
            tags = tagger.img_interrogate(img_path)

            # 输出标签结果
            print(f"图片 {img_path} 的标签：")
            for tag, confident in tags.items():
                print(f"标签：{tag}, 置信度：{confident}")

            # 这里可以根据需要将标签写入文件或其他操作
            # 例如写入到对应的 metadata.json 文件
            metadata_path = img_path.parent / 'metadata.json'
            if metadata_path.is_file():
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    metadata['tags'] = list(tags.keys())
                    with open(metadata_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=4)
                    print(f"已将标签写入 {metadata_path}")
                except Exception as e:
                    print(f"写入标签到 {metadata_path} 时出错：{e}")
        except Exception as e:
            print(f"处理图片 {img_path} 时出错：{e}")

# 调用示例
if __name__ == "__main__":
    process_images_with_wd14_tagger()