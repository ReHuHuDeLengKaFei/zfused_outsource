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

__all__ = ["publish_uvs"]

logger = logging.getLogger(__name__)

def _get_rendering_mesh():
    mesh = []
    rendering = []
    allDags = cmds.ls(dag = True)
    for dag in allDags:
        dag
        #get 
        if cmds.objExists("%s.rendering"%dag):
            value = cmds.getAttr("%s.rendering"%dag)
            if value:
                rendering.append(dag)
    for grp in rendering:
        allDags = cmds.ls(grp, dag = True, ni = True, type = "mesh")
        mesh += allDags
    return mesh

def _get_data(meshs):
    _data = []
    for _mesh in meshs:
        selectionList = om.MSelectionList()
        selectionList.add( _mesh )
        node = selectionList.getDependNode(0)
        fnMesh = om.MFnMesh(node)
        dag_info = {
            "transform":None,
            "shape":None,
            "numVertices":0,
            "numEdges":0,
            "numPolygons":0,
            "numUVSets":0,
            "uvs":None
        }
        dag_info["transform"] = cmds.listRelatives(_mesh, p = True)[0]
        dag_info["shape"] = _mesh
        dag_info["numVertices"] = fnMesh.numVertices
        dag_info["numEdges"] = fnMesh.numEdges
        dag_info["numPolygons"] = fnMesh.numPolygons
        dag_info["numUVSets"] = fnMesh.numUVSets
        #get uv
        uvs = []
        uvSetNames = fnMesh.getUVSetNames()
        for name in uvSetNames:
            uv_info = {
                "uvSetName":"",
                "uvs":[],
                "uvCounts":[],
                "uvIds":[]
            }
            uv_info["uvSetName"] = name
            uv_info["uvs"] = [list(set(i)) for i in fnMesh.getUVs(name)]
            AssignedUVs = fnMesh.getAssignedUVs()
            uv_info["uvCounts"] = list(set(AssignedUVs[0]))
            uv_info["uvIds"] = list(set(AssignedUVs[1]))
            uvs.append(uv_info)
        dag_info["uvs"] = uvs
        _data.append(dag_info)

    return _data

def publish_uvs(*args, **kwargs):
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
        _meshs = _get_rendering_mesh()
        _data = _get_data(_meshs)

        with open(_publish_file, "w") as handle:
            handle.write(json.dumps(_data,indent = 4,separators=(',',':')))

        # publish file
        _result = filefunc.publish_file(_publish_file, _production_file)
        _result = filefunc.publish_file(_publish_file, _cover_file)
    except Exception as e:
        logger.error(e)
        return False

    return True