 # coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import shutil
import logging
import datetime
import time
import glob

import maya.cmds as cmds

import zfused_api
import zfused_maya.node.core.attr as attr


logger = logging.getLogger(__name__)
_is_load = cmds.pluginInfo("AbcImport", query=True, loaded = True)
if not _is_load:
    try:
        logger.info("try load alembic plugin")
        cmds.loadPlugin("AbcImport")
    except Exception as e:
        logger.error(e)



def open_file(*args, **kwargs):
    """ receive file
        base receive file script
    :rtype: bool
    """
    # _task_id, _task_attr_input_id, _input_task_id, _input_task_attr_output_id = args
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
    _input_production_path = _input_task.production_path()
    
    # get file 
    # _file_index = "{:0>4d}".format(_input_task.last_version_index())
    if _index:
        _file_index = "{:0>4d}".format(_index)
    else:
        _file_index = "{:0>4d}".format(_input_task.last_version_index())
    _file_suffix = _input_task_attr_output.suffix()
    if _extended_version:
        _production_file = zfused_api.zFused.get("production_file", filter = {"TaskId": _input_task_id, "ProjectStepAttrId": _input_task_project_step_id, "Index": int(_file_index)})
        if _production_file:
            _production_file = _production_file[0]["Path"]
        else:
            _production_file = "{}/{}/{}.{}{}".format(_input_production_path,_input_task_attr_output.code(),_input_task.file_code(),_file_index, _file_suffix)
    else:
        _production_file = "{}/{}/{}{}".format(_input_production_path,_input_task_attr_output.code(),_input_task.file_code(), _file_suffix)
    
    # do somthing
    cmds.file(_production_file, o = True, f = True, options = "v=0;")
    # rfn = cmds.referenceQuery(rf, rfn = True)
    # _version_id = _input_task.last_version_id()
    # attr.set_node_attr(rfn, _input_task_attr_output_id, _version_id, "false")


def import_file(*args, **kwargs):
    """ receive file
        base receive file script
    :rtype: bool
    """
    # _task_id, _task_attr_input_id, _input_task_id, _input_task_attr_output_id = args
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
    _input_production_path = _input_task.production_path()
    
    # get file 
    # _file_index = "{:0>4d}".format(_input_task.last_version_index())
    if _index:
        _file_index = "{:0>4d}".format(_index)
    else:
        _file_index = "{:0>4d}".format(_input_task.last_version_index())
    _file_suffix = _input_task_attr_output.suffix()
    if _extended_version:
        _production_file = zfused_api.zFused.get("production_file", filter = {"TaskId": _input_task_id, "ProjectStepAttrId": _input_task_project_step_id, "Index": int(_file_index)})
        if _production_file:
            _production_file = _production_file[0]["Path"]
        else:
            _production_file = "{}/{}/{}.{}{}".format(_input_production_path,_input_task_attr_output.code(),_input_task.file_code(),_file_index, _file_suffix)
    else:
        _production_file = "{}/{}/{}{}".format(_input_production_path,_input_task_attr_output.code(),_input_task.file_code(), _file_suffix)
    
    # do somthing
    cmds.file(_production_file, i = True, options = "v=0;")
    # rfn = cmds.referenceQuery(rf, rfn = True)
    # _version_id = _input_task.last_version_id()
    # attr.set_node_attr(rfn, _input_task_attr_output_id, _version_id, "false")


def reference_file(*args, **kwargs):
    """ receive file
        base receive file script
    :rtype: bool
    """
    # _task_id, _task_attr_input_id, _input_task_id, _input_task_attr_output_id = args
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
    _input_task_project_step = zfused_api.step.ProjectStep(_input_task_project_step_id)
    _input_production_path = _input_task.production_path()
    
    # get file 
    if _index:
        _file_index = "{:0>4d}".format(_index)
    else:
        _file_index = "{:0>4d}".format(_input_task.last_version_index())
    _file_suffix = _input_task_attr_output.suffix()
    if _extended_version:
        _production_file = zfused_api.zFused.get("production_file", filter = {"TaskId": _input_task_id, "ProjectStepAttrId": _input_task_project_step_id, "Index": int(_file_index)})
        if _production_file:
            _production_file = _production_file[0]["Path"]
        else:
            _production_file = "{}/{}/{}.{}{}".format(_input_production_path,_input_task_attr_output.code(),_input_task.file_code(),_file_index, _file_suffix)
    else:
        _production_file = "{}/{}/{}{}".format(_input_production_path,_input_task_attr_output.code(),_input_task.file_code(), _file_suffix)
    
    if not os.path.isfile(_production_file):
        return

    # 如果文件存在
    # 查找是否是xgen文件
    _temp_file, _ = os.path.splitext(_production_file)
    _temp_files = glob.glob("{}*.xgen".format(_temp_file))
    if _temp_files:
        _is_load = cmds.pluginInfo("xgenToolkit", query=True, loaded = True)
        if not _is_load:
            try:
                logger.info("try load xgenToolkit plugin")
                cmds.loadPlugin("xgenToolkit")
            except Exception as e:
                logger.error(e)

    if _namespace:
        if not cmds.objExists(_namespace):
            cmds.createNode("transform", name = _namespace, p = ":")

    # 判定是否已存在
    _reference_nodes = cmds.ls(references = True)
    if _reference_nodes:
        for _reference_node in _reference_nodes:
            _reference_name_space = cmds.referenceQuery(_reference_node, namespace=True, shn = True)
            if _reference_name_space.startswith("{}__in__".format(_namespace)) or (not _namespace and not _reference_name_space) or (not _namespace and _reference_name_space.startswith(_input_task.file_code())):
                _file_name = cmds.referenceQuery(_reference_node, filename=True, withoutCopyNumber=True)
                if os.path.dirname(_file_name) == os.path.dirname(_production_file):
                    if _file_name == _production_file:
                        return True
                    else:
                        cmds.file(_production_file, loadReference = _reference_node, options='v=0;')
                        return True

    # do somthing
    _ori_assemblies = cmds.ls(assemblies=True)
    
    if _namespace:
        rf = cmds.file(_production_file, r = True, ns = "{}__in__{}_{}".format(_namespace, _input_task_project_step.file_code(), _input_task_attr_output.code()))
    else:
        _project = _input_task.project()
        _default_namespace = _project.variables("default_namespace", "__ns__00") 
        # _ns = "{}{}".format(_task.project_entity().file_code(), _default_namespace)
        rf = cmds.file(_production_file, r = True, ns = "{}{}".format(_input_task.file_code(), _default_namespace))
        # rf = cmds.file(_production_file, r = True, ns = "{}__ns__00".format(_input_task.file_code()))
    rfn = cmds.referenceQuery(rf, rfn = True)
    _version_id = _input_task.last_version_id()
    attr.set_node_attr(rfn, _input_task_attr_output_id, _version_id, "false")
    
    if _namespace:
        _new_assemblies = cmds.ls(assemblies=True)
        _tops = list(set(_new_assemblies) - set(_ori_assemblies))
        if _tops:
            for _top in _tops:
                if cmds.ls(_top,type='xgmPalette',dag=True):
                    if len(_namespace)>=20:
                        continue
                    
                try:
                    cmds.parent(_top, _namespace)
                except:
                    pass

#@zfused_api.reset
def reference_abc_(*args, **kwargs):
    # _task_id, _task_attr_input_id, _input_task_id, _input_task_attr_output_id = args
    _task_id = kwargs.get("task_id")
    _task_attr_input_id = kwargs.get("task_attr_input_id")
    _input_task_id = kwargs.get("input_task_id")
    _input_task_attr_output_id = kwargs.get("input_task_attr_output_id")
    _namespace = kwargs.get("namespace")
    _index = kwargs.get("index")

    _is_load = cmds.pluginInfo("AbcImport", query=True, loaded = True)
    if not _is_load:
        try:
            logger.info("try load alembic plugin")
            cmds.loadPlugin("AbcImport")
        except Exception as e:
            logger.error(e)

    _task_id =38538
    task_entity =zfused_api.task.Task(_task_id)
    project_entity = task_entity.project_entity()
    project_property =project_entity.property()

    _out_put_attr_id =43
    _input_task_attr_output = zfused_api.attr.Output(_out_put_attr_id)
    _out_put_attr_code = _input_task_attr_output.code()

    _output_step_id =318
    #steps_list =[318]
    #zfused_api.attr.Output(_output_attr_id)
    _input_task_project_step_code ='animation'
    assets =project_property.get('asset')
    for _asset in assets:
        _namespace =_asset.get('namespace')
        _id =_asset.get('id')
        _last_cache =_asset.get('last_cache')
        asset_entity =zfused_api.asset.Asset(_id)
        _asset_property =asset_entity.property()

        task_id =asset_entity.tasks([_output_step_id])[0].get('Id')
        _task =zfused_api.task.Task(task_id)
        #_task_property =_task.property()
        _last_vresion_id =_task.last_version_id()

        #for _step in steps_list:
        #_output_attr_handle = zfused_api.attr.Output(_step)
        #_attr_code = _output_attr_handle.code()
        _mat_ns =_namespace+_out_put_attr_code
        _geo_ns =_namespace
        _production_file = zfused_api.version.Version(_last_vresion_id).production_file(_out_put_attr_code)
        cmds.file(_production_file,ns =_namespace+_out_put_attr_code,r=True,mergeNamespacesOnClash=False,ignoreVersion=True)
        cmds.file(_last_cache,ns =_geo_ns,r=True,mergeNamespacesOnClash=False,ignoreVersion=True)
        try:
            if _asset_property:
                material_assign_list =_asset_property.get('material_assign')
                for _mat in material_assign_list:
                    cmds.select(cl=True)
                    _transform = _mat.get('transform')
                    _shader_engine = _mat.get('engine')
                    new_trans ='{}:{}'.format(_geo_ns,_transform)
                    _mesh_name =cmds.listRelatives(new_trans,c=True,ni=True,type ='mesh')
                    new_shader_engine ='{}:{}'.format(_mat_ns,_shader_engine)
                    _faces =_mat.get('faces')
                    if _faces:
                        for _face in _faces:
                            _face_name = '{}:{}.f[{}]'.format(_geo_ns,_transform,_face)
                            if '_' in _face_name:
                                _face_name =_face_name.replace('-',":")
                                cmds.select(_face_name,add=True)
                    else:
                        cmds.select(new_trans)
                    _sl =cmds.ls(sl=True)
                    s=cmds.sets(_sl,e=True,forceElement=new_shader_engine)
        except Exception as e:
            logger.error(e)
        # # _versions  =_task.versions()
        # # for _v in _versions:
        # #     _pr =_v.get('FilePath')
        # #     print(_pr)
        # # #print(_versions)
        # # break
        #
        #     # _output_attr_handle = zfused_api.attr.Output(_step)
        #     # _attr_code =_output_attr_handle.code()
        #     # _suffix =_output_attr_handle.suffix()
        #     # _file_code = _task.file_code()
        #     # _cover_file = "{}/{}/{}{}".format(_production_path, _attr_code, _file_code, _suffix)
        #     # if os.path.isfile(_cover_file):
        #     #     print('yes')

@zfused_api.reset
def alembic_in_(*args,**kwargs):
    # _task_id, _task_attr_input_id, _input_task_id, _input_task_attr_output_id = args
    _task_id = kwargs.get("task_id")
    _task_attr_input_id = kwargs.get("task_attr_input_id")
    _input_task_id = kwargs.get("input_task_id")
    _input_task_attr_output_id = kwargs.get("input_task_attr_output_id")
    _namespace = kwargs.get("namespace")
    _index = kwargs.get("index")

    _is_load = cmds.pluginInfo("AbcImport", query=True, loaded = True)
    if not _is_load:
        try:
            logger.info("try load alembic plugin")
            cmds.loadPlugin("AbcImport")
        except Exception as e:
            logger.error(e)

    # _task_id =38539
    # _task_attr_input_id =24
    # _input_task_id =38538
    # _input_task_attr_output_id =45

    task_entity =zfused_api.task.Task(_task_id)
    project_entity = task_entity.project_entity()
    project_property =project_entity.property()

    assets =project_property.get('asset')
    _input_task_entity =zfused_api.task.Task(_input_task_id)

    #获取材质步骤的ID
    out_put_attr_id =43
    _input_task_attr_output = zfused_api.attr.Output(out_put_attr_id)
    _out_put_attr_code = _input_task_attr_output.code()
    #暂时先忽略
    _material_step_id =318
    for _asset in assets:
        _namespace =_asset.get('namespace')
        _id =_asset.get('id')
        _last_cache =_asset.get('last_cache')
        _asset_entity =zfused_api.asset.Asset(_id)
        _asset_property =_asset_entity.property()
        _material_task_id =_asset_entity.tasks([_material_step_id])[0].get('Id')
        _material_task_entity =zfused_api.task.Task(_material_task_id)
        _materila_last_version = _material_task_entity.last_version_id()
        _mat_ns =_namespace+_out_put_attr_code
        _geo_ns =_namespace
        _production_file =zfused_api.version.Version(_materila_last_version).production_file(_out_put_attr_code)
        cmds.file(_production_file,ns =_namespace+_out_put_attr_code,r=True,mergeNamespacesOnClash=False,ignoreVersion=True)
        cmds.file(_last_cache,ns =_geo_ns,r=True,mergeNamespacesOnClash=False,ignoreVersion=True)
        try:
            if _asset_property:
                material_assign_list = _asset_property.get('material_assign')
                for _mat in material_assign_list:
                    _shape =_mat.get('shape')
                    _transform = _mat.get('transform')
                    _shader_engine = _mat.get('engine')
                    new_trans ='{}:{}'.format(_geo_ns,_transform)
                    _mesh_name =cmds.listRelatives(new_trans,c=True,ni=True,type ='mesh')
                    new_shape ='{}:{}'.format(_geo_ns,_shape)
                    shape_con_list =cmds.listConnections(new_shape,type ='shadingEngine')
                    if 'initialShadingGroup' in shape_con_list:
                        _shape_attr = '{}.instObjGroups[0]'.format(new_shape)
                        dst_attr =cmds.connectionInfo(_shape_attr,destinationFromSource=True)[0]

                        cmds.disconnectAttr(_shape_attr,dst_attr)
                    new_shader_engine ='{}:{}'.format(_mat_ns,_shader_engine)
                    _faces =_mat.get('faces')
                    if _faces:
                        for _face in _faces:
                            _face_name = '{}:{}.f[{}]'.format(_geo_ns,_transform,_face)
                            if '_' in _face_name:
                                _face_name =_face_name.replace('-',":")
                                cmds.select(_face_name,add=True)

                    else:
                        cmds.select(new_trans,add=True)
                    _sl =cmds.ls(sl=True)
                    cmds.sets(_sl,e=True,forceElement=new_shader_engine)
                    cmds.select(cl=True)

        except Exception as e:
            print(e)
    pass








@zfused_api.reset
def alembic_in(*args,**kwargs):
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

    # if _namespace:
    #     _relatives = zfused_api.zFused.get("relative", filter = { "NameSpace": _namespace, 
    #                                                               "TargetObject": _task.project_entity_type(),
    #                                                               "TargetId": _task.project_entity_id() })  
    #     if not _relatives:
    #         return
    #     _relative = _relatives[0]
    #     _relative_project_entity = zfused_api.objects.Objects(_relative.get("SourceObject"), _relative.get("SourceId"))
    
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
    
    # 判定是否已存在
    _reference_nodes = cmds.ls(references = True)
    if _reference_nodes:
        for _reference_node in _reference_nodes:
            _reference_name_space = cmds.referenceQuery(_reference_node, namespace=True, shn = True)
            if _reference_name_space.startswith("{}__in__".format(_namespace)) or (not _namespace and not _reference_name_space) or (not _namespace and _reference_name_space.startswith(_input_task.file_code())):
                _file_name = cmds.referenceQuery(_reference_node, filename=True, withoutCopyNumber=True)
                if os.path.dirname(_file_name) == os.path.dirname(_production_file):
                    if _file_name == _production_file:
                        return True
                    else:
                        cmds.file(_production_file, loadReference = _reference_node, options='v=0;')
                        return True

    cmds.file(_production_file, ns = "{}__in__{}".format(_namespace, _input_task_attr_output.code()), r = True, mergeNamespacesOnClash = False, ignoreVersion = True)
    

@zfused_api.reset
def camera_in(*args,**kwargs):
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

    # if _namespace:
    #     _relatives = zfused_api.zFused.get("relative", filter = { "NameSpace": _namespace, 
    #                                                               "TargetObject": _task.project_entity_type(),
    #                                                               "TargetId": _task.project_entity_id() })  
    #     if not _relatives:
    #         return
    #     _relative = _relatives[0]
    #     _relative_project_entity = zfused_api.objects.Objects(_relative.get("SourceObject"), _relative.get("SourceId"))
    
    # get file 
    if _index:
        _file_index = "{:0>4d}".format(_index)
    else:
        _file_index = "{:0>4d}".format(_input_task.last_version_index())
    _file_suffix = _input_task_attr_output.suffix()
    if _extended_version:
        # _file_index = "{:0>4d}".format(_input_task.last_version_index())
        _production_file = "{}/{}/{}.{}{}".format(_input_production_path, _input_task_attr_output.code(), _input_task.file_code(), _file_index, _file_suffix)
    else:
        _production_file = "{}/{}/{}{}".format(_input_production_path, _input_task_attr_output.code(), _input_task.file_code(), _file_suffix)

    # if _extended_version:
    #     _file_index = "{:0>4d}".format(0)
    # _production_file = "{}/{}/{}.{}{}".format(_input_production_path, _input_task_attr_output.code(), _input_task.file_code(), _file_index, _file_suffix)
    
    
    # 判定是否已存在
    _reference_nodes = cmds.ls(references = True)
    if _reference_nodes:
        for _reference_node in _reference_nodes:
            _reference_name_space = cmds.referenceQuery(_reference_node, namespace=True, shn = True)
            if _reference_name_space.startswith("camera") or (not _namespace and not _reference_name_space) or (not _namespace and _reference_name_space.startswith(_input_task.file_code())):
                _file_name = cmds.referenceQuery(_reference_node, filename=True, withoutCopyNumber=True)
                if os.path.dirname(_file_name) == os.path.dirname(_production_file):
                    if _file_name == _production_file:
                        return True
                    else:
                        cmds.file(_production_file, loadReference = _reference_node, options='v=0;')
                        return True

    cmds.file(_production_file, ns = "{}".format("camera"), r = True, lck=True, mergeNamespacesOnClash = False, ignoreVersion = True)

    return True

