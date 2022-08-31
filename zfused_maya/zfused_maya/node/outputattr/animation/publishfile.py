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
import zfused_maya.node.core.referencefile as referencefile
import zfused_maya.node.core.attr as attr
import zfused_maya.node.core.xgen as xgen

__all__ = ["publish_file"]

logger = logging.getLogger(__name__)


def fix_reference_file():
    _nodes = referencefile.nodes(False)
    #print(_nodes)
    if _nodes:
        for _node in _nodes:
            _attr = attr.get_node_attr(_node)
            _version_handle = zfused_api.version.Version(_attr["version_id"])
            _output_attr_handle = zfused_api.outputattr.OutputAttr(_attr["output_attr_id"])
            # _file = _version_handle.production_file(_output_attr_handle.code())
            _file = _version_handle.without_version_version()
            # cmds.file(_file, loadReference = _node, options = "v=0;")
            cmds.file(_file, loadReference=_node, lrd="asPrefs", options="v=0;")
            cmds.setAttr("{}.is_local".format(_node), "false", type="string")


# test
def publish_file(*args, **kwargs):
    # copy publish file

    """ 上传动画文件

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

    # _production_path = _task_handle.production_path()
    # _temp_path = _output_link_handle.temp_path()

    if kwargs.get("fix_version"):
        _file_index = "{:0>4d}".format(_task_handle.last_version_index(0))
    else:
        _file_index = "{:0>4d}".format(_task_handle.last_version_index() + 1)

    _production_file = "{}/{}/{}/{}/{}.{}{}".format(_production_path, _step_code, _software_code, _attr_code,
                                                    _file_code, _file_index, _suffix)
    _production_file_dir = os.path.dirname(_production_file)
    _cover_file = "{}/{}/{}/{}/{}{}".format(_production_path, _step_code, _software_code, _attr_code, _file_code,
                                            _suffix)
    _publish_file = "{}/{}/{}/{}/{}.{}{}".format(_temp_path, _step_code, _software_code, _attr_code, _file_code,
                                                 _file_index, _suffix)
    _backup_path = _task_handle.backup_path()
    # ("_temp_path:{}_step_code:{}_software_code:{}_attr_code:{}_file_code:{}_file_index:{}_suffix:{}_production_path:{}".format(_temp_path,_step_code,_software_code,_attr_code,_file_code,_file_index,_suffix,_production_path))
    _publish_file_dir = os.path.dirname(_publish_file)
    if not os.path.isdir(_publish_file_dir):
        os.makedirs(_publish_file_dir)

    _xgen_list = xgen.xgenfile()
    if _xgen_list:
        xgen.publishxgen()

    try:
        # save publish file
        cmds.file(rename=_publish_file)
        cmds.file(save=True, type=_file_format, f=True,lockReference=False)
        # copy publish file
        _xgen_list = xgen.xgenfile()
        if _xgen_list:
            xgen.publishxgen()

        # fix camera aspect ratio
        _cameras = cmds.ls("{}*".format(_file_code), type="camera")
        if _cameras:
            for _camera in _cameras:
                # get
                if cmds.getAttr("{}.filmFit".format(_camera)) == 3:
                    _v_f = cmds.getAttr("{}.verticalFilmAperture".format(_camera))
                    cmds.setAttr("{}.horizontalFilmAperture".format(_camera), _v_f * 2.503)
        
        cmds.file(save=True, type=_file_format, f=True)

        # fix reference

        fix_reference_file()
        
        cmds.file(save=True, type=_file_format, f=True)
        #print("--------------------------------------has no reference")

        # # 取消上传设定帧数，帧数由制片设定
        # # publish frame
        # min_frame = cmds.playbackOptions(q = True, min = True)
        # max_frame = cmds.playbackOptions(q = True, max = True)
        # (min_frame, max_frame)
        # ("update start frame", _output_link_handle)
        # _output_link_handle.update_start_frame(int(min_frame))
        # ("update end frame")
        # _output_link_handle.update_end_frame(int(max_frame))
        # ("is over ???")

        # # publish texture
        # _texture_files = texture.files()
        # if _texture_files:
        #     _path_set = texture.paths(_texture_files)[0]
        #     _intersection_path = max(_path_set)
        #     texture.publish_file(_texture_files, _intersection_path, _production_path + "/texture")
        #     # change maya texture node path
        #     _file_nodes = texture.nodes()
        #     if _file_nodes:
        #         texture.change_node_path(_file_nodes, _intersection_path, _production_path + "/texture")

        # publish alembic cache

        _alembic_files = alembiccache.files()
        if _alembic_files:
            _path_set = alembiccache.paths(_alembic_files)[0]
            _intersection_path = max(_path_set)
            alembiccache.publish_file(_alembic_files, _intersection_path, _production_path + "/cache/alembic")
            _file_nodes = alembiccache.nodes()
            if _file_nodes:
                alembiccache.change_node_path(_file_nodes, _intersection_path, _production_path + "/cache/alembic")

        # # delete unused material
        # material.delete_unused()
        # # fix mesh name
        # _is_rendering = renderinggroup.nodes()
        # fixmeshname.fix_mesh_name("_rendering", _is_rendering)
        # # recore material
        # material.record()

        # save publish file
        cmds.file(save=True, type=_file_format, f=True)

        # publish file
        _result = filefunc.publish_file(_publish_file, _production_file)
        _result = filefunc.publish_file(_publish_file, _cover_file)

        # link files
        zfused_api.files.new_file("task", _task_id, _production_file, int(_file_index))
        zfused_api.files.new_file("task", _task_id, _cover_file, int(_file_index))

        if _xgen_list:
            for _xgen_node in _xgen_list:

                _xgen_name = xgen._getxgenfilename(_xgen_node)
                _xgen_path = xgen._getxgenfile(_xgen_node)
                _cover_xgen_file = "{}/{}/{}/{}/{}".format(_production_path, _step_code, _software_code, _attr_code,
                                                           _xgen_name)
                _backup_xgenfile = "{}/{}".format(_backup_path, _xgen_name)
                #print("xgen_trancsform______________________________________")
                #print(_backup_xgenfile)

                if os.path.exists(_xgen_path):
                    filefunc.publish_file(_xgen_path, _cover_xgen_file)
                    filefunc.publish_file(_xgen_path, _backup_xgenfile)


    except Exception as e:
        logger.error(e)
        return False

    # open orignal file
    # cmds.file(_current_file, o = True, f = True, pmt = True)
    return True