import argparse
from pathlib import Path
from .unified_config import UnifiedConfig
from .task_dispatcher import TaskDispatcher
from .process_pool_manager import ProcessPoolManager
from .result_collector import ResultCollector
from .progress_monitor import ProgressMonitor
from .check_update import VersionChecker

def get_image_list_info(img_list_path: Path) -> list:
    with img_list_path.open('r', encoding='utf-8') as f:
        img_paths = [Path(line.strip()).resolve() for line in f if line.strip()]
    return [
        {'image_path': str(img_path), 'json_path': str(img_path.parent / 'metadata.json')}
        for img_path in img_paths
    ]

def main(config_path: Path, img_list_path: Path):
    config = UnifiedConfig.from_ini_file(config_path)
    if not config.validate():
        print("配置验证失败")
        return

    # 清晰的启动信息
    print("=" * 50)
    print("图像标注工具启动")
    print("=" * 50)
    print(f"模型路径:     {config.model.model_path}")
    print(f"标签路径:     {config.model.tags_path}")
    print(f"工作进程数:   {config.process.max_workers}")
    print(f"批处理大小:   {config.process.batch_size}")
    print(f"置信度阈值:   {config.tag.threshold}")
    print("-" * 50)

    checker = VersionChecker(config)
    checker.check_for_update()

    image_data = get_image_list_info(img_list_path)
    print(f"解析图片列表中...请等待...")
    print(f"找到图片数量: {len(image_data)}")
    if not image_data:
        print("没有需要处理的图片")
        input("程序结束，按回车键退出...")
        return

    print("正在初始化组件...")
    dispatcher = TaskDispatcher(config)
    pool_manager = ProcessPoolManager(config)
    result_collector = ResultCollector(config)

    batches = dispatcher.create_batches(image_data)
    print(f"已创建 {len(batches)} 个处理批次")

    worker_config = config.to_dict()
    pool_manager.start_workers(worker_config)

    progress_monitor = ProgressMonitor(dispatcher, pool_manager, result_collector)
    progress_monitor.start()

    try:
        print("开始处理图片...")
        pool_manager.submit_tasks(batches)
        completed_batches = 0
        total_batches = len(batches)
        
        while completed_batches < total_batches:
            result = pool_manager.get_results(timeout=120)
            if 'error' in result:
                if 'worker_id' in result:
                    raise RuntimeError(f"工作进程 {result['worker_id']} 失败: {result['error']}")
                print(f"\n获取结果出错: {result['error']}")
                continue
                
            result_collector.add_result(result)
            completed_batches += 1
            batch_size = len(result.get('results', []))
            dispatcher.update_progress(batch_size)
            
            # 每完成10个批次调整一次批处理大小
            if completed_batches % 10 == 0:
                summary = result_collector.get_summary()
                dispatcher.adjust_batch_size(
                    summary['success_rate'] / 100, 
                    summary['total_processing_time'] / completed_batches if completed_batches > 0 else 0
                )

        # 结果合并后统一更新JSON
        print("\n正在更新JSON文件...")
        result_collector.update_json_files()

        print("正在生成报告...")
        result_collector.generate_report()
        
        # 只在主线程调用一次最终报告
        progress_monitor.final_report()

    except KeyboardInterrupt:
        print("\n程序被用户中断")
    finally:
        print("\n正在清理资源...")
        progress_monitor.stop()
        pool_manager.shutdown()
    input("程序结束，按回车键退出...")
