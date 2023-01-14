# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import logging

import maya.cmds as cmds

import zfused_api

from zcore import zfile,transfer

import zfused_maya.node.core.material as material
import zfused_maya.node.core.renderinggroup as renderinggroup

__all__ = ["export_shader"]

logger = logging.getLogger(__name__)

# test
def export_shader(*args, **kwargs):
    """ 上传任务模型材质
        args: entity_type, entity_id, attr_id
    """
    _entity_type, _entity_id, _attr_id = args
    
    # attr
    _output_attr_handle = zfused_api.outputattr.OutputAttr(_attr_id)
    _suffix = _output_attr_handle.suffix()
    _file_format = _output_attr_handle.format()
    _attr_path = _output_attr_handle.path()
    
    # project step 
    _project_step_id = _output_attr_handle.data()["ProjectStepId"]
    _project_step_handle = zfused_api.step.ProjectStep(_project_step_id)
    _project_step_path = _project_step_handle.path()

    # entity 
    _entity_handle = zfused_api.objects.Objects(_entity_type, _entity_id)
    _entity_path = _entity_handle.path()

    # project 
    _project_handle = _entity_handle.project()
    _project_production_path = _project_handle.production_path()
    _project_temp_path = _project_handle.temp_path()

    # task
    _task = _entity_handle.tasks([_project_step_id])[0]
    _task_id = _task["Id"]
    _task_handle = zfused_api.task.Task(_task_id)
    if kwargs.get("fix_version"):
        _file_index = "{:0>4d}".format(_task_handle.last_version_index( 0 ))
    else:
        _file_index = "{:0>4d}".format(_task_handle.last_version_index() + 1)
    _file_name = "{}.{}{}".format(_entity_handle.code(),_file_index,_suffix)
    _cover_name = "{}{}".format(_entity_handle.code(),_suffix)

    _production_file = "{}/{}/{}/{}/{}".format( _project_production_path, _entity_path, _project_step_path, _attr_path, _file_name )
    _production_file_dir = os.path.dirname(_production_file)
    _cover_file = "{}/{}/{}/{}/{}".format( _project_production_path, _entity_path, _project_step_path, _attr_path, _cover_name )
    _publish_file = "{}/{}/{}/{}/{}".format( _project_temp_path, _entity_path, _project_step_path, _attr_path, _file_name )
    _publish_file_dir = os.path.dirname(_publish_file)
    if not os.path.isdir(_publish_file_dir):
        os.makedirs(_publish_file_dir)

    try:        
        # recore material
        material.record()
        # get all material
        _meshs = _get_rendering_mesh()
        if not _meshs:
            return False
        # 对大量模型操作时会卡死，弃用
        # cmds.select(_meshs, replace = True)
        # cmds.hyperShade(shaderNetworksSelectMaterialNodes = True)
        _sg = cmds.listConnections(_meshs,d = 1,type = "shadingEngine")
        _mat = [cmds.listConnections("{}.surfaceShader".format(i),d = 1)[0] for i in set(_sg)]
        cmds.select(_mat,r =1)
        cmds.file(_publish_file, op = "v=0;", type = "mayaBinary", pr = True, es = True, f = True)
        
        # publish file
        transfer.send_file_to_server(_publish_file, _production_file)
        transfer.send_file_to_server(_publish_file, _cover_file)

        # record in database
        _file_info = zfile.get_file_info(_publish_file, _production_file)
        zfused_api.task.new_production_file([_file_info], _task_id, _attr_id, int(_file_index) )

    except Exception as e:
        logger.error(e)
        return False

    return True


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
        allDags = cmds.ls(grp, dag = True, ni = True)
        mesh += allDags
    return mesh
