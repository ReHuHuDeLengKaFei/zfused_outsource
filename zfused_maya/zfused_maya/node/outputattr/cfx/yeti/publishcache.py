# coding:utf-8
# --author-- binglu.wang
from __future__ import print_function

import os
import sys
import json
import logging

import maya.cmds as cmds

import zfused_api
from zcore import filefunc

import zfused_maya.core.record as record
import zfused_maya.node.core as core
import zfused_maya.node.core.yeti as yeti
import zfused_maya.node.core.yeticache as yeticache

__all__ = ["publish_cache"]

logger = logging.getLogger(__name__)

PREPFRAME = 8

# load yeti plugin
_is_load = cmds.pluginInfo("pgYetiMaya", query=True, loaded = True)
if not _is_load:
    try:
        logger.info("try load pgYetiMaya plugin")
        cmds.loadPlugin("pgYetiMaya")
    except Exception as e:
        logger.error(e)
        sys.exit()

@core.viewportOff
def publish_cache(*args, **kwargs):
    """ publish yeticache

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

    _production_json_file = "{}/{}/{}.{}{}".format(_task_handle.production_path(),_attr_code,_file_code,_file_index,_suffix)
    _publish_json_file = "{}/{}/{}.{}{}".format(_task_handle.temp_path(),_attr_code,_file_code,_file_index,_suffix)

    _start_frame = int(cmds.playbackOptions(q = True,min = True))-PREPFRAME
    _end_frame = int(cmds.playbackOptions(q = True,max = True))+PREPFRAME

    try:
        _pgnodes = yeticache.nodes()
        _info,_batch = yeticache.get_upload_info(_pgnodes,4,"{}/{}".format(_production_file_dir, _file_index), "{}/{}".format(_publish_file_dir, _file_index))
        _publish_dict = {}
        _path_list = []
        _path = ""
        _yeti_nodes = []
        for _k,_v in _batch.items():
            _publish_dict[_v[0]] = _v[1]
            logger.info("export cache: {}".format(_v[0]))
            _yeti_nodes.append(_k)
            # yeticache.create_cache(_k,_v[0],_start_frame,_end_frame,3)
            # _path += "|{}".format(_v[0])
            _path_list.append(_v[0])
        _path = "|".join(_path_list)
        cmds.pgYetiCommand(_yeti_nodes, writeCache = _path,range = [_start_frame, _end_frame], samples = 3,updateViewport = 0, generatePreview = 0)
        with open(_publish_json_file,"w") as info:
            json.dump(_info, info,indent = 4,separators=(',',':'))
        # _result = filefunc.publish_file(_publish_json_file,_production_json_file,True)
        _result = filefunc.publish_file(_publish_json_file,_production_json_file)
        for _k1,_v1 in _publish_dict.items():
            _local_path = os.path.dirname(_k1)
            for _file in os.listdir(_local_path):
                _production_file = "{}/{}".format(os.path.dirname(_v1),_file)
                _publish_file = "{}/{}".format(_local_path,_file)
                # _result = filefunc.publish_file(_publish_file, _production_file,True)
                _result = filefunc.publish_file(_publish_file, _production_file)
    except Exception as e:
        logger.error(e)
        return False
    return True

if __name__ == '__main__':
    publish_cache()
