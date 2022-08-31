 # coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import shutil
import logging
import datetime
import time
import json

import maya.cmds as cmds

import zfused_api

logger = logging.getLogger(__name__)


# 此函数输入参数需要修改 目前不算合理
def import_shader_record(argv_task_id, argv_attr_id, argv_attr_code, argv_attr_type, argv_attr_mode, argv_attr_local):

    if not argv_task_id:
        return
    _task_handle = zfused_api.task.Task(argv_task_id)
    _version_id = _task_handle.last_version_id()
    if not _version_id:
        return
    _production_path = _task_handle.production_path()
    _version_handle = zfused_api.version.Version(_version_id)
    _file_index = _version_handle.index()
    # _production_file = _version_handle.production_file()
    # get from production 
    _production_file = zfused_api.zFused.get("production_file", filter = {"TaskId": argv_task_id, "ProjectStepAttrId": argv_attr_id, "Index": int(_file_index)})
    if _production_file:
        _production_file = _production_file[0]["Path"]
    else:
        # _production_file = "{}/{}/{}.{}{}".format(_production_path,_input_attr_handle.code(),_task_handle.file_code(),_file_index, _file_suffix)
        return
    #print(_production_file)
    _record = []
    
    # read json file
    with open(_production_file, "r") as handle:
        data = handle.read()
        _record = json.loads(data)
    if not _record:
        return

    # assign material
    for _sg in _record:
        #print(_sg)
        _meshs = _sg["mesh"]
        if _meshs:
            for _mesh in _meshs:
                cmds.select(cmds.ls("*:{}".format(_mesh)), r = True)
                cmds.hyperShade(assign = _sg["shader"][0])
    cmds.select(cl = True)