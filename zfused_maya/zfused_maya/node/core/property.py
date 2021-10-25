# -*- coding: utf-8 -*-
# --author-- lanhua.zhou

import time
import tempfile
import json

import maya.cmds as cmds
import pymel.core as pm

import zfused_api

from zcore import filefunc

import zfused_maya.core.record as record
import zfused_maya.node.core.renderinggroup as renderinggroup


def _write_to_disk(project_entity, data = {}):
    if not data:
        return
    _production_path = project_entity.production_path()
    _production_file = "{}/{}.property".format(_production_path, project_entity.code())
    # _production_file = "{}/.property".format(_production_path)
    _temp_file = "%s/%s.property"%(tempfile.gettempdir(),time.time())
    with open(_temp_file, "w") as handle:
        json.dump(data, handle, indent = 4)
    print(_temp_file, _production_file)
    filefunc.publish_file(_temp_file, _production_file)


# ==================================================================
# geometry
def get_geometrys():
    _geometry = []
    _is_rendering = renderinggroup.nodes()
    _objs = []
    if _is_rendering:
        _objs = pm.ls(_is_rendering, dag=True, type='mesh')
    else:
        _objs = pm.ls(dag=True, type='mesh')
    if not _objs:
        return _geometry
    for _obj in _objs:
        _mesh = {}
        _mesh["shape"] = _obj.name()
        _mesh["transform"] = _obj.getTransform().name()
        # -----------------------------------------------------------------------------
        _full_path = _obj.fullPath()
        if _is_rendering:
            for _rendering_node in _is_rendering:
                _export_node = "|" + _rendering_node.split("|")[-1]
                if _rendering_node in _full_path:
                    _full_path =   _export_node + _full_path.split(_rendering_node)[-1]
        _mesh["full_path"] = _full_path

        _mesh["vertices"] = _obj.numVertices()
        _mesh["edges"] = _obj.numEdges()
        _mesh["faces"] = _obj.numFaces()
        _mesh["polygons"] = _obj._numPolygons()     
        _geometry.append(_mesh)
    return _geometry

def get_boundingbox():
    _box = []
    _is_rendering = renderinggroup.nodes()
    _objs = []
    if _is_rendering:
        _objs = pm.ls(_is_rendering, dag=True, type='mesh')
    else:
        _objs = pm.ls(dag=True, type='mesh')
    if not _objs:
        return _box
    _box = pm.exactWorldBoundingBox(_objs)
    return _box

def geometry(project_entity = None):
    # ==================================================================
    # 写入 property geometry 属性内容
    _project_entity = project_entity
    _geometry = get_geometrys()
    if _project_entity:
        _project_entity.update_property("geometry", _geometry)
        # boundingbox
        _box = get_boundingbox()
        if _box:
            _project_entity.update_property("boundingbox", _box)
        # write to disk cache
        _data = _project_entity.property()
        _write_to_disk(_project_entity, _data)


# ==================================================================
# material and material
def get_engines():
    # 获取所有shading engines
    _engines = []
    _meshs = cmds.ls(type="mesh")
    for _mesh in _meshs:
        _mesh_sgs = cmds.listConnections(_mesh, type = "shadingEngine")
        _engines += _mesh_sgs
    return list(set(_engines))

def get_materials():
    # 获取所有材质
    pass

def get_material_assigns():
    return []

def material(project_entity):
    # ==================================================================
    # 写入 property material 属性内容
    _project_entity = project_entity
    _engines = get_engines()
    if _project_entity:
        _project_entity.update_property("engine", _engines)
        # write to disk cache
        _data = _project_entity.property()
        _write_to_disk(_project_entity, _data)

def material_assign(project_entity):
    # ==================================================================
    # 写入 property material assign 属性内容
    _project_entity = project_entity
    _material_assigns = get_material_assigns()
    if _project_entity:
        _project_entity.update_property("material_assign", _material_assigns)
        # write to disk cache
        _data = _project_entity.property()
        _write_to_disk(_project_entity, _data)

# ==================================================================
# assets
def get_assets():
    _asset = []
    # 获取reference文件
    _reference_nodes = cmds.ls(rf = True)
    for _node in _reference_nodes:
        _file_path = cmds.referenceQuery(_node, f = True, wcn = True)
        _namespace = cmds.referenceQuery(_node, namespace = True)
        _production_files = zfused_api.zFused.get("production_file_record", filter = {"Path": _file_path})
        if _production_files:
            _production_file = _production_files[-1]
            _task_id = _production_file.get("TaskId")
            _task = zfused_api.task.Task(_task_id)
            _task_project_entity = _task.project_entity()
            if _task_project_entity.object() == "asset":
                _asset.append( {
                    "id": _task_project_entity.id(),
                    "code": _task_project_entity.code(),
                    "namespace": _namespace
                } )
    return _asset

def asset(project_entity = None):
    # ==================================================================
    # 写入 property assets 属性内容
    _project_entity = project_entity
    _asset = get_assets()
    if _asset and _project_entity:
        _project_entity.update_property("asset", _asset)
        # write to disk cache
        _data = _project_entity.property()
        _write_to_disk(_project_entity, _data)


# ==================================================================
# assembly
def get_assemblys():
    _assembly = []
    # 获取reference文件
    _reference_nodes = cmds.ls(rf = True)
    for _node in _reference_nodes:
        _file_path = cmds.referenceQuery(_node, f = True, wcn = True)
        _namespace = cmds.referenceQuery(_node, namespace = True)
        _production_files = zfused_api.zFused.get("production_file_record", filter = {"Path": _file_path})
        if _production_files:
            _production_file = _production_files[-1]
            _task_id = _production_file.get("TaskId")
            _task = zfused_api.task.Task(_task_id)
            _task_project_entity = _task.project_entity()
            if _task_project_entity.object() == "assembly":
                _assembly.append( {
                    "id": _task_project_entity.id(),
                    "code": _task_project_entity.code(),
                    "namespace": _namespace
                } )
    return _assembly

def assembly(project_entity = None):
    # ==================================================================
    # 写入 property assemblys 属性内容
    _project_entity = project_entity
    _assembly = get_assemblys()
    if _assembly and _project_entity:
        _project_entity.update_property("assembly", _assembly)
        # write to disk cache
        _data = _project_entity.property()
        _write_to_disk(_project_entity, _data)