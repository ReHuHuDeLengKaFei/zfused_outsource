# -*- coding: utf-8 -*-
# --author-- lanhua.zhou

""" 文件整理 上传服务器 链接数据库 """

import logging

import maya.cmds as cmds

from zfused_maya.core import refparser
_logger = logging.getLogger(__name__)


def open_current_file():
    _current_file = cmds.file(q=True, sn=True)
    print(_current_file)
    cmds.file(_current_file, o=True, f=True, options="v=0;")


def replace_reference_relative(src_file, replace_relative_file):
    if src_file.endswith(".mb"):
        return True

    # 分析文件
    _maya_reference_parser = refparser.MayaRefParser(src_file)

    # 替换文件
    _maya_reference_parser.update_file(src_file,replace_relative_file)

    return True


