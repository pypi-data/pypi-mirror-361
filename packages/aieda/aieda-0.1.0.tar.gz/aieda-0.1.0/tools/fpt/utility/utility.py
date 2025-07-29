#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File    :   utility.py
@Time    :   2022/09/15 15:49:52
@Author  :   shuaiying long
@Version :   1.0
@Contact :   longshy@pcl.ac.cn
@Desc    :   The definitions of common functions.
'''

def find_all_char(string, ch):
    pos = []
    start_len = 0
    while True:
        index = string.find(ch, start_len)
        if index == -1:
            break
        pos.append(index)
        start_len = index+1
    return pos


def find_last_char(string, ch):
    pos = []
    start_len = 0
    while True:
        index = string.find(ch, start_len)
        if index == -1:
            break
        pos.append(index)
        start_len = index+1
    return pos[-1]


