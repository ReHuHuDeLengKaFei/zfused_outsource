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
import zfused_maya.node.core.yeti as yeti
import zfused_maya.node.core.fixmeshname as fixmeshname
import zfused_maya.node.core.renderinggroup as renderinggroup
import zfused_maya.node.core.referencefile as referencefile

__all__ = ["publish_file"]

logger = logging.getLogger(__name__)

# test
def publish_file(*args, **kwargs):
    """ 上传绑定文件
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
    #print(_production_path)
    _publish_file = "{}/{}/{}/{}/{}.{}{}".format( _temp_path, _step_code, _software_code, _attr_code, _file_code, _file_index, _suffix )
    _publish_file_dir = os.path.dirname(_publish_file)
    if not os.path.isdir(_publish_file_dir):
        os.makedirs(_publish_file_dir)

        
    try:
        # save publish file
        cmds.file(rename = _publish_file)
        cmds.file(save = True, type = _file_format, f = True)
        
        # publish texture
        _texture_files = texture.files()
        if _texture_files:
            _path_set = texture.paths(_texture_files)[0]
            _intersection_path = max(_path_set)
            texture.publish_file(_texture_files, _intersection_path, _production_path + "/texture/rig")
            # change maya texture node path
            _file_nodes = texture.nodes()
            if _file_nodes:
                texture.change_node_path(_file_nodes, _intersection_path, _production_path + "/texture/rig")
        
        # publish yetinode texture
        _yeti_texture_dict = yeti._get_yeti_attr("texture","file_name")
        if _yeti_texture_dict:
            _path_set = yeti.paths([i.replace("\\","/") for i in _yeti_texture_dict.values()])[0]
            _intersection_path = max(_path_set)
            yeti.publish_file(_yeti_texture_dict.values(), _intersection_path, _production_path + "/texture/yeti")
            yeti.change_node_path(_yeti_texture_dict,_intersection_path, _production_path + "/texture/yeti")

        # publish alembic cache
        _alembic_files = alembiccache.files()
        if _alembic_files:
            _path_set = alembiccache.paths(_alembic_files)[0]
            _intersection_path = max(_path_set)
            alembiccache.publish_file(_alembic_files, _intersection_path, _production_file_dir + "/cache/alembic")
            _file_nodes = alembiccache.nodes()
            if _file_nodes:
                alembiccache.change_node_path(_file_nodes, _intersection_path, _production_file_dir + "/cache/alembic")

        # import all reference
        referencefile.import_all_references()
        # remove all namesapce
        referencefile.remove_all_namespaces()
        # delete unused material
        material.delete_unused()
        
        # fix mesh name
        _is_rendering = renderinggroup.nodes()
        shader_dict = fixmeshname.fix_mesh_name("_rendering", _is_rendering, True)

        # repair shader
        cmds.file(save = True, type = _file_format, f = True)
        if shader_dict:
            for k2,v2 in shader_dict.items():
                cmds.select(v2)
                cmds.hyperShade(assign = "lambert1")
                cmds.hyperShade(assign = k2)

        # repair arnold id
        _meshs = cmds.ls(type = "mesh", ap = True)
        for _mesh in _meshs:
            _attrs = cmds.listAttr(_mesh, st = "mtoa_constant*")
            if not _attrs:
                continue
            if not len(_attrs) == 4:
                continue
            if not _mesh.endswith("_orig"):
                continue 
            _parent = cmds.listRelatives(_mesh, p = True, f = True)
            # #print(_parent)
            if not _parent:
                continue
            _parent = _parent[0]
            _fix_mesh = cmds.listRelatives(_parent, f = True, children=True, shapes=True, noIntermediate=True, type="mesh")[0] 
            _id_attr_name  = _attrs[0]
            _id_attr_number = [
                cmds.getAttr("{}.{}".format(_mesh, _attrs[1])),
                cmds.getAttr("{}.{}".format(_mesh, _attrs[2])),
                cmds.getAttr("{}.{}".format(_mesh, _attrs[3]))
            ]                
            if cmds.objExists("{}.{}".format(_fix_mesh, _id_attr_name)):
                cmds.deleteAttr( "{}.{}".format(_fix_mesh, _id_attr_name) )
            _attr_name = _id_attr_name
            cmds.addAttr(_fix_mesh, ln = _attr_name, at = "double3");
            cmds.addAttr(_fix_mesh, ln = "{}X".format(_attr_name), at = "double", p = _attr_name) 
            cmds.addAttr(_fix_mesh, ln = "{}Y".format(_attr_name), at = "double", p = _attr_name)
            cmds.addAttr(_fix_mesh, ln = "{}Z".format(_attr_name), at = "double", p = _attr_name)
            cmds.setAttr("{}.{}X".format(_fix_mesh, _attr_name), e = True, k = True ) 
            cmds.setAttr("{}.{}Y".format(_fix_mesh, _attr_name), e = True, k = True )
            cmds.setAttr("{}.{}Z".format(_fix_mesh, _attr_name), e = True, k = True )
            cmds.setAttr("{}.{}X".format(_fix_mesh, _attr_name), _id_attr_number[0] )
            cmds.setAttr("{}.{}Y".format(_fix_mesh, _attr_name), _id_attr_number[1] )
            cmds.setAttr("{}.{}Z".format(_fix_mesh, _attr_name), _id_attr_number[2] )

        cmds.file(save = True, type = _file_format, f = True)

        # publish file
        _result = filefunc.publish_file(_publish_file, _production_file)
        _result = filefunc.publish_file(_publish_file, _cover_file)

        # link files
        zfused_api.files.new_file("task", _task_id, _production_file, int(_file_index))
        zfused_api.files.new_file("task", _task_id, _cover_file, int(_file_index))
        
    except Exception as e:
        logger.error(e)
        return False

    # open orignal file
    # cmds.file(_current_file, o = True, f = True, pmt = True)
    return True

if __name__ == '__main__':
    publish_file()