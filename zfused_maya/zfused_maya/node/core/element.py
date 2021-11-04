# -*- coding: utf-8 -*-
# --author-- lanhua.zhou

""" 关联操作集合 """

from __future__ import print_function

import os
import sys
import glob
import copy 
import json

import maya.cmds as cmds

import zfused_api
import zfused_maya.core.record as record

from . import attr


__CACHE_DICT = {
    "namespace": "",
    "reference_node": "",
    "link_object": "asset",
    "link_id": 0,
    "task_id": 0,
    "project_step_id": 0,
    "output_attr": "",
    "output_attr_id": 0,
    "version": 0,
    "version_id": 0,
    "project_id": 0,
    "relation_ship": "reference",
    "is_local": "false"
}


def scene_elements():
    """ get maya file scene elemnets

    :rtype: list
    """
    _scene_elements = []

    _project_id = record.current_project_id()
    if not _project_id:
        return _scene_elements

    # get rendering elements
    _rendering_groups = []
    _groups = cmds.ls(dag = True)
    for _group in _groups:
        if cmds.objExists("{}.redering".format(_group)):
            _is_rendering = cmds.getAttr("{}.redering".format(_group))
            if _is_rendering:
                _rendering_groups.append(_group)
    _all_references = {}
    for _rendering in _rendering_groups:
        if cmds.referenceQuery(_redering, isNodeReferenced = True):
            _node = cmds.referenceQuery(_redering, referenceNode = True)
            if not _all_references.keys().__contains__(_node):
                _all_references[_node] = []
            _all_references[_node].append(obj)
    for _reference in _all_references.keys():
        namespace = cmds.referenceQuery(_reference, namespace = True)
        if namespace.startswith(":"):
            namespace = namespace[1::]
        rfn = cmds.referenceQuery(_reference, rfn = True)
        #get attr
        _node_attr = attr.get_node_attr(rfn)
        if not _node_attr:
            continue
        if _node_attr["project_id"] != _project_id:
            continue
        copy_data = copy.deepcopy(__CACHE_DICT)
        for k in _node_attr.keys():
            if copy_data.keys().__contains__(k):
                copy_data[k] = _node_attr[k]
        copy_data["namespace"] = namespace
        copy_data["reference_node"] = rfn
        _scene_elements.append(copy_data)

    # reference node
    _reference_nodes = cmds.ls(type = "reference")
    for _node in _reference_nodes:
        if _node not in _all_references.keys():
            try:
                namespace = cmds.referenceQuery(_node, namespace = True)
            except:
                continue
            if namespace.startswith(":"):
                namespace = namespace[1::]
            _rfn = cmds.referenceQuery(_node, rfn = True)
            
            # 判定是否存在二级参考
            _pns = cmds.referenceQuery(_node, rfn = True, p = True)
            if _pns:
                continue
            
            #get attr
            # ref_attr = node.GetAttr(_rfn)
            _node_attr = attr.get_node_attr(_rfn)
            if not _node_attr:
                continue
            if _node_attr["project_id"] != _project_id:
                continue
            copy_data = copy.deepcopy(__CACHE_DICT)
            for k in _node_attr.keys():
                if copy_data.keys().__contains__(k):
                    copy_data[k] = _node_attr[k]
            copy_data["namespace"] = namespace
            copy_data["reference_node"] = _rfn
            _scene_elements.append(copy_data)
    
    # gpu

    
    # sets
    _sets = cmds.ls(type = "objectSet")
    for _set in _sets:
        _attr = attr.get_node_attr(_set)
        if _attr:
            if ":" not in _set:
                _attr["relation_ship"] = "parity"
                _scene_elements.append(_attr)

    return _scene_elements


def replace_by_step(element, project_step_id):
    """ replace file by new project step

    """
    _link_object = element["link_object"]
    _link_id = element["link_id"]
    _reference_node = element["reference_node"]

    _replace_tasks = zfused_api.zFused.get("task", filter = { "Object": _link_object,
                                                              "LinkId": _link_id,
                                                              "ProjectStepId": project_step_id})
    if not _replace_tasks:
        return
    _replace_task = _replace_tasks[0]
    _replace_task_handle = zfused_api.task.Task(_replace_task["Id"])
    _version_id = _replace_task_handle.last_version_id()
    if not _version_id:
        return
    _version_handle = zfused_api.version.Version(_version_id)
    # get replace file
    _step = "file"
    _path = _replace_task_handle.production_path()
    _name = _version_handle.data()["FilePath"]
    _file_path = "{}/{}{}".format(_path, _step, _name)

    # 是否要判定下载到本机 。。。
    #   
    cmds.file(_file_path, loadReference = _reference_node)

    #rewrite node info
    cmds.setAttr("%s.link_id"%element["reference_node"], str(_link_id), type = "string")
    cmds.setAttr("%s.task_id"%element["reference_node"], str(_replace_task["Id"]), type = "string")
    #version = versionHandle.data()["Index"]
    cmds.setAttr("%s.version_id"%element["reference_node"], str(_version_id), type = "string")

    element["version_id"] = _version_id
    element["link_id"] = _link_id
    element["task_id"] = _replace_task["Id"]
    
    return element



class ReferenceElement(object):
    def __init__(self, element):
        self._data = element


    def reference_node(self):
        """ get reference node
        """
        return self._data["reference_node"]

    def link(self):
        """ get link object and id

        """
        return self._data["link_object"], self._data["link_id"]

    def file(self):
        """ get element file

        """
        _version_id = self._data["version_id"]
        _version_handle = zfused_api.version.Version(_version_id)
        return _version_handle.production_file()

    def replace_by_project_step(self, project_step_id):
        """ 
        """
        if project_step_id == self._data["project_step_id"]:
            return

        # get project
        _project_step_handle = zfused_api.step.ProjectStep(project_step_id)

        # key output attr
        _key_output_attr = _project_step_handle.key_output_attr()

        # get step file
        _link_handle = zfused_api.objects.Objects(self._data["link_object"], self._data["link_id"])
        _version = _link_handle.project_step_versions(project_step_id)
        if not _version:
            return 
        _version_handle = zfused_api.version.Version(_version[-1]["Id"])
        _file = _version_handle.production_file()
        _reference_node = self.reference_node()
        
        attr.set_node_attr(_reference_node, _key_output_attr["Id"], _version_handle.id(), "true")
        # relatives.create_relatives()

        cmds.file(_file, loadReference = _reference_node)

    def replace_by_derivative(self, link_object, link_id):
        """ replace by derivative
        """ 
        _project_step_handle = zfused_api.step.ProjectStep(self._data["project_step_id"])
        # key output attr
        _key_output_attr = _project_step_handle.key_output_attr()
        
        _link_handle = zfused_api.objects.Objects(link_object, link_id)
        _version = _link_handle.project_step_versions(self._data["project_step_id"])
        if not _version:
            return 
        _version_handle = zfused_api.version.Version(_version[-1]["Id"])
        _production_file = _version_handle.production_file()

        # # 测试
        # _project_handle = zfused_api.project.Project(_version_handle.data().get("ProjectId"))
        # _production_file = _production_file.replace(_project_handle.production_path(),"$PRODUCTION_PATH")

        _reference_node = self.reference_node()
        attr.set_node_attr(_reference_node, _key_output_attr["Id"], _version_handle.id(), "true")
        cmds.file(_production_file, loadReference = _reference_node)

    def update(self):
        """ update version
        """
        # get last version
        # 
        _task_handle = zfused_api.task.Task(self._data["task_id"])
        _last_version_id = _task_handle.last_version_id()
        if _last_version_id == self._data["version_id"]:
            return True
        _version_handle = zfused_api.version.Version(_last_version_id)
        _production_file = _version_handle.production_file()
        
        # # 测试
        # _project_handle = zfused_api.project.Project(_version_handle.data().get("ProjectId"))
        # _production_file = _production_file.replace(_project_handle.production_path(),"$PRODUCTION_PATH")
        
        # get reference node
        _reference_node = self.reference_node()
        
        cmds.setAttr("%s.version" % _reference_node, str(_version_handle.data()["Index"]), type="string")
        cmds.setAttr("%s.version_id" % _reference_node, str(_last_version_id), type="string")
        self._data["version"] = _version_handle.data()["Index"]
        self._data["version_id"] = _last_version_id
        # relatives.create_relatives()
        cmds.file(_production_file, loadReference = _reference_node, f = True)

        # # save reference change
        # if cmds.referenceQuery(_reference_node,p = 1,rfn = 1):
        #     _savefile = cmds.referenceQuery(_reference_node,p = 1,f = 1)
        #     cmds.file(_savefile,sr = 1,f = 1)

    def copy(self):
        """ copy
        """
        pass


def get_asset(elements, title, _dict = {}):
    '''arrange asset info
    '''
    for _element in elements:
        _link_handle = zfused_api.objects.Objects(_element["link_object"], _element["link_id"])
        _assetname = _link_handle.code()
        _step_handle = zfused_api.step.ProjectStep(_element["project_step_id"])
        _step_code = _step_handle.code()
        #print(_step_code)
        if title.split("/")[0] in _step_code:
        # if _step_code.startswith("shader"):
            _task_handle = zfused_api.task.Task(_element["task_id"])
            _last_version_id = _task_handle.last_version_id()
            _version_handle = zfused_api.version.Version(_last_version_id)
            if _assetname in _dict:
                _dict[_assetname]["namespace"].append(_element["namespace"])
            else:
                _dict[_assetname] = {}
                _dict[_assetname]["namespace"] = [_element["namespace"]]
                _dict[_assetname]["path"] = _version_handle.production_file()
            _dict[_assetname]["namespace"] = list(set(_dict[_assetname]["namespace"]))
    return _dict