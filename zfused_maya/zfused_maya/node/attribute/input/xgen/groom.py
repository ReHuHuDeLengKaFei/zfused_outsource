# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import logging


import maya.cmds as cmds


import zfused_api


from zfused_maya.node.core import groom
from zfused_maya.node.core import xgen

import xgenm as xg
import xgenm.xgGlobal as xgg

logger = logging.getLogger(__name__)
_is_load = cmds.pluginInfo("AbcImport", query=True, loaded = True)
if not _is_load:
    try:
        logger.info("try load alembic plugin")
        cmds.loadPlugin("AbcImport")
    except Exception as e:
        logger.error(e)


@zfused_api.reset
def alembic_merge(*args,**kwargs):
    # _task_id, _task_attr_input_id, _input_task_id, _input_task_attr_output_id, _namesapce = args
    _task_id = kwargs.get("task_id")
    _task_attr_input_id = kwargs.get("task_attr_input_id")
    _input_task_id = kwargs.get("input_task_id")
    _input_task_attr_output_id = kwargs.get("input_task_attr_output_id")
    _namespace = kwargs.get("namespace")
    _index = kwargs.get("index")

    _task = zfused_api.task.Task(_task_id)
    _task_attr_input = zfused_api.attr.Input(_task_attr_input_id)
    _extended_version = _task_attr_input.extended_version()
    if _index == -1:
        _extended_version = False
    elif _index:
        _extended_version = True

    _input_task = zfused_api.task.Task(_input_task_id)
    _input_task_attr_output = zfused_api.attr.Output(_input_task_attr_output_id)
    _input_task_project_step_id = _input_task_attr_output.project_step_id()
    _input_production_path = _input_task.cache_path()

    # get file 
    if _index:
        _file_index = "{:0>4d}".format(_index)
    else:
        _file_index = "{:0>4d}".format(_input_task.last_version_index())
    _file_suffix = _input_task_attr_output.suffix()
    if _extended_version:
        # _file_index = "{:0>4d}".format(_input_task.last_version_index())
        _production_file = "{}/{}/{}.{}{}".format(_input_production_path, _input_task_attr_output.code(), _namespace, _file_index, _file_suffix)
    else:
        _production_file = "{}/{}/{}{}".format(_input_production_path, _input_task_attr_output.code(), _namespace, _file_suffix)
    if not os.path.isfile(_production_file):
        _production_file = _production_file.replace(_input_task_attr_output.code(), "groom_caching")
    # get asset material file
    print(_namespace)
    _rf_nodes = cmds.ls( rf = True )
    for _rf_node in _rf_nodes:
        _inr = cmds.referenceQuery(_rf_node, inr = True)
        if not _inr:
            _exist_namespace = cmds.referenceQuery(_rf_node, namespace = True, shn = True)
            print(_exist_namespace)
            # get rendering attribute
            if _exist_namespace.split("__in__")[0].split("|")[-1] == _namespace:
                _cachings = groom.nodes()
                print(_cachings)
                if not _cachings:
                    continue
                _cachings = cmds.ls(_cachings, sn = True)
                for _caching in _cachings:
                    if _caching.startswith("{}:".format(_exist_namespace)) or _caching.startswith("|{}:".format(_exist_namespace)):
                        print(_caching)
                        print(_production_file)
                        _caching = cmds.ls(_caching, l = True)[0]
                        cmds.AbcImport(_production_file, mode = 'import', connect = _caching)
                # cmds.file(_production_file, ns = "{}__in__{}".format(_namespace, _input_task_attr_output.code()), r = True, mergeNamespacesOnClash = False, ignoreVersion = True)


@zfused_api.reset
def alembic_assign(*args,**kwargs):
    # _task_id, _task_attr_input_id, _input_task_id, _input_task_attr_output_id, _namesapce = args
    _task_id = kwargs.get("task_id")
    _task_attr_input_id = kwargs.get("task_attr_input_id")
    _input_task_id = kwargs.get("input_task_id")
    _input_task_attr_output_id = kwargs.get("input_task_attr_output_id")
    _namespace = kwargs.get("namespace")
    _index = kwargs.get("index")

    _task = zfused_api.task.Task(_task_id)
    _task_attr_input = zfused_api.attr.Input(_task_attr_input_id)
    _extended_version = _task_attr_input.extended_version()
    if _index == -1:
        _extended_version = False
    elif _index:
        _extended_version = True

    _input_task = zfused_api.task.Task(_input_task_id)
    _input_task_attr_output = zfused_api.attr.Output(_input_task_attr_output_id)
    _input_task_project_step_id = _input_task_attr_output.project_step_id()
    _input_production_path = _input_task.cache_path()

    # get file 
    if _index:
        _file_index = "{:0>4d}".format(_index)
    else:
        _file_index = "{:0>4d}".format(_input_task.last_version_index())
    _file_suffix = _input_task_attr_output.suffix()
    if _extended_version:
        # _file_index = "{:0>4d}".format(_input_task.last_version_index())
        _production_file = "{}/{}/{}.{}{}".format(_input_production_path, _input_task_attr_output.code(), _namespace, _file_index, _file_suffix)
    else:
        _production_file = "{}/{}/{}{}".format(_input_production_path, _input_task_attr_output.code(), _namespace, _file_suffix)

    # get asset
    _rf_nodes = cmds.ls( rf = True )
    for _rf_node in _rf_nodes:
        _inr = cmds.referenceQuery(_rf_node, inr = True)
        if not _inr:
            _exist_namespace = cmds.referenceQuery(_rf_node, namespace = True, shn = True)
            print(_exist_namespace)
            # get rendering attribute
            if _exist_namespace.split("__in__")[0].split("|")[-1] == _namespace:                
                # 获取 xgen collection and description
                _growmeshs = []
                _all_palettes = xg.palettes()
                for _palette in _all_palettes:
                    if not _palette.startswith(_exist_namespace):
                        continue
                    _des_editor = xgg.DescriptionEditor
                    _des_editor.setCurrentPalette(_palette)
                    _pale_descs = xg.descriptions(_palette)

                    # for _desc in _pale_descs:
                    #     _des_editor.setCurrentDescription(_desc)    
                    #     if _extended_version:
                    #         _file_index = "{:0>4d}".format(_input_task.last_version_index())
                    #         _production_file = "{}/{}/{}_{}_{}.{}{}".format(_input_production_path, _input_task_attr_output.code(), _namespace, _palette.split(":")[-1], _desc.split(":")[-1], _file_index, _file_suffix)
                    #     else:
                    #         _production_file = "{}/{}/{}_{}_{}{}".format(_input_production_path, _input_task_attr_output.code(), _namespace, _palette.split(":")[-1], _desc.split(":")[-1], _file_suffix)
                    #     print(_production_file)
                    #     print(os.path.isfile(_production_file))
                    #     xg.setAttr('renderer', 'Arnold Renderer', _palette, _desc, 'RendermanRenderer')
                    #     xg.setAttr('custom__arnold_rendermode', '1', _palette, _desc, 'RendermanRenderer')
                    #     # xg.setAttr('custom__arnold_useAuxRenderPatch', '1', _palette, _desc, 'RendermanRenderer')
                    #     xg.setAttr('custom__arnold_multithreading', '1', _palette, _desc, 'RendermanRenderer')
                    #     # xg.setAttr('custom__arnold_auxRenderPatch', str(_production_file), _palette, _desc, 'RendermanRenderer')
                    #     if not os.path.isfile(_production_file):
                    #         continue
                    #     xg.setAttr('useCache', '1', _palette, _desc, 'SplinePrimitive')
                    #     xg.setAttr('cacheFileName', _production_file, _palette, _desc, 'SplinePrimitive')
                    #     xg.setAttr('liveMode', '0', _palette, _desc, 'SplinePrimitive')
                    #     _des_editor.refresh("Full")

                    for _desc in _pale_descs:
                        exist_short_ns = cmds.referenceQuery(_palette, ns=1, shn=True)
                        short_ns = exist_short_ns.split('__in__')[0]
                        _palette_name = _palette.replace('{}:'.format(exist_short_ns), "")

                        if _extended_version:
                            # _file_index = "{:0>4d}".format(_input_task.last_version_index())
                            _production_file = "{}/{}/{}_{}.{}{}".format(_input_production_path, _input_task_attr_output.code(), _namespace, _palette.split(":")[-1], _file_index, _file_suffix)
                        else:
                            _production_file = "{}/{}/{}_{}{}".format(_input_production_path, _input_task_attr_output.code(), _namespace, _palette.split(":")[-1], _file_suffix)
                        print(_production_file)
                        print(os.path.isfile(_production_file))
                        if not os.path.isfile(_production_file):
                            _production_file = _production_file.replace(_input_task_attr_output.code(), "growmesh_batch")

                        # _production_file = '{}/{}/{}_{}{}'.format(_cache_path, _attr_code, short_ns, _palette_name, _suffix)
                        # if not os.path.exists(_production_file):
                        #     continue

                        xg.setAttr("renderer", "Arnold Renderer", _palette, _desc, "RendermanRenderer")
                        # 设置渲染模式
                        xg.setAttr("custom__arnold_rendermode", "1", _palette, _desc, "RendermanRenderer")
                        # 开启读取缓存
                        xg.setAttr("custom__arnold_useAuxRenderPatch", "1", _palette, _desc, "RendermanRenderer")
                        oldpatchfile = xg.getAttr("custom__arnold_auxRenderPatch", _palette, _desc, "RendermanRenderer")
                        if _production_file == oldpatchfile:
                            continue
                        xg.setAttr("custom__arnold_auxRenderPatch", _production_file, _palette, _desc, "RendermanRenderer")
                        cmds.setAttr(_desc + ".ai_use_aux_render_patch", 1)
                        cmds.setAttr(_desc + ".ai_batch_render_patch", _production_file, type='string')

                continue


def assgin_growmesh(task_id, stepcode, suffix):
    _task_id = task_id
    _task_entity = zfused_api.task.Task(_task_id)
    _project_entity = _task_entity.project_entity()
    _software_code = _task_entity.software().code()
    _cache_path = _project_entity.cache_path() + '/cfx/{}'.format(_software_code)

    # # get file 
    # _file_suffix = _input_task_attr_output.suffix()
    # if _extended_version:
    #     _file_index = "{:0>4d}".format(_input_task.last_version_index())
    #     _production_file = "{}/{}/{}.{}{}".format(_input_production_path, _input_task_attr_output.code(), _namespace, _file_index, _file_suffix)
    # else:
    #     _production_file = "{}/{}/{}{}".format(_input_production_path, _input_task_attr_output.code(), _namespace, _file_suffix)

    _all_palettes = xgen.get_all_palettes()
    _attr_code = stepcode
    _suffix = suffix
    for _palette in _all_palettes:
        _descriptions = xg.descriptions(_palette)
        for _description in _descriptions:
            exist_short_ns = cmds.referenceQuery(_palette, ns=1, shn=True)
            short_ns = exist_short_ns.split('__in__')[0]
            _palette_name = _palette.replace('{}:'.format(exist_short_ns), "")
            #grow_mesh_grp = xgen.get_growmesh(_palette)
            _cover_file = '{}/{}/{}_{}{}'.format(_cache_path, _attr_code, short_ns, _palette_name, _suffix)
            if not os.path.exists(_cover_file):
                continue
            xg.setAttr("renderer", "Arnold Renderer", _palette, _description, "RendermanRenderer")
            # 设置渲染模式
            xg.setAttr("custom__arnold_rendermode", "1", _palette, _description, "RendermanRenderer")
            # 开启读取缓存
            xg.setAttr("custom__arnold_useAuxRenderPatch", "1", _palette, _description, "RendermanRenderer")
            oldpatchfile = xg.getAttr("custom__arnold_auxRenderPatch", _palette, _description, "RendermanRenderer")
            if _cover_file == oldpatchfile:
                continue
            xg.setAttr("custom__arnold_auxRenderPatch", _cover_file, _palette, _description, "RendermanRenderer")
            cmds.setAttr(_description + ".ai_use_aux_render_patch", 1)
            cmds.setAttr(_description + ".ai_batch_render_patch", _cover_file, type='string')

    return True