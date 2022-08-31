# coding:utf-8
# --author-- binglu.wang
from __future__ import print_function

import os
import json
import logging

import maya.cmds as cmds

import zfused_api
import zfused_maya.core.record as record
import zfused_maya.node.core.element as element
import zfused_maya.node.core.alembiccache as alembiccache

__all__ = ["import_cache"]
logger = logging.getLogger(__name__)

# load abc plugin
_is_load = cmds.pluginInfo("AbcImport", query=True, loaded = True)
if not _is_load:
    try:
        logger.info("try load AbcImport plugin")
        cmds.loadPlugin("AbcImport")
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

def set_resolution_size():
    """
    """
    _project_id = record.current_project_id()
    _project_handle = zfused_api.project.Project(_project_id)
    _width,_height = _project_handle.config["ImageWidth"], _project_handle.config["ImageHeight"]
    cmds.setAttr("defaultResolution.width", _width)
    cmds.setAttr("defaultResolution.height", _height)


def _rebuild_cache()

def import_cache(argv_task_id, argv_attr_id, argv_attr_code, argv_attr_type, argv_attr_mode, argv_attr_local):
    '''import alembic cache
    '''

    _file_title = "shader/redshift"
    
    # input task
    _input_task_id = argv_task_id
    _input_task_handle = zfused_api.task.Task(_input_task_id)
    # get shot frame
    _project_entity = _input_task_handle.project_entity()
    _start_frame = _project_entity.start_frame()
    _end_frame = _project_entity.end_frame()
    cmds.playbackOptions(min = _start_frame, max = _end_frame)
    set_resolution_size()
    # get shot version
    _input_production_path = _input_task_handle.production_path()
    _version_id = _input_task_handle.last_version_id()
    if not _version_id:
        return
    # get json path
    _version_handle = zfused_api.version.Version(_version_id)
    _outputattr_handle = zfused_api.outputattr.OutputAttr(argv_attr_id)
    _attr_file = "{}/{}/{}{}".format(_input_production_path, argv_attr_code, _version_handle.data()["Name"], _outputattr_handle.data()["Suffix"])
    if not os.path.exists(_attr_file):
        return False
    # get shot info
    _elements = element.scene_elements()
    _asset_dict = element.get_asset(_elements, _file_title)
    _info = get_cache_info(_attr_file)

    # merge alembic cache
    for item in _info:
        _asset,_ns,_node,_path = item
        try:
            if _asset and _asset in _asset_dict and _asset_dict[_asset]["namespace"]:
                _tex_ns = _asset_dict[_asset]["namespace"][0]
                logger.info("load asset:{}".format(_path))
                alembiccache.import_cache(_asset, _ns, _node, _path, "{}:{}".format( _tex_ns, _node))
                _asset_dict[_asset]["namespace"].pop(0)
            else:
                logger.info("load camera:{}".format(_path))
                _log = alembiccache.import_cache(_asset,_ns,_node,_path)
        except:
            logger.warning("wrong load cache:{}".format(_path))
    return True

if __name__ == '__main__':
    import_cache()
