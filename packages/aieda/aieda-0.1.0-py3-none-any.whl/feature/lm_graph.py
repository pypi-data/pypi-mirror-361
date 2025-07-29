#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File : lm_graph.py
@Author : yell
@Desc : feature for large model
"""

from database.enum import EdaTool, FeatureOption, FlowStep
from workspace.path import WorkspacePath, LargeModelFeatureType
from flow.flow_db import DbFlow
from database.large_model import *
from utility.json_parser import JsonParser
from typing import List, Dict, Tuple, Any
from math import gcd
from collections import defaultdict
import pandas as pd
from tqdm import tqdm
import networkx as nx
import json
from dataclasses import asdict
import yaml
import orjson
import os
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import os


class LmGraph:
    """feature statis"""

    def __init__(self, dir_workspace: str, eda_tool: EdaTool):
        self.dir_workspace = dir_workspace
        self.eda_tool = eda_tool
        self.workspace = WorkspacePath(dir_workspace)

    def get_graph(self) -> List[LmNet]:
        flow = DbFlow(eda_tool=self.eda_tool, step=FlowStep.route)
        files = list(self._iter_json_files(self.workspace.get_feature_lm(
            flow=flow,
            feature_option=FeatureOption.large_model,
            lm_feature_type=LargeModelFeatureType.lm_nets,
        )))
        lm_nets = []
        for fp in tqdm(files, desc="Parsing nets batch file"):
            lm_nets.extend(self._parse_nets(fp))
        return lm_nets

        # ctx = mp.get_context('fork')
        # with ProcessPoolExecutor(max_workers=os.cpu_count(),
        #                          mp_context=ctx) as exe:
        #     lm_nets = list(tqdm(exe.map(self._parse_nets, files), total=len(files),
        #                         desc="Parsing nets batch file"))
        # return lm_nets

    @staticmethod
    def _iter_json_files(root: str):
        for ent in os.scandir(root):
            if ent.is_dir():
                yield from LmGraph._iter_json_files(ent.path)
            elif ent.name.endswith(".json"):
                yield ent.path

    def _parse_nets(self, batch_filepath: str) -> List[LmNet]:
        with open(batch_filepath, "rb") as f:
            lm_nets_metadata = orjson.loads(f.read())
        lm_nets = []
        for net_metadata in lm_nets_metadata:
            lm_net = self._parse_net(net_metadata)
            if lm_net:
                lm_nets.append(lm_net)
        return lm_nets

    def _parse_net(self, net_metadata: Dict[str, Any]) -> LmNet:
        lm_net = LmNet()
        lm_net.id = net_metadata.get("id")
        lm_net.name = net_metadata.get("name")

        # net feature
        net_feature = LmNetFeature()
        feature_data = net_metadata.get('feature', {})
        net_feature.llx = feature_data.get('llx')
        net_feature.lly = feature_data.get('lly')
        net_feature.urx = feature_data.get('urx')
        net_feature.ury = feature_data.get('ury')
        net_feature.wire_len = feature_data.get('wire_len')
        net_feature.via_num = feature_data.get('via_num')
        net_feature.drc_num = feature_data.get('drc_num')
        net_feature.R = feature_data.get('R')
        net_feature.C = feature_data.get('C')
        net_feature.power = feature_data.get('power')
        net_feature.delay = feature_data.get('delay')
        net_feature.slew = feature_data.get('slew')
        net_feature.fanout = feature_data.get('fanout')

        if 'aspect_ratio' in feature_data:
            net_feature.aspect_ratio = feature_data.get('aspect_ratio')
            net_feature.width = feature_data.get('width')
            net_feature.height = feature_data.get('height')
            net_feature.area = feature_data.get('area')
            net_feature.l_ness = feature_data.get('l_ness')
            net_feature.drc_type = feature_data.get('drc_type')
            net_feature.volume = feature_data.get('volume')
            net_feature.layer_ratio = feature_data.get('layer_ratio')
            net_feature.rsmt = feature_data.get('rsmt')

        lm_net.feature = net_feature

        # pins
        lm_net.pin_num = net_metadata.get("pin_num", 0)
        json_pins = net_metadata.get("pins", [])
        for json_pin in json_pins:
            lm_pin = LmPin()
            lm_pin.id = json_pin.get("id")
            lm_pin.instance = json_pin.get("i")
            lm_pin.pin_name = json_pin.get("p")
            lm_pin.is_driver = json_pin.get("driver")

            lm_net.pins.append(lm_pin)

        # wires
        lm_net.wire_num = net_metadata.get("wire_num", 0)
        json_wires = net_metadata.get("wires", [])
        for json_wire in json_wires:
            lm_wire = LmWire()
            lm_wire.id = json_wire.get("id")

            # wire feature
            wire_feature = LmWireFeature()
            wire_feature_data = json_wire.get("feature", {})
            wire_feature.wire_width = wire_feature_data.get("wire_width")
            wire_feature.wire_len = wire_feature_data.get("wire_len")
            wire_feature.drc_num = wire_feature_data.get("drc_num")
            wire_feature.R = wire_feature_data.get("R")
            wire_feature.C = wire_feature_data.get("C")
            wire_feature.power = wire_feature_data.get("power")
            wire_feature.delay = wire_feature_data.get("delay")
            wire_feature.slew = wire_feature_data.get("slew")
            wire_feature.congestion = wire_feature_data.get("congestion")
            wire_feature.wire_density = wire_feature_data.get(
                "wire_density")
            wire_feature.drc_type = wire_feature_data.get("drc_type")

            lm_wire.feature = wire_feature

            # wire connections
            wire_data = json_wire.get("wire", {})
            wire_connections = LmPath()

            lm_node1 = LmNode()
            lm_node1.id = wire_data.get("id1")
            lm_node1.x = wire_data.get("x1")
            lm_node1.y = wire_data.get("y1")
            lm_node1.real_x = wire_data.get("real_x1")
            lm_node1.real_y = wire_data.get("real_y1")
            lm_node1.row = wire_data.get("r1")
            lm_node1.col = wire_data.get("c1")
            lm_node1.layer = wire_data.get("l1")
            lm_node1.pin_id = wire_data.get("p1")
            wire_connections.node1 = lm_node1

            lm_node2 = LmNode()
            lm_node2.id = wire_data.get("id2")
            lm_node2.x = wire_data.get("x2")
            lm_node2.y = wire_data.get("y2")
            lm_node2.real_x = wire_data.get("real_x2")
            lm_node2.real_y = wire_data.get("real_y2")
            lm_node2.row = wire_data.get("r2")
            lm_node2.col = wire_data.get("c2")
            lm_node2.layer = wire_data.get("l2")
            lm_node2.pin_id = wire_data.get("p2")
            wire_connections.node2 = lm_node2

            lm_wire.wire = wire_connections

            # path
            lm_wire.path_num = json_wire.get("path_num", 0)
            json_paths = json_wire.get("paths", [])
            for json_path in json_paths:
                wire_path = LmPath()

                lm_path_node1 = LmNode()
                lm_path_node1.id = json_path.get("id1")
                lm_path_node1.x = json_path.get("x1")
                lm_path_node1.y = json_path.get("y1")
                lm_path_node1.real_x = json_path.get("real_x1")
                lm_path_node1.real_y = json_path.get("real_y1")
                lm_path_node1.row = json_path.get("r1")
                lm_path_node1.col = json_path.get("c1")
                lm_path_node1.layer = json_path.get("l1")
                wire_path.node1 = lm_path_node1

                lm_path_node2 = LmNode()
                lm_path_node2.id = json_path.get("id2")
                lm_path_node2.x = json_path.get("x2")
                lm_path_node2.y = json_path.get("y2")
                lm_path_node2.real_x = json_path.get("real_x2")
                lm_path_node2.real_y = json_path.get("real_y2")
                lm_path_node2.row = json_path.get("r2")
                lm_path_node2.col = json_path.get("c2")
                lm_path_node2.layer = json_path.get("l2")
                wire_path.node2 = lm_path_node2

                lm_wire.paths.append(wire_path)

            lm_net.wires.append(lm_wire)

        # routing graph
        routing_graph_data = net_metadata.get("routing_graph", {})
        vertices = []
        for v in routing_graph_data.get("vertices", []):
            point = LmNetRoutingPoint(
                x=v["x"],
                y=v["y"],
                layer_id=v["layer_id"]
            )
            vertex = LmNetRoutingVertex(
                id=v["id"],
                is_pin=v["is_pin"],
                is_driver_pin=v["is_driver_pin"],
                point=point
            )
            vertices.append(vertex)

        edges = []
        for e in routing_graph_data.get("edges", []):
            path = [LmNetRoutingPoint(**p) for p in e["path"]]
            edge = LmNetRoutingEdge(source_id=e["source_id"],
                                    target_id=e["target_id"], path=path)
            edges.append(edge)
        routing_graph = LmNetRoutingGraph(vertices=vertices, edges=edges)
        lm_net.routing_graph = routing_graph

        return lm_net


class LmWirePatternGen:
    def __init__(self, epsilon: int = 1):
        self._epsilon = epsilon
        self._patterns: Dict[str, LmWirePatternSeq] = {}
        self._pattern_count: Dict[str, int] = defaultdict(int)

    def pattern_summary(self, csv_path: str = None) -> pd.DataFrame:
        df = pd.DataFrame(self._pattern_count.items(),
                          columns=["Pattern", "Count"])
        df.sort_values(by="Count", ascending=False,
                       inplace=True, ignore_index=True)
        if csv_path:
            df.to_csv(csv_path, index=False)
        return df

    def add_wire(self, wire: LmWire) -> LmWirePatternSeq:
        pattern = self.gen_pattern(wire)
        self.add_pattern(pattern)
        return pattern

    def add_pattern(self, pattern: LmWirePatternSeq):
        if pattern.name in self._pattern_count:
            self._pattern_count[pattern.name] += 1
        else:
            self._patterns[pattern.name] = pattern
            self._pattern_count[pattern.name] = 1

    def gen_pattern(self, wire: LmWire) -> LmWirePatternSeq:
        point_list = self._get_point_list(wire)
        pattern = self._calc_pattern(point_list)
        return pattern

    def _get_point_list(self, wire: LmWire) -> List[LmWirePatternPoint]:
        paths = wire.paths
        points = [
            LmWirePatternPoint(path.node1.x, path.node1.y, path.node1.layer)
            for path in paths
        ]
        end = LmWirePatternPoint(
            paths[-1].node2.x, paths[-1].node2.y, paths[-1].node2.layer
        )
        points.append(end)
        return points

    def _calc_pattern(self, points: List[LmWirePatternPoint]) -> LmWirePatternSeq:
        sorted_points = points[:]
        if sorted_points[0].x > sorted_points[-1].x or (
            sorted_points[0].x == sorted_points[-1].x
            and sorted_points[0].y > sorted_points[-1].y
        ):
            sorted_points.reverse()

        pattern = LmWirePatternSeq()
        for i in range(len(sorted_points) - 1):
            start = sorted_points[i]
            end = sorted_points[i + 1]
            x_same = start.x == end.x
            y_same = start.y == end.y
            z_same = start.z == end.z
            if x_same and y_same and z_same:
                continue

            if x_same and y_same:
                direction = LmWirePatternDirection.VIA
                length = 1
            elif x_same:
                direction = (
                    LmWirePatternDirection.TOP
                    if start.y < end.y
                    else LmWirePatternDirection.BOTTOM
                )
                length = abs(start.y - end.y)
            else:
                direction = (
                    LmWirePatternDirection.RIGHT
                    if start.x < end.x
                    else LmWirePatternDirection.LEFT
                )
                length = abs(start.x - end.x)

            pattern.units.append(LmWirePatternUnit(direction, length))

        if not pattern.units:
            return pattern

        max_common_factor = pattern.units[0].length
        for unit in pattern.units:
            max_common_factor = gcd(max_common_factor, unit.length)

        for unit in pattern.units:
            unit.length //= max_common_factor

        pattern_name = ""
        for unit in pattern.units:
            direction = unit.direction.name[0]
            normalized_length = unit.length // self._epsilon + 1
            pattern_name += f"{direction}{normalized_length}"

        pattern.name = pattern_name
        return pattern


class LmNetsPatternsGen:
    def __init__(self, epsilon: int = 1):
        self._gen = LmWirePatternGen(epsilon=epsilon)

    def gen(self, lm_nets: List[LmNet]):
        for lm_net in tqdm(lm_nets):
            wires = lm_net.wires
            for wire in wires:
                self._gen.add_wire(wire)

    def summary(self, csv_path: str = None):
        return self._gen.pattern_summary(csv_path)


class LmNetSeqConverter:
    def __init__(self, epsilon: int = 1):
        self._gen = LmWirePatternGen(epsilon=epsilon)
        self._seqs = []

    def build_seqs(self, lm_nets: List[LmNet]) -> List[LmNetSeq]:
        for lm_net in lm_nets:
            graph = self._convert(lm_net)
            seqs = self._convert_to_seq(graph)
            self._seqs.extend(seqs)
        return self._seqs

    def save_seqs(self, json_path: str):
        with open(json_path, "w") as f:
            json.dump(self._seqs, f, default=asdict)

    def load_seqs(self, json_path: str) -> List[LmNetSeq]:
        with open(json_path, "r") as f:
            self._seqs = json.load(f)
        return self._seqs

    def _convert(self, lm_net: LmNet) -> nx.Graph:
        # edge with pattern
        graph = nx.Graph()
        wires = lm_net.wires
        for wire in wires:
            wire: LmWire
            start = wire.wire.node1
            end = wire.wire.node2

            pattern = self._gen.add_wire(wire)
            pattern_name = pattern.name
            if start.id not in graph:
                graph.add_node(start.id, pos=(start.x, start.y, start.layer))
            if end.id not in graph:
                graph.add_node(end.id, pos=(end.x, end.y, end.layer))
            graph.add_edge(start.id, end.id, pattern=pattern_name)

        return graph

    def _convert_to_seq(self, net_graph: nx.Graph) -> List[LmNetSeq]:
        seqs = []
        source = 0
        for node in net_graph.nodes:
            if net_graph.degree(node) == 1:
                source = node
                break
        targets = []
        for node in net_graph.nodes:
            if net_graph.degree(node) == 1 and node != source:
                targets.append(node)
        for target in targets:
            loc_seq = []
            pattern_seq = []
            path = nx.shortest_path(net_graph, source, target)
            for vertex in path:
                pos = net_graph.nodes[vertex]["pos"]
                loc_seq.append(LmWirePatternPoint(pos[0], pos[1], pos[2]))
            for i in range(1, len(path)):
                pattern = net_graph[path[i - 1]][path[i]]["pattern"]
                pattern_seq.append(pattern)
            seq = LmNetSeq(loc_seq, pattern_seq)
            seqs.append(seq)
        return seqs


class LmTimingGraphSeqConverter:
    def __init__(self, epsilon: int = 1):
        self._gen = LmWirePatternGen(epsilon=epsilon)
        self._seqs = []

    def convert(self, timing_wire_graph, lm_nets: List[LmNet]) -> nx.Graph:
        nodes = timing_wire_graph.nodes
        edges = timing_wire_graph.edges
        graph = nx.Graph()
        # build nodes
        for node in nodes:
            graph.add_node(node.name, is_pin=node.is_pin, is_port=node.is_port)
        # build edges
        wire_map = self._build_wire_map(lm_nets)
        for edge in edges:
            from_node = nodes[edge.from_node]
            to_node = nodes[edge.to_node]
            key = (
                (int)(from_node.name.split(":")[1]),
                (int)(to_node.name.split(":")[1]),
            )
            pattern = "" if key not in wire_map else self._gen.add_wire(
                wire_map[key])
            graph.add_edge(
                from_node.name,
                to_node.name,
                feature_R=edge.feature_R,
                feature_C=edge.feature_C,
                feature_from_slew=edge.feature_from_slew,
                feature_to_slew=edge.feature_to_slew,
                is_net_edge=edge.is_net_edge,
                pattern=pattern,
            )
        return graph

    def convert_to_seq(self, graph: nx.Graph) -> List[LmNetSeq]:
        seqs = []
        pass

    def _build_wire_map(self, lm_nets: List[LmNet]) -> Dict[Tuple[int, int], LmWire]:
        wire_map = {}
        for lm_net in lm_nets:
            wires = lm_net.wires
            for wire in wires:
                wire: LmWire
                start = wire.wire.node1.id
                end = wire.wire.node2.id
                wire_map[(start, end)] = wire
                wire_map[(end, start)] = wire
        return wire_map


class LmTimingWireGraphBuilder:
    """The parser for LM wire timing graph."""

    def __init__(self, dir_workspace: str, eda_tool: EdaTool):
        self.dir_workspace = dir_workspace
        self.eda_tool = eda_tool
        self.workspace = WorkspacePath(dir_workspace)

    def get_wire_graph(self) -> LmTimingWireGraph:

        flow = DbFlow(eda_tool=self.eda_tool, step=FlowStep.route)
        feature_dir = self.workspace.get_feature_lm(
            flow=flow,
            feature_option=FeatureOption.large_model,
            lm_feature_type=LargeModelFeatureType.lm_wire_graph,
        )

        yaml_path = feature_dir + "timing_wire_graph.yaml"

        if not os.path.exists(yaml_path):
            return None

        with open(yaml_path, "r") as file:
            print("load wire graph yaml start")
            wire_nodes = []
            wire_edges = []

            # not use yaml module
            # wire_graph_data = yaml.safe_load(file)
            # print("load wire graph yaml end")
            # # wire graph
            # for item_name, item in wire_graph_data.items():
            #     if "node" in item_name:
            #         wire_node = LmTimingWireGraphNode(item["name"], item["is_pin"], item["is_port"])
            #         wire_nodes.append(wire_node)

            #     if "edge" in item_name:
            #         from_index = item["from_node"]
            #         to_index = item["to_node"]
            #         wire_edge = LmTimingWireGraphEdge(from_index, to_index)
            #         wire_edges.append(wire_edge)

            wire_node = None
            wire_edge = None
            edge_set = set()
            for _, line in tqdm(
                enumerate(file), desc="Processing load wire graph yaml"
            ):
                line = line.strip()
                if line.startswith("node_"):
                    if wire_node is not None:
                        wire_nodes.append(wire_node)
                        wire_node = None
                elif line.startswith("edge_"):
                    # add last node
                    if wire_node is not None:
                        wire_nodes.append(wire_node)
                        wire_node = None

                    if wire_edge is not None:
                        if not (wire_edge.from_node, wire_edge.to_node) in edge_set:
                            wire_edges.append(wire_edge)
                            edge_set.add(
                                (wire_edge.from_node, wire_edge.to_node))
                        wire_edge = None
                else:
                    # Split at the first colon only
                    key, value = line.split(":", 1)
                    if key == "name":
                        wire_node = LmTimingWireGraphNode(
                            value.strip(), False, False)
                    elif key == "is_pin":
                        wire_node.is_pin = True if int(
                            value.strip()) == 1 else False
                    elif key == "is_port":
                        wire_node.is_port = True if int(
                            value.strip()) == 1 else False
                    elif key == "from_node":
                        wire_edge = LmTimingWireGraphEdge(
                            int(value.strip()), None)
                    elif key == "to_node":
                        wire_edge.to_node = int(value.strip())

            # add last edge
            wire_edges.append(wire_edge)
            wire_timing_graph = LmTimingWireGraph(wire_nodes, wire_edges)

            print("load wire graph yaml end")
            print("wire graph nodes num: ", len(wire_nodes))
            print("wire graph edges num: ", len(wire_edges))
            return wire_timing_graph

        return None
