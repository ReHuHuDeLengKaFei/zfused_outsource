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

import zfused_maya.node.core.element as element
import zfused_maya.node.core.alembiccache as alembiccache
import zfused_maya.node.core.proxycontainer as proxycontainer

logger = logging.getLogger(__name__)

_is_load = cmds.pluginInfo("redshift4maya", query=True, loaded = True)
if not _is_load:
    try:
        logger.info("try load AbcImport plugin")
        cmds.loadPlugin("redshift4maya")
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

def build_structure(parent_node_list, parent, global_instance_dict):
    _parent_name = parent
    _current_project_id = record.current_project_id()
    for parent_node in parent_node_list:
        node_type = parent_node['node_type']
        child     = parent_node['child']
        namespace = parent_node['namespace']
        name      = parent_node['name']
        attr      = parent_node['attr']
        name = name.split("|")[-1]

        if node_type == "assemblyReference":
            _assets = zfused_api.zFused.get("asset", filter = {"Code": name, "ProjectId":_current_project_id})
            if not _assets:
                node_type = "transform"
            else:
                node_type = "proxycontainer"
                _asset_handle = zfused_api.asset.Asset(_assets[0]["Id"])
                _production_path = _asset_handle.production_path()
                _proxy_file = "{}/shader/redshift/maya2017/proxy/{}.rs".format(_production_path, _asset_handle.file_code())
                _gpu_file = "{}/shader/redshift/maya2017/gpu/{}.abc".format(_production_path, _asset_handle.file_code())

        if node_type == "proxycontainer":
            if name not in global_instance_dict.keys():
                _node_name, _, _ = proxycontainer.create_rs_container(_proxy_file, _gpu_file, False)
                global_instance_dict[name] = _node_name
                # _proxy_group = cmds.group(n = "{}_rsProxy_group".format(name), em = True)
                # _mesh = cmds.polyCube(n = "{}_rsProxy".format(name),ch = 0)[0]
                # _mesh = cmds.parent(_mesh, _proxy_group)[0]
                # global_instance_dict[name] = _mesh
                
                # _mesh = cmds.polyCube(n = "{}_rsProxy".format(name),ch = 0)[0]
                # _meshshape = cmds.listRelatives(_mesh,s = 1)[0]
                # _rsnode = cmds.createNode("RedshiftProxyMesh",n = name)
                # cmds.connectAttr("{}.o".format(_rsnode),"{}.i".format(_meshshape))
                # cmds.setAttr("{}.fileName".format(_rsnode), _proxy_file,type = "string")
                # cmds.setAttr("{}.displayMode".format(_rsnode), 1)
                # _group_name = cmds.group(_mesh, name = "{}_instance_group".format(name))
                # global_instance_dict[name] = _group_name

            # _ins_name = global_instance_dict[name]
            # _node_name = cmds.instance(_ins_name)[0]
            # _child_name = cmds.listRelatives(_node_name, c = True)[0]
            # if _parent_name:
            #     _new_node_name = cmds.parent(_child_name, _parent_name, add = True, s = True)[0]
            #     # delete 
            #     cmds.delete(_node_name)
            #     _node_name = _new_node_name
            _ins_name = global_instance_dict[name]
            _node_name = cmds.instance(_ins_name)[0]
            if _parent_name:
                _node_name = cmds.parent(_node_name, _parent_name)[0]
        else:
            if name == _parent_name:
                name = "{}_dup_01".format(name)
            _node_name = cmds.createNode(node_type, name = name, parent = _parent_name)
        

        # 设置属性值
        for attr_name, attr_info in attr.items():
            attr_value = attr_info['static_data']
            if node_type == "proxycontainer":
                if attr_name in ["rpx", "rpy", "rpz", "spx", "spy", "spz"]:
                    continue
            cmds.setAttr(_node_name + '.' + attr_name, attr_value)

        # # xform
        # if parent_node.has_key("xform"):
        #     xform     = parent_node["xform"]
        #     if not node_type == "proxycontainer":
        #         cmds.xform(_node_name, ws = True, rt = xform[0])
        #         cmds.xform(_node_name, ws = True, t = xform[1])
        #         cmds.xform(_node_name, ws = True, ro = xform[2])
        #         cmds.xform(_node_name, ws = True, st = xform[3])
        #         cmds.xform(_node_name, ws = True, s = xform[4])
                
        if child:
            build_structure(child, _node_name, global_instance_dict)

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

    #print(_attr_file)
    _datas = read_json_file(_attr_file)
    _global_instance_dict = {}
    build_structure(_datas, "", _global_instance_dict)
    if _global_instance_dict:
        for _,_value in _global_instance_dict.items():
            cmds.delete(_value)

    return
