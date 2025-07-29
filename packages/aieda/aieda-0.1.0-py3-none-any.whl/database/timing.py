#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   timing.py
@Time    :   2024/10/10 10:28:18
@Author  :   Dawn Li 
@Version :   1.0
@Contact :   dawnli619215645@gmail.com
@Desc    :   Timing Feature from Timing Eval iEDA
'''


from dataclasses import dataclass


@dataclass
class FeatureTiming(object):
    WNS: float = None
    TNS: float = None
    suggest_freq: float = None
    dynamic_power: float = None
    static_power: float = None
