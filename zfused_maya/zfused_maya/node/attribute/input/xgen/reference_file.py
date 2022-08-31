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


logger = logging.getLogger(__name__)


def reference_file(*args, **kwargs):
    """ receive file
        base receive file script
    :rtype: bool
    """
    # _task_id, _task_attr_input_id, _input_task_id, _input_task_attr_output_id = args
    _task_id = kwargs.get("task_id")
    _task_attr_input_id = kwargs.get("task_attr_input_id")
    _input_task_id = kwargs.get("input_task_id")
    _input_task_attr_output_id = kwargs.get("input_task_attr_output_id")
    _namespace = kwargs.get("namespace")
    _index = kwargs.get("index")
    
    _task = zfused_api.task.Task(_task_id)
    _task_attr_input = zfused_api.attr.Input(_task_attr_input_id)
    _extended_version = _task_attr_input.extended_version()
    if _index == -1:
        _extended_version = False
    elif _index:
        _extended_version = True

    _input_task = zfused_api.task.Task(_input_task_id)
    _input_task_attr_output = zfused_api.attr.Output(_input_task_attr_output_id)
    _input_task_project_step_id = _input_task_attr_output.project_step_id()
    _input_production_path = _input_task.production_path()
    
    # get file 
    # _file_index = "{:0>4d}".format(_input_task.last_version_index())
    if _index:
        _file_index = "{:0>4d}".format(_index)
    else:
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


    # 判定是否已存在
    _reference_nodes = cmds.ls(references = True)
    if _reference_nodes:
        for _reference_node in _reference_nodes:
            _reference_name_space = cmds.referenceQuery(_reference_node, namespace=True, shn = True)
            if _reference_name_space.startswith("{}__in__".format(_namespace)) or (not _namespace and not _reference_name_space) or (not _namespace and _reference_name_space.startswith(_input_task.file_code())):
                _file_name = cmds.referenceQuery(_reference_node, filename=True, withoutCopyNumber=True)
                if os.path.dirname(_file_name) == os.path.dirname(_production_file):
                    if _file_name == _production_file:
                        return True
                    else:
                        cmds.file(_production_file, loadReference = _reference_node)
                        return True

    # do somthing
    _ori_assemblies = cmds.ls(assemblies=True)
    
    if _namespace:
        rf = cmds.file(_production_file, r = True, ns = ":")
    else:
        rf = cmds.file(_production_file, r = True, ns = ":")
    rfn = cmds.referenceQuery(rf, rfn = True)
    _version_id = _input_task.last_version_id()
    attr.set_node_attr(rfn, _input_task_attr_output_id, _version_id, "false")
    
    _new_assemblies = cmds.ls(assemblies=True)
    _tops = list(set(_new_assemblies) - set(_ori_assemblies))
    if _tops:
        if cmds.objExists("geometry"):
            for _top in _tops:
                try:
                    cmds.parent(_top, "geometry")
                except:
                    pass
