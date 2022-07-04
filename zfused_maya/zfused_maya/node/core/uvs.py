# -*- coding: UTF-8 -*-
"""
@Time    : 2022/6/30 14:08
@Author  : Jerris_Cheng
@File    : uvs.py
@Description:
"""
from __future__ import print_function

import maya.cmds as cmds
from maya import OpenMaya
from pymel import core

from zfused_maya.node.core import renderinggroup


def uvs(group=None):
    # uvs_data = {}
    # _render_dags = renderinggroup.nodes()
    if group:
        polygons = cmds.ls(group, type='mesh', dag=True, l=True)
    else:
        polygons = renderinggroup.nodes()
    if not polygons:
        return None
    uv_data_bundle = {}
    for index, polygon in enumerate(polygons):
        # exported_polygons.append(polygon)
        if not core.objExists(polygon):
            core.displayWarning(
                'not found the object called <%s>!...' % polygon)
            result = False
            continue
        # studio_maya.node = polygon
        mdag_path = getDagPath(polygon)
        data = getData(mdag_path)
        uv_data_bundle.setdefault(index, data)
    return uv_data_bundle


def getDagPath(node):
    mselection = OpenMaya.MSelectionList()
    mselection.add(node)
    mdag_path = OpenMaya.MDagPath()
    mselection.getDagPath(0, mdag_path)
    return mdag_path


def getData(mdag_path):
    mfn_mesh = OpenMaya.MFnMesh(mdag_path)
    set_names = []
    mfn_mesh.getUVSetNames(set_names)
    uv_data = {}
    for index, set_name in enumerate(set_names):
        u_array = OpenMaya.MFloatArray()
        v_array = OpenMaya.MFloatArray()
        mfn_mesh.getUVs(u_array, v_array, set_name)
        uv_counts = OpenMaya.MIntArray()
        uv_ids = OpenMaya.MIntArray()
        mfn_mesh.getAssignedUVs(uv_counts, uv_ids, set_name)
        current_set_data = {
            # 'set_name': set_name.encode(),
            'u_array': list(u_array),
            'v_array': list(v_array),
            'uv_counts': list(uv_counts),
            'uv_ids': list(uv_ids)
        }
        uv_data.setdefault(index, current_set_data)
    num_polygons, polygon_vertices = getFacesVertices(mfn_mesh)
    final_data = {
        'uv_sets': uv_data,
        # 'long_name': mdag_path.fullPathName().encode(),
        # 'short_name': mdag_path.fullPathName().split('|')[-1],
        # 'shape_node': mfn_mesh.name().encode(),
        'num_polygons': num_polygons,
        'polygon_vertices': polygon_vertices
    }
    return final_data


def getFacesVertices(mfn_mesh=None):
    num_polygons = mfn_mesh.numPolygons()
    polygon_vertices = []
    for index in range(num_polygons):
        mint_array = OpenMaya.MIntArray()
        mfn_mesh.getPolygonVertices(index, mint_array)
        polygon_vertices.append(list(mint_array))
    return num_polygons, polygon_vertices
#
