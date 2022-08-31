# coding:utf-8
# --author-- binglu.wang
from __future__ import print_function

import os
import sys
import json
import logging

import maya.cmds as cmds

import zfused_api
import zfused_maya.node.core.element as element
import zfused_maya.node.core.yeticache as yeticache

__all__ = ["import_yeti_cache"]
logger = logging.getLogger(__name__)

_is_load = cmds.pluginInfo("pgYetiMaya", query=True, loaded = True)
if not _is_load:
    try:
        logger.info("try load pgYetiMaya plugin")
        cmds.loadPlugin("pgYetiMaya")
    except Exception as e:
        logger.error(e)
        sys.exit()

def get_cache_info(cache_file):
    '''load json info
    '''
    with open(cache_file, 'r') as info:
        dataInfo = json.load(info)
        info.close()
    return dataInfo

def arrange_info(info,_dict = {}):
    for _i in info:
        _asset,_ns,_node,_path = _i
        if _asset not in _dict:
            _dict[_asset] = {}
        if _ns not in _dict[_asset]:
            _dict[_asset][_ns] = []
        _dict[_asset][_ns].append(_node)
        _dict[_asset][_ns].append(_path)
    return _dict


def import_yeti_cache(argv_task_id, argv_attr_id, argv_attr_code, argv_attr_type, argv_attr_mode, argv_attr_local):
    # 思路：
    # 镜头打开后查询json信息，如果有，根据json信息对比文件中的元素领取yeti材质文件，然后附缓存
    _file_title = "fur/yeti"

    _input_task_id = argv_task_id
    _input_task_handle = zfused_api.task.Task(_input_task_id)
    _input_production_path = _input_task_handle.production_path()
    _version_id = _input_task_handle.last_version_id()
    if not _version_id:
        return
    _version_handle = zfused_api.version.Version(_version_id)
    _outputattr_handle = zfused_api.outputattr.OutputAttr(argv_attr_id)
    _attr_file = "{}/{}/{}{}".format(_input_production_path, argv_attr_code, _version_handle.data()["Name"], _outputattr_handle.data()["Suffix"]) 
    if not os.path.exists(_attr_file):
        return False
    # get shot info
    _elements = element.scene_elements()
    _asset_dict = element.get_asset(_elements,_file_title)
    _info = get_cache_info(_attr_file)
    if not _info:
        return
    _info = arrange_info(_info)
    # merge yeti cache
    for _asset in _info:
        for item in _info[_asset].values():
            if _asset in _asset_dict and _asset_dict[_asset]["namespace"]:
                _tex_ns = _asset_dict[_asset]["namespace"][0]
                try:
                    _nodes = item[::2]
                    _paths = item[1::2]
                    for _node,_path in zip(_nodes,_paths):
                        logger.info("load yeticache:{}".format(_path))
                        yeticache.import_cache(_path,"{}:{}".format(_tex_ns,_node))
                except:
                    logger.warning("wrong load yeti cache:{}".format(_path))
                _asset_dict[_asset]["namespace"].pop(0)
    return True

if __name__ == '__main__':
    import_yeti_cache()