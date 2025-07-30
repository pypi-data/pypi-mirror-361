#Anaconda/envs/netorchestr python
# -*- coding: utf-8 -*-
'''
psimplemodule.py
===============

.. module:: psimplemodule
  :platform: Windows
  :synopsis: 简单模块，完成离散事件仿真模块收发处理的基本功能。

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

from __future__ import annotations

import simpy
from typing import Tuple

from netorchestr.eventlog import Logger

from netorchestr.envir.psimplelink import PSimpleLink
from netorchestr.envir.psimplemessage import PSimpleMessage
from netorchestr.envir.psimplegate import PSimpleGate

class PSimpleModule:
    def __init__(self, name:str):
        """模块定义

        Args:
            name (str): 自定义模块名称
            schedule (Schedule): 模块预约行为所需的事件调度器对象
            logger (Logger, optional): 模块日志记录器对象
        """
        
        self.name = name
        """模块名称"""
        
        self.gates:dict[PSimpleGate,Tuple[PSimpleLink, PSimpleGate]] = {}
        """模块的门 'PSimpleGate' 与对应的链路模型 'PSimpleLink' 和所连接的门 'PSimpleGate' 的映射表"""
                   
        
    def _activate(self, schedule:simpy.Environment, logger:Logger):
        """激活模块
        
        """
        self.scheduler:simpy.Environment = schedule
        """模块的事件调度器"""
        
        self.logger:Logger = logger
        """模块的日志记录器"""
        
        self.req_processor = simpy.Resource(self.scheduler, capacity=1) 
        """simpy 资源处理器"""
        
        self.req2msg:dict[simpy.Resource:PSimpleMessage] = {}
        """simpy 资源请求-消息映射表"""
        
        for gate in self.gates:
            gate._activate(self.scheduler)
        
        self.scheduler.process(self.__init())
        self.scheduler.process(self.__run())
    
    
    def __init(self):
        """模块初始化
        
        """
        yield self.scheduler.timeout(0)
        self.initialize()
        

    def initialize(self):
        """模块初始化
        
        """
        pass
        
        
    def send_msg(self, msg:PSimpleMessage, gate_name:str):
        """发送消息
        
        """
        out_gate = None
        for gate in self.gates:
            if gate.name == gate_name:
                out_gate = gate
                break
        if out_gate is None:
            self.logger.error(f"{self.scheduler.now}: Module '{self.name}' does not have outgate named '{gate_name}'")
            return
        
        
        aim_link:PSimpleLink = self.gates[out_gate][0]
        aim_gate:PSimpleGate = self.gates[out_gate][1]
        aim_module:PSimpleModule = aim_gate.ofModule

        self.logger.debug(f"{self.scheduler.now}: Module '{self.name}' sends message '{msg.id}' to module '{aim_module.name}' via outgate '{gate_name}' and link '{aim_link.name}'")
        
        self.scheduler.process(self.__deliver_msg(msg, aim_link.delay, aim_gate))
        
    def __deliver_msg(self, message, delay, aim_gate:PSimpleGate):
        """私有方法：在传播时延之后将消息放入目标模块的门的消息缓存区
        
        """
        yield self.scheduler.timeout(delay)
        aim_gate.msg_buffer.put(message)

    def recv_msg(self, msg:PSimpleMessage, gate:PSimpleGate):
        raise NotImplementedError("recv_msg() method should be implemented by subclass")
    
    def __run(self):
        """节点的主循环，处理消息接收和响应"""
        while True:
            gate_to_event: dict[PSimpleGate, simpy.Event] = {
                gate: gate.msg_buffer.get() for gate in self.gates
            }
            
            gate_event = yield self.scheduler.any_of(gate_to_event.values())
            
            for gate, event in gate_to_event.items():
                if event in gate_event:
                    message = event.value  # 获取消息
                    self.logger.debug(f"{self.scheduler.now}: Module '{self.name}' receives message '{message.id}' from module '{gate.ofModule.name}' via ingate '{gate.name}'")
                    self.recv_msg(message, gate)
                    break
            

            
            
