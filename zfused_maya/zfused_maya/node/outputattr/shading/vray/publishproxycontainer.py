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
    output_entity_type, output_entity_id, output_attr_id = args

    _output_attr_handle = zfused_api.outputattr.OutputAttr(output_attr_id)
    _suffix = _output_attr_handle.suffix()
    _file_format = _output_attr_handle.format()
    _attr_code = _output_attr_handle.code()

    _project_step_id = _output_attr_handle.data()["ProjectStepId"]
    _project_step_handle = zfused_api.step.ProjectStep(_project_step_id)
    _step_code = _project_step_handle.code()
    _software_code = zfused_api.software.Software(_project_step_handle.data()["SoftwareId"]).code()
    
    _output_link_handle = zfused_api.objects.Objects(output_entity_type, output_entity_id)
    _production_path = _output_link_handle.production_path()
    _temp_path = _output_link_handle.temp_path()
    _file_code = _output_link_handle.file_code()

    _task = _output_link_handle.tasks([_project_step_id])[0]
    _task_id = _task["Id"]
    _task_handle = zfused_api.task.Task(_task_id)
    if kwargs.get("fix_version"):
        _file_index = "{:0>4d}".format(_task_handle.last_version_index( 0 ))
    else:
        _file_index = "{:0>4d}".format(_task_handle.last_version_index() + 1)

    _production_file = "{}/{}/{}/{}/{}.{}{}".format( _production_path, _step_code, _software_code, _attr_code, _file_code, _file_index, _suffix )
    _production_file_dir = os.path.dirname(_production_file)
    _cover_file = "{}/{}/{}/{}/{}{}".format(_production_path, _step_code, _software_code, _attr_code, _file_code, _suffix)
    _publish_file = "{}/{}/{}/{}/{}.{}{}".format( _temp_path, _step_code, _software_code, _attr_code, _file_code, _file_index, _suffix )
    _publish_file_dir = os.path.dirname(_publish_file)
    if not os.path.isdir(_publish_file_dir):
        os.makedirs(_publish_file_dir)

    try:
        _proxy_ele = "proxy"
        # get element file path
        _proxy_path = "%s/%s/%s/%s/%s.%s%s"%(_production_path,  _step_code, _software_code,_proxy_ele, _file_code, _file_index, _suffix)
        _cover_proxy_file = "%s/%s/%s/%s/%s%s"%(_production_path,  _step_code, _software_code,_proxy_ele, _file_code, _suffix)

        _current_file = cmds.file(q = 1,sn = 1)
        # cmds.file(new = 1,f = 1)
        # proxycontainer.create_vray_container(_proxy_path, _gpu_path)
        # cmds.file(rename = _publish_file)
        # cmds.file(save = True, type = _file_format, f = True)
        # publish file
        #print(_production_file)
        _result = filefunc.publish_file(_proxy_path, _production_file)
        
        # if not os.path.exists(_cover_file):
            # cmds.file(new = 1,f = 1)
            # proxycontainer.create_vray_container(_cover_proxy_file,_cover_gpu_file)
            # cmds.file(rename = _cover_publish_file)
            # cmds.file(save = True, type = _file_format, f = True)
            # publish file
        _result = filefunc.publish_file(_cover_proxy_file, _cover_file)
            
    except Exception as e:
        logger.error(e)
        return False
    # open orignal file
    if _current_file:
        cmds.file(_current_file, o = True, f = True, pmt = False)
    return True

if __name__ == '__main__':
    publish_proxy_container()