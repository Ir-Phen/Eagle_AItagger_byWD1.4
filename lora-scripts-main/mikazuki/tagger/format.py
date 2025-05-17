import re
import hashlib

from typing import Dict, Callable, NamedTuple
from pathlib import Path


class Info(NamedTuple):
    path: Path
    output_ext: str


def hash(i: Info, algo='sha1') -> str:
    try:
        hash = hashlib.new(algo)
    except ImportError:
        raise ValueError(f"'{algo}' is invalid hash algorithm")

    # TODO: 可以散列大图像吗？
    with open(i.path, 'rb') as file:
        hash.update(file.read())

    return hash.hexdigest()


pattern = re.compile(r'\[([\w:]+)\]')

# 所有函数必须返回字符串或引发TypeError或ValueError
# 其他错误将导致扩展错误
available_formats: Dict[str, Callable] = {
    'name': lambda i: i.path.stem,
    'extension': lambda i: i.path.suffix[1:],
    'hash': hash,

    'output_extension': lambda i: i.output_ext
}


def format(match: re.Match, info: Info) -> str:
    matches = match[1].split(':')
    name, args = matches[0], matches[1:]

    if name not in available_formats:
        return match[0]

    return available_formats[name](info, *args)
