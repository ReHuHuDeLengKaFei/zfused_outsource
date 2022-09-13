# coding:utf-8
# --author-- binglu.wang
from __future__ import print_function

import os
import sys
import logging

import maya.cmds as cmds

import zfused_api
from zcore import filefunc

import zfused_maya.core.record as record

import zfused_maya.node.core.texture as texture
import zfused_maya.node.core.renderinggroup as renderinggroup

__all__ = ["publish_proxy"]

logger = logging.getLogger(__name__)


_is_load = cmds.pluginInfo("mtoa", query=True, loaded = True)
if not _is_load:
    try:
        logger.info("try load mtoa plugin")
        cmds.loadPlugin("mtoa")
    except Exception as e:
        logger.error(e)
        sys.exit()

def publish_proxy(*args, **kwargs):
    """ publish rsProxy

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
        # change_tex
        # _texture_files = texture.files()
        # if _texture_files:
        #     _path_set = texture.paths(_texture_files)[0]
        #     _intersection_path = max(_path_set)
        #     _file_nodes = texture.nodes()
        #     if _file_nodes:
        #         texture.change_node_path(_file_nodes, _intersection_path, _production_path + "/texture")

        _is_rendering = renderinggroup.nodes()
        # save publish file
        cmds.select(_is_rendering,r = 1,ne = 1)
        cmds.arnoldExportAss(_is_rendering, f = _publish_file, fp = 1, s = 1, bb = 1)

        # publish file
        _result = filefunc.publish_file(_publish_file, _production_file)
        _result = filefunc.publish_file(_publish_file, _cover_file)

    except Exception as e:
        logger.error(e)
        return False
    # open orignal file
    # cmds.file(_current_file, o = True, f = True, pmt = True)
    return True

if __name__ == '__main__':
    publish_proxy()