# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os.path
import sys,time,logging,zfused_api
import maya.cmds as cmds

from zcore import filefunc,zfile

from zfused_maya.node.core import improve

from zfused_maya.node.core import renderinggroup,alembiccache,property,fixmeshname


logger = logging.getLogger(__name__)
_is_load = cmds.pluginInfo("AbcExport", query=True, loaded = True)
if not _is_load:
    try:
        logger.info("try load alembic plugin")
        cmds.loadPlugin("AbcExport")
    except Exception as e:
        logger.error(e)
        sys.exit()

# 缓存预留帧 后面需要存放在数据库上 
PREPFRAME = 8
EXPORTATTR = ["worldSpace", "writeVisibility", "uvWrite","writeUVSets"]

# @improve.viewportOff
def export_cache(*args, **kwargs):
    """ 发布动画abc
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
    _file_code =_task.file_code()
    if kwargs.get("fix_version"):
        _file_index = "{:0>4d}".format(_task.last_version_index( 0 ))
    else:
        _file_index = "{:0>4d}".format(_task.last_version_index() + 1)

    _start_frame = int(cmds.playbackOptions(q = True,min = True))-PREPFRAME
    _end_frame = int(cmds.playbackOptions(q = True,max = True))+PREPFRAME
    
    _publish_path = _task.temp_path()
    _cache_path = _task.cache_path()
    
    _abc_jobs = []
    _trans_list = []

    _project_porperty = _project_entity.property()

    _extend_attr = {}
    # 采样
    _sample = kwargs.get("sample")
    if _sample:
        _extend_attr["step"] = _sample

    # 记录 缓存 上传
    _render_dags = renderinggroup.nodes()
    _assets = kwargs.get("assets")
    if not _assets:
        _assets = _project_porperty.get('asset')
    if _assets:
        for _asset in _assets:
            _rfn = _asset.get('rfn')
            _l_ns = _asset.get('namespace')
            for _dag in _render_dags:

                fixmeshname.fix_deformed_mesh_name("_rendering", _dag)

                _dag_dict = {}
                _short_ns = cmds.referenceQuery(_dag,ns = 1,shn=True)
                _attr_code = 'asset'
                _publish_file = '{}/{}/{}.{}{}'.format(_publish_path,_attr_code,_short_ns, _file_index,_suffix)
                _cache_file = '{}/{}/{}.{}{}'.format(_cache_path,_attr_code,_short_ns,_file_index,_suffix)
                _cover_file = '{}/{}/{}{}'.format(_cache_path,_attr_code,_short_ns,_suffix)
                jober = alembiccache.create_frame_cache(_publish_file,_start_frame,_end_frame,_dag,*EXPORTATTR, **_extend_attr)
                if _short_ns == _l_ns:
                    _abc_jobs.append(jober)

                    _dag_dict['publish_file'] = _publish_file
                    _dag_dict['cover_file'] = _cover_file
                    _dag_dict['cache_file'] = _cache_file
                    # 关联信息
                    _dag_dict['relative_entity_type'] = "asset"
                    _dag_dict['relative_entity_id'] = _asset.get("id")
                    _dag_dict['relative_name_space'] = _asset.get("namespace")
                    _trans_list.append(_dag_dict)

                    _asset['last_cache'] = _cover_file
                    
                    _project_step_caches = _asset.get('project_step_caches')
                    if _project_step_caches:
                        _is_has = False
                        for _cache in _project_step_caches:
                            _step = _cache.get('step')
                            if _step == _task_step:
                                _is_has = True
                                _cache['path'] = _cache_file
                        if not _is_has:
                            _project_step_caches.append({
                                "step": _task_step,
                                "path": _cache_file
                            })
                    else:
                        _cache_dict = {}
                        _cache_dict['step'] = _task_step
                        _cache_dict['path'] = _cache_file
                        _project_step_caches.append(_cache_dict)
                    _asset['project_step_caches'] = _project_step_caches

    #  摄像机
    _cameras = _project_porperty.get('camera')
    if _cameras:
        for _camera in _cameras:
            _attr_code = "camera"
            camera_node = _camera.get('node')        
            camera_publish_file = '{}/{}/{}.{}{}'.format(_publish_path,_attr_code,_file_code,_file_index,_suffix)
            
            camera_jober = alembiccache.create_frame_cache(camera_publish_file,_start_frame,_end_frame,camera_node,*EXPORTATTR, **_extend_attr)
            _abc_jobs.append(camera_jober)

    try:
        # 输出缓存
        if _abc_jobs:
            cmds.AbcExport( j = _abc_jobs )

        # _cache_file_info = []
        # for _tran in _trans_list:
        #     publish_file = _tran.get('publish_file')
        #     cover_file   = _tran.get('cover_file')
        #     cache_file   = _tran.get('cache_file')
        #     _result = filefunc.publish_file(publish_file, cache_file)
        #     _result = filefunc.publish_file(publish_file, cover_file)

        #     _file_info = zfile.get_file_info(publish_file, cache_file)
        #     _file_info['relative_entity_type'] = _tran.get("relative_entity_type")
        #     _file_info['relative_entity_id'] = _tran.get("relative_entity_id")
        #     _file_info['relative_name_space'] = _tran.get("relative_name_space")
        #     _cover_file_info = zfile.get_file_info(publish_file, cover_file)
        #     _cover_file_info['relative_entity_type'] = _tran.get("relative_entity_type")
        #     _cover_file_info['relative_entity_id'] = _tran.get("relative_entity_id")
        #     _cover_file_info['relative_name_space'] = _tran.get("relative_name_space")
        #     _cache_file_info.append(_file_info)
        #     _cache_file_info.append(_cover_file_info)

        # # record production file
        # if _cache_file_info:
        #     zfused_api.task.new_production_file(_cache_file_info, _task_id, _output_attr_id, int(_file_index) )

    except Exception as e:
        logger.error(e)
        print(e)
        return False
    return True























    


