# -*- coding: UTF-8 -*-
'''
@Time    : 2022/4/1 18:01
@Author  : Jerris_Cheng
@File    : publish_growmesh_batch.py
@Description:
'''

from __future__ import print_function

import logging
import sys

import maya.cmds as cmds

import zfused_api

from zcore import filefunc,zfile

from zfused_maya.node.core import xgen,alembiccache

logger = logging.getLogger(__name__)
_is_load = cmds.pluginInfo("AbcExport", query=True, loaded=True)
if not _is_load:
    try:
        logger.info("try load alembic plugin")
        cmds.loadPlugin("AbcExport")
    except Exception as e:
        logger.error(e)
        sys.exit()

# 缓存预留帧 后面需要存放在数据库上
PREPFRAME = 8
EXPORTATTR = ["worldSpace", "uvWrite",'stripNamespaces',"writeUVSets"]


def publish_alembic(*args, **kwargs):
    """ 发布xgen 生长面abc
    """

    _task_id, _output_attr_id = args
    _output_attr_handle = zfused_api.attr.Output(_output_attr_id)
    _file_format = _output_attr_handle.format()
    _suffix = _output_attr_handle.suffix()
    _attr_code = _output_attr_handle.code()
    _task = zfused_api.task.Task(_task_id)
    _task_step = _task.project_step().code()

    _production_path = _task.production_path()
    _project_entity = _task.project_entity()
    _file_code = _task.file_code()
    if kwargs.get("fix_version"):
        _file_index = "{:0>4d}".format(_task.last_version_index(0))
    else:
        _file_index = "{:0>4d}".format(_task.last_version_index() + 1)

    # _start_frame = int(cmds.playbackOptions(q=True, min=True)) - 50
    # _end_frame = int(cmds.playbackOptions(q=True, max=True)) + PREPFRAME

    _publish_path = _task.temp_path()
    _cache_path = _task.cache_path()
    _abc_jobs = []
    _trans_list = []

    _project_porperty = _project_entity.property()
    # 记录 缓存 上传
    _assets = kwargs.get("assets")
    if not _assets:
        _assets = _project_porperty.get('asset')
    _asset_namespaces = [_asset.get("namespace") for _asset in _assets]

    _all_palettes = xgen.get_all_palettes()
    for _pallette in _all_palettes:
        _dag_dict = {}
        _short_ns = cmds.referenceQuery(_pallette, ns=1, shn=True)

        if _short_ns not in _asset_namespaces:
            continue

        _palette_name = _pallette.replace('{}:'.format(_short_ns), "")
        # grow_mesh_grp = xgen.get_growmesh(_pallette)
        _publish_file = '{}/{}/{}_{}.{}{}'.format(_publish_path, "growmesh_batch", _short_ns, _palette_name, _file_index, _suffix)
        _cache_file = '{}/{}/{}_{}.{}{}'.format(_cache_path, _attr_code, _short_ns,_palette_name, _file_index, _suffix)
        _cover_file = '{}/{}/{}_{}{}'.format(_cache_path, _attr_code, _short_ns,_palette_name, _suffix)
        _dag_dict['publish_file'] = _publish_file
        _dag_dict['cover_file'] = _cover_file
        _dag_dict['cache_file'] = _cache_file
        _trans_list.append(_dag_dict)

    try:
        # 输出缓存
        # cmds.AbcExport( j = _abc_jobs )

        _cache_file_info = []

        for _tran in _trans_list:
            print(_tran)
            publish_file = _tran.get('publish_file')
            cover_file = _tran.get('cover_file')
            cache_file = _tran.get('cache_file')
            _result = filefunc.publish_file(publish_file, cache_file)
            _result = filefunc.publish_file(publish_file, cover_file)

            _file_info = zfile.get_file_info(publish_file, cache_file)
            # _file_info['relative_entity_type'] = _tran.get("relative_entity_type")
            # _file_info['relative_entity_id'] = _tran.get("relative_entity_id")
            # _file_info['relative_name_space'] = _tran.get("relative_name_space")

            _cover_file_info = zfile.get_file_info(publish_file, cover_file)
            # _cover_file_info['relative_entity_type'] = _tran.get("relative_entity_type")
            # _cover_file_info['relative_entity_id'] = _tran.get("relative_entity_id")
            # _cover_file_info['relative_name_space'] = _tran.get("relative_name_space")

            _cache_file_info.append(_file_info)
            _cache_file_info.append(_cover_file_info)

        # record production file
        if _cache_file_info:
            zfused_api.task.new_production_file(_cache_file_info, _task_id, _output_attr_id, int(_file_index), fix_version = kwargs.get("fix_version"))


    except Exception as e:
        logger.error(e)
        # print(e)
        return False
    print(u'发布True')
    return True
