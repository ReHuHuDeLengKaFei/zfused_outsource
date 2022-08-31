# coding:utf-8
# --author-- lanhua.zhou

"""
    上传 assembly definition 文件
"""

from __future__ import print_function

import os
import logging

import maya.cmds as cmds

import zfused_api
from zcore import filefunc

import zfused_maya.core.record as record

import zfused_maya.node.core.assembly as assembly

logger = logging.getLogger(__name__)


# load gpu plugin
_is_load = cmds.pluginInfo("sceneAssembly", query=True, loaded = True)
if not _is_load:
    try:
        logger.info("load scene assembly plugin")
        cmds.loadPlugin("sceneAssembly")
    except Exception as e:
        logger.error(e)
        sys.exit()

def publish_ad(*args, **kwargs):
    """ publish assembly definition file

    :rtype: bool
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
        cmds.file(new = True, f = True)
        cmds.file(rename = _publish_file)
        cmds.file(save = True, type = _file_format, f = True)
        
        # create assembly definition node
        _create_assembly_node(_task_handle.data()["Id"])

        #print("assembly node ")

        cmds.file(save = True, type = _file_format, f = True)
        # publish file
        _result = filefunc.publish_file(_publish_file, _production_file)
        _result = filefunc.publish_file(_publish_file, _cover_file)

    except Exception as e:
        logger.error(e)
        return False


    #  publish file
    _result = filefunc.publish_file(_publish_file, _production_file)
    _result = filefunc.publish_file(_publish_file, _cover_file)  

    return True

    """
    try:
        # save publish file
        cmds.file(rename = _publish_file)
        cmds.file(save = True, type = _file_type, f = True)

        # publish texture
        _texture_files = texture.files()
        if _texture_files:
            _path_set = texture.paths(_texture_files)[0]
            _intersection_path = max(_path_set)
            texture.publish_file(_texture_files, _intersection_path, _backup_path + "/texture")
            # change maya texture node path
            _file_nodes = texture.nodes()
            if _file_nodes:
                texture.change_node_path(_file_nodes, _intersection_path, _backup_path + "/texture")
        
        # publish alembic cache
        _alembic_files = alembiccache.files()
        if _alembic_files:
            _path_set = alembiccache.paths(_alembic_files)[0]
            _intersection_path = max(_path_set)
            alembiccache.publish_file(_alembic_files, _intersection_path, _backup_path + "/cache/alembic")
            _file_nodes = alembiccache.nodes()
            if _file_nodes:
                alembiccache.change_node_path(_file_nodes, _intersection_path, _backup_path + "/cache/alembic")

        # save publish file
        cmds.file(save = True, type = _file_type, f = True)
        
        # publish file
        _result = filefunc.publish_file(_publish_file, _backup_file)

    except Exception as e:
        logger.error(e)
        return False
    """

def _create_assembly_node(task_id):
    """ create assembly definition node
    """
    _task_handle = zfused_api.task.Task(task_id)
    _project_step_handle = zfused_api.step.ProjectStep(_task_handle.data()["ProjectStepId"])
    asset_id = _task_handle.project_entity_id()
    _asset_handle = zfused_api.asset.Asset(asset_id)
    _code = _asset_handle.code()   
    _assembly_definition = assembly.create_assembly_definition(_code)
    
    # _current_project_id = record.current_project_id()
    # if not _current_project_id:
    #     return 
    
    _current_project_id = _task_handle.data()["ProjectId"]
    # get is assembly attr
    _project_handle = zfused_api.project.Project(_current_project_id)
    _assembly_attrs = _project_step_handle.assembly_attributes()
    #print(_assembly_attrs)
    for _assembly_attr in _assembly_attrs:
        _project_step_id = _assembly_attr["ProjectStepId"]
        _task = zfused_api.zFused.get("task", filter = {"ProjectEntityType":"asset","ProjectEntityId":asset_id,"ProjectStepId":_project_step_id})
        if not _task:
            continue
        _task_id = _task[0]["Id"]
        _task_handle = zfused_api.task.Task(_task_id)
        _production_path = _task_handle.production_path()
        
        # _last_version_index = _task_handle.last_version_index()
        # if not _last_version_index:
        #     continue
        # _file = "%s/%s/%s.%04d%s"%(_production_path, 
        #                            _assembly_attr["Code"], 
        #                            self._asset_handle.code(), 
        #                            _last_version_index, 
        #                            _assembly_attr["Suffix"])

        _file = "%s/%s/%s%s"%( _production_path,
                               _assembly_attr["Code"], 
                               _asset_handle.code(),
                               _assembly_attr["Suffix"])
        if _assembly_attr["Suffix"].endswith("abc"):
            _assembly_definition.create_representation(_assembly_attr["Code"], "Cache", _file)
        else:
            _assembly_definition.create_representation(_assembly_attr["Code"], "Scene", _file)

    _assembly_definition.set_active(_assembly_attrs[0]["Code"])