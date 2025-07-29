#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : lm_graph.py
@Author : yell
@Desc : feature for large model
'''

from database.enum import EdaTool, FeatureOption, FlowStep
from workspace.path import WorkspacePath, LargeModelFeatureType
from flow.flow_db import DbFlow
from database.large_model import *
from typing import List, Tuple
import numpy as np
import pandas as pd
import logging
from joblib import Parallel, delayed
from tqdm import tqdm
from numba import njit, prange
from utility.json_parser import JsonParser
import os


def _parse_patch(json_path: str) -> LmPatch:
    lm_patch = LmPatch()

    json_parser = JsonParser(json_path)
    if json_parser.read():
        json_patch = json_parser.get_json_data()

        # patch
        lm_patch.id = json_patch.get('id')
        lm_patch.patch_id_row = json_patch.get('patch_id_row')
        lm_patch.patch_id_col = json_patch.get('patch_id_col')
        lm_patch.llx = json_patch.get('llx')
        lm_patch.lly = json_patch.get('lly')
        lm_patch.urx = json_patch.get('urx')
        lm_patch.ury = json_patch.get('ury')
        lm_patch.row_min = json_patch.get('row_min')
        lm_patch.row_max = json_patch.get('row_max')
        lm_patch.col_min = json_patch.get('col_min')
        lm_patch.col_max = json_patch.get('col_max')
        lm_patch.area = json_patch.get('area')
        lm_patch.cell_density = json_patch.get('cell_density')
        lm_patch.pin_density = json_patch.get('pin_density')
        lm_patch.net_density = json_patch.get('net_density')
        lm_patch.macro_margin = json_patch.get('macro_margin')
        lm_patch.RUDY_congestion = json_patch.get('RUDY_congestion')
        lm_patch.EGR_congestion = json_patch.get('EGR_congestion')
        lm_patch.timing_map = json_patch.get('timing_map')
        lm_patch.power_map = json_patch.get('power_map')
        lm_patch.ir_drop_map = json_patch.get('ir_drop_map')   

        # patch layer
        json_patch_layers = json_patch.get('patch_layer', [])
        for json_patch_layer in json_patch_layers:
            patch_layer = LmPatchLayer()
            patch_layer.id = json_patch_layer.get('id')
            patch_layer.net_num = json_patch_layer.get('net_num')
            feature = json_patch_layer.get('feature', {})
            patch_layer.wire_width = feature.get('wire_width')
            patch_layer.wire_len = feature.get('wire_len')
            patch_layer.wire_density = feature.get('wire_density')
            patch_layer.congestion = feature.get('congestion')

            json_nets = json_patch_layer.get('nets', [])
            for json_net in json_nets:
                # net
                lm_net = LmNet()
                lm_net.id = json_net.get('id')
                lm_net.name = json_net.get('name')

                # wires
                lm_net.wire_num = json_net.get('wire_num')
                json_wires = json_net.get('wires', [])
                for json_wire in json_wires:
                    lm_wire = LmWire()
                    lm_wire.id = json_wire.get('id')

                    # wire feature
                    wire_feature = LmWireFeature()
                    feature = json_wire.get('feature', {})
                    wire_feature.wire_len = feature.get('wire_len')

                    lm_wire.feature = wire_feature

                    # path
                    lm_wire.path_num = json_wire.get('path_num')
                    json_paths = json_wire.get('paths', [])
                    for json_path in json_paths:
                        wire_path = LmPath()

                        lm_path_node1 = LmNode()
                        lm_path_node1.id = json_path.get('id1')
                        lm_path_node1.x = json_path.get('x1')
                        lm_path_node1.y = json_path.get('y1')
                        lm_path_node1.row = json_path.get('r1')
                        lm_path_node1.col = json_path.get('c1')
                        lm_path_node1.layer = json_path.get('l1')
                        lm_path_node1.pin_id = json_path.get('p1')
                        wire_path.node1 = lm_path_node1

                        lm_path_node2 = LmNode()
                        lm_path_node2.id = json_path.get('id2')
                        lm_path_node2.x = json_path.get('x2')
                        lm_path_node2.y = json_path.get('y2')
                        lm_path_node2.row = json_path.get('r2')
                        lm_path_node2.col = json_path.get('c2')
                        lm_path_node2.layer = json_path.get('l2')
                        lm_path_node2.pin_id = json_path.get('p2')
                        wire_path.node2 = lm_path_node2

                        lm_wire.paths.append(wire_path)

                    lm_net.wires.append(lm_wire)

                patch_layer.nets.append(lm_net)

            lm_patch.patch_layer.append(patch_layer)

    return lm_patch


class LmPatchs():
    """feature statis"""

    def __init__(self, dir_workspace: str, eda_tool: EdaTool):
        self.dir_workspace = dir_workspace
        self.eda_tool = eda_tool
        self.workspace = WorkspacePath(dir_workspace)

    def get_patches(self) -> List[LmPatch]:
        lm_patches = []

        flow = DbFlow(eda_tool=self.eda_tool, step=FlowStep.route)
        feature_dir = self.workspace.get_feature_lm(flow=flow,
                                                    feature_option=FeatureOption.large_model,
                                                    lm_feature_type=LargeModelFeatureType.lm_patches)
        logging.info("Start to read patches...")
        for root, _, files in os.walk(feature_dir):
            # lm_patches = Parallel(backend="loky")(delayed(_parse_patch)(os.path.join(root, file))
            #                                       for file in tqdm(files, desc="Reading patches"))
            lm_patches = [_parse_patch(os.path.join(root, file))
                          for file in tqdm(files, desc="Reading patches")]

        return lm_patches


@dataclass
class PathData:
    channel_id: int
    node1_x: float
    node1_y: float
    node2_x: float
    node2_y: float


@dataclass
class PatchData:
    patch_id_row: int
    patch_id_col: int
    lly: int
    ury: int
    llx: int
    urx: int
    paths: List[PathData]


@njit(parallel=True)
def _resize_3D_matrix_numba(matrix: np.ndarray, size: Tuple[int, int]) -> np.ndarray:
    """
    Numba-accelerated function to resize a 3D matrix by resizing each 2D channel.

    Args:
        matrix (np.ndarray): The input 3D matrix.
        size (Tuple[int, int]): The output size.
    """
    size_x, size_y = size
    channels, orig_x, orig_y = matrix.shape
    result = np.zeros((channels, size_x, size_y), dtype=np.float64)

    # Precompute block sizes and start indices for both dimensions
    x_block_sizes = np.full(size_x, orig_x // size_x, dtype=np.int32)
    for i in range(orig_x % size_x):
        x_block_sizes[i] += 1

    y_block_sizes = np.full(size_y, orig_y // size_y, dtype=np.int32)
    for j in range(orig_y % size_y):
        y_block_sizes[j] += 1

    x_start_indices = np.zeros(size_x, dtype=np.int32)
    y_start_indices = np.zeros(size_y, dtype=np.int32)

    for i in range(1, size_x):
        x_start_indices[i] = x_start_indices[i - 1] + x_block_sizes[i - 1]

    for j in range(1, size_y):
        y_start_indices[j] = y_start_indices[j - 1] + y_block_sizes[j - 1]

    # Iterate over each channel
    for c in prange(channels):
        # Iterate over each block in x and y dimensions
        for i in range(size_x):
            for j in range(size_y):
                x_start = x_start_indices[i]
                x_end = x_start + x_block_sizes[i]
                y_start = y_start_indices[j]
                y_end = y_start + y_block_sizes[j]

                sum_val = 0.0
                count = 0
                for xi in range(x_start, x_end):
                    for yi in range(y_start, y_end):
                        sum_val += matrix[c, xi, yi]
                        count += 1

                if count > 0:
                    result[c, i, j] = sum_val / count
                else:
                    result[c, i, j] = 0.0

        # Normalize each channel by its maximum value
        max_val = 0.0
        for i in range(size_x):
            for j in range(size_y):
                if result[c, i, j] > max_val:
                    max_val = result[c, i, j]

        if max_val > 0.0:
            for i in range(size_x):
                for j in range(size_y):
                    result[c, i, j] /= max_val

    return result


def _process_patch(n_channels: int, roughness: int, patch_data: PatchData) -> Tuple[int, int, np.ndarray]:
    # Initialize the matrix for this patch
    patch_width = (patch_data.urx - patch_data.llx) // roughness
    patch_height = (patch_data.ury - patch_data.lly) // roughness

    matrix = np.zeros((n_channels, patch_height, patch_width))

    # Iterate over each channel
    for path in patch_data.paths:
        x1 = (path.node1_x - patch_data.llx) // roughness
        x2 = (path.node2_x - patch_data.llx) // roughness
        y1 = (path.node1_y - patch_data.lly) // roughness
        y2 = (path.node2_y - patch_data.lly) // roughness
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        # Update the matrix
        matrix[path.channel_id, y1:y2 + 1, x1:x2 + 1] += 1

    return (patch_data.patch_id_row, patch_data.patch_id_col, matrix)


def _process_resized_patch(n_channels: int, roughness: int, patch_data: PatchData, patch_size: Tuple[int, int]) -> Tuple[int, int, np.ndarray]:
    row, col, matrix = _process_patch(n_channels, roughness, patch_data)

    return (row, col, _resize_3D_matrix_numba(matrix, patch_size))


class LmPatchOperator():
    def __init__(self, roughness: int = 1, ignore_empty: bool = False, patch_size: Tuple[int, int] = None):
        # (row, col) -> (#layer/channel, height, width)
        self._matrices: List[List[np.ndarray]] = []
        self._channels: List[int] = []
        self._roughness: int = roughness
        self._ignore_empty: bool = ignore_empty
        self._patch_size: Tuple[int, int] = patch_size

    def get_channels(self) -> List[int]:
        return self._channels

    def to_matrix(self, patches: List[LmPatch]) -> List[List[np.ndarray]]:
        """
        Convert a list of LmPatch objects into a #layer-channel image representation.
        Each channel represents a wire_feature (e.g., wire_width, wire_len, etc.).

        Args:
            patches (List[LmPatch]): The input list of patch objects.

        Returns:
            #layer-channel images map (row,col) -> (#layer, height, width).
            List[List[np.ndarray]]: The output list of matrices.
        """

        logging.info("Start to convert patch to image...")
        if len(patches) == 0:
            logging.warning("No patches found, aborting...")
            return None
        # Pre-process
        self._find_feasible_channels(patches)

        # Determine matrix dimensions
        n_row = max(patch.patch_id_row for patch in patches) + 1
        n_col = max(patch.patch_id_col for patch in patches) + 1

        # Initialize matrices
        self._matrices = [
            [None for _ in range(n_col)] for _ in range(n_row)]
        patches_data = [self._extract_patch_data(
            patch) for patch in patches]

        if self._patch_size is None:
            results = Parallel(backend="threading")(
                delayed(_process_patch)(len(self._channels), self._roughness, patch_data) for patch_data in tqdm(patches_data, desc="Processing patches")
            )
        else:
            results = Parallel(backend="threading")(
                delayed(_process_resized_patch)(len(self._channels), self._roughness, patch_data, self._patch_size) for patch_data in tqdm(patches_data, desc="Processing patches")
            )
        # Assign the processed matrices to their respective positions
        for row, col, matrix in results:
            self._matrices[row][col] = matrix

        # Count the number of processed patches
        processed_patches = len(results)

        logging.info(
            f"> #Patches: {processed_patches}, #Rows: {n_row}, #Cols: {n_col}, (Resolution: {self._roughness})")

        return self._matrices

    def distribution_analysis(self, csv_path: str = None) -> pd.DataFrame:
        """
        Analyze the distribution of routing wire

        Args:
            csv_path (str): The output CSV file path.

        Returns:
            pd.DataFrame: The output DataFrame.
        """
        logging.info("Start to analyze the distribution of routing wire...")

        # Initialize lists to store results
        patch_id_rows, patch_id_cols, layer_ids, sums, densities = [], [], [], [], []

        # Precompute sizes to avoid repeated calculations in loops
        n_row, n_col = len(self._matrices), len(self._matrices[0])
        for row_id in range(n_row):
            for col_id in range(n_col):
                matrix = self._matrices[row_id][col_id]
                if matrix is None:
                    continue

                # Vectorized calculation of sums and densities
                layer_sums = np.sum(matrix, axis=(1, 2))
                layer_size = matrix.shape[1] * matrix.shape[2]
                layer_densities = layer_sums / layer_size

                # Use numpy to quickly extend lists
                num_layers = len(layer_sums)
                patch_id_rows.extend([row_id] * num_layers)
                patch_id_cols.extend([col_id] * num_layers)
                layer_ids.extend(range(num_layers))
                sums.extend(layer_sums)
                densities.extend(layer_densities)

        # Convert lists to a DataFrame
        df = pd.DataFrame({
            'patch_id_row': np.array(patch_id_rows, dtype=np.int32),
            'patch_id_col': np.array(patch_id_cols, dtype=np.int32),
            'layer_id': np.array(layer_ids, dtype=np.int32),
            'sum': np.array(sums, dtype=np.int32),
            'density': np.array(densities, dtype=np.float32),
        })

        # Calculate and log zero statistics
        zero_mask = (df['sum'] == 0)
        zero_count = zero_mask.sum()
        total_count = len(df)
        zero_ratio = zero_count / total_count * 100
        logging.info(
            f"> #Empty wire matrix: {zero_count} / {total_count}, ratio: {zero_ratio:.2f}%"
        )

        # Group by 'layer_id' and calculate stats
        layer_group = df.groupby('layer_id')['sum']
        count_by_layer = layer_group.size()
        zero_by_layer = layer_group.apply(lambda x: (x == 0).sum())
        ratio_by_layer = zero_by_layer / count_by_layer * 100

        # Log layer-specific statistics
        for layer_id, total_num in count_by_layer.items():
            z_count = zero_by_layer[layer_id]
            z_ratio = ratio_by_layer[layer_id]
            logging.info(
                f"> Layer {layer_id}: #Empty wire matrix: {z_count} / {total_num}, ratio: {z_ratio:.2f}%"
            )

        # Save to CSV if path is provided
        if csv_path:
            df.to_csv(csv_path, index=False)
            logging.info(f"Distribution result has been saved to {csv_path}.")

        return df

    def _find_feasible_channels(self, patches: List[LmPatch]):
        """
        Find feasible channels from a list of LmPatch objects.

        Args:
            patches (List[LmPatch]): The input list of patch objects.
        """
        logging.info("Start to find feasible channels...")
        # Find feasible channels
        original_channels = [
            layer.id for layer in patches[0].patch_layer]
        logging.info(f"> #Original Total channels: {len(original_channels)}")

        if not self._ignore_empty:
            self._channels = original_channels
        else:
            for channel in original_channels:
                is_empty = True
                for patch in patches:
                    for layer in patch.patch_layer:
                        if layer.id != channel:
                            continue

                        for net in layer.nets:
                            net: LmNet
                            if (len(net.wires) > 0):
                                is_empty = False
                                break
                if not is_empty:
                    self._channels.append(channel)
                else:
                    logging.warning(
                        f"Channel {channel} is empty and will be ignored")

        logging.info(f"> #Feasible Total channels: {len(self._channels)}")

    def _extract_patch_data(self, patch: LmPatch) -> PatchData:
        """
        Extract the patch data from an LmPatch object.

        Args:
            patch (LmPatch): The input patch object.

        Returns:
            PatchData: The output patch data.
        """
        paths = []
        for layer_id in self._channels:
            layer = patch.patch_layer[layer_id]
            for net in layer.nets:
                for wire in net.wires:
                    for path in wire.paths:
                        node1, node2 = path.node1, path.node2
                        if node1 is None or node2 is None:
                            continue
                        path_data = PathData(
                            channel_id=layer_id,
                            node1_x=node1.x,
                            node1_y=node1.y,
                            node2_x=node2.x,
                            node2_y=node2.y
                        )
                        paths.append(path_data)

        return PatchData(
            patch_id_row=patch.patch_id_row,
            patch_id_col=patch.patch_id_col,
            lly=patch.lly,
            ury=patch.ury,
            llx=patch.llx,
            urx=patch.urx,
            paths=paths
        )
