#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
iEDA流程运行模块

提供命令行接口和编程接口来运行iEDA EDA流程
"""

import sys
import os
import json
from typing import List, Optional
import argparse
from pathlib import Path

# 库模式导入 - 使用相对导入
try:
    # 库模式：从已安装的包导入
    from aieda.utility.folder_permission import FolderPermissionManager
    from aieda.database.enum import EdaTool, FlowStep
    from aieda.flow.flow_db import DbFlow
    from aieda.engine.cts import EngineCTS
    from aieda.engine.placement import EnginePlacement
    from aieda.engine.routing import EngineRouting
    from aieda.engine.net_opt import EngineNetOpt 
    from aieda.engine.timing_opt import EngineTimingOpt
    from aieda.engine.gds import EngineGDS
    from aieda.flow.run_flow_ieda import RunFlowIEDA
except ImportError:
    # 开发模式：使用相对导入
    try:
        from ...utility.folder_permission import FolderPermissionManager
        from ...database.enum import EdaTool, FlowStep
        from ...flow.flow_db import DbFlow
        from ...engine.cts import EngineCTS
        from ...engine.placement import EnginePlacement
        from ...engine.routing import EngineRouting
        from ...engine.net_opt import EngineNetOpt 
        from ...engine.timing_opt import EngineTimingOpt
        from ...engine.gds import EngineGDS
        from ...flow.run_flow_ieda import RunFlowIEDA
    except ImportError:
        # 兼容原始的绝对路径导入方式
        current_dir = os.path.split(os.path.abspath(__file__))[0]
        aieda_dir = current_dir.rsplit('/', 2)[0]
        sys.path.append(aieda_dir)
        
        from utility.folder_permission import FolderPermissionManager
        from database.enum import EdaTool, FlowStep
        from flow.flow_db import DbFlow
        from engine.cts import EngineCTS
        from engine.placement import EnginePlacement
        from engine.routing import EngineRouting
        from engine.net_opt import EngineNetOpt 
        from engine.timing_opt import EngineTimingOpt
        from engine.gds import EngineGDS
        from flow.run_flow_ieda import RunFlowIEDA


class FlowManager:
    """EDA流程管理器"""
    
    def __init__(self, design: str, workspace_path: str, eda_tool: str = "iEDA"):
        """初始化流程管理器
        
        Args:
            design: 设计名称
            workspace_path: 工作空间路径模板，包含{design}占位符
            eda_tool: EDA工具类型
        """
        self.design = design
        self.workspace_path = workspace_path
        self.eda_tool = eda_tool
        
        # 设置环境变量
        os.environ['eda_tool'] = eda_tool
        
        # 构建实际工作空间路径
        self.dir_workspace = workspace_path.format(design=design)
        
        # 创建流程运行器
        self.flow_runner = RunFlowIEDA(dir_workspace=self.dir_workspace)
    
    def reset_flow_steps(self, step: Optional[str] = None) -> None:
        """重置流程步骤状态"""
        reset_flow_steps(self.design, self.workspace_path, step)
    
    def run_flow(self) -> bool:
        """运行完整流程"""
        try:
            result = self.flow_runner.run()
            return result
        except Exception as e:
            print(f"流程运行失败: {e}")
            return False
    
    def get_flow_status(self) -> dict:
        """获取流程状态"""
        flow_json_path = os.path.join(self.dir_workspace, "config", "flow.json")
        
        if not os.path.exists(flow_json_path):
            return {"error": f"流程配置文件不存在: {flow_json_path}"}
        
        try:
            with open(flow_json_path, 'r', encoding='utf-8') as f:
                flow_data = json.load(f)
            return flow_data
        except Exception as e:
            return {"error": f"读取流程配置失败: {e}"}


def reset_flow_steps(design: str, workspace_path: str, step: Optional[str] = None) -> None:
    """
    修改 flow.json 文件，根据指定的步骤调整流程状态：
    - 将指定步骤及其之后的所有步骤状态设置为 "unstart"
    - 将指定步骤之前的所有步骤状态设置为 "success"
    
    参数:
        design: 设计名称
        workspace_path: 工作空间路径，包含{design}占位符
        step: 从哪个步骤开始执行，如果为 None 则重置所有步骤为 "unstart"
    
    返回:
        None
    """
    # 构建 flow.json 文件路径
    dir_workspace = workspace_path.format(design=design)
    flow_json_path = os.path.join(dir_workspace, "config", "flow.json")
    
    # 检查文件是否存在
    if not os.path.exists(flow_json_path):
        print(f"错误: 文件不存在 - {flow_json_path}")
        return
    
    try:
        # 读取 flow.json 文件
        with open(flow_json_path, 'r', encoding='utf-8') as f:
            flow_data = json.load(f)
        
        # 修改状态
        found_step = False
        success_count = 0
        unstart_count = 0
        
        for item in flow_data.get("flow", []):
            current_step = item.get("step")
            current_state = item.get("state")
            
            # 如果找到指定的起始步骤，标记为已找到
            if step and current_step == step:
                found_step = True
            
            # 如果没有指定步骤，或者已经找到指定步骤，则设置为 "unstart"
            if step is None or found_step:
                if current_state != "unstart":
                    item["state"] = "unstart"
                    unstart_count += 1
            # 如果在指定步骤之前，则设置为 "success"
            elif step and not found_step:
                if current_state != "success":
                    item["state"] = "success"
                    success_count += 1
        
        # 写入修改后的数据
        with open(flow_json_path, 'w', encoding='utf-8') as f:
            json.dump(flow_data, f, indent=4)
        
        # 打印修改结果
        if step is None:
            print(f"已将所有 {unstart_count} 个步骤的状态重置为 'unstart'")
        elif not found_step:
            print(f"错误: 未找到步骤 '{step}'")
        else:
            print(f"已将 '{step}' 之前的 {success_count} 个步骤设置为 'success'")
            print(f"已将 '{step}' 及其之后的 {unstart_count} 个步骤设置为 'unstart'")
            
    except json.JSONDecodeError:
        print(f"错误: 无法解析 JSON 文件 - {flow_json_path}")
    except Exception as e:
        print(f"错误: {str(e)}")


def main():
    """命令行入口函数"""
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='iEDA流程运行工具')
    
    # 添加参数
    parser.add_argument('--design', type=str, default='gcd', 
                        help='设计名称, 默认值为gcd')
    parser.add_argument('--path', type=str, 
                        default='/data/project_share/yhqiu/{design}/workspace', 
                        help='工作空间路径，需包含{design}占位符')
    parser.add_argument('--step', type=str, default=None, 
                        help='从哪个阶段开始执行流程, 默认从头开始执行全流程。'
                             '可选: fixFanout, place, CTS, optDrv, optHold, legalization, route, filler')
    parser.add_argument('--tool', type=str, default='iEDA',
                        help='EDA工具类型，默认为iEDA')
    parser.add_argument('--status', action='store_true',
                        help='只查看流程状态，不运行流程')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 创建流程管理器
    flow_manager = FlowManager(
        design=args.design,
        workspace_path=args.path,
        eda_tool=args.tool
    )
    
    # 如果只是查看状态
    if args.status:
        status = flow_manager.get_flow_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        return
    
    # 重置流程步骤
    flow_manager.reset_flow_steps(step=args.step)
    
    # 运行流程
    print(f"开始运行 {args.tool} 流程...")
    print(f"设计: {args.design}")
    print(f"工作空间: {flow_manager.dir_workspace}")
    if args.step:
        print(f"从步骤开始: {args.step}")
    
    success = flow_manager.run_flow()
    
    if success:
        print("✅ 流程运行成功!")
        sys.exit(0)
    else:
        print("❌ 流程运行失败!")
        sys.exit(1)


# 编程接口函数
def run_ieda_flow(design: str, workspace_path: str, step: Optional[str] = None, 
                  eda_tool: str = "iEDA") -> bool:
    """编程接口：运行iEDA流程
    
    Args:
        design: 设计名称
        workspace_path: 工作空间路径模板
        step: 从哪个步骤开始，None表示从头开始
        eda_tool: EDA工具类型
    
    Returns:
        bool: 是否成功
    """
    flow_manager = FlowManager(design, workspace_path, eda_tool)
    flow_manager.reset_flow_steps(step)
    return flow_manager.run_flow()


if __name__ == "__main__":
    main()