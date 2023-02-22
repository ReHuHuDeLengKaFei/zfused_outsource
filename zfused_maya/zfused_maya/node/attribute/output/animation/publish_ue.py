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
from zcore import zfile,transfer,filefunc
from zfused_maya.core import record

CAM_KEYWORD_LIST = ['cam', 'CAM', 'FKXR','EP']
# ASSET_TYPE_LIST = ['Chars', 'Props']
ASSET_TYPE_LIST = ['char', 'prop', 'env']
# ASSET_TYPE_LIST = ['ch', 'env', 'pr', 'wolf']
ATTR_LIST_TRANSFORM = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
ATTR_LIST_CAM_SHAPE = ['focalLength']
ROOT_JOINT_NAME = 'DeformationSystem'
# ROOT_JOINT_NAME = 'Root_M'
# ROOT_GEO_NAME = 'geometry_grp'
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

def get_playback_frames(*args):
    start_frame = int(playbackOptions(query = True, minTime = True))
    end_frame = int(playbackOptions(query = True, maxTime = True))
    return start_frame, end_frame

def export_fbx(frame_start, frame_end, fbx_path):
    frame_start = str(frame_start)
    frame_end   = str(frame_end)
    mel.eval('FBXResetExport;')
    mel.eval('FBXExportFileVersion "FBX201800"')
    mel.eval('FBXExportInputConnections -v false;')
    mel.eval('FBXExportBakeComplexAnimation -v true;')
    mel.eval("FBXExportSplitAnimationIntoTakes -clear;")
    mel.eval('FBXExportConvertUnitString "cm"')
    mel.eval('FBXExportInputConnections -v 0')
    mel.eval('FBXExportSplitAnimationIntoTakes -v \"Take_001\" ' + frame_start + ' ' + frame_end)
    mel.eval('FBXExport -f \"' + fbx_path + '\" -s')

def get_cam_list(*args):
	cam_list = []
	cam_list_all = ls(type = 'camera')
	for cam in cam_list_all:
		for cam_keyword in CAM_KEYWORD_LIST:
			if cam_keyword in str(cam):
			    cam_list.append(listRelatives(cam, parent = True)[0])
	return cam_list

def get_cam_dict(frame_ext = 10):
    cam_old       = get_cam_list()[0]
    cam_shape_old = listRelatives(cam_old, shapes = True)[0]
    cam_new = camera()
    cam_shape_new = cam_new[1]
    cam_new = cam_new[0]
    cam_name = str(cam_old)
    rename(cam_old, str(cam_old) + '1')
    rename(cam_new, cam_name)
    parent(cam_new, cam_old)
    setAttr(cam_new + '.translateX', 0)
    setAttr(cam_new + '.translateY', 0)
    setAttr(cam_new + '.translateZ', 0)
    setAttr(cam_new + '.rotateX', 0)
    setAttr(cam_new + '.rotateY', 0)
    setAttr(cam_new + '.rotateZ', 0)
    focal_length = getAttr(cam_shape_old + '.focalLength')
    setAttr(cam_shape_new + '.focalLength', focal_length)
    parent(cam_new, world = True)
    parentConstraint(cam_old, cam_new, maintainOffset = True, weight = 1)

    cam_export = camera()
    cam_shape_export = cam_export[1]
    cam_export = cam_export[0]
    
    print(get_playback_frames())
    frame_start, frame_end = get_playback_frames()
    frame_start_ext = frame_start - frame_ext
    frame_end_ext = frame_end + frame_ext
    
    cam_value_dict = collections.OrderedDict()
    cam_value_dict['cam_name'] = cam_name
    cam_value_dict['frame_start'] = frame_start_ext
    cam_value_dict['frame_end']   = frame_end_ext
    cam_value_dict['focal_length'] = focal_length
    cam_value_dict['focal_length_key_list'] = []

    if keyframe(cam_shape_old, attribute = 'focalLength', query = True, keyframeCount = True) != 0:
        attr_node = PyNode(cam_shape_old + '.focalLength')
        for frame in range(frame_start_ext, frame_end_ext):
            attr_value = attr_node.get(time = frame)
            cam_value_dict['focal_length_key_list'].append(attr_value)
    
    return cam_value_dict

def check_root_joint():
    root_check_dict = collections.OrderedDict()

    for asset_type in ASSET_TYPE_LIST:
        asset_dict = collections.OrderedDict()
        ref_list = ls(references = True)
        if ref_list != []:
            for ref in ref_list:
                try:
                    ref_path = referenceQuery(ref, filename = True)
                    asset_type_dir = '/' + asset_type + '/'
                    if asset_type_dir in ref_path:
                        ref_namespace = referenceQuery(ref, namespace = True).split(':')[-1]
                        root_exist = objExists(ref_namespace + ':' + ROOT_NAME)
                        root_check_dict[ref_namespace] = root_exist
                except:
                    print(ref, '            bad bad')
    return(root_check_dict)

def export_shot(shot_data_dir, zfused_dict = {}, frame_ext = 10):
    #ogs(pause = True)
    ref_count = 0
    for asset_type in ASSET_TYPE_LIST:
        asset_type_dir = '/' + asset_type + '/'
        ref_list = ls(references = True)
        if ref_list != []:
            for ref in ref_list:
                try:
                    ref_path = referenceQuery(ref, filename = True)
                    if asset_type_dir in ref_path:
                        ref_count += 1
                except:
                    print(ref, '            bad bad')
    #print(ref_count)
    progress_window = window(title = u'大家好我是进度条')
    columnLayout()
    progressControl = progressBar(maxValue = ref_count + 1, width = 300)
    showWindow(progress_window)

    file_name = os.path.splitext(os.path.split(sceneName())[1])[0].split('.')[0]
    version   = 0
    try:
        version   = os.path.splitext(os.path.split(sceneName())[1])[0].split('.')[1]
    except:
        pass
    frame_start, frame_end = get_playback_frames()
    frame_start_ext = frame_start - frame_ext
    frame_end_ext = frame_end + frame_ext

    file_export_list = []

    shot_dict = collections.OrderedDict()
    shot_dict['shot_name'] = file_name
    shot_dict['version']   = version
    shot_dict['maya_file'] = sceneName()
    shot_dict['shot_data_dir']   = shot_data_dir
    shot_dict['frame_start'] = frame_start
    shot_dict['frame_end']   = frame_end
    shot_dict['frame_start_ext'] = frame_start_ext
    shot_dict['frame_end_ext']   = frame_end_ext
    cam_dict  = collections.OrderedDict()
    char_dict = collections.OrderedDict()
    shot_dict['cam'] = cam_dict

    fps = currentUnit(time = True, query = True)
    shot_dict['fps'] = fps
    _time = time.localtime(time.time())
    time_formated = '{}.{}.{} {}:{}:{}'.format(_time.tm_year, _time.tm_mon, _time.tm_mday, _time.tm_hour, _time.tm_min, _time.tm_sec)
    shot_dict['time'] = time_formated
    shot_dict['zfused'] = zfused_dict

    
    if get_cam_list():
        cam_value_dict = get_cam_dict(frame_ext)
        cam_name = cam_value_dict['cam_name']
        cam_fbx_file  = os.path.join(shot_data_dir, cam_name + '.fbx').replace('\\', '/')
        # cam_fbx_name  = os.path.split(cam_fbx_file)[1]
        cam_dict[cam_name] = collections.OrderedDict()
        cam_dict[cam_name]['fbx']  = cam_fbx_file
        cam_dict[cam_name]['fbx_name'] = os.path.split(cam_fbx_file)[1]
        cam_dict[cam_name]['focal_length']  = cam_value_dict['focal_length']
        cam_dict[cam_name]['focal_length_key_list']  = cam_value_dict['focal_length_key_list']
        print(cam_value_dict)

        select(cam_name, replace = True)
        export_fbx(frame_start_ext, frame_end_ext, cam_fbx_file)
        file_export_list.append(cam_fbx_file)
        delete(cam_name)
    progressBar(progressControl, edit = True, step= 1)

    for asset_type in ASSET_TYPE_LIST:
        asset_dict = collections.OrderedDict()
        shot_dict[asset_type] = asset_dict
        ref_node_list = ls(references = True)
        if ref_node_list != []:
            for ref_node in ref_node_list:
                try:
                    ref_path = referenceQuery(ref_node, filename = True)
                    asset_type_dir = '/' + asset_type + '/'
                    if asset_type_dir in ref_path:
                        if referenceQuery(ref_node, isLoaded = True):
                            # print(ref_node)
                            print(ref_path)
                            ref_namespace = referenceQuery(ref_node, namespace = True).split(':', 1)[-1]
                            print(ref_namespace)
                            asset_name = ref_path.split(asset_type_dir)[1].split('/')[0]
                            #ani_name = file_name + '_' + asset_name
                            ani_name = file_name + '_' + ref_namespace.replace(':', '___')
                            fbx_path = os.path.join(shot_data_dir, ani_name + '.fbx').replace('\\', '/')
                            fbx_name = os.path.split(fbx_path)[1]
                            asset_dict[ref_namespace] = collections.OrderedDict()
                            asset_dict[ref_namespace]['maya_path']  = ref_path
                            asset_dict[ref_namespace]['maya_node']  = str(ref_node)
                            asset_dict[ref_namespace]['asset_name'] = asset_name
                            asset_dict[ref_namespace]['ani_name']   = ani_name
                            asset_dict[ref_namespace]['fbx_path']   = ''
                            asset_dict[ref_namespace]['fbx_name']   = ''
                            asset_dict[ref_namespace]['root_joint_available'] = False
                            asset_dict[ref_namespace]['root_geo_available'] = False
                            print(asset_dict)
                            if objExists(ref_namespace + ':' + ROOT_JOINT_NAME):
                                try:
                                    setAttr(ref_namespace + ':Main.jointVis', 1)
                                except:
                                    pass
                                asset_dict[ref_namespace]['root_joint_available'] = True
                                joint_root = ls(ref_namespace + ':' + ROOT_JOINT_NAME)
                                print(joint_root)
                                joint_parent = cmds.listRelatives(joint_root, parent = True)
                                print(joint_parent)
                                
                                if objExists(ref_namespace + ':' + asset_name + '_' + ROOT_GEO_NAME):
                                    asset_dict[ref_namespace]['root_geo_available'] = True
                                    geo_root = ls(ref_namespace + ':' + asset_name + '_' + ROOT_GEO_NAME)
                                    print(geo_root)
                                    geo_parent = cmds.listRelatives(geo_root, parent = True)
                                    print(geo_parent)
                                
                                    cmds.file(ref_path, importReference = True)
                                    
                                    parent(joint_root, world = True)
                                    parent(geo_root, world = True)
                                    parentConstraint(joint_parent, joint_root, maintainOffset = True, weight = 1)
                                    
                                    select(geo_root, joint_root, replace = True)
                                    export_fbx(frame_start_ext, frame_end_ext, fbx_path)
                                    asset_dict[ref_namespace]['fbx_path'] = fbx_path
                                    asset_dict[ref_namespace]['fbx_name'] = fbx_name
                                    file_export_list.append(fbx_path)
                                else:
                                    cmds.file(ref_path, importReference = True)
                                    parent(joint_root, world = True)
                                    parentConstraint(joint_parent, joint_root, maintainOffset = True, weight = 1)

                                    select(joint_root, replace = True)
                                    export_fbx(frame_start_ext, frame_end_ext, fbx_path)
                                    asset_dict[ref_namespace]['fbx_path'] = fbx_path
                                    asset_dict[ref_namespace]['fbx_name'] = fbx_name
                                    file_export_list.append(fbx_path)
                                
                                control_main = ref_namespace + ':Main'
                                if listAttr(control_main, string = 'jointVis'):
                                    asset_dict[ref_namespace]['jointVis'] = []
                                    if keyframe(control_main, attribute = 'jointVis', query = True, keyframeCount = True) != 0:
                                        attr_node = PyNode(control_main + '.jointVis')
                                        for frame in range(frame_start_ext, frame_end_ext):
                                            attr_value = attr_node.get(time = frame)
                                            asset_dict[ref_namespace]['jointVis'].append(attr_value)

                            else:
                                pass
                except:
                    print(ref, '            bad bad')
            progressBar(progressControl, edit = True, step= 1)
    
    shot_json_file = os.path.join(shot_data_dir, file_name + '.json').replace('\\', '/')
    write_json_file(shot_dict, shot_json_file)
    file_export_list.insert(0, shot_json_file)
    deleteUI(progress_window)

    return shot_json_file



def publish_ue(*args, **kwargs):
    _task_id, _output_attr_id = args
    print('publish ue')

    # _output_attr_handle = zfused_api.attr.Output(_output_attr_id)
    # print('_output_attr_handle:             ', _output_attr_handle)
    # _file_format = _output_attr_handle.format()
    # print('_file_format:                    ', _file_format)
    # _suffix = _output_attr_handle.suffix()
    # print('_suffix:                         ', _suffix)
    # _attr_code = _output_attr_handle.code()
    # print('_attr_code:                      ', _attr_code)

    _task = zfused_api.task.Task(_task_id)
    _task_name = _task.code()
    _production_path = _task.production_path()
    _project_entity_production_path = _task.project_entity().production_path()
    _temp_path = _task.temp_path()
    _file_code = _task.file_code()
    _output_attr_handle = zfused_api.attr.Output(_output_attr_id)
    _file_format = _output_attr_handle.format()
    _suffix = _output_attr_handle.suffix()
    _attr_code = _output_attr_handle.code()
    
    # print('_task_name:                           ', _task_name)
    _shot_id = _task._data["ProjectEntityId"]
    _shot = zfused_api.shot.Shot(_shot_id)
    _shot_name = _shot.code()
    # print('_shot_name:                           ', _shot_name)

    _sequence_id = _shot._data["SequenceId"]
    _sequence_name = zfused_api.sequence.Sequence(_sequence_id).code()
    # print('_sequence_name:                       ', _sequence_name)

    # _episode_id = _shot._data["EpisodeId"]
    # _episode_name = zfused_api.episode.Episode(_episode_id).code()
    # print('_episode_name:                       ', _episode_name)

    _project_id = record.current_project_id()
    _project = zfused_api.project.Project(_project_id)
    _cache_path = _project.cache_path()
    _ue_cache_root = "{}/{}".format(_cache_path, 'ue')
    # print(_ue_cache_root)
    _ue_json_fbx_dir = "{}/{}".format(_ue_cache_root, 'json/fbx')

    # _ue_shot_dir = "{}/{}/{}/{}".format(_ue_cache_root, _episode_name, _sequence_name, _shot_name)
    _file_index = "{:0>4d}".format(_task.last_version_index( 0 ) + 1)
    # print('_file_index 0: ', _file_index)

    _production_file = "{}/{}/{}/{}{}".format( _production_path, _attr_code, _file_index, _file_code, _suffix )
    _production_file_dir = os.path.dirname(_production_file)
    _cover_file = "{}/{}/{}{}".format(_production_path, _attr_code, _file_code, _suffix)
    _publish_file = "{}/{}/{}/{}{}".format( _temp_path, _attr_code, _file_index, _file_code, _suffix )
    _publish_file_dir = os.path.dirname(_publish_file)

    # _ue_fbx_version_dir = "{}/{}/{}/".format(_ue_shot_dir, 'fbx', _file_index)
    _ue_fbx_version_dir = _publish_file_dir
    # print(_ue_fbx_version_dir)
    
    

    _user_id = zfused_api.zFused.USER_ID
    _user_handle = zfused_api.user.User(_user_id)
    _name_cn = _user_handle.name()
    _name_en = _user_handle.code()
    # print(_name_en, _name_cn)
    
    zfused_dict = collections.OrderedDict()
    # zfused_dict['episode_name'] = _episode_name
    zfused_dict['sequence_name'] = _sequence_name
    zfused_dict['shot_name'] = _shot_name
    zfused_dict['task_name'] = _task_name
    zfused_dict['file_index'] = _file_index
    zfused_dict['user_name'] = _name_en
    # print(zfused_dict)


    # _path = _task.path()
    # print('_path:                           ', _path)
    # _production_path = _task.production_path()
    # print('_production_path:                ', _production_path)
    # _transfer_path = _task.transfer_path()
    # print('_transfer_path:                  ', _transfer_path)
    # _backup_path = _task.backup_path()
    # print('_backup_path:                    ', _backup_path)
    # _work_path = _task.work_path()
    # print('_work_path:                      ', _work_path)
    # _project_entity_production_path = _task.project_entity().production_path()
    # print('_project_entity_production_path: ', _project_entity_production_path)
    # _temp_path = _task.temp_path()
    # print('_temp_path:                      ', _temp_path)
    # _file_code = _task.file_code()
    # print('_file_code:                      ', _file_code)
    
    if not os.path.isdir(_ue_fbx_version_dir):
        os.makedirs(_ue_fbx_version_dir)
    # if not os.path.isdir(_ue_json_fbx_dir):
    #     os.makedirs(_ue_json_fbx_dir)
    # print(_ue_fbx_version_dir)
    # print(_ue_json_fbx_dir)
    try:
        # print(_ue_fbx_version_dir)
        # print(zfused_dict)
        shot_json_file = export_shot(_ue_fbx_version_dir, zfused_dict)
        # print(shot_json_file)
        local_file_list = os.listdir(_ue_fbx_version_dir)
        for local_file_name in local_file_list:
            # print(local_file_name)
            local_file = os.path.join(_ue_fbx_version_dir, local_file_name).replace('\\', '/')
            cache_file = os.path.join(_production_file_dir, local_file_name).replace('\\', '/')
            # print(cache_file)
            _result = filefunc.publish_file(local_file, cache_file)
            print(_result)
        _result = filefunc.publish_file(_publish_file, _cover_file)
        print(_result)
        # shot_json_file_copy = "{}/{}".format(_ue_json_fbx_dir, shot_json_file.split('/')[-1])
        # shutil.copyfile(shot_json_file, shot_json_file_copy)
    except Exception as e:
        logger.error(e)
        print(e)
        return False
    return True
