# -*- coding: utf-8 -*-
# --author-- lanhua.zhou

""" 文件整理 上传服务器 链接数据库 """

import maya.cmds as cmds


def open_current_file():
    _current_file = cmds.file(q=True, sn=True)
    print(_current_file)
    cmds.file(_current_file, o = True, f = True, options = "v=0;")



def replace_reference_relative(src_file, replace_relative_file):
    if src_file.endswith(".mb"):
        return True
    
    # 分析文件
    


    # 替换文件



    return True