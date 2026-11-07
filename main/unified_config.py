"""统一配置管理器"""
import configparser
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, field

@dataclass
class ModelConfig:
    model_path: Path
    tags_path: Path
    device_id: int = 0

@dataclass
class TagConfig:
    threshold: float = 0.5
    replace_underscore: bool = True
    underscore_excludes: List[str] = field(default_factory=list)
    escape_tags: bool = False
    use_chinese_name: bool = True
    additional_tags: List[str] = field(default_factory=list)
    exclude_tags: List[str] = field(default_factory=list)
    sort_alphabetically: bool = False

@dataclass
class ProcessConfig:
    max_workers: int = 2
    batch_size: int = 8
    max_retries: int = 3
    checkpoint_interval: int = 100
    add_write_mode: bool = False

@dataclass
class ReportConfig:
    create_csv_report: bool = False

@dataclass
class VersionConfig:
    version: str = "4.0.0"
    update_notes: str = ""

@dataclass
class UnifiedConfig:
    version: VersionConfig = field(default_factory=VersionConfig)
    model: ModelConfig = field(default_factory=lambda: ModelConfig(Path(""), Path("")))
    tag: TagConfig = field(default_factory=TagConfig)
    process: ProcessConfig = field(default_factory=ProcessConfig)
    report: ReportConfig = field(default_factory=ReportConfig)

    @classmethod
    def from_ini_file(cls, config_path: Path) -> 'UnifiedConfig':
        parser = configparser.ConfigParser()
        parser.read(config_path, encoding='utf-8')
        
        version = VersionConfig(
            version=parser.get("Version", "version", fallback="4.0.0"),
            update_notes=parser.get("Version", "update_notes", fallback="")
        )
        
        model = ModelConfig(
            model_path=Path(parser.get("Model", "model_path")),
            tags_path=Path(parser.get("Model", "tags_path")),
            device_id=parser.getint("Model", "device_id", fallback=0)
        )
        
        tag = TagConfig(
            threshold=parser.getfloat("Tag", "threshold", fallback=0.5),
            replace_underscore=parser.getboolean("Tag", "replace_underscore", fallback=True),
            underscore_excludes=cls._parse_list(parser.get("Tag", "underscore_excludes", fallback="")),
            escape_tags=parser.getboolean("Tag", "escape_tags", fallback=False),
            use_chinese_name=parser.getboolean("Tag", "use_chinese_name", fallback=True),
            additional_tags=cls._parse_list(parser.get("Tag", "additional_tags", fallback="")),
            exclude_tags=cls._parse_list(parser.get("Tag", "exclude_tags", fallback="")),
            sort_alphabetically=parser.getboolean("Tag", "sort_alphabetically", fallback=False)
        )
        
        process = ProcessConfig(
            max_workers=parser.getint("Process", "max_workers", fallback=2),
            batch_size=parser.getint("Process", "batch_size", fallback=8),
            max_retries=parser.getint("Process", "max_retries", fallback=3),
            checkpoint_interval=parser.getint("Process", "checkpoint_interval", fallback=100),
            add_write_mode=parser.getboolean("Json", "add_write_mode", fallback=False)
        )
        
        report = ReportConfig(
            create_csv_report=parser.getboolean("Json", "is_creat_image_info_csv", fallback=False)
        )
        
        return cls(version=version, model=model, tag=tag, process=process, report=report)
    
    @staticmethod
    def _parse_list(value: str) -> List[str]:
        return [item.strip() for item in value.split(',') if item.strip()]
    
    def validate(self) -> bool:
        try:
            if not self.model.model_path.exists():
                raise ValueError(f"模型文件不存在: {self.model.model_path}")
            if not self.model.tags_path.exists():
                raise ValueError(f"标签文件不存在: {self.model.tags_path}")
            if self.model.device_id < 0:
                raise ValueError(f"DirectML 设备编号不能小于 0: {self.model.device_id}")
            if not 0 <= self.tag.threshold <= 1:
                raise ValueError(f"阈值必须在0-1之间: {self.tag.threshold}")
            if self.process.max_workers <= 0:
                raise ValueError(f"工作进程数必须大于0: {self.process.max_workers}")
            return True
        except Exception as e:
            print(f"配置验证失败: {e}")
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'version': self.version.__dict__,
            'model': {
                'model_path': str(self.model.model_path),
                'tags_path': str(self.model.tags_path),
                'device_id': self.model.device_id
            },
            'tag': self.tag.__dict__,
            'process': self.process.__dict__,
            'report': self.report.__dict__
        }
