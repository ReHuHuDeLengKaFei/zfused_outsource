# coding:utf-8
# --author-- ning.qin
from __future__ import print_function

import os
import re
import sys
import shutil
import logging
import json
import time

import maya.cmds as cmds
from pymel.core import *

import zfused_api
from zfused_maya.core import record

CAM_KEYWORD_LIST = ['CAM', 'cam']
# ASSET_TYPE_LIST = ['Chars', 'Props']
ASSET_TYPE_LIST = ['char', 'prop', 'env']
ATTR_LIST_TRANSFORM = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
ATTR_LIST_CAM_SHAPE = ['focalLength']
ROOT_JOINT_NAME = 'DeformationSystem'
ROOT_GEO_NAME = 'geometry_grp'
shader_json_dir = 'V:/FKXR/cache/ue/shaderMetadata'

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

#shader_json_path = 'P:/projects/PN/assets/Chars/C003JinMinZaiA/texture/final/C003JinMinZaiA_shaderMetadata.json'
def export_ref_abc(abc_file_path, root_geo, frame_start = 101, frame_end = 110):
    # root_geo = ref_namespace + ':geometry_grp'
    job_command = '-frameRange {} {} -uvWrite -writeColorSets -writeFaceSets -worldSpace -root {} -file {}'.format(frame_start, frame_end, root_geo, abc_file_path)
    print(job_command)
    AbcExport(j = job_command)

def export_shot(shot_data_dir, zfused_dict = {}, frame_ext = 3):
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
    version = 0
    try:
        version = os.path.splitext(os.path.split(sceneName())[1])[0].split('.')[1]
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
        cam_fbx_file  = shot_data_dir + cam_name + '.fbx'
        cam_dict[cam_name] = collections.OrderedDict()
        cam_dict[cam_name]['fbx']  = cam_fbx_file
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
                # try:
                ref_path = referenceQuery(ref_node, filename = True)
                asset_type_dir = '/' + asset_type + '/'
                if asset_type_dir in ref_path:
                    if referenceQuery(ref_node, isLoaded = True):
                        print(ref_node)
                        print(asset_type)
                        ref_namespace = referenceQuery(ref_node, namespace = True).split(':', 1)[-1]
                        asset_name = ref_path.split(asset_type_dir)[1].split('/')[0]
                        ani_name = file_name + '_' + ref_namespace.replace(':', '___')
                        abc_file_path = '{}{}.abc'.format(shot_data_dir, ani_name)

                        asset_dict[ref_namespace] = collections.OrderedDict()
                        asset_dict[ref_namespace]['maya_path']  = ref_path
                        asset_dict[ref_namespace]['maya_node']  = str(ref_node)
                        asset_dict[ref_namespace]['asset_name'] = asset_name
                        asset_dict[ref_namespace]['ani_name']   = ani_name
                        asset_dict[ref_namespace]['shaderMetadata'] = ''
                        asset_dict[ref_namespace]['abc_path']   = ''
                        # tex_ma_dir = os.path.split(ref_path)[0].replace('/rig/', '/texture/')
                        shader_json_path = '{}/{}_shaderMetadata.json'.format(shader_json_dir, asset_name)
        
                        # if os.path.isdir(tex_ma_dir):
                        #     #print(tex_ma_dir)
                        #     for tex_ma_dir_file in os.listdir(tex_ma_dir):
                        #         #print(tex_ma_dir_file)
                        #         if tex_ma_dir_file.split('.')[-1] == 'json':
                        #             #print(tex_ma_dir_file)
                        #             shader_json_path = tex_ma_dir + '/' + tex_ma_dir_file
                        #             print(shader_json_path)
                        if os.path.isfile(shader_json_path):
                            asset_dict[ref_namespace]['shaderMetadata'] = shader_json_path
                            print(shader_json_path)
                            shader_dict = read_json_file(shader_json_path)
                            print(shader_dict)
                            
                            all_sg_list = cmds.ls(type='shadingEngine')
                            delete_sg_list = [old_sg for old_sg in all_sg_list if ref_namespace in old_sg]
                            print(delete_sg_list)
                            cmds.delete(delete_sg_list)
                            
                            root_geo =  '{}:{}'.format(ref_namespace, ROOT_GEO_NAME)
                            lambert_name = ref_namespace + '_reset'
                            reset_lambert = cmds.shadingNode('lambert', asShader = 1, n = '%s_lambert'%lambert_name)
                            reset_shadingEngine = cmds.sets(renderable = 1,noSurfaceShader = 1,empty = 1, n = "%sSG"%lambert_name)
                            cmds.connectAttr(reset_lambert + '.outColor', reset_shadingEngine + '.surfaceShader')
                            cmds.sets(root_geo, forceElement = reset_shadingEngine)
                            
                            for shader in shader_dict:
                                new_lambert = cmds.shadingNode('lambert', asShader = 1, n = '%s_lambert'%shader)
                                new_shadingEngine = cmds.sets(renderable = 1,noSurfaceShader = 1,empty = 1, n = "%sSG"%shader)
                                cmds.connectAttr(new_lambert + '.outColor', new_shadingEngine + '.surfaceShader')
                                cmds.select([new_lambert, new_shadingEngine])
                                for js_name in shader_dict[shader]:
                                    new_mesh_name = ref_namespace + ':' + js_name.split('|')[-1]
                                    reShaderMeshList = cmds.ls(new_mesh_name)
                                    if reShaderMeshList:
                                        if len(reShaderMeshList)>1:
                                            cmds.warning("WARNING!Find more than 2 mesh in this Scenes:\n%s"%reShaderMeshList)
                                        for mesh_face in reShaderMeshList:
                                            cmds.sets(mesh_face, forceElement=new_shadingEngine)
                                    else:
                                        cmds.warning("WARNING!%s not find!" % new_mesh_name)
                            
                            export_ref_abc(abc_file_path, root_geo, frame_start_ext, frame_end_ext)
                            asset_dict[ref_namespace]['abc_path'] = abc_file_path
                            file_export_list.append(abc_file_path)
                        else:
                            # raise Exception("Cannot find ShaderMetadata in %s" % shader_json_path)
                            print("Cannot find ShaderMetadata in %s" % shader_json_path)

                # except:
                #     print(ref, '            bad bad')
            progressBar(progressControl, edit = True, step= 1)
    
    shot_json_file = shot_data_dir + file_name + '.json'
    write_json_file(shot_dict, shot_json_file)
    file_export_list.insert(0, shot_json_file)
    deleteUI(progress_window)
    #return file_export_list

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
    # print('_task_name:                           ', _task_name)
    _shot_id = _task._data["ProjectEntityId"]
    _shot = zfused_api.shot.Shot(_shot_id)
    _shot_name = _shot.code()
    # print('_shot_name:                           ', _shot_name)

    _sequence_id = _shot._data["SequenceId"]
    _sequence_name = zfused_api.sequence.Sequence(_sequence_id).code()
    # print('_sequence_name:                       ', _sequence_name)

    _episode_id = _shot._data["EpisodeId"]
    _episode_name = zfused_api.episode.Episode(_episode_id).code()
    # print('_episode_name:                       ', _episode_name)

    _project_id = record.current_project_id()
    _project = zfused_api.project.Project(_project_id)
    _cache_path = _project.cache_path()
    _ue_cache_root = "{}/{}".format(_cache_path, 'ue')
    # print(_ue_cache_root)
    _ue_json_abc_dir = "{}/{}".format(_ue_cache_root, 'json/abc')

    _ue_shot_dir = "{}/{}/{}/{}".format(_ue_cache_root, _episode_name, _sequence_name, _shot_name)
    _file_index = "{:0>4d}".format(_task.last_version_index( 0 ) + 1)
    # print('_file_index 0: ', _file_index)
    _ue_abc_version_dir = "{}/{}/{}/".format(_ue_shot_dir, 'abc', _file_index)
    print(_ue_abc_version_dir)
    
    

    _user_id = zfused_api.zFused.USER_ID
    _user_handle = zfused_api.user.User(_user_id)
    _name_cn = _user_handle.name()
    _name_en = _user_handle.code()
    # print(_name_en, _name_cn)
    
    zfused_dict = collections.OrderedDict()
    zfused_dict['episode_name'] = _episode_name
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
    
    if not os.path.isdir(_ue_abc_version_dir):
        os.makedirs(_ue_abc_version_dir)
    if not os.path.isdir(_ue_json_abc_dir):
        os.makedirs(_ue_json_abc_dir)
    try:
        shot_json_file = export_shot(_ue_abc_version_dir, zfused_dict)
        shot_json_file_copy = "{}/{}".format(_ue_json_abc_dir, shot_json_file.split('/')[-1])
        shutil.copyfile(shot_json_file, shot_json_file_copy)
    except Exception as e:
        logger.error(e)
        print(e)
        return False
    return True
