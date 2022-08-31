# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import logging

import maya.cmds as cmds

import zfused_api

from zcore import zfile,transfer

import zfused_maya.node.core.clear as clear
import zfused_maya.node.core.alembiccache as alembiccache
import zfused_maya.node.core.texture as texture
import zfused_maya.node.core.material as material
import zfused_maya.node.core.fixmeshname as fixmeshname
import zfused_maya.node.core.renderinggroup as renderinggroup

__all__ = ["export_file"]

logger = logging.getLogger(__name__)

def export_file(*args, **kwargs):
    """ 上传任务模型文件
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
        # save publish file
        cmds.file(rename = _publish_file)
        cmds.file(save = True, type = _file_format, f = True, options = "v=0;")
        # fix mesh name
        _is_rendering = renderinggroup.nodes()
        fixmeshname.fix_mesh_name("_rendering", _is_rendering)
        # recore material
        material.record()
        # publish texture
        _texture_files = texture.files()
        if _texture_files:
            _texture_path = "{}/{}/texture".format(_project_production_path,_entity_path)
            _path_set = texture.paths(_texture_files)[0]
            _intersection_path = max(_path_set)
            texture.publish_file(_texture_files, _intersection_path, _texture_path)
            # change maya texture node path
            _file_nodes = texture.nodes()
            if _file_nodes:
                texture.change_node_path(_file_nodes, _intersection_path, _texture_path)
        
        # publish alembic cache
        _alembic_files = alembiccache.files()
        if _alembic_files:
            _alembic_path = "{}/{}/cache/alembic".format(_project_production_path,_entity_path)
            _path_set = alembiccache.paths(_alembic_files)[0]
            _intersection_path = max(_path_set)
            alembiccache.publish_file(_alembic_files, _intersection_path, _alembic_path)
            _file_nodes = alembiccache.nodes()
            # change alembic path
            if _file_nodes:
                alembiccache.change_node_path(_file_nodes, _intersection_path, _alembic_path)
        
        # save publish file
        cmds.file(save = True, type = _file_format, f = True, options = "v=0;")
        
        # publish file
        # _result = filefunc.publish_file(_publish_file, _production_file)
        # _result = filefunc.publish_file(_publish_file, _cover_file)
        transfer.send_file_to_server(_publish_file, _production_file)
        transfer.send_file_to_server(_publish_file, _cover_file)
        
        # record in database
        _file_info = zfile.get_file_info(_publish_file, _production_file)
        zfused_api.task.new_production_file([_file_info], _task_id, _attr_id, int(_file_index) )

        # link files
        zfused_api.files.new_file("task", _task_id, _production_file, int(_file_index))
        zfused_api.files.new_file("task", _task_id, _cover_file, int(_file_index))
    except Exception as e:
        logger.error(e)
        return False

    return True

if __name__ == '__main__':
    publish_file()