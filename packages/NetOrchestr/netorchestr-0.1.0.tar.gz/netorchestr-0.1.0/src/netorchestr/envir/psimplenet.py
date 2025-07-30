#Anaconda/envs/netorchestr python
# -*- coding: utf-8 -*-
'''
psimplenet.py
=========

.. module:: psimplenet
  :platform: Windows
  :synopsis: ***模块，用于***功能。

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

from netorchestr.envir.psimplemodule import PSimpleModule
from netorchestr.envir.psimplelink import PSimpleLink
from netorchestr.eventlog import Logger

class PSimpleNet:
    def __init__(self, name:str):
        self.name = name
        self.scheduler = simpy.Environment()
        self.logger = Logger(name=name)
        
        self.modules:list[PSimpleModule] = []
        self.links:list[PSimpleLink] = []

    def add_module(self, module:PSimpleModule):
        self.modules.append(module)
    
    def run(self,until:int):
        for module in self.modules:
            module._activate(self.scheduler, self.logger)
            
            for gate in module.gates:
                self.links.append(module.gates[gate][0])
                
        self.scheduler.run(until=until)



