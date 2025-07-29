#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : lm_path.py
@Time : 2025/01/20 15:04:36
@Author : simin tao
@Version : 1.0
@Contact : taosm@pcl.ac.cn, liuh0326@163.com
@Desc : 
'''
import yaml
import torch
import hashlib

from database.enum import EdaTool, FeatureOption, FlowStep
from workspace.path import WorkspacePath, LargeModelFeatureType
from database.large_model import LmTimingWireGraphNode, LmTimingWireGraphEdge, LmTimingWirePathGraph

class LmTimingWirePathGraphBuilder:
    def __init__(self, file_path, eda_tool: EdaTool = None, step = None):
        # for timing predict
        self.file_path = file_path
        self.data = None
        self.capacitance_list = []
        self.slew_list = []
        self.resistance_list = []
        self.incr_list = []
        
        # record path nodes
        self.nodes = []
        
        # for flow control
        self.eda_tool = eda_tool
        self.step = step

    def load_data(self):
        """Load YAML data from the file."""
        try:
            with open(self.file_path, 'r') as f:
                self.data = yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading file: {e}")

    def parse_data(self):
        """Parse nodes, net arcs, and instance arcs in order."""
        remove_parentheses_content = lambda s: s[:s.find('(')].strip() if s.find('(')!= -1 else s
        for key, value in self.data.items():
            if key.startswith("node_"):
                # Parse node
                self.capacitance_list.append(value.get("Capacitance", 0))
                self.slew_list.append(value.get("slew", 0))
                self.resistance_list.append(0)  # Default R value for nodes
                
                # record pin node
                node_name = value.get("Point", "")
                # remove instance cell name
                node_name = remove_parentheses_content(node_name)
                if not len(self.nodes) or node_name != self.nodes[-1]: 
                    self.nodes.append(node_name)
                    
            elif key.startswith("net_arc_"):
                self.incr_list.append(value.get("Incr", 0))
                for edge_key, edge_value in value.items():
                    if edge_key.startswith("edge_"):
                        self.capacitance_list.append(edge_value.get("wire_C", 0))
                        self.slew_list.append(edge_value.get("to_slew", 0))
                        self.resistance_list.append(edge_value.get("wire_R", 0))
                        
                        # record edge node
                        self.nodes.append(edge_value.get("wire_to_node", ""))
  
            elif key.startswith("inst_arc_"):
                self.incr_list.append(value.get("Incr", 0))


    def get_combined_tensor(self):
        """Combine all lists into a single 2D tensor with each list as a row."""
        combined_data = [
            self.capacitance_list,
            self.slew_list,
            self.resistance_list
        ]
        tensor = torch.tensor(combined_data, dtype=torch.float32)
        return tensor

    def get_incr_tensor(self):
        """Get the tensor of Incr values and calculate the sum."""
        incr_tensor = torch.tensor(self.incr_list, dtype=torch.float32)
        incr_sum = incr_tensor.sum().item()
        return incr_tensor, incr_sum

    @staticmethod
    def pad_tensors(tensor_list, max_length):
        """Pad all tensors in the list to the max length."""
        padded_tensors = []
        for tensor in tensor_list:
            padded = torch.nn.functional.pad(tensor, (0, max_length - tensor.size(1)), "constant", 0)
            padded_tensors.append(padded)
        return padded_tensors
    
    def generate_hash(self):
        """Generate a hash for the concatenated unique strings."""
        concatenated = "".join(self.nodes)
        hash_object = hashlib.md5(concatenated.encode())
        return hash_object.hexdigest() 

    
    def construct_path_graph(self) -> LmTimingWirePathGraph:
        r"""construct a path graph from yaml data.
        """
        wire_path_nodes = []
        wire_path_edges = []
        for index, node_name in enumerate(self.nodes):
            parts = node_name.split(":")
            is_port = True if len(parts) == 1 else False
            is_pin = True if len(parts) == 2 and not parts[1].isdigit() else False
            wire_path_node = LmTimingWireGraphNode(node_name, is_pin, is_port)
            wire_path_nodes.append(wire_path_node)
            
            if index > 0:
                wire_path_edge = LmTimingWireGraphEdge(index - 1, index)
                wire_path_edges.append(wire_path_edge)
                
        wire_path_graph = LmTimingWirePathGraph(wire_path_nodes, wire_path_edges)
        return wire_path_graph
