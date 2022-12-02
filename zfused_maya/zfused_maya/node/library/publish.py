# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import logging

import maya.cmds as cmds

import zfused_api

from zcore import transfer,filefunc,zfile

import zfused_maya.core.record as record

from zfused_maya.node.core import yeti,attr,check,alembiccache,texture,referencefile,relatives,element,scene

logger = logging.getLogger(__name__)


def publish(infomation):
    """ 上传任务备份文件
    """
    _current_file = cmds.file(q = True, sn = True)
    _suffix = os.path.splitext(_current_file)[-1]
    infomation["suffix"] = _suffix
    _file_size = os.path.getsize(_current_file)
    infomation["size"] = _file_size
    _format = cmds.file(q = True, typ = True)[0]
    infomation["format"] = _format

    _library_id = infomation.get("library_id")
    _library_entity_id = infomation.get("library_entity_id")
    _code = infomation.get("code")
    _renderer = infomation.get("renderer")
    _software_id = infomation.get("software_id")
    _description = infomation.get("description")

    _library_handle = zfused_api.library.Library(_library_id)
    _library_entity_handle = zfused_api.library.LibraryEntity(_library_entity_id)

    _library_path = _library_handle.data().get("Path")
    _library_entity_path = "{}/{}".format(_library_path, _library_entity_handle.data().get("Code"))

    # temp file
    _base_name = os.path.basename(_current_file)
    _temp_file = "{}/{}".format(os.getenv('TEMP'), _base_name)
    cmds.file(rename = _temp_file)
    cmds.file(save = True, type = _format, f = True, options = "v=0;")

    
    _edition_path = "{}/{}".format(_library_entity_path, _code)
    _edition_name = "{}/{}/{}{}".format(_library_entity_path, _code, _code, _suffix)

    try:
        # publish texture
        _texture_files = texture.files()
        if _texture_files:
            _path_set = texture.paths(_texture_files)[0]
            _intersection_path = max(_path_set)
            texture.publish_file(_texture_files, _intersection_path, _edition_path + "/texture")
            # change maya texture node path
            _file_nodes = texture.nodes()
            if _file_nodes:
                texture.change_node_path(_file_nodes, _intersection_path, _edition_path + "/texture")
        # publish alembic cache
        _alembic_files = alembiccache.files()
        if _alembic_files:
            _path_set = alembiccache.paths(_alembic_files)[0]
            _intersection_path = max(_path_set)
            alembiccache.publish_file(_alembic_files, _intersection_path, _edition_path + "/cache/alembic")
            _file_nodes = alembiccache.nodes()
            if _file_nodes:
                alembiccache.change_node_path(_file_nodes, _intersection_path, _edition_path + "/cache/alembic")
        # publish reference file
        _reference_files = referencefile.files()
        if _reference_files:
            _path_set = referencefile.paths(_reference_files)[0]
            _intersection_path = max(_path_set)
            referencefile.publish_file(_reference_files, _intersection_path, _edition_path + "/reference")
            _file_nodes = referencefile.nodes()
            if _file_nodes:
                referencefile.change_node_path(_file_nodes, _intersection_path, _edition_path + "/reference")
        # publish yetinode texture
        _yeti_texture_file = yeti.tex_files()
        if _yeti_texture_file:
            _path_set = yeti.paths(_yeti_texture_file)[0]
            _intersection_path = max(_path_set)
            yeti.publish_file(_yeti_texture_file, _intersection_path, _edition_path + "/texture/yeti")
            _yeti_texture_dict = yeti._get_yeti_attr("texture","file_name")
            yeti.change_node_path(_yeti_texture_dict,_intersection_path, _edition_path + "/texture/yeti")
        
        # save publish file
        cmds.file(save = True, type = _format, f = True, options = "v=0;")
        # publish file
        filefunc.publish_file(_temp_file, _edition_name)
        _,_err = zfused_api.library.new_edition(_library_id, _library_entity_id, _code, _software_id, _renderer, _description, _format, _suffix, _file_size)
        if _err:
            _library_entity_handle.update_count()
            cmds.file(new = True, f = True)
        else:
            cmds.file(_current_file, o = True, f = True, pmt = False)
        return _err
    except Exception as e:
        logger.error(e)
        cmds.file(_current_file, o = True, f = True, pmt = False)
        return False
    return False