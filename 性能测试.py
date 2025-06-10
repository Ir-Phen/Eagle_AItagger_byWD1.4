from pathlib import Path
import psutil
import os
import time

from Tagger import setup_tagger_service

try:
    from pynvml import * # For NVIDIA GPUs
    _has_pynvml = True
except ImportError:
    print("Warning: pynvml not found. GPU monitoring will be unavailable.")
    _has_pynvml = False

# --- 单个图片推理资源消耗测试 (在 Tagger.py 内部进行) ---
print("\n--- 开始 Tagger.py 内部的单个图片推理资源消耗测试 ---")

import configparser # 在这里导入，因为 if __name__ == "__main__": 块通常是独立的运行环境

# 模拟 config_data
# 假设 config.ini 位于 Tagger.py 相同目录下
base_dir = Path(__file__).resolve().parent 
global_config_path = base_dir / 'config.ini' 
config_data_test = configparser.ConfigParser()


config_data_test.read(global_config_path, encoding='utf-8')


# 模拟模型路径
# 请确保 config.ini 中的 'Model' 路径设置正确，或者直接在这里提供绝对路径
model_path_test = config_data_test.get('Model', 'model_path', fallback='')
tags_path_test = config_data_test.get('Model', 'tags_path', fallback='')

if model_path_test:
    model_path_test = (base_dir / model_path_test).resolve()
if tags_path_test:
    tags_path_test = (base_dir / tags_path_test).resolve()

# 将解析后的绝对路径更新回 config_data_test，以便 TaggerService 正确获取
config_data_test.set('Model', 'model_path', str(model_path_test) if model_path_test else '')
config_data_test.set('Model', 'tags_path', str(tags_path_test) if tags_path_test else '')


# 准备一个测试图片路径
# !!! 替换为你的实际图片路径 !!!
test_image_path = Path(r"E:\动画与设计资源库.library\images\LZ35RW7ZS18PT.info\58766297_p0.jpg").resolve() # 例如：Path("C:/Users/YourUser/Pictures/my_test_image.png")
# 或者使用一个简单的模拟文件路径进行结构测试，如果不想实际执行推理
# test_image_path = Path("./simulated_image.jpg") # 确保这个文件存在，即使是空的也可以，Image.open()会尝试打开

if not test_image_path.exists():
    print(f"错误: 测试图片 '{test_image_path}' 不存在。请修改为实际图片路径或确保文件存在。")
elif not model_path_test.exists():
    print(f"错误: 模型文件 '{model_path_test}' 不存在。请检查 config.ini 中 'model_path' 的设置。")
elif not tags_path_test.exists():
    print(f"错误: 标签文件 '{tags_path_test}' 不存在。请检查 config.ini 中 'tags_path' 的设置。")
else:
    # 获取当前进程ID
    process = psutil.Process(os.getpid())

    print("\n--- 阶段1: 模型加载前 ---")
    cpu_percent_before = process.cpu_percent(interval=None) # Non-blocking call
    mem_info_before = process.memory_info()
    print(f"CPU使用率: {cpu_percent_before:.2f}%")
    print(f"内存使用: {mem_info_before.rss / (1024 * 1024):.2f} MB (RSS), {mem_info_before.vms / (1024 * 1024):.2f} MB (VMS)")
    
    # GPU信息 (如果可用)
    initial_gpu_mem = 0
    if _has_pynvml:
        try:
            nvmlInit()
            handle = nvmlDeviceGetHandleByIndex(0) # 通常是第一块GPU
            info = nvmlDeviceGetMemoryInfo(handle)
            initial_gpu_mem = info.used / (1024 * 1024)
            print(f"GPU显存使用 (设备0): {initial_gpu_mem:.2f} MB")
        except NVMLError as error:
            print(f"GPU监控错误: {error}")
            _has_pynvml = False # Disable GPU monitoring if error

    # 2. 模型加载 (通过 setup_tagger_service)
    print("\n--- 阶段2: 模型加载中 ---")
    load_start_time = time.time()
    tagger_service_test = setup_tagger_service(config_data_test) # 模型加载在此发生
    load_end_time = time.time()
    print(f"模型加载耗时: {load_end_time - load_start_time:.4f} 秒")

    # 3. 模型加载后资源使用
    print("\n--- 阶段3: 模型加载后 (推理前) ---")
    cpu_percent_after_load = process.cpu_percent(interval=None)
    mem_info_after_load = process.memory_info()
    print(f"CPU使用率: {cpu_percent_after_load:.2f}% (相对于启动前变化: {cpu_percent_after_load - cpu_percent_before:.2f}%)")
    print(f"内存使用: {mem_info_after_load.rss / (1024 * 1024):.2f} MB (RSS), {mem_info_after_load.vms / (1024 * 1024):.2f} MB (VMS)")
    print(f"内存变化: {(mem_info_after_load.rss - mem_info_before.rss) / (1024 * 1024):.2f} MB (RSS)")
    
    if _has_pynvml:
        try:
            info = nvmlDeviceGetMemoryInfo(handle)
            gpu_mem_after_load = info.used / (1024 * 1024)
            print(f"GPU显存使用 (设备0): {gpu_mem_after_load:.2f} MB")
            print(f"GPU显存变化: {gpu_mem_after_load - initial_gpu_mem:.2f} MB")
        except NVMLError as error:
            print(f"GPU监控错误: {error}")

    # 4. 单次推理
    print("\n--- 阶段4: 执行单次推理 ---")
    infer_start_time = time.time()
    tags_result = tagger_service_test.process_single_image(test_image_path) # 执行推理
    infer_end_time = time.time()
    print(f"单次推理耗时: {infer_end_time - infer_start_time:.4f} 秒")
    print(f"检测到的标签数量: {len(tags_result)}")
    # print("部分标签:", list(tags_result.keys())[:5]) # 打印前5个标签

    # 5. 推理后资源使用 (会相对稳定，主要是峰值观察)
    print("\n--- 阶段5: 推理后资源使用 ---")
    # CPU 占用百分比在短时间调用后通常是零或接近零，因为它是自上次调用以来的平均值。
    # 要观察推理期间的峰值 CPU 利用率，需要更复杂的循环监控。
    cpu_percent_after_infer = process.cpu_percent(interval=None) 
    mem_info_after_infer = process.memory_info()
    print(f"CPU使用率: {cpu_percent_after_infer:.2f}%")
    print(f"内存使用: {mem_info_after_infer.rss / (1024 * 1024):.2f} MB (RSS), {mem_info_after_infer.vms / (1024 * 1024):.2f} MB (VMS)")
    
    if _has_pynvml:
        try:
            info = nvmlDeviceGetMemoryInfo(handle)
            gpu_mem_after_infer = info.used / (1024 * 1024)
            print(f"GPU显存使用 (设备0): {gpu_mem_after_infer:.2f} MB")
        except NVMLError as error:
            print(f"GPU监控错误: {error}")

    # 6. 模型卸载
    print("\n--- 阶段6: 模型卸载 ---")
    if hasattr(tagger_service_test.interrogator, 'unload') and callable(tagger_service_test.interrogator.unload):
        tagger_service_test.interrogator.unload()
        print("模型已卸载")
    
    print("\n--- 阶段7: 模型卸载后资源使用 ---")
    cpu_percent_after_unload = process.cpu_percent(interval=None)
    mem_info_after_unload = process.memory_info()
    print(f"CPU使用率: {cpu_percent_after_unload:.2f}%")
    print(f"内存使用: {mem_info_after_unload.rss / (1024 * 1024):.2f} MB (RSS), {mem_info_after_unload.vms / (1024 * 1024):.2f} MB (VMS)")
    print(f"内存变化 (相对于加载后): {(mem_info_after_unload.rss - mem_info_after_load.rss) / (1024 * 1024):.2f} MB (RSS)")

    if _has_pynvml:
        try:
            nvmlShutdown() # 关闭NVML连接
        except NVMLError as error:
            print(f"GPU监控关闭错误: {error}")

print("\n--- Tagger.py 内部的单个图片推理资源消耗测试结束 ---")