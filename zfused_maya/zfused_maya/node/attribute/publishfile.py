 # coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import shutil
import logging
import datetime
import time

import maya.cmds as cmds

import zfused_api

from zfused_maya.node.core import check

from zfused_maya.ui.widgets import checkwidget

logger = logging.getLogger(__file__)



def publish_file(*args, **kwargs):
    """ publish file
        base publish file script
    :rtype: bool
    """
    _task_id = args[0]
    _task = zfused_api.task.Task(_task_id)
    _project_entity = _task.project_entity()
    _project_step = _task.project_step()

    # 查看雷区
    _forbidden_script = _project_step.forbidden_script()
    if _forbidden_script:
        forbidden_value = True
        exec(_forbidden_script)
        if not forbidden_value:
            return
    
    # 检查节点
    _project_step_checks = _project_step.checks()
    if _project_step_checks:
        
        if not check.Check.value:
            _ui = checkwidget.CheckWidget(_project_step_checks)
            _ui.show()
        if check.Check.value == True:
            check.Check.value = False
        else:
            return False