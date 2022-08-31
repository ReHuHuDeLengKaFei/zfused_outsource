# -*- coding: UTF-8 -*-
'''
@Time    : 2020/12/15 14:59
@Author  : Jerris_Cheng
@File    : tempxeportcamera.py
'''

from zcore import filefunc

#import exportcamera as exportcamera
import maya.cmds as cmds
import maya.mel as mm
import sys

_list_txt="B:/temp/jerris/temp_ep013.txt"
base_path="P:/PYGC/dcc/shot"
shot_list=[]
import os
tempcamera_path="D:/temp/20201215/camera"

_is_load = cmds.pluginInfo("fbxmaya", query=True, loaded = True)
if not _is_load:
    try:
        cmds.loadPlugin("fbxmaya")
    except Exception as e:
        print(e)


PREPFRAME=8
with open(_list_txt) as e:
    _info=e.readlines()
    for i in _info:
        newname=i.replace("\n","")
        s=newname.replace("\r","")
        shot_list.append(s)
shot_camera_dict={}
for _shot in shot_list:
    _list=_shot.split("_")
    ep=_list[0]
    seq=_list[1]
    shot=_list[2]
    _path="P:/PYGC/dcc/shot/{}/{}/{}/animation/maya2019/file/{}.ma".format(ep,seq,shot,_shot)
    if os.path.exists(_path):

        camera_path="P:/PYGC/dcc/shot/{}/{}/{}/animation/maya2019/camera".format(ep,seq,shot)
        shot_camera_dict[_shot]=[_path,camera_path]

def getcameraname():
    shortname=cmds.file(q=True,sceneName=True,shortName=True)
    camreaname=shortname.replace(".ma","_cam")
    return camreaname


def gettimerange():
    starttime=cmds.playbackOptions(q=True,animationStartTime=True)
    endtime=cmds.playbackOptions(q=True,animationEndTime=True)
    return [int(starttime),int(endtime)]


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

_publish_dict={}
for i in shot_camera_dict.keys():
    cmds.file(f=1,new=1)
    try:


        _file_code=i
        filepath=shot_camera_dict.get(i)[0]
        _camera_path=shot_camera_dict.get(i)[1]

        cmds.file(filepath,f=1,iv=1,o=1)


        _start_frame = int(cmds.playbackOptions(q=True, min=True)) - PREPFRAME
        _end_frame = int(cmds.playbackOptions(q=True, max=True)) + PREPFRAME
        _cams = cmds.ls("{}*".format(_file_code), fl=1, type="camera")
        _camera_transforms = []

        for _cam in _cams:
            _cam_trans = cmds.listRelatives(_cam, p=1)[0]
            _camera_transforms.append(_cam_trans)
            # 判定父组是否为偏移
            _cam_parent = cmds.listRelatives(_cam_trans, p=True)
            if _cam_parent:
                _cam_parent = _cam_parent[0]
                if _cam_parent == "offset_camera":
                    # 冻结位移属性
                    cmds.setAttr("{}.inheritsTransform".format(_cam_trans), 0)

                _publish_file=tempcamera_path+"/{}.fbx".format(_cam_trans)
                _production_file=_camera_path+"/0001/{}.fbx".format(_cam_trans)
                if not os.path.isdir(os.path.dirname(_publish_file)):
                    os.makedirs(os.path.dirname(_publish_file))

                _result=export_camera_fbx(_cam_trans,_publish_file,_start_frame,_end_frame)
                filefunc.publish_file(_publish_file, _production_file,True)
    except Exception as e:
        print(e)
    cmds.file(f=1,new=1)




