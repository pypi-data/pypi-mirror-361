#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File : summary.py
@Author : yell
@Desc : drc database
'''

import sys
import os

from dataclasses import dataclass
from dataclasses import field
from typing import List
from numpy import double, uint, uint64

@dataclass
class StageSummary(object):
    stage: str = None
    die_usage : double = 0.0
    core_usage : double = 0.0
    num_instances : int = 0
    num_nets : int = 0
    num_pins : uint64 = None
    wire_len : double = None

@dataclass
class DesignSummary(object):
    design_name: str = None
    eda_tool : str = None
    die_area : double = 0.0
    core_area : double = 0.0
    num_iopins : int = 0
    num_iopad : int =0
    num_macros : int = 0
    num_layers : int = 0
    num_layers_routing : int = 0
    num_layers_cut : int = 0
    max_fanout : uint = None
    stage_list: List[StageSummary] = field(default_factory=list)
