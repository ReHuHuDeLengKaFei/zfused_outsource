# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import sys
import logging

import maya.cmds as cmds

import zfused_api

from zcore import zfile,transfer,filefunc

# from zfused_maya.core import transfer

from zfused_maya.node.core import renderinggroup

__all__ = ["export_alembic"]

logger = logging.getLogger(__name__)

# load abc plugin
_is_load = cmds.pluginInfo("AbcExport", query=True, loaded = True)
if not _is_load:
    try:
        logger.info("try load alembic plugin")
        cmds.loadPlugin("AbcExport")
    except Exception as e:
        logger.error(e)
        sys.exit()
        
def export_alembic(*args, **kwargs):
    """ 上传模型abc文件
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
        # get rendering group
        _rendering_group = renderinggroup.nodes()
        if _rendering_group:
            _job = "-frameRange 1 1 -attr rendering -stripNamespaces -uvWrite -writeColorSets -writeFaceSets -worldSpace -writeVisibility -writeUVSets -root {} -file {}".format(" ".join(_rendering_group), _publish_file)
            cmds.AbcExport(j = [_job])
            filefunc.publish_file(_publish_file, _production_file)
            filefunc.publish_file(_publish_file, _cover_file)      
            # record in database
            _file_info = zfile.get_file_info(_publish_file, _production_file)
            zfused_api.task.new_production_file([_file_info], _task_id, _attr_id, int(_file_index) )

    except Exception as e:
        logger.error(e)
        return False

    return True

if __name__ == '__main__':
    publish_file()