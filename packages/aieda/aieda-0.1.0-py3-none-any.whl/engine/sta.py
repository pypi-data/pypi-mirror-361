#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : sta.py
@Author : yell
@Desc : STA framework
'''
from engine.base import EngineBase
from database.enum import EdaTool
from flow.flow_db import DbFlow
from tools.iEDA.module.sta import IEDASta
from database.enum import FlowStep, EdaTool
from tools.innovus.module.sta import InnovusSTA
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class StaRCNode:
    """RC Tree Node"""
    coord_x : int
    coord_y : int
    layer : int
    
    node_id : int

    def __repr__(self):
        return f"StaRCNode(coord_x={self.coord_x}, coord_y={self.coord_y}, layer={self.layer})"

@dataclass(frozen=True)
class StaRCObjNode(StaRCNode):
    """RC Tree Object Node"""
    obj_node : str

@dataclass(frozen=True)
class StaRCEdge:
    """RC Tree Edge"""
    src_node : StaRCNode
    dst_node : StaRCNode

from dataclasses import dataclass, field

@dataclass    
class StaRCTree:
    """RC Tree"""
    nodes: set = field(default_factory=set)
    edges: list = field(default_factory=list)
    driver_node: Optional[StaRCObjNode] = None
    load_nodes: list = field(default_factory=list)
    
    def get_node_id(self, node):
        for i, n in enumerate(self.nodes):
            if n == node:
                return i
    def draw(self, filename=None):
        import matplotlib.pyplot as plt
        import networkx as nx

        G = nx.DiGraph()
        pos = {}

        # Add nodes
        for node in self.nodes:
            pos[node] = (node.coord_x, node.coord_y)
            G.add_node(node)

        # Add edges
        for edge in self.edges:
            G.add_edge(edge.src_node, edge.dst_node)

        # Draw all nodes
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=300)
        # Draw edges
        nx.draw_networkx_edges(G, pos, arrows=True)

        # Highlight driver node in red
        if self.driver_node and self.driver_node in G.nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=[self.driver_node], node_color='red', node_size=400)

        # Highlight load nodes in red
        load_nodes_in_graph = [n for n in self.load_nodes if n in G.nodes]
        if load_nodes_in_graph:
            nx.draw_networkx_nodes(G, pos, nodelist=load_nodes_in_graph, node_color='red', node_size=400)

        # Draw labels
        labels = {node: str(node) for node in G.nodes}
        nx.draw_networkx_labels(G, pos, labels, font_size=8)

        plt.axis('off')
        if filename:
            plt.savefig(filename, bbox_inches='tight')
        else:
            plt.show()
        plt.close()
        
    def graphviz_draw(self, filename=None):
        import graphviz
        dot = graphviz.Digraph(format='png')

        # Add nodes
        for node in self.nodes:
            label = str(node)
            if node == self.driver_node:
                dot.node(str(id(node)), label, color='red', style='filled', fillcolor='red')
            elif node in self.load_nodes:
                dot.node(str(id(node)), label, color='red', style='filled', fillcolor='red')
            else:
                dot.node(str(id(node)), label)

        # Add edges
        for index, edge in enumerate(self.edges):
            dot.edge(str(id(edge.src_node)), str(id(edge.dst_node)))
            
        with open("graphviz_output.dot", "w", encoding="utf-8") as f:
            f.write(dot.source)

        if filename:
            dot.render(filename, view=False, cleanup=True)
        else:
            from IPython.display import display
            display(dot)

@dataclass 
class StaDesignRCTree:
    """Design RC Tree"""
    rc_trees = {}

class EngineSTA(EngineBase):
    """STA framework"""      
    def run(self):
        return super().run()

    def run_ieda(self):
        # run iEDA
        run_flow = IEDASta(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog)
        run_flow.run_sta()

        return self.get_result()

    def init_sta(self):
        """init sta"""
        sta_engine = IEDASta(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog)
        sta_engine.init_sta()

    def make_rc_tree(self, timing_json_file: str) -> StaDesignRCTree:
        import json

        design_rc_tree = StaDesignRCTree()

        with open(timing_json_file, 'r', encoding='utf-8') as f:
            for line in f:                
                data = json.loads(line)
                driver = data['driver']
                if driver not in design_rc_tree.rc_trees:
                    design_rc_tree.rc_trees[driver] = StaRCTree()
                else:
                    print("find exist driver %s" % driver)

                one_rc_tree = design_rc_tree.rc_trees[driver]

                load = data['load']
                points = data['points']                

                driver_node = StaRCObjNode(points[0][0], points[0][1], points[0][2], len(one_rc_tree.nodes), driver)
                if driver_node not in one_rc_tree.nodes:
                    one_rc_tree.driver_node = driver_node
                    one_rc_tree.nodes.add(one_rc_tree.driver_node)

                load_node = StaRCObjNode(points[-1][0], points[-1][1], points[-1][2], len(one_rc_tree.nodes), load)
                if load_node not in one_rc_tree.nodes:
                    one_rc_tree.load_nodes.append(load_node)
                    one_rc_tree.nodes.add(load_node)
                else:
                    continue

                previous_node = None
                for point in points:
                    if point == points[0]:
                        previous_node = one_rc_tree.driver_node
                        continue

                    if point == points[-1]:
                        if previous_node:
                            one_rc_tree.edges.append(StaRCEdge(previous_node, one_rc_tree.load_nodes[-1]))
                        continue

                    one_point_node = StaRCNode(point[0], point[1], point[2], len(one_rc_tree.nodes))
                    if one_point_node not in one_rc_tree.nodes:
                        one_rc_tree.nodes.add(one_point_node)
                        if previous_node:
                            one_rc_tree.edges.append(StaRCEdge(previous_node, one_point_node))

                        previous_node = one_point_node
                    else:
                        print("point node already exists %s" % one_point_node)
                        for point_node in one_rc_tree.nodes:
                            if hash(one_point_node) == hash(point_node):
                                previous_node = point_node

            print("build rc tree done.")

        return design_rc_tree

    def init_sta_one_rc(self, one_net_rc_tree: StaRCTree):
        sta_engine = IEDASta(dir_workspace = self.dir_workspace,
                        input_def = self.input_def, 
                        output_def = self.output_def, 
                        output_verilog = self.output_verilog)

        driver_node = one_net_rc_tree.driver_node
        if driver_node is not None:
            driver_name = driver_node.obj_node
        else:
            driver_name = None
            raise Exception("Driver node not found")

        net_name = sta_engine.get_net_name(driver_name)
        net_segment_edge = one_net_rc_tree.edges
        for edge in net_segment_edge:
            edge_src_node = edge.src_node
            edge_dst_node = edge.dst_node
            
            src_node_id = edge_src_node.node_id
            snk_node_id = edge_dst_node.node_id

            if edge_src_node.layer == edge_dst_node.layer:
                layer_id = (int)(edge_src_node.layer / 2) + 2  # layer id TBD
                dbu = 2000.0 # hard code dbu
                segment_length = abs(
                    edge_dst_node.coord_x - edge_src_node.coord_x
                ) + abs(edge_dst_node.coord_y - edge_src_node.coord_y)
                
                segment_length = segment_length / dbu

                edge_resistance = sta_engine.get_net_segment_resistance(
                    layer_id, segment_length
                )
                edge_capacitance = sta_engine.get_net_segment_capacitance(
                    layer_id, segment_length
                )
            else:
                # via tbd
                edge_capacitance = 0.001
                edge_resistance = 5
            
            if isinstance(edge_src_node, StaRCObjNode):
                src_rc_node_name = sta_engine.make_rc_tree_obj_node(
                    edge_src_node.obj_node, edge_capacitance / 2
                )

            else:
                src_rc_node_name = sta_engine.make_rc_tree_inner_node(
                    net_name, src_node_id, edge_capacitance / 2
                )
                
            if isinstance(edge_dst_node, StaRCObjNode):
                dst_rc_node_name = sta_engine.make_rc_tree_obj_node(
                    edge_dst_node.obj_node, edge_capacitance / 2
                )
            else:
                dst_rc_node_name = sta_engine.make_rc_tree_inner_node(
                    net_name, snk_node_id, edge_capacitance / 2
                )
                
            sta_engine.make_rc_tree_edge(
                    net_name, src_rc_node_name, dst_rc_node_name, edge_resistance
                )
        sta_engine.update_rc_tree_info(net_name)
        
    def init_sta_rc(self, design_rc_tree: StaDesignRCTree):
        for one_net_rc_tree in design_rc_tree.rc_trees.values():
            self.init_sta_one_rc(one_net_rc_tree)
        
    def update_and_report_sta(self):
        sta_engine = IEDASta(dir_workspace = self.dir_workspace,
                        input_def = self.input_def, 
                        output_def = self.output_def, 
                        output_verilog = self.output_verilog)
        
        sta_engine.update_timing()
        sta_engine.report_sta()
        return sta_engine.get_wire_timing_data()

    def run_innovus(self):
        if(self.step == None):
            self.step = DbFlow(eda_tool=EdaTool.INNOVUS,
                          pre_flow=self.pre_step,
                          step=FlowStep.sta)

        self.build_path()

        # run innovus
        run_flow = InnovusSTA(dir_workspace = self.dir_workspace,
                               dir_resource = self.dir_resource,
                              input_def = self.input_def, 
                              input_verilog = self.input_verilog,
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog,
                              pre_step = self.pre_step,
                              step = self.step,
                              task = self.task)
        run_flow.run_sta()

        return self.get_result()

    def refine_libs(self):
        run_flow = IEDASta(dir_workspace = self.dir_workspace,
                              input_def = self.input_def, 
                              output_def = self.output_def, 
                              output_verilog = self.output_verilog)

        libs = run_flow.get_used_lib()

        # refine
        self.workspace.reset_path_libs(libs)
        self.workspace.reset_path_ieda_libs(libs)
