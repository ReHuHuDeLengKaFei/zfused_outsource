# coding:utf-8
# --author-- ning.qin
from __future__ import print_function

import os
import sys
import shutil
import logging
import json
import time

import maya.cmds as cmds
from pymel.core import *

import zfused_api
from zfused_maya.core import record
from zfused_maya.node.core import renderinggroup
from zcore import filefunc,zfile

logger = logging.getLogger(__name__)

def read_json_file(file_path):
    with open(os.path.abspath(file_path), "r") as json_file:
        json_dict = json.load(json_file)
    return json_dict if json_dict else {}
def write_json_file(json_dict, file_path):
    with open(file_path,"w") as json_file:
        json_file.write(json.dumps(json_dict,indent = 4,separators=(',',':'), sort_keys = False))
        json_file.close()

def get_material_face_dict():
    material_face_dict = {}
    material_list = ls(type = 'standardSurface')
    _default_materials = ["standardSurface1"]
    for material in material_list:
        if material.name() not in _default_materials:
            #print(material)
            hyperShade(objects = material)
            face_selection = ls(selection = True)
            select(polyListComponentConversion(face_selection, toFace = True))
            face_selection = ls(selection = True, long = True)
            face_list = []
            for face in face_selection:
                face_list.append(face.name())
            #print(face_list)
            material_face_dict[material.name()] = face_list
    return material_face_dict

def export_json(json_file):
    json_dict = {}
    material_face_dict = get_material_face_dict()
    json_dict['material_face'] = material_face_dict
    write_json_file(json_dict, json_file)

def publish_ue_json(*args, **kwargs):
    _task_id, _output_attr_id = args
    print('----------------------------------publish ue json------------------------------------')

    _output_attr_handle = zfused_api.attr.Output(_output_attr_id)
    _file_format = _output_attr_handle.format()
    _suffix = _output_attr_handle.suffix()
    _attr_code = _output_attr_handle.code()
    _task = zfused_api.task.Task(_task_id)
    _production_path = _task.production_path()
    _project_entity_production_path = _task.project_entity().production_path()
    _temp_path = _task.temp_path()
    _file_code = _task.file_code()
    if kwargs.get("fix_version"):
        _file_index = "{:0>4d}".format(_task.last_version_index( 0 ))
    else:
        _file_index = "{:0>4d}".format(_task.last_version_index() + 1)

    _production_file = "{}/{}/{}.{}{}".format( _production_path, _attr_code, _file_code, _file_index, _suffix )
    _cover_file = "{}/{}/{}{}".format(_production_path, _attr_code, _file_code, _suffix)
    _publish_file = "{}/{}/{}.{}{}".format( _temp_path, _attr_code, _file_code, _file_index, _suffix )
    _publish_file_dir = os.path.dirname(_publish_file)
    print(_publish_file)
    if not os.path.isdir(_publish_file_dir):
        os.makedirs(_publish_file_dir)
    _rendering_group = renderinggroup.nodes()
    print(_rendering_group)

    try:
        if _rendering_group:
            export_json(_publish_file)
            _result = filefunc.publish_file(_publish_file,_production_file)
            _result = filefunc.publish_file(_publish_file,_cover_file)
    except Exception as e:
        logger.error(e)
        print(e)
        return False
    return True