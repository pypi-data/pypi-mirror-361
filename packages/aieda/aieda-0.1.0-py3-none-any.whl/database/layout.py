#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File : layout.py
@Author : yell
@Desc : layout database
'''

import sys
import os

from dataclasses import dataclass
from dataclasses import field

from database.enum import TrackDirection, LayerType

@dataclass     
class Layout(object):
     """basic feature package"""
     top_name : str = ""
     dbu : int = 0
     die = None
     core = None
     rows = None
     tracks : list = field(default_factory=list)
    #  layers : list = field(default_factory=list)
     routing_layers : list = field(default_factory=list)
    #  cut_layers : list = field(default_factory=list)

@dataclass     
class Die(object):
    """die structure"""
    llx : int = 0
    lly : int = 0
    urx : int = 0
    ury : int = 0
    
@dataclass     
class Core(object):
    """core structure"""
    llx : int = 0
    lly : int = 0
    urx : int = 0
    ury : int = 0
    
@dataclass     
class Rows(object):
    """row structure"""
    num_rows : int = 0
    row_width : int = 0
    row_height : int = 0
    
class Track(object):
    """track structure"""
    layer : str = ""
    prefer_dir : TrackDirection = TrackDirection.none
    num : int = 0
    start : int = 0
    step : int = 0
    
class Layer(object):
    """layer structure"""
    name : str = ""
    type : LayerType = LayerType.none
    min_width : int = 0
    max_width : int = 0
    width : int = 0
    area : int = 0