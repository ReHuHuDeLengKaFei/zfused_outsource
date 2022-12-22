# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os.path
import sys,time,logging,zfused_api
import maya.cmds as cmds

from zcore import filefunc,zfile

from zfused_maya.node.core import renderinggroup,alembiccache,property

from pymel import core

import maya.mel as mel

__all__ = ["publish_camera"]

logger = logging.getLogger(__name__)
_is_load = cmds.pluginInfo("AbcExport", query=True, loaded = True)
if not _is_load:
    try:
        logger.info("try load alembic plugin")
        cmds.loadPlugin("AbcExport")
    except Exception as e:
        logger.error(e)
        sys.exit()

# 缓存预留帧 后面需要存放在数据库上 
PREPFRAME = 8
EXPORTATTR = ["worldSpace", "writeVisibility", "uvWrite","writeUVSets"]


def publish_camera(*args, **kwargs):
    """ 发布动画abc
    """
    _task_id, _output_attr_id = args
    _output_attr_handle = zfused_api.attr.Output(_output_attr_id)
    _file_format = _output_attr_handle.format()
    _suffix = _output_attr_handle.suffix()
    _attr_code = _output_attr_handle.code()

    _task = zfused_api.task.Task(_task_id)
    _task_step = _task.project_step().code()
    # _production_path = _task.cache_path()
    # if not os.path.dirname(_production_path):
    _production_path = _task.production_path()
    _project_entity = _task.project_entity()
    _file_code =_task.file_code()
    if kwargs.get("fix_version"):
        _file_index = "{:0>4d}".format(_task.last_version_index( 0 ))
    else:
        _file_index = "{:0>4d}".format(_task.last_version_index() + 1)

    _project_porperty = _project_entity.property()
    print(_project_porperty)

    _start_frame = int(cmds.playbackOptions(q = True,min = True))-50
    _end_frame = int(cmds.playbackOptions(q = True,max = True))+PREPFRAME

    _publish_path = _task.temp_path()
    _cache_path =_task.cache_path()
    # renderdags = renderinggroup.nodes()
    _trans_list =[]

    _cameras = _project_porperty.get('camera')
    if not _cameras:
        _cameras = _project_porperty.get('camera')

    #_cameras = _project_porperty.get('asset')
    print(_cameras)

    if not _cameras:
        return True

    for _camera in _cameras:
        # _attr_code = "camera"
        camera_node =_camera.get('node')        
        camera_publish_file ='{}/{}/{}.{}{}'.format(_publish_path,"camera",_file_code,_file_index,_suffix)
        camera_cache_file = '{}/{}/{}.{}{}'.format(_cache_path,_attr_code,_file_code,_file_index,_suffix)
        camera_cover_file = '{}/{}/{}{}'.format(_cache_path,_attr_code,_file_code,_suffix)
        
        camera_dict ={}
        camera_dict['publish_file'] = camera_publish_file
        camera_dict['cover_file'] = camera_cover_file
        camera_dict['cache_file'] = camera_cache_file
        _camera['path'] = camera_cover_file
        
        _trans_list.append(camera_dict)
    
    # 记录摄像机数据
    _project_entity.update_property('Camera',_cameras)
    _datas  = _project_entity.property()
    property._write_to_disk(_project_entity,_datas)

    try:
        _cache_file_info = []
        for _tran in _trans_list:
            publish_file = _tran.get('publish_file')
            cover_file   = _tran.get('cover_file')
            cache_file   = _tran.get('cache_file')
            _result = filefunc.publish_file(publish_file,cache_file)
            _result = filefunc.publish_file(publish_file,cover_file)

            _file_info = zfile.get_file_info(publish_file, cache_file)
            _cover_file_info = zfile.get_file_info(publish_file, cover_file)
            _cache_file_info.append(_file_info)
            _cache_file_info.append(_cover_file_info)

        # record production file
        if _cache_file_info:
            zfused_api.task.new_production_file(_cache_file_info, _task_id, _output_attr_id, int(_file_index), fix_version = kwargs.get("fix_version"))

    except Exception as e:
        logger.error(e)
        print(e)
        return False
    return True







def publish_ue_camera(*args,**kwargs):

    """ 发布动画abc
    """

    def export_fbx(frame_start, frame_end, fbx_path, camera=None):
        if camera:
            cmds.select(clear=True)
            cmds.select(camera, replace=True)
        mel.eval('FBXResetExport;')
        mel.eval('FBXExportFileVersion "FBX201800"')
        mel.eval('FBXExportBakeComplexAnimation -v true;')
        mel.eval("FBXExportSplitAnimationIntoTakes -clear;")
        mel.eval('FBXExportConvertUnitString "cm"')
        mel.eval('FBXExportInputConnections -v 0')
        mel.eval('FBXExportSplitAnimationIntoTakes -v \"cam\" ' + str(frame_start) + ' ' + str(frame_end))
        mel.eval('FBXExport -f \"' + fbx_path + '\" -s')
        #cmds.file(fbx_path,force=True,options="v=0;",type = "FBX export",pr=True,es =True)
    _task_id, _output_attr_id = args
    _output_attr_handle = zfused_api.attr.Output(_output_attr_id)
    _file_format = _output_attr_handle.format()
    _suffix = _output_attr_handle.suffix()
    _attr_code = _output_attr_handle.code()


    _task = zfused_api.task.Task(_task_id)
    _task_step = _task.project_step().code()
    # _production_path = _task.cache_path()
    # if not os.path.dirname(_production_path):
    _production_path = _task.production_path()
    _project_entity = _task.project_entity()
    _file_code =_task.file_code()
    if kwargs.get("fix_version"):
        _file_index = "{:0>4d}".format(_task.last_version_index( 0 ))
    else:
        _file_index = "{:0>4d}".format(_task.last_version_index() + 1)

    _project_porperty = _project_entity.property()
    print(_project_porperty)

    _start_frame = int(cmds.playbackOptions(q = True,min = True))-50
    _end_frame = int(cmds.playbackOptions(q = True,max = True))+PREPFRAME

    _publish_path = _task.temp_path()
    _cache_path =_task.cache_path()
    # renderdags = renderinggroup.nodes()
    _trans_list =[]

    _cameras = _project_porperty.get('camera')
    if not _cameras:
        _cameras = get_local_camera(_task_id)
    #_cameras = _project_porperty.get('asset')
    print(_cameras)

    if not _cameras:
        return True
    cam_old = _cameras[0]
    cam_shape_old =core.listRelatives(cam_old, shapes = True)[0]
    cam_new = core.camera()
    cam_shape_new = cam_new[1]
    cam_new       = cam_new[0]
    core.parent(cam_new, cam_old)
    core.setAttr(cam_new + '.translateX', 0)
    core.setAttr(cam_new + '.translateY', 0)
    core.setAttr(cam_new + '.translateZ', 0)
    core.setAttr(cam_new + '.rotateX', 0)
    core.setAttr(cam_new + '.rotateY', 0)
    core.setAttr(cam_new + '.rotateZ', 0)
    focal_length =core. getAttr(cam_shape_old + '.focalLength')
    core.setAttr(cam_shape_new + '.focalLength', focal_length)
    core.expression(string = cam_shape_new + '.focalLength = ' + cam_shape_old + '.focalLength;', object = cam_shape_new, alwaysEvaluate = True)
    core.rename(cam_new, 'cam_ue')
    core.parent(cam_new, world = True)
    core.parentConstraint(cam_old, cam_new, maintainOffset = True, weight = 1)
    #cmds.select(clear=True)
    core.select(cam_new, replace = True)
    # __out_fbx_path = '{}/{}/{}{}'.format(_publish_path,_attr_code,_file_code,_suffix)
    # _out_fbx_path = os.path.abspath(__out_fbx_path)
    _out_fbx_path = 'D:/temp/pygc/{}{}'.format(_file_code,_suffix)
    #_out_fbx_path = r'D:/zfused/work/PYGC/dcc/shot/ep050/seq004/shot171/animation/camera/temps.001.fbx'
    if not os.path.exists(os.path.dirname(_out_fbx_path)):
        os.makedirs(os.path.dirname(_out_fbx_path))
    _production_fbx_path = '{}/{}/{}.{}{}'.format(_cache_path,_attr_code,_file_code,_file_index,_suffix)
    _production_cover_fbx_path = '{}/{}/{}{}'.format(_cache_path,_attr_code,_file_code,_suffix)
    print(_out_fbx_path)

    export_fbx(_start_frame, _end_frame, _out_fbx_path)
    try:
        #传输文件
        filefunc.publish_file(_out_fbx_path, _production_fbx_path)
        filefunc.publish_file(_out_fbx_path, _production_cover_fbx_path)
        #记录文件
    # production file
        _file_info = zfile.get_file_info(_out_fbx_path, _production_fbx_path)
        _cover_file_info = zfile.get_file_info(_out_fbx_path, _production_cover_fbx_path)
        zfused_api.task.new_production_file([_file_info, _cover_file_info], _task_id, _output_attr_id,int(_file_index))
    except Exception as e:
        return False
    return True











def get_local_camera(task_Id):
    """
    获取本地摄像机
    :return:
    """
    _task = zfused_api.task.Task(task_Id)
    _project_entity = _task.project_entity()
    _name = _project_entity.file_code()
    _camera_shape = cmds.ls("*%s*" % _name, type="camera")

    if not _camera_shape:
        return None
    return cmds.listRelatives(_camera_shape,p=True)




    



