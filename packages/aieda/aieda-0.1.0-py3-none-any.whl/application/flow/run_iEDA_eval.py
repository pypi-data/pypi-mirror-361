#!/usr/bin/env python
# -*- encoding: utf-8 -*-
######################################################################################
# import ai-eda as root

######################################################################################
import sys
import os
import argparse
from typing import Optional

# set EDA tools working environment
# option : iEDA innovus PT dreamPlace
os.environ['eda_tool'] = "iEDA"

current_dir = os.path.split(os.path.abspath(__file__))[0]
aieda_dir = current_dir.rsplit('/', 2)[0]
sys.path.append(aieda_dir)

print(f"current_dir = {current_dir}")
print(f"aieda_dir = {aieda_dir}")

from feature.io import FeatureIO
from database.enum import EdaTool, FlowStep, FeatureOption
from flow.flow_db import DbFlow


def run_feature_evaluation(design: str, workspace_path: str, step: Optional[str] = None) -> None:
    """
    运行特征评估
    
    参数:
        design: 设计名称
        workspace_path: 工作空间路径，包含{design}占位符
        step: 要评估的流程步骤, 默认为place
    
    返回:
        None
    """
    # 构建工作空间路径
    dir_workspace = workspace_path.format(design=design)
    if not os.path.exists(dir_workspace):
        print(f"错误: 工作空间不存在 - {dir_workspace}")
        return
    
    # 确定要使用的流程步骤
    flow_step = FlowStep.place  # 默认为place
    
    # 如果指定了步骤，则尝试转换为FlowStep枚举值
    if step:
        try:
            # 将字符串转换为FlowStep枚举
            flow_step = getattr(FlowStep, step) if step in dir(FlowStep) else FlowStep[step]
            print(f"使用指定步骤: {flow_step.value}")
        except (AttributeError, KeyError):
            # 提示有效的选项并退出程序
            valid_steps = [attr for attr in dir(FlowStep) 
                          if not attr.startswith('_') 
                          and attr != 'value' 
                          and attr != 'name']
            print(f"错误: 无效的步骤 '{step}'")
            print(f"有效的步骤包括: {', '.join(valid_steps)}")
            sys.exit(1)  # 使用非零退出码表示错误
    else:
        print(f"使用默认步骤: {flow_step.value}")
    
    try:
        # 创建FeatureIO对象并生成评估
        metrics_eval = FeatureIO(
            dir_workspace=dir_workspace,
            eda_tool=EdaTool.IEDA, 
            feature_option=FeatureOption.eval,
            flow=DbFlow(eda_tool=EdaTool.IEDA, step=flow_step)
        )
        metrics_eval.generate(reload=True)
        print(f"特征评估完成！")
    except Exception as e:
        print(f"错误: 生成特征评估时出错 - {str(e)}")

if __name__ == "__main__":
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='指标评估工具')
    parser.add_argument('--design', type=str, default='gcd', 
                        help='设计名称, 默认值为gcd')
    parser.add_argument('--path', type=str, default='/data/project_share/yhqiu/{design}/workspace', 
                        help='工作空间路径，需包含{design}占位符，默认值为/data/project_share/yhqiu/{design}/workspace')
    parser.add_argument('--step', type=str, default=None, 
                        help='要评估的流程步骤, 默认为place。目前可选: place, cts')
    args = parser.parse_args()
    
    # 特征评估
    run_feature_evaluation(design=args.design, workspace_path=args.path, step=args.step)
    
    exit(0)
