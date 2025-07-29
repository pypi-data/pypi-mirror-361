#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File : drc.py
@Author : yell
@Desc : drc database
'''

import sys
import os

from dataclasses import dataclass
from dataclasses import field
from typing import List


@dataclass
class DrcShape(object):
    llx: float = None
    lly: float = None
    urx: float = None
    ury: float = None
    net_ids: list = field(default_factory=list)
    inst_ids: list = field(default_factory=list)


@dataclass
class DrcLayer(object):
    layer: str = None
    number: int = None
    shapes: List[DrcShape] = field(default_factory=list)


@dataclass
class DrcDistribution(object):
    type: str = None
    number: int = None
    layers: List[DrcLayer] = field(default_factory=list)


@dataclass
class DrcDistributions(object):
    number: int = None
    drc_list: List[DrcDistribution] = field(default_factory=list)
