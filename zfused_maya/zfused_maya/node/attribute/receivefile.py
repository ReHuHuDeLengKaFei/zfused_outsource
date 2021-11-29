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
import zfused_maya.node.core.attr as attr


logger = logging.getLogger(__file__)



def reference_file(*args, **kwargs):
    """ receive file
        base receive file script
    :rtype: bool
    """
    _task_id, _task_attr_input_id, _input_task_id, _input_task_attr_output_id = args

    # print(_task_id, _task_attr_input_id, _input_task_id, _input_task_attr_output_id)
    _task = zfused_api.task.Task(_task_id)
    _task_attr_input = zfused_api.attr.Input(_task_attr_input_id)
    _extended_version = _task_attr_input.extended_version()


    _input_task = zfused_api.task.Task(_input_task_id)
    _input_task_attr_output = zfused_api.attr.Output(_input_task_attr_output_id)
    _input_task_project_step_id = _input_task_attr_output.project_step_id()
    _input_production_path = _input_task.production_path()
    
    # get file 
    _file_index = "{:0>4d}".format(_input_task.last_version_index())
    _file_suffix = _input_task_attr_output.suffix()
    if _extended_version:
        _production_file = zfused_api.zFused.get("production_file", filter = {"TaskId": _input_task_id, "ProjectStepAttrId": _input_task_project_step_id, "Index": int(_file_index)})
        if _production_file:
            _production_file = _production_file[0]["Path"]
        else:
            _production_file = "{}/{}/{}.{}{}".format(_input_production_path,_input_task_attr_output.code(),_input_task.file_code(),_file_index, _file_suffix)
    else:
        _production_file = "{}/{}/{}{}".format(_input_production_path,_input_task_attr_output.code(),_input_task.file_code(), _file_suffix)
    
    print(_production_file)

    # do somthing
    rf = cmds.file(_production_file, r = True, ns = _input_task.file_code())
    rfn = cmds.referenceQuery(rf, rfn = True)
    _version_id = _input_task.last_version_id()
    attr.set_node_attr(rfn, _input_task_attr_output_id, _version_id, "false")


