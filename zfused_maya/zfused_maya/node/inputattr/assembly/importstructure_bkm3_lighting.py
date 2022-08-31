# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function
from collections import defaultdict

import os
import json
import logging

import maya.cmds as cmds

import zfused_api

import zfused_maya.core.record as record
import zfused_maya.node.core as core

import zfused_maya.node.core.element as element
import zfused_maya.node.core.alembiccache as alembiccache
import zfused_maya.node.core.proxycontainer as proxycontainer


_is_load = cmds.pluginInfo("mtoa", query=True, loaded = True)
if not _is_load:
    try:
        logger.info("try load arnold plugin")
        cmds.loadPlugin("mtoa")
    except Exception as e:
        logger.error(e)

def read_json_file(file_path):
    with open(os.path.abspath(file_path), "r") as json_file:
        json_dict = json.load(json_file)
    return json_dict if json_dict else {}

def write_json_file(json_dict, file_path):
    with open(file_path,"w") as json_file:
        json_file.write(json.dumps(json_dict, indent = 4, separators=(',',':')))
        json_file.close()

@core.viewportOff
def build_structure(parent_node_list, parent, global_instance_dict, global_instance_num_dict, all_assets):
    _parent_name = parent
    _current_project_id = record.current_project_id()
    for parent_node in parent_node_list:
        # print(parent_node)
        node_type = parent_node['node_type']
        child     = parent_node['child']
        namespace = parent_node['namespace']
        name      = parent_node['name']
        attr      = parent_node['attr']
        name = name.split("|")[-1]
        #print(name)
        if node_type == "assemblyReference":
            if not name in all_assets:
                node_type = "transform"
            else:
                node_type = "proxycontainer"
                _asset_handle = zfused_api.asset.Asset(all_assets[name])
                _production_path = _asset_handle.production_path()
                _proxy_file = "{}/shader/arnold/maya2018/proxy/{}.ass".format(_production_path, _asset_handle.file_code())
                _gpu_file = "{}/shader/arnold/maya2018/gpu/{}.abc".format(_production_path, _asset_handle.file_code())

        if node_type == "proxycontainer":
            if name not in global_instance_dict.keys():
                _node_name, _, _ = proxycontainer.create_ass_container(_proxy_file, _gpu_file, False)
                global_instance_dict[name] = [_node_name]
                global_instance_num_dict[_node_name] = 0
            if global_instance_num_dict[global_instance_dict[name][-1]] >= 499:
                #print("new instance ==========================================================")
                _node_name, _, _ = proxycontainer.create_ass_container(_proxy_file, _gpu_file, False)
                global_instance_dict[name].append(_node_name)
                global_instance_num_dict[_node_name] = 0

            _ins_name = global_instance_dict[name][-1]
            _node_name = cmds.instance(_ins_name)[0]
            global_instance_num_dict[global_instance_dict[name][-1]] = global_instance_num_dict[global_instance_dict[name][-1]] + 1
            if _parent_name:
                _node_name = cmds.parent(_node_name, _parent_name)[0]
                # # fix shear
                cmds.setAttr("{}.shearXZ".format(_node_name), 0)
                cmds.setAttr("{}.shearXY".format(_node_name), 0)
                cmds.setAttr("{}.shearYZ".format(_node_name), 0)
        else:
            if name == _parent_name:
                name = "{}_dup_01".format(name)
            _node_name = cmds.createNode(node_type, name = name, parent = _parent_name)
        # matrix
        if parent_node.has_key("matrix"):
            try:
                _visibility = attr["visibility"]
                cmds.setAttr("{}.visibility".format(_node_name), _visibility['static_data'])
            except:
                pass
            _matrix = parent_node["matrix"]
            cmds.xform(_node_name, m = _matrix, ws = True)
        else:
            for attr_name, attr_info in attr.items():
                attr_value = attr_info['static_data']
                if node_type != "proxycontainer":
                    if attr_name in ["rpx", "rpy", "rpz", "spx", "spy", "spz"]:
                        continue
                cmds.setAttr(_node_name + '.' + attr_name, attr_value)

            # xform
            if parent_node.has_key("xform"):
                xform     = parent_node["xform"]
                if not node_type == "proxycontainer":
                    cmds.xform(_node_name, ws = True, rt = xform[0])
                    cmds.xform(_node_name, ws = True, t = xform[1])
                
        if child:
            build_structure(child, _node_name, global_instance_dict, global_instance_num_dict, all_assets)

def import_structure(argv_task_id, argv_attr_id, argv_attr_code, argv_attr_type, argv_attr_mode, argv_attr_local):
    """ 导入场景结构
    """
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
    _datas = read_json_file(_attr_file)
    _global_instance_dict = {}
    global_instance_num_dict = {}
    _current_project_id = record.current_project_id()
    # _assets = zfused_api.zFused.get("asset", filter = {"ProjectId":_current_project_id})
    _assets = zfused_api.asset.cache([_current_project_id])
    _asset_dict = {}
    list(map(lambda _asset: _asset_dict.setdefault(_asset["Code"], _asset["Id"]), _assets))
    # cmds.undoInfo(openChunk = 1)
    build_structure(_datas, "", _global_instance_dict, global_instance_num_dict, _asset_dict)
    # cmds.undoInfo(closeChunk = 1)
    if _global_instance_dict:
        for _,_value in _global_instance_dict.items():
            cmds.delete(_value)

    return
