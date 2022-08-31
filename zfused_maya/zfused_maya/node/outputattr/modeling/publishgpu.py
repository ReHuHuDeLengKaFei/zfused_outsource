 # coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import logging

import maya.cmds as cmds

import zfused_api
from zcore import filefunc

import zfused_maya.core.record as record

import zfused_maya.node.core.shadingengine as shadingengine
import zfused_maya.node.core.renderinggroup as renderinggroup
import zfused_maya.node.core.reducemesh as reducemesh

logger = logging.getLogger(__name__)


# load gpu plugin
_is_load = cmds.pluginInfo("gpuCache", query=True, loaded = True)
if not _is_load:
    try:
        logger.info("try load gpu plugin")
        cmds.loadPlugin("gpuCache")
    except Exception as e:
        logger.error(e)
        sys.exit()

def publish_gpu(*args, **kwargs):
    """ publish gpu file

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

    _file_name = "{}.{}".format(_file_code, _file_index)


    try:
        # change shading color
        _engines = shadingengine.get_shading_engines()
        # 
        for _index, _engine in enumerate(_engines):
            _color = shadingengine.get_node_shading_color(_engine)
            # 可能会出问题
            if _color:
                shadingengine.set_node_shading_color(_engine, _color)
        shadingengine.switch_color_shader(_engines)
        
        _is_rendering = renderinggroup.nodes()
        _rendering_groups = " ".join(_is_rendering)
        #   is animation ???
        _alembic_nodes = cmds.ls(type = "AlembicNode")
        if _alembic_nodes:
            _start_time = cmds.playbackOptions(q = True, min = True)
            _end_time = cmds.playbackOptions(q = True, max = True)
            cmds.gpuCache(_rendering_groups, startTime = _start_time, endTime = _end_time, writeMaterials = True, directory = _publish_file_dir, fileName = _file_name) #allDagObjects = True)
        else:
            # will reduce mesh
            # get gpu reduce percentage
            _reduce_percentage = _output_link_handle.xattr("gpu_reduce_percentage")
            if _reduce_percentage == "100":
                cmds.gpuCache(_rendering_groups, startTime = 1, endTime = 1, writeMaterials = True, directory = _publish_file_dir, fileName = _file_name) #allDagObjects = True)
            else:
                reducemesh.reduce_mesh(float(_reduce_percentage), _publish_file_dir, _file_name)
        logger.info("export alembic gpu file : {}".format(_publish_file))
    except Exception as e:
        logger.info("error export alembic gpu file : {}\n{}".format(_publish_file, e))
        return False
    finally:
        # change orignail shader
        shadingengine.switch_orignail_shader(_engines)


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