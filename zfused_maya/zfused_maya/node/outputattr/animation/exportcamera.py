# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import sys
import logging

import maya.cmds as cmds
import maya.mel as mm

import zfused_api

from zcore import filefunc

import zfused_maya.core.record as record

import zfused_maya.node.core.alembiccache as alembiccache
import zfused_maya.node.core.texture as texture
import zfused_maya.node.core.material as material
import zfused_maya.node.core.fixmeshname as fixmeshname
import zfused_maya.node.core.renderinggroup as renderinggroup
import zfused_maya.node.core.referencefile as referencefile
import zfused_maya.node.core.attr as attr


__all__ = ["export_camera"]

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
        # sys.exit()

_fbx_load=cmds.pluginInfo("fbxmaya", query=True, loaded = True)
if not _fbx_load:
    try:
        logger.info("try load fbx plugin")
        cmds.loadPlugin("fbxmaya")
    except Exception as f:
        logger.error(f)





def export_camera_fbx(camera, fbx_path, frame_start, frame_end):
    cam_shape_old = cmds.listRelatives(camera, shapes = True)[0]
    cam_new       = cmds.camera()
    cam_shape_new = cam_new[1]
    cam_new       = cam_new[0]

    try:
        cmds.parent(cam_new, camera)
        cmds.setAttr(cam_new + '.translateX', 0)
        cmds.setAttr(cam_new + '.translateY', 0)
        cmds.setAttr(cam_new + '.translateZ', 0)
        cmds.setAttr(cam_new + '.rotateX', 0)
        cmds.setAttr(cam_new + '.rotateY', 0)
        cmds.setAttr(cam_new + '.rotateZ', 0)
        focal_length = cmds.getAttr(cam_shape_old + '.focalLength')
        cmds.setAttr(cam_shape_new + '.focalLength', focal_length)
        cmds.expression(string = cam_shape_new + '.focalLength = ' + cam_shape_old + '.focalLength;', object = cam_shape_new, alwaysEvaluate = True)
        cmds.rename(cam_new, 'cam_ue')
        cam_new = "cam_ue"
        cmds.parent(cam_new, world = True)
        cmds.parentConstraint(camera, cam_new, maintainOffset = True, weight = 1)
        cmds.select(cam_new, replace = True)
        # fbx export
        mm.eval('FBXResetExport;')
        mm.eval('FBXExportFileVersion "FBX201800"')
        mm.eval('FBXExportBakeComplexAnimation -v true;')
        mm.eval("FBXExportSplitAnimationIntoTakes -clear;")
        mm.eval('FBXExportConvertUnitString "cm"')
        mm.eval('FBXExportInputConnections -v 0')
        mm.eval('FBXExportSplitAnimationIntoTakes -v \"cam\" ' + str(frame_start) + ' ' + str(frame_end))
        mm.eval('FBXExport -f \"' + fbx_path + '\" -s')
    except Exception as e:
        print(e)
    finally:
        cmds.delete(cam_new)

def export_camera(*args, **kwargs):
    """ 上传动画文件
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

    # _production_path = _task_handle.production_path()
    # _temp_path = _output_link_handle.temp_path()

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
        _job = []
        _publish_dict = {}
        # _abc_suffix = "abc"

        _start_frame = int(cmds.playbackOptions(q = True,min = True))-PREPFRAME
        _end_frame = int(cmds.playbackOptions(q = True,max = True))+PREPFRAME

        _cams = cmds.ls("{}*".format(_file_code),fl = 1,type = "camera")
        if not _cams:
            return

        _camera_transforms = [] 
        for _cam in _cams:
            _cam_trans = cmds.listRelatives(_cam,p = 1)[0]
            _camera_transforms.append(_cam_trans)
            # 判定父组是否为偏移
            _cam_parent = cmds.listRelatives(_cam_trans, p = True)
            if _cam_parent:
                _cam_parent = _cam_parent[0]
                if _cam_parent == "offset_camera":
                    #冻结位移属性
                    cmds.setAttr("{}.inheritsTransform".format(_cam_trans), 0)

            _production_file = "{}/{}/{}{}".format(_production_file_dir, _file_index, _cam_trans, _suffix)
            _publish_file = "{}/{}/{}{}".format(_publish_file_dir, _file_index, _cam_trans, _suffix)

            if not os.path.isdir(os.path.dirname(_publish_file)):
                os.makedirs(os.path.dirname(_publish_file))

            export_camera_fbx(_cam_trans, _publish_file, _start_frame, _end_frame)

            # _joborder = alembiccache.create_frame_cache(_publish_file, _start_frame, _end_frame, _cam_trans, *EXPORTATTR)
            # _job.append(_joborder)

            # _json.append(["",_cam_trans,"",_production_file])
            _publish_dict[_publish_file] = _production_file

        # export camera alembic
        # cmds.AbcExport(j = _job)

        # publish
        for _key,_value in _publish_dict.items():
            filefunc.publish_file(_key, _value)

        # 还原
        for _camera in _camera_transforms:
            cmds.setAttr("{}.inheritsTransform".format(_camera), 1)

        # # publish file
        # _result = filefunc.publish_file(_publish_file, _production_file)
        # _result = filefunc.publish_file(_publish_file, _cover_file)

    except Exception as e:
        logger.error(e)
        return False

    # open orignal file
    # cmds.file(_current_file, o = True, f = True, pmt = True)
    return True