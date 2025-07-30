#Anaconda/envs/netorchestr python
# -*- coding: utf-8 -*-
'''
module.py
=========

.. module:: psimplelink
  :platform: Windows
  :synopsis: 链路模块，用于实现简易链路相关的功能。

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

class PSimpleLink:
    def __init__(self,name:str='Link',delay:float=100.0) -> None:
        """链路模型初始化

        Args:
            name (str, optional): 链路名称. 默认值为'Link'.
            delay (float, optional): 链路时延设置，单位ms. 默认值为100.0.
        """
        self.name = name
        self.delay = delay
        