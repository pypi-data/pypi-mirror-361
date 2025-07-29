#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File : main.py
@Time : 2022/07/11 10:23:08
@Author : shuaiying long
@Version : 1.0
@Contact : longshy@pcl.ac.cn
@Desc : The top script of ibm project.
'''


# from writer.writer import Writer
# from parser.parser import Parser, TimingPathParser, FanloadViolatParser
# from tkinter import Tcl
# import sys
# import os
# BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, BASE)


# def run_netparser():
#     filename_reader = "/home/longshuaiying/iBM/tests/example/report_command_rpt/result/reportWire.rpt"
#     filename_writer = "/home/longshuaiying/iBM/ibm/report/net_wire_length.csv"
#     parser = Parser()
#     # reader = Reader()
#     writer = Writer()
#     net_list = parser.net_parser(filename_reader)
#     writer.net_writer(filename_writer, net_list)


# def run_hinstparser():
#     filename_reader = "/home/longshuaiying/iBM/tests/example/report_command_rpt/result/report_area_detail.rpt"
#     filename_writer = "/home/longshuaiying/iBM/ibm/report/area.csv"
#     parser = Parser()
#     writer = Writer()
#     hinst_list = parser.hinst_parser(filename_reader)
#     writer.hinst_writer(filename_writer, hinst_list)


# def run_timingparser():
#     filename_reader = "/home/longshuaiying/run_data/work_0/beihai_Flow/pd_data/pr/rpt/i-perf/iCTS/2022-08-02/innovus/CTS/timingReports/asic_top_postCTS_all_hold.tarpt"
#     filename_writer = "/home/longshuaiying/iBM/ibm/report/hold_timingpath.csv"
#     timingpath_parser = TimingPathParser(filename_reader)
#     concate_timing_path_list = []
#     concate_timing_path_list = timingpath_parser.parser_concatetimingpath()
#     writer = Writer()
#     writer.timingpath_writer(filename_writer, concate_timing_path_list)


# def run_fanloadparser():
#     filename_reader = "/home/longshuaiying/run_data/work_0/beihai_Flow/pd_data/pr/rpt/i-perf/iCTS/2022-08-02/innovus/CTS/timingReports/asic_top_postCTS.fanout"
#     filename_writer = "/home/longshuaiying/iBM/ibm/report/fanload_violat.csv"
#     fanloadviolat_parser = FanloadViolatParser(filename_reader)
#     fanout_load_violat_info = fanloadviolat_parser.parser_fanoutloadviolat()
#     writer = Writer()
#     writer.fanloadviolat_writer(filename_writer, fanout_load_violat_info)


# def run_sourcetcl():
#     tcl = Tcl()
#     run_paths: list[str] = ["source /home/longshuaiying/iBM/ibm/fpt/command/Stage1.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage2.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage3.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage4.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage5.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage6.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage7.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage8.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage9.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage10.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage11.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage12.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage13.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage14.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage15.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage16.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage17.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage18.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage19.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage20.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage21.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage22.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage23.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage24.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage25.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage26.tcl",
#                             "source /home/longshuaiying/iBM/ibm/fpt/command/Stage27.tcl"]
#     for run_path in run_paths:
#         tcl.eval(run_path)


if __name__ == '__main__':
    # run_timingparser()
    pass
