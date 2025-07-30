#Anaconda/envs/netorchestr python
# -*- coding: utf-8 -*-
'''
psimplegate.py
=========

.. module:: psimplegate
  :platform: Windows
  :synopsis: 简单门模块，用于实现链路与模块之间的通信功能。

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

import simpy


class PSimpleGate():
    """简单门类，用于实现链路与模块之间的通信功能。"""

    def __init__(self, name: str, ofModule):
        """初始化简单门对象

        Args:
            name (str): 门名称
            scheduler (simpy.Environment): simpy 事件调度对象
        """
        
        self.name = name
        """门名称"""
        
        self.ofModule = ofModule
        """所属模块对象"""
        
        
    def _activate(self, scheduler: simpy.Environment):
        """使用 simpy 事件调度器激活门"""
        
        self.scheduler = scheduler
        """simpy 事件调度对象"""
        
        self.msg_buffer = simpy.Store(self.scheduler)
        """消息缓冲区"""
        

    def put(self, msg):
        """向门内缓冲区放入消息

        Args:
            msg (_type_): _description_
        """
        
        self.msg_buffer.put(msg)
        


