import pandas as pd
from typing import Tuple, List, Dict
from PIL import Image
from pathlib import Path
import re
import json

tag_escape_pattern = re.compile(r'([\\()])')

class Interrogator:
    @staticmethod
    def postprocess_tags(
        tags: Dict[str, float],
        threshold=0.35,
        additional_tags: List[str] = [],
        exclude_tags: List[str] = [],
        sort_by_alphabetical_order=False,
        add_confident_as_weight=False,
        replace_underscore=False,
        replace_underscore_excludes: List[str] = [],
        escape_tag=False
    ) -> Dict[str, float]:
        for t in additional_tags:
            tags[t] = 1.0

        # those lines are totally not "pythonic" but looks better to me
        tags = {
            t: c

            # sort by tag name or confident
            for t, c in sorted(
                tags.items(),
                key=lambda i: i[0 if sort_by_alphabetical_order else 1],
                reverse=not sort_by_alphabetical_order
            )

            # filter tags
            if (
                c >= threshold
                and t not in exclude_tags
            )
        }

        new_tags = []
        for tag in list(tags):
            new_tag = tag

            if replace_underscore and tag not in replace_underscore_excludes:
                new_tag = new_tag.replace('_', ' ')

            if escape_tag:
                new_tag = tag_escape_pattern.sub(r'\\\1', new_tag)

            if add_confident_as_weight:
                new_tag = f'({new_tag}:{tags[tag]})'

            new_tags.append((new_tag, tags[tag]))
        tags = dict(new_tags)

        return tags

    def __init__(self, name: str) -> None:
        self.name = name

    def load(self):
        raise NotImplementedError()

    def unload(self) -> bool:
        unloaded = False

        if hasattr(self, 'model') and self.model is not None:
            del self.model
            unloaded = True
            print(f'Unloaded {self.name}')

        if hasattr(self, 'tags'):
            del self.tags

        return unloaded

    def interrogate(
        self,
        image: Image,
        device: str
    ) -> Tuple[
        Dict[str, float],  # rating confidents
        Dict[str, float]  # tag confidents
    ]:
        raise NotImplementedError()

# 本地化的
class WaifuDiffusionInterrogator(Interrogator):
    def __init__(
        self,
        name: str,
        model_path: str,  # 直接传入本地模型路径
        tags_path: str,   # 直接传入本地标签路径
        **kwargs
    ) -> None:
        super().__init__(name)
        self.model_path = Path(model_path)
        self.tags_path = Path(tags_path)
        self.kwargs = kwargs

    def load(self) -> None:
        from onnxruntime import InferenceSession

        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        if self.kwargs.get("use_cpu", True):
            providers.pop(0)

        self.model = InferenceSession(str(self.model_path), providers=providers)
        print(f'Loaded {self.name} model from {self.model_path}')

        self.tags = pd.read_csv(self.tags_path)

# 本地化的
class MLDanbooruInterrogator(Interrogator):
    def __init__(
        self,
        name: str,
        model_path: str,  # 直接传入本地模型路径
        tags_path: str,    # 直接传入本地标签路径
        **kwargs
    ) -> None:
        super().__init__(name)
        self.model_path = Path(model_path)
        self.tags_path = Path(tags_path)
        self.kwargs = kwargs

    def load(self) -> None:
        from onnxruntime import InferenceSession
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        if self.kwargs.get("use_cpu", True):
            providers.pop(0)
        self.model = InferenceSession(str(self.model_path), providers=providers)
        print(f'Loaded {self.name} model from {self.model_path}')

        with open(self.tags_path, 'r', encoding='utf-8') as filen:
            self.tags = json.load(filen)
