# coding:utf-8
# --author-- lanhua.zhou
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
import zfused_maya.node.core.element as element
import zfused_maya.node.core.alembiccache as alembiccache
import zfused_maya.node.core.fixmeshname as fixmeshname
import zfused_maya.node.core.renderinggroup as renderinggroup
import zfused_maya.node.core.yeticache as yeticache
import zfused_maya.node.core.displaylayer as displaylayer

__all__ = ["publish_abc"]
logger = logging.getLogger(__name__)

PREPFRAME = 8
EXPORTATTR = ["worldSpace", "writeVisibility", "uvWrite"]


# load abc plugin
_is_load = cmds.pluginInfo("AbcExport", query=True, loaded = True)
if not _is_load:
    try:
        logger.info("try load pgYetiMaya plugin")
        cmds.loadPlugin("AbcExport")
    except Exception as e:
        logger.error(e)
        sys.exit()

@core.viewportOff
def publish_abc(*args, **kwargs):
    """ publish alembiccache
    
    """
    def get_cam_info(abcSuffix,fileCode,startFrame,endFrame,_job = [],_json = [],_dict = {}):
        # _alljob = []
        _cams = cmds.ls("{}*".format(fileCode),fl = 1,type = "camera")
        if not _cams:
            return
        for _cam in _cams:
            _cam_trans = cmds.listRelatives(_cam,p = 1)[0]
            _production_file = "{}/{}/{}.{}".format(_production_file_dir,_file_index,_cam_trans,abcSuffix)
            _publish_file = "{}/{}/{}.{}".format(_publish_file_dir,_file_index,_cam_trans,abcSuffix)
            _joborder = alembiccache.create_frame_cache(_publish_file,startFrame,endFrame,_cam_trans,*EXPORTATTR)
            _job.append(_joborder)
            _json.append(["",_cam_trans,"",_production_file])
            _dict[_publish_file] = _production_file

    def get_asset_info(renderdag,abcSuffix,fileCode,startFrame,endFrame,_job = [],_json = [],_dict = {}):
        # _alljob = []
        _assets = yeticache.get_asset_list()
        fixmeshname.fix_deformed_mesh_name("_rendering", renderdag)
        for _dag in renderdag:
            _ns = cmds.referenceQuery(_dag,ns = 1)
            if _ns.startswith(":"):
                _ns = _ns[1:]
            if _ns in _assets:
                _sns = cmds.referenceQuery(_dag,ns = 1,shn = 1)
                _production_file = "{}/{}/{}.{}".format(_production_file_dir,_file_index,_sns,abcSuffix)
                _publish_file = "{}/{}/{}.{}".format(_publish_file_dir,_file_index,_sns,abcSuffix)
                _joborder = alembiccache.create_frame_cache(_publish_file,startFrame,endFrame,_dag,*EXPORTATTR)
                _job.append(_joborder)
                # 依次是：assetname,namespace,nodename,cachepath
                _json.append([_assets[_ns],_sns,_dag.split(":")[-1],_production_file])
                _dict[_publish_file] = _production_file


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
    _publish_json_file = "{}/{}/{}.{}{}".format(_task_handle.temp_path(),_attr_code,_file_code,_file_index, _suffix)

    _abc_suffix = "abc"

    _start_frame = int(cmds.playbackOptions(q = True,min = True))-PREPFRAME
    _end_frame = int(cmds.playbackOptions(q = True,max = True))+PREPFRAME
    
    # 单独发布接口，返回空发布全部
    renderdag = []
    if not renderdag:
        renderdag = renderinggroup.nodes()
    _norenders = displaylayer.norender_info(displaylayer.nodes())
    # enable norender attributes
    if _norenders:
        for i in _norenders:
            _attr = "{}.v".format(i)
            if cmds.objExists(_attr) and cmds.getAttr(_attr) != 0:
                cmds.setAttr(_attr,0)
    # get info
    _alljob = []
    _json_info = []
    upload_dict = {}
    # get_cam_info(_abc_suffix,_file_code,_start_frame,_end_frame,_alljob,_json_info,upload_dict)
    get_asset_info(renderdag,_abc_suffix,_file_code,_start_frame,_end_frame,_alljob,_json_info,upload_dict)
    
    try:
        with open(_publish_json_file,"w") as info:
            json.dump(_json_info, info,indent = 4,separators=(',',':'))
        # _result = filefunc.publish_file(_publish_json_file,_production_json_file,True)
        _result = filefunc.publish_file(_publish_json_file,_production_json_file)
        cmds.AbcExport(j = _alljob)
        for _k,_v in upload_dict.items():
            # _result = filefunc.publish_file(_k,_v,True)
            _result = filefunc.publish_file(_k,_v)

    except Exception as e:
        logger.error(e)
        return False
    return True

if __name__ == '__main__':
    publish_abc()
