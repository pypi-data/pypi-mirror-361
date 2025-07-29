#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File : design.py
@Author : yell
@Desc : design database
'''

import sys
import os

from dataclasses import dataclass
from dataclasses import field

from numpy import uint64

from database.enum import CellType, OrientType, PlaceStatus, NetType

@dataclass     
class Design(object):
     """basic feature package"""
     instances : list = field(default_factory=list)
     nets : list = field(default_factory=list)
     
    
@dataclass     
class Instance(object):
    """instance structure"""
    name : str = ""
    master : str = ""
    type : CellType = CellType.none
    llx : int = 0
    lly : int = 0
    urx : int = 0
    ury : int = 0
    orient : OrientType = OrientType.none
    status : PlaceStatus = PlaceStatus.none
    pins : list = field(default_factory=list)
    
@dataclass     
class Pin(object):
    """pin structure"""
    name : str = ""
    instance : str = ""
    net : str = ""
    center_x : int = 0
    center_y : int = 0
    
@dataclass     
class Net(object):
    """net structure"""
    name : str = ""
    type : NetType = NetType.none
    pin_number : uint64 = None
    wire_len : uint64 = None
    segment_number : uint64 = None
    via_number : uint64 = None
    pins : list = field(default_factory=list)
    
class NetPin(object):
    """pin in net"""
    pin_name : str = ""
    instance_name : str = ""


