# -*- coding: UTF-8 -*-
"""
@Time    : 2022/10/17 13:46
@Author  : Jerris_Cheng
@File    : publish_file.py
@Description:
"""
from __future__ import print_function

import os.path

import zfused_api


from zfused_maya.node.outputattr import util

import maya.cmds as cmds

import os
def publish_file(*args,**kwargs):
    _task_id,_out_put_attr_id = args
    _file = kwargs.get('file')
    print(args)
    print(kwargs)
    if not os.path.exists(_file):

        return False,'No file'
    cmds.file(_file, o=True, f=True)
    _task = zfused_api.task.Task(_task_id)
    _project_entity = _task.project_entity()
    _project_step = _task.project_step()
    _output_scripts = _project_step.output_attrs()

    _project_step_checks = _project_step.checks()
    error_infos  =[]
    if _project_step_checks:
        _value = True
        for _project_step_check in _project_step_checks:
            _check = _project_step_check.check()
            _check_script = _check.check_script()
            if _project_step_check.is_ignore():
                continue
            _check_status =False
            _check_info =None
            exec (_check_script)
            #_check_status,_check_info  = exec('print 123')
            if _check_status is False:
                error_infos.append(_check_info)
                _value = False

        if _value is False:
            return False,error_infos

    #util.publish_file(_task_id,is_auto=True)
    print('1111111111111111111111111111111111111111111111111111111111111111111111111')



    #     _ui = checkwidget.CheckWidget(_project_step_checks)
    #     if not check.Check.value:
    #         _ui.show()
    #     if check.Check.value == True:
    #         _ui.close()
    #         check.Check.value = False
    #     else:
    #         return False