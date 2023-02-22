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

ROOT_JOINT_NAME = 'DeformationSystem'
# ROOT_JOINT_NAME = 'Root_M'
ROOT_GEO_NAME = 'geometry_group'

logger = logging.getLogger(__name__)
_is_load = cmds.pluginInfo("fbxmaya", query=True, loaded = True)
if not _is_load:
    try:
        logger.info("try load fbx plugin")
        cmds.loadPlugin("fbxmaya")
    except Exception as e:
        logger.error(e)
        sys.exit()

def read_json_file(file_path):
    with open(os.path.abspath(file_path), "r") as json_file:
        json_dict = json.load(json_file)
    return json_dict if json_dict else {}
def write_json_file(json_dict, file_path):
    with open(file_path,"w") as json_file:
        json_file.write(json.dumps(json_dict,indent = 4,separators=(',',':'), sort_keys = False))
        json_file.close()

def check_root_geo_num():
    root_geo_list = []
    transform_node_list = ls(type = 'transform')
    for transform_node in transform_node_list:
        if str(transform_node).startswith('CHR_') and str(transform_node).endswith('_Geometry'):
            root_geo_list.append(transform_node)
        elif str(transform_node).startswith('Prop_') and str(transform_node).endswith('_Geometry'):
            root_geo_list.append(transform_node)
    return len(root_geo_list)

def get_root_geo():
    root_geo = ''
    asset_name = ''
    transform_node_list = ls(type = 'transform')
    for transform_node in transform_node_list:
        if str(transform_node).endswith(ROOT_GEO_NAME):
            root_geo = transform_node
            asset_name = root_geo.replace(ROOT_GEO_NAME, '')
    return root_geo, asset_name

def check_root_joint_num():
    root_joint_list = ls(ROOT_JOINT_NAME)
    return len(root_joint_list)

def get_root_joint():
    root_joint = ls(ROOT_JOINT_NAME)[0]
    return root_joint


def export_fbx(rendering_group, fbx_path, frame_start = 0, frame_end = 1):
    select(rendering_group, r = True)
    frame_start = str(frame_start)
    frame_end   = str(frame_end)
    mel.eval('FBXResetExport;')
    mel.eval('FBXExportFileVersion "FBX202000"')
    mel.eval('FBXExportInputConnections -v false;')
    # mel.eval('FBXExportBakeComplexAnimation -v true;')
    mel.eval("FBXExportSplitAnimationIntoTakes -clear;")
    mel.eval('FBXExportConvertUnitString "cm"')
    mel.eval('FBXExportInputConnections -v 0')
    # mel.eval('FBXExportSplitAnimationIntoTakes -v \"Take_001\" ' + frame_start + ' ' + frame_end)
    mel.eval('FBXExport -f \"' + fbx_path + '\" -s')

def export_fbx_rig(fbx_path):
    mel.eval('FBXResetExport;')
    mel.eval('FBXExportFileVersion "FBX202000"')
    mel.eval('FBXExportBakeComplexAnimation -v false;')
    mel.eval('FBXExportConvertUnitString "cm"')
    mel.eval('FBXExportInputConnections -v 0')
    mel.eval('FBXExport -f \"' + fbx_path + '\" -s')

def export_rig(rendering_group, fbx_path):
    root_joint = get_root_joint()
    root_geo = rendering_group

    root_joint_parented = parent(root_joint, world = True)
    root_geo_parented = parent(root_geo, world = True)
    select(root_joint_parented, replace = True)
    select(root_geo_parented, add = True)
    export_fbx_rig(fbx_path)


def publish_ue(*args, **kwargs):
    _task_id, _output_attr_id = args
    print('----------------------------------publish ue------------------------------------')

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
    _rendering_group = renderinggroup.nodes()[0]
    print(_rendering_group)

    try:
        if _rendering_group:
            export_rig(_rendering_group, _publish_file)
            _result = filefunc.publish_file(_publish_file,_production_file)
            _result = filefunc.publish_file(_publish_file,_cover_file)
    except Exception as e:
        logger.error(e)
        print(e)
        return False
    return True