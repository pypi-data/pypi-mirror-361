#Anaconda/envs/netorchestr python
# -*- coding: utf-8 -*-
'''
psimplemessage.py
================

.. module:: psimplemessage
  :platform: Windows
  :synopsis: 消息模块，用于离散事件仿真中各模块之间传输消息的实体。

.. moduleauthor:: WangXi

简介
----

该模块实现了***的功能，主要用于***应用程序中。它提供了以下特性：

- 使用***组件呈现***
- 支持基本***控制操作（如***、***、***等）。

版本
----

- 版本 1.0 (2025/07/11): 初始版本

'''

import sys
from dataclasses import dataclass, asdict

@dataclass
class PSimpleMessage:
    '''
    消息类，用于消息的发送和接收。
    '''
    timestamp: float
    sender: str
    receiver: str
    content: str
    id: str
    
    def __len__(self) -> int:
        """
        获取对象占用的内存空间大小（包括所有字段）

        Returns:
            int: 消息对象占用的总内存空间大小（字节）
        """
        
        # 对象自身的内存占用
        size = sys.getsizeof(self)
        
        # 获取所有字段的值并计算它们的内存占用
        for value in asdict(self).values():
            # 基本类型（如float、str）的内存占用
            size += sys.getsizeof(value)
            
            # 如果是容器类型（如list、dict），递归计算其元素的内存占用
            if isinstance(value, list):
                for item in value:
                    size += sys.getsizeof(item)
            elif isinstance(value, dict):
                for k, v in value.items():
                    size += sys.getsizeof(k) + sys.getsizeof(v)
        
        return size



