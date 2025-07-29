#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File : layge_model.py
@Author : yell
@Desc : large model feature database
'''


from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


@dataclass
class LmNode:
    id: Optional[int] = None
    x: Optional[int] = None
    y: Optional[int] = None
    real_x: Optional[int] = None
    real_y: Optional[int] = None
    row: Optional[int] = None
    col: Optional[int] = None
    layer: Optional[int] = None
    pin_id: Optional[int] = None


@dataclass
class LmPath:
    node1: Optional[LmNode] = None
    node2: Optional[LmNode] = None


@dataclass
class LmWireFeature:
    wire_width: Optional[int] = None
    wire_len: Optional[int] = None
    drc_num: Optional[int] = None
    R: Optional[float] = None
    C: Optional[float] = None
    power: Optional[float] = None
    delay: Optional[float] = None
    slew: Optional[float] = None
    congestion: Optional[float] = None
    wire_density: Optional[float] = None
    drc_type: List[str] = field(default_factory=list)


@dataclass
class LmWire:
    id: Optional[int] = None
    feature: Optional[LmWireFeature] = None
    wire: Optional[LmPath] = None
    path_num: Optional[int] = None
    paths: List[LmPath] = field(default_factory=list)


@dataclass
class LmPin:
    id: Optional[int] = None
    pin_name: Optional[str] = None
    instance: Optional[str] = None
    is_driver: Optional[str] = None


@dataclass
class LmNetFeature:
    llx: Optional[int] = None
    lly: Optional[int] = None
    urx: Optional[int] = None
    ury: Optional[int] = None
    wire_len: Optional[int] = None
    via_num: Optional[int] = None
    drc_num: Optional[int] = None
    R: Optional[float] = None
    C: Optional[float] = None
    power: Optional[float] = None
    delay: Optional[float] = None
    slew: Optional[float] = None
    fanout: Optional[int] = None
    aspect_ratio: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    area: Optional[int] = None
    l_ness: Optional[float] = None
    drc_type: List[str] = field(default_factory=list)
    volume: Optional[int] = None
    layer_ratio: List[float] = field(default_factory=list)
    rsmt: Optional[int] = None


@dataclass
class LmNetRoutingPoint:
    x: int
    y: int
    layer_id: int

    def __str__(self):
        return f"({self.x}, {self.y}, {self.layer_id})"

    def __repr__(self):
        return f"Point({self.x}, {self.y}, {self.layer_id})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.layer_id == other.layer_id

    def __hash__(self):
        return hash((self.x, self.y, self.layer_id))


@dataclass
class LmNetRoutingVertex:
    id: int
    is_pin: bool
    is_driver_pin: bool
    point: LmNetRoutingPoint


@dataclass
class LmNetRoutingEdge:
    source_id: int
    target_id: int
    path: List[LmNetRoutingPoint]


@dataclass
class LmNetRoutingGraph:
    vertices: List[LmNetRoutingVertex]
    edges: List[LmNetRoutingEdge]


@dataclass
class LmNet:
    id: Optional[int] = None
    name: Optional[str] = None
    feature: Optional[LmNetFeature] = None
    pin_num: Optional[int] = None
    pins: List[LmPin] = field(default_factory=list)
    wire_num: Optional[int] = None
    wires: List[LmWire] = field(default_factory=list)
    routing_graph: Optional[LmNetRoutingGraph] = None


@dataclass
class LmPatchLayer:
    id: Optional[int] = None
    net_num: Optional[int] = None
    nets: List[LmNet] = field(default_factory=list)
    wire_width: Optional[int] = None
    wire_len: Optional[int] = None
    wire_density: Optional[float] = None
    congestion: Optional[float] = None


@dataclass
class LmPatch:
    id: Optional[int] = None
    patch_id_row: Optional[int] = None
    patch_id_col: Optional[int] = None
    llx: Optional[int] = None
    lly: Optional[int] = None
    urx: Optional[int] = None
    ury: Optional[int] = None
    row_min: Optional[int] = None
    row_max: Optional[int] = None
    col_min: Optional[int] = None
    col_max: Optional[int] = None
    patch_layer: List[LmPatchLayer] = field(default_factory=list)
    area: Optional[int] = None
    cell_density: Optional[float] = None
    pin_density: Optional[int] = None
    net_density: Optional[float] = None
    macro_margin: Optional[int] = None
    RUDY_congestion: Optional[float] = None
    EGR_congestion: Optional[float] = None
    timing_map: Optional[float] = None
    power_map: Optional[float] = None
    ir_drop_map: Optional[float] = None


@dataclass
class LmWirePatternPoint(object):
    x: int = None
    y: int = None
    z: int = None


@dataclass
class LmWirePatternDirection(Enum):
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    VIA = "VIA"


@dataclass
class LmWirePatternUnit:
    direction: LmWirePatternDirection = None
    length: int = None


@dataclass
class LmWirePatternSeq:
    name: str = None
    units: List[LmWirePatternUnit] = field(default_factory=list)


@dataclass
class LmNetSeq:
    loc_seq: List[LmWirePatternPoint] = field(default_factory=list)
    pattern_seq: List[LmWirePatternSeq] = field(default_factory=list)


@dataclass
class LmTimingWireGraphNode:
    name: str = None
    is_pin: bool = False
    is_port: bool = False


@dataclass
class LmTimingWireGraphEdge:
    from_node: int = None
    to_node: int = None


@dataclass
class LmTimingWireGraph(object):
    nodes: List[LmTimingWireGraphNode] = field(default_factory=list)
    edges: List[LmTimingWireGraphEdge] = field(default_factory=list)


@dataclass
class LmTimingWirePathGraph(object):
    nodes: List[LmTimingWireGraphNode] = field(default_factory=list)
    edges: List[LmTimingWireGraphEdge] = field(default_factory=list)
