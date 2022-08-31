# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import logging

import maya.cmds as cmds

import zfused_api
from zcore import filefunc

import zfused_maya.core.record as record

import zfused_maya.node.core.alembiccache as alembiccache
import zfused_maya.node.core.texture as texture
import zfused_maya.node.core.material as material
import zfused_maya.node.core.fixmeshname as fixmeshname
import zfused_maya.node.core.renderinggroup as renderinggroup

__all__ = ["publish_material"]

logger = logging.getLogger(__name__)

# test
def publish_material(*args, **kwargs):
    """ 上传任务模型文件
    
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
        cmds.file(rename = _publish_file)
        cmds.file(save = True, type = _file_format, f = True)
        
        # fix mesh name
        _is_rendering = renderinggroup.nodes()
        fixmeshname.fix_mesh_name("_rendering", _is_rendering)

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
        _result = filefunc.publish_file(_publish_file, _production_file)
        _result = filefunc.publish_file(_publish_file, _cover_file)

    except Exception as e:
        logger.error(e)
        return False

    # open orignal file
    # cmds.file(_current_file, o = True, f = True, pmt = True)
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

if __name__ == '__main__':
    publish_material()