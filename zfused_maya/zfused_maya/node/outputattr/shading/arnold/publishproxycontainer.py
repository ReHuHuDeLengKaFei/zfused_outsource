# coding:utf-8
# --author-- binglu.wang
from __future__ import print_function

import os
import logging

import maya.cmds as cmds

import zfused_api
from zcore import filefunc

import zfused_maya.core.record as record

import zfused_maya.node.core.proxycontainer as proxycontainer

__all__ = ["publish_proxy_container"]

logger = logging.getLogger(__name__)


def publish_proxy_container(*args, **kwargs):
    """ publish rsProxy container

    :rtype: bool
    """
    _attr_code = "proxycontainer"
    _file_suffix = "mb"
    _file_format = "mayaBinary"

    _gpu_ele = "gpu"
    _gpu_suffix = "abc"
    _proxy_ele = "proxy"
    _proxy_suffix = "ass"

    # get current task id
    _task_id = record.current_task_id()
    _task_handle = zfused_api.task.Task(_task_id)
    _object_handle = _task_handle.project_entity()
    _file_code = _object_handle.file_code()
    _file_index = _task_handle.last_version_index() + 1

    _production_path = _task_handle.production_path()
    _production_file = "%s/%s/%s.%04d.%s"%(_production_path, _attr_code, _file_code, _file_index, _file_suffix)
    _cover_file = "%s/%s/%s.%s"%(_production_path, _attr_code, _file_code, _file_suffix)

    # get publish file path
    _temp_path = "{}/{}".format(_task_handle.temp_path(), _attr_code)
    _file_name = "%s.%04d"%(_file_code, _file_index)
    _publish_file = "%s/%s.%04d.%s"%(_temp_path, _file_code, _file_index, _file_suffix)
    _cover_publish_file = "%s/%s.%s"%(_temp_path, _file_code, _file_suffix)

    _publish_file_dir = os.path.dirname(_publish_file)

    # get element file path
    _gpu_path = "%s/%s/%s.%04d.%s"%(_production_path, _gpu_ele, _file_code, _file_index, _gpu_suffix)
    _cover_gpu_file = "%s/%s/%s.%s"%(_production_path, _gpu_ele, _file_code, _gpu_suffix)
    _proxy_path = "%s/%s/%s.%04d.%s"%(_production_path, _proxy_ele, _file_code, _file_index, _proxy_suffix)
    _cover_proxy_file = "%s/%s/%s.%s"%(_production_path, _proxy_ele, _file_code, _proxy_suffix)

    if not os.path.isdir(_publish_file_dir):
        os.makedirs(_publish_file_dir)
    try:
        _current_file = cmds.file(q = 1,sn = 1)
        # cmds.file(rename = _publish_file)
        # cmds.file(save = True, type = _file_format, f = True)
        cmds.file(new = 1,f = 1)
        proxycontainer.create_ass_container(_proxy_path, _gpu_path)
        cmds.file(rename = _publish_file)
        cmds.file(save = True, type = _file_format, f = True)
        # publish file
        _result = filefunc.publish_file(_publish_file, _production_file)
        
        if not os.path.exists(_cover_file):
            cmds.file(new = 1,f = 1)
            proxycontainer.create_ass_container(_cover_proxy_file,_cover_gpu_file)
            cmds.file(rename = _cover_publish_file)
            cmds.file(save = True, type = _file_format, f = True)
            # publish file
            _result = filefunc.publish_file(_cover_publish_file, _cover_file)
            
    except Exception as e:
        logger.error(e)
        return False
    # open orignal file
    if _current_file:
        cmds.file(_current_file, o = True, f = True, pmt = False)
    return True

if __name__ == '__main__':
    publish_proxy_container()