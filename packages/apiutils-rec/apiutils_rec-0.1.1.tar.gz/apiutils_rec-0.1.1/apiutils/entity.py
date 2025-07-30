# SPDX-License-Identifier: MIT

"""
API 模块

该模块提供了对API字符串的解析和标准化功能。它支持从字符串创建API对象，检查API是否为标准API，并获取可能的标准API列表。
允许用户自义定标准APIs
"""

import re
import pathlib
import pandas as pd
from typing import Optional, List, Tuple, Sequence

_src_dir = pathlib.Path(__file__).parent.resolve()


def _get_doc_api_fullname() -> Tuple[List[str], List[str]]:
    doc = pd.read_csv(
        _src_dir / 'dataset' / 'doc' / 'doc_APIs_descriptions.csv'
    )[['API', 'description']].to_dict()
    return list(doc['API'].values()), list(doc['description'].values())


class API:
    """
    API对象, Java API Fullname的封装
    """
    _standard_api_strings, _standard_api_description = _get_doc_api_fullname()
    _dot_string_pattern = r'\b([a-zA-Z0-9_]+(\.[a-zA-Z0-9_]+)+)(\((.*?)\))?'
    _standard_apis = None

    def __init__(self, api_str: str, description: Optional[str] = None) -> None:
        """
        初始化API对象，使用正则表达式匹配第一个出现的API字符串

        Args:
            api_str: 一段包含API的字符串
            description: 可选，API的描述
        """
        self.fullname: str = ''
        self.method: str = ''
        self.prefix: str = ''
        self.args: Optional[list] = None
        self.parts: List[str] = []
        self.description: Optional[str] = description

        match = re.search(API._dot_string_pattern, api_str)
        if match:
            self.fullname = match.group(1)
            if not match.group(3):
                self.args = None
            else:
                self.args = (
                    [arg.strip() for arg in match.group(4).split(',') if arg.strip()]
                    if match.group(4) else []
                )
            self.prefix, self.method = self.fullname.rsplit('.', 1)
            self.parts = self.fullname.split('.')
        else:
            raise ValueError(f"Invalid API string: {api_str}")

    @classmethod
    def from_string(cls, api_str: str) -> List['API']:
        """
        从字符串中解析API对象列表

        Args:
            api_str: 包含API字符串的字符串，可以是单个API或多个API的组合

        Returns: API对象列表

        """
        if not isinstance(api_str, str):
            raise TypeError(f"API string must be a string, but got {type(api_str)}")
        apis = []
        standard_apis_map = {api.fullname: api for api in cls.get_standard_apis()}
        for match in re.finditer(cls._dot_string_pattern, api_str):
            api_fullname = match.group(1)
            args = match.group(3) or ''
            api = cls(api_fullname + args)

            if api.fullname in standard_apis_map:
                api.description = standard_apis_map[api.fullname].description

            apis.append(api)
        return apis

    @classmethod
    def set_standard_apis(cls,
                          standard_apis: List[str],
                          standard_api_descriptions: Optional[List[str]]) -> None:
        """
        设置标准API列表，用于检查API是否标准或匹配可能的标准API

        Args:
            standard_apis: API字符串列表
            standard_api_descriptions: 可选，API描述列表
        """
        # cls._standard_apis = [cls(api_str) for api_str in standard_apis]
        cls._standard_api_strings = standard_apis
        cls._standard_api_description = standard_api_descriptions or [None] * len(standard_apis)
        cls._standard_apis = [cls(api_str, api_doc)
                              for api_str, api_doc in
                              zip(cls._standard_api_strings, cls._standard_api_description)]

    @classmethod
    def get_standard_apis(cls) -> Sequence['API']:
        """
        获取标准API列表

        Returns: List[API]
        """
        if not cls._standard_apis:
            cls._standard_apis = [cls(api_str, api_doc)
                                  for api_str, api_doc in
                                  zip(cls._standard_api_strings, cls._standard_api_description)]
        return cls._standard_apis

    @property
    def is_standard(self, with_args: bool = False) -> bool:
        """
        判断API是否为标准API

        Args:
            with_args: 判断时是否考虑参数，默认为False

        Returns: bool
        """
        if not with_args:
            return any(self.fullname == api.fullname for api in self.get_standard_apis())
        else:
            return any(self.fullname == api.fullname and self.args == api.args
                       for api in self.get_standard_apis())

    def get_possible_standard_apis(self, matched_ps: int = 1, first: bool = False) -> List['API']:
        """
        获取可能的标准API列表，便于后期指标计算

        Args:
            matched_ps: 匹配阈值，>=1，即只有除方法名外的至少一个部分完全匹配，才可认为为同一API
            first: 是否只返回第一个匹配的API，默认为False

        Returns: List['API']

        Raises:
            ValueError: 当matched_ps小于1时抛出
            ValueError: 当当前API无效时抛出
        """
        if matched_ps < 1:
            raise ValueError('numbers of matched part must be greater than 1')
        if self.is_standard:
            return [self]
        if not (self.fullname and self.method):
            raise ValueError('API is not valid')
        p_apis = []
        for standard_api in API.get_standard_apis():
            # +1 表示方法名也要匹配
            if self.parts[::-1][:matched_ps+1] == standard_api.parts[::-1][:matched_ps+1]:
                p_apis.append(standard_api)
                if first:
                    break
        return p_apis

    def __eq__(self, other):
        if isinstance(other, API):
            return self.fullname == other.fullname and self.args == other.args
        return False

    def __hash__(self):
        args_tuple = tuple(self.args) if self.args is not None else ()
        return hash((self.fullname, args_tuple))

    def __repr__(self):
        return f"API({str(self)})"

    def __str__(self):
        r = f"{self.fullname}"
        if self.args is not None:
            r += f"({', '.join(self.args)})"
        return r

    def __len__(self):
        return len(self.parts)
