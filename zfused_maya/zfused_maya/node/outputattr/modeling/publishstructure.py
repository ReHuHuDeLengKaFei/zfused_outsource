# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import sys
import os
import logging
import json

import maya.cmds as cmds
import maya.api.OpenMaya as om

import zfused_api
from zcore import filefunc

import zfused_maya.core.record as record

import zfused_maya.node.core.alembiccache as alembiccache
import zfused_maya.node.core.texture as texture
import zfused_maya.node.core.material as material
import zfused_maya.node.core.fixmeshname as fixmeshname
import zfused_maya.node.core.renderinggroup as renderinggroup

__all__ = ["publish_structure"]

logger = logging.getLogger(__name__)


def publish_structure(*args, **kwargs):
    """ 上传任务模型结构
    
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
        # save publish file
        _structure_data = {}
        _structure_data["assets_info"] = _get_asset_info()
        _structure_data["materials_info"] = _get_mat_info()
        # _structure_data["texture_info"] = _get_texture_info()

        with open(_publish_file, "w") as handle:
            handle.write(json.dumps(_structure_data, indent = 4, separators=(',',':')))

        # publish file
        _result = filefunc.publish_file(_publish_file, _production_file)
        _result = filefunc.publish_file(_publish_file, _cover_file)
    except Exception as e:
        logger.error(e)
        return False

    # open orignal file
    # cmds.file(_current_file, o = True, f = True, pmt = True)
    return True

def _get_asset_info():
    # 获取模型信息
    meshLists = cmds.ls(type = "mesh",fl = 1)
    # 移除文件内的中间模型
    intermediateObjects = cmds.ls(meshLists, io=1, fl=1)
    for intermediateObject in intermediateObjects:
        if intermediateObject in meshLists:
            meshLists.remove(intermediateObject)

    transLists = cmds.listRelatives(meshLists,p = 1,pa = 1)
            
    mSel = om.MSelectionList()
    mDagPath = om.MDagPath()
    assetDirs = {}
    
    for transList in transLists:
        mSel.clear()
        mSel.add(transList)
        mDagPath = mSel.getDagPath(0)
        mFnMesh = om.MFnMesh(mDagPath)
        mName = mDagPath.partialPathName()
        assetDirs[mName] = {}
        assetDirs[mName]["fullPathName"] = mDagPath.fullPathName()
        assetDirs[mName]["numVertices"] = mFnMesh.numVertices
        ########
        assetDirs[mName]["numEdges"] = mFnMesh.numEdges
        assetDirs[mName]["numPolygons"] = mFnMesh.numPolygons
        uvSetName = mFnMesh.getUVSetNames()[0]
        assetDirs[mName]["uvSetName"] = uvSetName
        #assetDirs[mName]["UVcoord"] = mFnMesh.getUVs(UVSetName)
        assetDirs[mName]["numUVs"] = len([i for i in mFnMesh.getAssignedUVs()[1]])
        #assetDirs[mName]["uvIDs"] = [i for i in mFnMesh.getAssignedUVs()[1]]
        ########
    return assetDirs

def _get_mat_info():
    # 获取材质信息
    def getfaceID():
        cmds.hyperShade(objects = '')
        tempNames = cmds.ls(sl = 1)
        meshNames = []
        mSel = om.MSelectionList()
        for tempName in tempNames:
            tempName
            if tempName.find(".f[")== -1:
                if cmds.nodeType(tempName) != "mesh":
                    continue
                transName = cmds.listRelatives(tempName,p = 1,pa = 1)[0]
                mSel.clear()
                mSel.add(tempName)
                mDagPath = mSel.getDagPath(0)
                mFnMesh = om.MFnMesh(mDagPath)
                tempFaceName = "%s.f[0:%s]"%(transName,int(mFnMesh.numPolygons)-1)
                meshNames.append(tempFaceName)
                tempFaceName
            else:
                meshNames.append(tempName)
        return meshNames

    materialDirs = {}
    shadingEngines = cmds.ls(type = "shadingEngine")
    shadingEngines.remove("initialParticleSE")

    for shadingEngine in shadingEngines:
        materialDirs[shadingEngine] = {}
        cmds.select(shadingEngine,r = 1,ne = 1)
        materialDirs[shadingEngine]["faceID"] = getfaceID()

        surfaceShader = cmds.listConnections("%s.surfaceShader"%shadingEngine)
        if surfaceShader:
            materialDirs[shadingEngine]["surfaceShader"] = surfaceShader
            tempshaderID = []
            try:
                tempshaderID = []
                tempshaderID.append(typeShader[0])
                tempshaderID.append(cmds.getAttr("%s.vrayMaterialId"%typeShader[0]))
                tempshaderID.extend(cmds.getAttr("%s.vrayColorId"%typeShader[0]))
                materialDirs[shadingEngine]["%s"%typeShader] = tempshaderID
            except:
                pass

        volumeShader = cmds.listConnections("%s.volumeShader"%shadingEngine)
        if volumeShader:
            materialDirs[shadingEngine]["volumeShader"] = volumeShader

        displacementShader = cmds.listConnections("%s.displacementShader"%shadingEngine)
        if displacementShader:
            materialDirs[shadingEngine]["displacementShader"] = displacementShader

    return materialDirs

# def _get_texture_info():
#     # 获取贴图信息
#     _dict = texture.TEXTURE_ATTR_DICT
#     textureDirs = {}
#     texFiles = texture.nodes()
#     if texFiles:
#         for texFile in texFiles:
#             _type = cmds.nodeType(texFile)
#             texPath = cmds.getAttr('%s.%s'%(texFile,_dict[_type]))
#             textureDirs[texFile] = texPath
#     return textureDirs