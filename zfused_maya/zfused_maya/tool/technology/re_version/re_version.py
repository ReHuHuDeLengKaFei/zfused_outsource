# -*- coding: UTF-8 -*-
"""
@Time    : 2022/9/22 15:39
@Author  : Jerris_Cheng
@File    : re_version.py
@Description:
"""
from __future__ import print_function

import os

from . import cores
reload(cores)

from . import error_window
reload(error_window)
import maya.cmds as cmds
from PySide2 import QtWidgets
def without_version_open_file():
    _file_path, filetype = QtWidgets.QFileDialog.getOpenFileName(None,"Open File", "./", "ma(*.ma)")
    
    if not os.path.exists(_file_path):
        return
    _result,_nodes = cores.update_file(_file_path)
    if _result:
        cmds.file(_file_path,o=True,type='mayaAscii',options ="v=0;p=17;f=0",f=True,ignoreVersion =True)
    else:
        app = error_window.ErrorWindow(_nodes)
        app.show()
        pass