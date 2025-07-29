#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File : enum.py
@Author : yell
@Desc : enum definition
'''

from enum import Enum

class TaskState(Enum):
    """task running state
    """
    Unstart = "unstart"
    Success = "success"
    Ongoing = "ongoing"
    Imcomplete = "incomplete"

class TaskOption(Enum):
    """task job
    """
    NO_TASK = None
    RUN_EDA = "run_eda"
    RUN_FPT = "run_fpt"
    RUN_SRCX = "run_starrc" 

class EdaTool(Enum):
    """EDA tool for different step.
    """
    EDI = "edi"
    IEDA = "iEDA"
    DC = "DC"
    INNOVUS = "innovus"
    PT = "PT"
    CALIBRE = "calibre"
    DREAMPLACE = "dreamplace"
    XPLACE = "Xplace"
    OPENROAD = "OpenROAD"
    STARRC = "StarRC"
        
class Process(Enum):
    """chip process
    """
    process_110nm = 1
    process_t28 = 2
    process_sky130 = 3
    
class FlowStep(Enum):
    """PR step
    """
    NoStep = ""
    initFlow = "initFlow"
    initDB = "initDB"
    edi = "edi"
    floorplan = "floorplan"
    pdn = "PDN"
    prePlace = "prePlace"
    place = "place"
    globalPlace = "gp"
    detailPlace = "dp"
    cts = "CTS"
    route = "route"
    globalRouting = "gr"
    detailRouting = "dr"
    eco = "eco"
    fixFanout = "fixFanout"
    optDrv = "optDrv"
    optHold = "optHold"
    optSetup = "optSetup"
    legalization = "legalization"
    filler = "filler"
    drc = "drc"
    sta = "sta"
    rcx = "rcx"
    gds = "gds"
    full_flow = 'full_flow'
    
class FptState(Enum):
    """FPT State
    """
    off = "off"
    on = "on"
    
class PTState(Enum):
    """PT
    """
    off = "off"
    on = "on"

class TrackDirection(Enum):
    """track direction
    """
    none = ""
    horizontal = "H"
    vertical = "V"
    
class LayerType(Enum):
    """layer type
    """
    none = ""
    routing = "routing"
    cut = "cut"
    
class CellType(Enum):
    """cell type
    """
    none = ""
    pad = "pad"
    core = "core"
    
class OrientType(Enum):
    """cell type
    """
    none = ""
    N_R0 = "N"
    W_R90 = "W"
    S_R180 = "S"
    E_R270 = "E"
    FN_MY = "FN"
    FE_MY90 = "FE"
    FS_MX = "FS"
    FW_MX90 = "FW"
    
class PlaceStatus(Enum):
    """placement status
    """
    none = ""
    fixed = "fixed"
    cover = "cover"
    placed = "placed"
    unplaced = "unplaced"
    
    
class NetType(Enum):
    """net type
    """
    none = ""
    signal = "signal"
    clock = "clock"
    power = "power"
    ground = "ground"
    
class EvalCongestionType(Enum):
    """congestion type in evaluation
    """
    none = 0
    instance_density = 1
    pin_density = 2
    net_congestion = 3
    gr_congestion = 4
    macro_margin_h = 5
    macro_margin_v = 6
    continuous_white_space = 7
    macro_margin = 8
    macro_channel = 9
    
class EvalRudyType(Enum):
    """RUDY type in evaluation
    """
    none = 0
    rudy = 1
    pin_rudy = 2
    lut_rudy = 3
    
class EvalInstanceStatus(Enum):
    """congestion type in evaluation
    """
    none = 0
    fixed = 1
    cover = 2
    placed = 3
    unplaced = 4

class EvalWirelengthType(Enum):
    """wirelength type in evaluation
    """
    none = 0
    hpwl = 1
    flute = 2
    b2b = 3
    egr = 4

class EvalDirection(Enum):
    """direction type in evaluation
    """
    none = 0
    h = 1
    v = 2
    
class FeatureOption(Enum):
    """feature options
    """
    NoFeature = None
    summary = "summary" # default
    tools = "tool"
    eval_map = "eval_map"
    drc = "drc"
    eval = "eval"
    timing_eval = "timing_eval"
    baseline_drc = "baseline_drc"
    baseline_sta = "baseline_sta"
    baseline_power = "baseline_power"
    large_model = "large_model"

class DSEMethod(Enum):
    """different EDA DSE method.
    """
    WANDB = "wandb"
    OPTUNA = "optuna"
    NNI = "nni"
