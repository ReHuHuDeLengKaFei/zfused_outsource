# coding:utf-8
# --author-- ning.qin
from __future__ import print_function

import os
import sys
import shutil
import logging
import json
import time

import maya.cmds as cmds
from pymel.core import *

import zfused_api
from zfused_maya.core import record
from zfused_maya.node.core import renderinggroup
from zcore import filefunc,zfile

logger = logging.getLogger(__name__)
_is_load = cmds.pluginInfo("mayaUsdPlugin", query=True, loaded = True)
if not _is_load:
    try:
        logger.info("try load usd plugin")
        cmds.loadPlugin("mayaUsdPlugin")
    except Exception as e:
        logger.error(e)
        sys.exit()


def export_usd(rendering_group, usd_path):
    select(rendering_group, r = True)
    cmds.mayaUSDExport(file = usd_path, selection = True, exportMaterialCollections = True)


def publish_usd(*args, **kwargs):
    _task_id, _output_attr_id = args
    print('----------------------------------publish usd------------------------------------')

    _output_attr_handle = zfused_api.attr.Output(_output_attr_id)
    _file_format = _output_attr_handle.format()
    _suffix = _output_attr_handle.suffix()
    _attr_code = _output_attr_handle.code()
    _task = zfused_api.task.Task(_task_id)
    _production_path = _task.production_path()
    _project_entity_production_path = _task.project_entity().production_path()
    _temp_path = _task.temp_path()
    _file_code = _task.file_code()
    if kwargs.get("fix_version"):
        _file_index = "{:0>4d}".format(_task.last_version_index( 0 ))
    else:
        _file_index = "{:0>4d}".format(_task.last_version_index() + 1)

    _production_file = "{}/{}/{}.{}{}".format( _production_path, _attr_code, _file_code, _file_index, _suffix )
    _cover_file = "{}/{}/{}{}".format(_production_path, _attr_code, _file_code, _suffix)
    _publish_file = "{}/{}/{}.{}{}".format( _temp_path, _attr_code, _file_code, _file_index, _suffix )

    _publish_file_dir = os.path.dirname(_publish_file)
    print(_publish_file)
    if not os.path.isdir(_publish_file_dir):
        os.makedirs(_publish_file_dir)
    _rendering_group = renderinggroup.nodes()
    print(_rendering_group)

    try:
        if _rendering_group:
            export_usd(_rendering_group, _publish_file)
            _result = filefunc.publish_file(_publish_file,_production_file)
            _result = filefunc.publish_file(_publish_file,_cover_file)
    except Exception as e:
        logger.error(e)
        print(e)
        return False
    return True