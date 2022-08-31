# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import json
import logging

import maya.cmds as cmds

import zfused_api

import zfused_maya.core.record as record

import zfused_maya.node.core.element as element
import zfused_maya.node.core.alembiccache as alembiccache
import zfused_maya.node.core.proxycontainer as proxycontainer
import zfused_maya.node.core.assembly as assembly


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
        #if namespace != '':
        #    name = namespace + ':' + name
        if node_type == "assemblyReference":
            _assets = zfused_api.zFused.get("asset", filter = {"Code": name, "ProjectId":_current_project_id})
            if not _assets:
                node_type = "transform"
            else:
                node_type = "assemblyReference"
                _asset_handle = zfused_api.asset.Asset(_assets[0]["Id"])
                _production_path = _asset_handle.production_path()
                _proxy_file = "{}/model/maya2017/assemblyDefinition/{}.mb".format(_production_path, _asset_handle.file_code())

        if node_type == "assemblyReference":
            if name not in global_instance_dict.keys():
                _assembly = assembly.create_assembly_reference(name, _proxy_file)
                _node_name = _assembly.name()
                _group_name = cmds.group(_node_name, name = "{}_instance_group".format(name))
                global_instance_dict[name] = _group_name

                for attr_name, attr_info in attr.items():
                    attr_value = attr_info['static_data']
                    if node_type == "assemblyReference":
                        if attr_name in ["rpx", "rpy", "rpz", "spx", "spy", "spz"]:
                            # if attr_value:
                            # continue
                            cmds.setAttr(_group_name + '.' + attr_name, attr_value)

            _ins_name = global_instance_dict[name]
            _node_name = cmds.instance(_ins_name)[0]
            # _child_name = cmds.listRelatives(_node_name, c = True, type = "assemblyReference")[0]
            # if _parent_name:
            #     _new_node_name = cmds.parent(_child_name, _parent_name, add = True, s = True)[0]
            #     # delete 
            #     cmds.delete(_node_name)
            #     _node_name = _new_node_name
            if _parent_name:
                _node_name = cmds.parent(_node_name, _parent_name)[0]
                # fix shear
                # cmds.setAttr("{}.shearXZ".format(_node_name), 0)
                # cmds.setAttr("{}.shearXY".format(_node_name), 0)
                # cmds.setAttr("{}.shearYZ".format(_node_name), 0)
        else:
            if name == _parent_name:
                name = "{}_dup_01".format(name)
            _node_name = cmds.createNode(node_type, name = name, parent = _parent_name)

        # if node_type == "assemblyReference":
        #     _assembly = assembly.create_assembly_reference(name, _proxy_file)
        #     _node_name = _assembly.name()
        #     if _parent_name:
        #         _node_name = cmds.parent(_node_name, _parent_name)[0]
        # else:
        #     if name == _parent_name:
        #         name = "{}_dup_01".format(name)
        #     _node_name = cmds.createNode(node_type, name = name, parent = _parent_name)

        for attr_name, attr_info in attr.items():
            attr_value = attr_info['static_data']
            if node_type != "assemblyReference":
                if attr_name in ["rpx", "rpy", "rpz", "spx", "spy", "spz"]:
                    # if attr_value:
                    continue
            cmds.setAttr(_node_name + '.' + attr_name, attr_value)

        # xform
        if parent_node.has_key("xform"):
            xform     = parent_node["xform"]
            if not node_type == "assemblyReference":
                cmds.xform(_node_name, ws = True, rt = xform[0])
                cmds.xform(_node_name, ws = True, t = xform[1])

        # matrix
        if parent_node.has_key("matrix"):
            _matrix = parent_node["matrix"]
            cmds.xform(_node_name, m = _matrix, ws = True)

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
            #print(_value)
            cmds.delete(_value)