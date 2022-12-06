# -*- coding: utf-8 -*-
# --author-- lanhua.zhou

""" 文件整理 上传服务器 链接数据库 """

import maya.cmds as cmds


def local_open_current_file(*args, **kwargs):
    _current_file = cmds.file(q=True, sn=True)
    print(_current_file)
    cmds.file(_current_file, o = True, f = True, options = "v=0;")
