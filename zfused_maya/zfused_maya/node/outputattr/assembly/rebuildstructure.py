# coding:utf-8
# --author-- ning.qin
# 从json重建场景结构

import os
import json
from pymel.core import *
import maya.cmds as cmds

def read_json_file(file_path):
    with open(os.path.abspath(file_path), "r") as json_file:
        json_dict = json.load(json_file)
    return json_dict if json_dict else {}
def write_json_file(json_dict, file_path):
    with open(file_path,"w") as json_file:
        json_file.write(json.dumps(json_dict,indent = 4,separators=(',',':')))
        json_file.close()

file_path = 'X:/BKM2/sequence/seq066/assembly/maya2017/structure/seq066.json'
root_node_list = read_json_file(file_path)

def build_structure(parent_node_list, parent):
    for parent_node in parent_node_list:
        node_type = parent_node['node_type']
        child     = parent_node['child']
        namespace = parent_node['namespace']
        name      = parent_node['name']
        attr      = parent_node['attr']
        if namespace != '':
            name = namespace + ':' + name
        if parent == '':
            createNode(node_type, name = name)
        else:
            createNode(node_type, name = name, parent = parent)
        for attr_name, attr_info in attr.items():
            attr_value = attr_info['static_data']
            setAttr(name + '.' + attr_name, attr_value)
        
        build_structure(child, name)
build_structure(root_node_list, '')



#   
# new
import json
import maya.cmds as cmds

import zfused_api
import zfused_maya.core.record as record

import zfused_maya.node.core.proxycontainer as pc

_current_project_id = record.current_project_id()

def read_json_file(file_path):
    with open(os.path.abspath(file_path), "r") as json_file:
        json_dict = json.load(json_file)
    return json_dict if json_dict else {}

def build_structure(parent_node_list, parent):
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
                node_type = "proxycontainer"
                _asset_handle = zfused_api.asset.Asset(_assets[0]["Id"])
                _production_path = _asset_handle.production_path()
                _proxy_file = "{}/shader/redshift/maya2017/proxy/{}.rs".format(_production_path, _asset_handle.file_code())
                _gpu_file = "{}/shader/redshift/maya2017/gpu/{}.abc".format(_production_path, _asset_handle.file_code())
                
        if parent == '':
            if node_type == "proxycontainer":
                #cmds.file(_proxy_file, i = True)
                _node_name,_,_ = pc.create_rs_container(_proxy_file,_gpu_file)
            else:
                _node_name = cmds.createNode(node_type, name = name, parent = "")
        else:
            if node_type == "proxycontainer":
                _node_name,_,_ = pc.create_rs_container(_proxy_file,_gpu_file)
                cmds.parent(_node_name, parent)
            else:
                _node_name = cmds.createNode(node_type, name = name, parent = parent)
            #_node_name = cmds.createNode(node_type, name = name, parent = parent)
        for attr_name, attr_info in attr.items():
            attr_value = attr_info['static_data']
            cmds.setAttr(_node_name + '.' + attr_name, attr_value)
        build_structure(child, _node_name)

_file = "X:/BKM2/shot/seq006/shot001/animation/maya2017/structure/seq006_shot001.0001.json"


_data_list = read_json_file(_file)


build_structure(_data_list, "")