import multiprocessing as mp
from pathlib import Path
import time
from typing import List, Dict, Any
from PIL import Image
from .tagger import TaggerService
from .unified_config import UnifiedConfig, VersionConfig, ModelConfig, TagConfig, ProcessConfig, ReportConfig

class ModelWorker:
    """模型工作进程"""
    def __init__(self, config_dict: Dict[str, Any]):
        model_config = ModelConfig(
            model_path=Path(config_dict['model']['model_path']),
            tags_path=Path(config_dict['model']['tags_path']),
            device_id=config_dict['model'].get('device_id', 0)
        )
        tag_config = TagConfig(**config_dict['tag'])
        process_config = ProcessConfig(**config_dict['process'])
        report_config = ReportConfig(**config_dict['report'])
        version_config = VersionConfig(**config_dict['version'])

        self.config = UnifiedConfig(
            version=version_config,
            model=model_config,
            tag=tag_config,
            process=process_config,
            report=report_config
        )
        
        self.tagger_service = None
        self._load_model()

    def _load_model(self):
        max_retries = self.config.process.max_retries
        retry_count = 0
        while retry_count < max_retries:
            try:
                print(f"工作进程 {mp.current_process().name} 正在加载模型 (尝试 {retry_count + 1}/{max_retries})")
                self.tagger_service = TaggerService(self.config)
                print(f"工作进程 {mp.current_process().name} 模型加载完成")
                return
            except Exception as e:
                retry_count += 1
                print(f"工作进程 {mp.current_process().name} 加载失败: {e}")
                if retry_count == max_retries:
                    raise RuntimeError(f"模型加载失败: {e}") from e
                time.sleep(2)
        raise RuntimeError("模型加载失败，已重试多次")

    def process_batch(self, batch_data: List[Dict]) -> List[Dict]:
        """处理批次，只返回标签结果，不更新JSON"""
        results = []
        for item in batch_data:
            image_path = Path(item['image_path'])
            json_path = Path(item['json_path'])
            if not image_path.exists():
                results.append({
                    'image_path': str(image_path),
                    'json_path': str(json_path),
                    'tags': [],
                    'success': False,
                    'error': f'图片未找到: {image_path}'
                })
                continue
            try:
                tags_dict = self.tagger_service.process_single_image(image_path)
                tag_list = list(tags_dict.keys())
                results.append({
                    'image_path': str(image_path),
                    'json_path': str(json_path),
                    'tags': tag_list,
                    'success': True,
                    'error': None
                })
            except Exception as e:
                results.append({
                    'image_path': str(image_path),
                    'json_path': str(json_path),
                    'tags': [],
                    'success': False,
                    'error': f'处理失败: {str(e)}'
                })
        return results

    def unload(self):
        if self.tagger_service:
            self.tagger_service.unload()

def worker_process(config_dict: Dict[str, Any], task_queue: mp.Queue, 
                   result_queue: mp.Queue, worker_id: int):
    worker = None
    try:
        worker = ModelWorker(config_dict)
        # 简化工作进程启动日志
        while True:
            task = task_queue.get()
            if task is None:
                break
            batch_id, batch_data = task
            start_time = time.time()
            results = worker.process_batch(batch_data)
            processing_time = time.time() - start_time
            
            # 只在处理时间异常长时记录
            if processing_time > 30:
                print(f"\n工作进程 {worker_id} 完成批次 {batch_id} (耗时: {processing_time:.1f}秒)")
            
            result_queue.put({
                'batch_id': batch_id,
                'worker_id': worker_id,
                'results': results,
                'processing_time': processing_time
            })
    except Exception as e:
        print(f"\n工作进程 {worker_id} 发生错误: {e}")
        result_queue.put({
            'batch_id': -1,
            'worker_id': worker_id,
            'error': str(e),
            'results': []
        })
    finally:
        if worker:
            worker.unload()
