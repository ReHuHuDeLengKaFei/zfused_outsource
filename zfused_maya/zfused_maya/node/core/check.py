# coding:utf-8
# --author-- lanhua.zhou

""" zfused maya 检查机制 """

from __future__ import print_function

from collections import defaultdict

import os
import logging

import maya.cmds as cmds
import pymel.core as pm

import zfused_api 

import zfused_maya.core.record as record 

from . import texture

class Check(object):
    """ check base object
    """
    value = False

def defult_asset_node():
    nodes=cmds.ls("defaultLegacyAssetGlobals")
    if not nodes:
        return True,None
    _info=u"存在不应存在的修型节点，请处理\n"
    for _node in nodes:
        _info +=_node

    return False,_info


def null_reference():
    _references = cmds.ls(rf=True)
    _null_reference = []
    if not _references:
        return True, None
    info = u"存在无用的reference节点:\n"
    for _reference in _references:
        try:
            cmds.referenceQuery(_reference, f=1)
        except:
            info += _reference + "\n"
            _null_reference.append(_reference)
    if len(_null_reference) == 0:
        return True, None
    return False, info

def standard_surface():
    _default_materials = ["lambert1", "particleCloud1", "standardSurface1"]
    _materials = cmds.ls(mat = True)
    _materials = list( set(_materials) - set(_default_materials))
    _is_error = False
    info = u"场景存在非标准材质球(standard surface material)\n"
    for _material in _materials:
        _type = cmds.nodeType(_material)
        if _type not in ["standardSurface","lambert","phong","blin"]:
            _is_error = True
            info += "{}\n".format(_material)
    if _is_error:
        return False, info
    return True, None

def lost_material():
    _polygons = cmds.ls(type = "mesh", ni = True)
    _is_error = False
    info = u"场景存在mesh丢失质球(lost material)\n"
    for _polygon in _polygons:
        _sgs = cmds.listConnections(_polygon, type = "shadingEngine")
        if not _sgs:
            _is_error = True
            info += "{}\n".format(_polygon)
    if _is_error:
        return False, info
    return True, None

def multi_material():
    _polygons = cmds.ls(type = "mesh", ni = True)
    _is_error = False
    info = u"场景存在单mesh多材质球(multi material)\n"
    for _polygon in _polygons:
        _sgs = cmds.listConnections(_polygon, type = "shadingEngine")
        if _sgs:
            _sgs = list(set(_sgs))
            if len(_sgs) > 1:
                _is_error = True
                info += "{}\n".format(_polygon)
    if _is_error:
        return False, info
    return True, None

def material_assign_faces():
    _polygons = cmds.ls(type = "mesh", ni = True)
    _is_error = False
    info = u"场景存在单材质球按面赋材质(face assign)[重新选择物体赋下材质]\n"
    for _polygon in _polygons:
        _trans = cmds.listRelatives(_polygon, p = True)[0]
        _sgs = cmds.listConnections(_polygon, type = "shadingEngine")
        if _sgs:
            _sgs = list(set(_sgs))
            if len(_sgs) == 1:
                _faces = cmds.sets(_sgs[0], q = True)
                _faces = [_face for _face in _faces if "{}.f[".format(_trans) in _face ]
                print(_faces)
                if len(_faces):
                    print(_faces)
                    _is_error = True
                    info += "{}\n".format(_polygon)
    if _is_error:
        return False, info
    return True, None


def lock_file():
    _is_lock = cmds.file(q = True, lf = True)
    if _is_lock:
        return False, u"文件处于锁住状态"
    return True, None

def check_attr():
    #get all transform
    _un = ["front","persp","side","top"]
    _all_trans = cmds.ls(type = "transform")
    _use_tans = list(set(_all_trans) - set(_un))
    _de = []
    for _tans in _use_tans:
        _t = cmds.getAttr("%s.translate"%_tans)
        _r = cmds.getAttr("%s.rotate"%_tans)
        _s = cmds.getAttr("%s.scale"%_tans)
        # _child = cmds.listRelatives(_tans, c = True, type = "mesh")
        # if _child:
        if _t != [(0.0, 0.0, 0.0)] or _r != [(0.0, 0.0, 0.0)] or _s != [(1.0, 1.0, 1.0)]:
            _de.append(_tans)
    if _de:
        info = u"通道属性值不为空\n"
        for child in _de:
            info += "{}\n".format(child)
        return False,info
    return True, None

def check_history():
    _history = []
    allDags = pm.ls(dag = 1)
    for dag in allDags: 
        _his = dag.history()
        #_his = [n for n in dag.history(il=1, pdo = True)]
        _his = [n for n in dag.history(il=1, pdo = True) if n.type() not in ["shadingEngine", "AlembicNode", "time"] ]
        if _his and dag.type() == "mesh":
            _history.append(dag)
    if _history:
        _history = list(set(_history))
        info = u"错误:部分模型存在历史记录\n"
        for child in _history:
            info += u"%s\n"%child
        return False,info

    return True, None


def multi_rendering_group():
    rendering = []
    _renderingdag = [i for i in cmds.ls(dag = 1) if cmds.objExists("{}.rendering".format(i))]
    if _renderingdag:
        for dag in _renderingdag:
            value = cmds.getAttr("%s.rendering"%dag)
            if value:
                rendering.append(dag)
        if rendering:
            if len(rendering) == 1:
                return True, None
            else:
                info = u"存在超过一个的可渲染组，请隐藏不参加渲染的组并关闭rendering属性\n"
                info += "\n".join(rendering)
                return False,info
    else:
        info = u"没有可用渲染组，请修改rendering属性值\n"
        info += "\n".join(_renderingdag)
        return False,info

def rendering_group():
    rendering = []
    allDags = cmds.ls(dag = True)
    for dag in allDags:
        if cmds.objExists("%s.rendering"%dag):
            value = cmds.getAttr("%s.rendering"%dag)
            if value:
                rendering.append(dag)
    #return rendering
    if not rendering:
        info = u"文件组织结构错误,请用分组工具分组整合文件\n"
        return False, info
    return True, None

def camera_name():
    _task_id = record.current_task_id()
    if not _task_id:
        return False, info
    _task_handle = zfused_api.task.Task(_task_id)
    _obj_handle = zfused_api.objects.Objects(_task_handle.data()["Object"], _task_handle.data()["LinkId"])
    _name = _obj_handle.file_code()
    info = u"当前摄像机名称与任务名{}不匹配\n".format(_name)
    if not cmds.ls("*%s*"%_name, type = "camera"):
        return False,info    
    return True,None

def file_name():
    _info = u"当前文件名称与任务名不匹配\n"
    _task_id = record.current_task_id()
    if not _task_id:
        return False, _info
    _task_handle = zfused_api.task.Task(_task_id)
    _obj_handle = zfused_api.objects.Objects(_task_handle.data()["Object"], _task_handle.data()["LinkId"])
    _name = _obj_handle.file_code()
    _file_name = cmds.file(q = True, sn = True)
    if not os.path.basename(_file_name).startswith(_name):
        return False,_info    
    return True,None

def file_node():
    """ check file node is not null

    """
    _file_nodes = texture.error_nodes()        
    if len(_file_nodes) > 1:
        info = u"file节点存在错误贴图路径,请用贴图管理工具检查\n"
        for _file_node in _file_nodes:
            info += "{}\n".format(_file_node)
        return False, info
    return True, None

def reference_file_node():
    """ check reference file

    """
    pass

def texture_path():
    """ check texture file path
    """
    _info = ""
    _files = texture.files()
    if not _files:
        return True, None
    _paths = texture.paths(_files)
    if len(_paths) > 1:
        info = u"贴图存在不同路径下,请用贴图管理工具检查\n"
        for _path in _paths:
            info += "{}\n".format(max(_path))
        return False, info
    return True, None

def animation_layer():
    """ check animation layer

    """
    _lays = cmds.ls(type = "animLayer")
    if len(_lays) > 0:
        info = u"场景存在多余动画层\n"
        for _layer in _lays:
            info += "{}\n".format(_layer)
        return False, info
    return True, None

def unknown_node():
    """ check unknown nodes

    """
    _nodes = cmds.ls(type = "unknown")
    if len(_nodes) > 0:
        info = "场景存在未知节点\n"
        for _node in _nodes:
            info += "{}\n".format(_node)
        return False,info
    return True, None

def camera():
    """ check camera

    """
    _extra_camera = ["facial_cam"]
    _cameras = cmds.ls(type = "camera")
    _left_cameras = list(set(_cameras) - set(["frontShape","topShape","perspShape","sideShape"]))
    if _left_cameras:
        info = "场景存在多余摄像机\n"
        for _camera in _left_cameras:
            _is_extra = False
            for _cam in _extra_camera:
                if _cam in _camera:
                    _is_extra = True
            if _is_extra:
                continue
            info += "{}\n".format(_camera)
        return False,info
    return True,None

def reference():
    """ check reference file

    """
    _references = cmds.ls(type = "reference")
    if _references:
        info = "场景存在参考文件\n"
        for _reference in _references:
            info += "{}\n".format(_reference)
        return False,info
    return True,None

def equal_namespace():
    _rf_nodes = cmds.ls( rf = True )

    _rf_ns_node = {}
    _error_rf_nodes = []
    for _rf_node in _rf_nodes:
        _inr = cmds.referenceQuery(_rf_node, inr = True)
        if not _inr:
            try:
                _namespace = cmds.referenceQuery(_rf_node, namespace = True)
                if _namespace not in _rf_ns_node.keys():
                    _rf_ns_node[_namespace] = _rf_node
                else:
                    _error_rf_nodes.append((_rf_node, _rf_ns_node[_namespace]))
            except:
                try:
                    cmds.lockNode(_rf_node, lock=False)
                    cmds.delete(_rf_node)
                except:
                    pass
    # return _error_rf_nodes
    if _error_rf_nodes:
        info = "场景存在namespace相同参考\n"
        for _error_rf_node in _error_rf_nodes:
            info += "{} - {}\n".format(_error_rf_node[0],_error_rf_node[1])
        return False,info
    return True,None
    
def light():
    """ check light

    """
    _lights = cmds.ls(type = cmds.listNodeTypes("light"))
    
    if _lights:
        info = "场景存在多余灯光节点\n"
        for _light in _lights:
            info += "{}\n".format(_light)
        return False,info
    return True, None

def anim_curve():
    """ check anim curves

    """
    _cures = cmds.ls(type = 'animCurve')
    if _cures:
        info = "场景存在动画曲线\n"
        for _cure in _cures:
            info += "{}\n".format(_cure)
        return False,info
    return True, None

def display_layer():
    """ check display layer
    """
    import pymel.core as core
    _layers = [Layer for Layer in core.ls(type = 'displayLayer') if not core.referenceQuery(Layer, isNodeReferenced = True) and Layer.name() != 'defaultLayer' and cmds.getAttr("%s.identification"%Layer) != 0]
    if _layers:
        info = "场景存在显示层\n"
        for _layer in _layers:
            info += "{}\n".format(_layer)
        return False,info
    return True, None

def render_layer():
    """ check render layer

    """
    import pymel.core as core
    _layers = [Layer for Layer in core.ls(type = 'renderLayer') if not core.referenceQuery(Layer, isNodeReferenced = True) and Layer.name() != 'defaultRenderLayer']
    if _layers:
        info = "场景存在渲染层\n"
        for _layer in _layers:
            info += "{}\n".format(_layer)
        return False,info
    return True, None

def namespace():
    """ check namespace
    """
    _namespaces = cmds.namespaceInfo(recurse = True, listOnlyNamespaces = True)
    _namespaces = list(set(_namespaces) - set(["shared","UI"]))
    if _namespaces:
        info = "场景中存在命名空间\n"
        for _namespace in _namespaces:
            info += "{}\n".format(_namespace)
        return False,info
    return True, None

def repeat(node_type = "mesh"):
    """ 检查重命名
    """
    def get_uuid_info():
        # 记录相同uuid下的mesh
        uuid_dict = {}
        _meshes = cmds.ls(type = 'mesh', ap = True)
        for _mesh in _meshes:
            _uuid = cmds.ls(_mesh, uuid = True)[0]
            uuid_dict.setdefault(_uuid,[]).append(_mesh)
        return uuid_dict

    _is_repeat = False

    # _lists = cmds.ls(noIntermediate = 1, type = node_type)
    # _repeat_list = defaultdict(list)
    # for _shape, _index in [(_shape.split("|")[-1], _index) for _index, _shape in enumerate(_lists) ]:
    #     _repeat_list[_shape].append(_index)
    # info = "场景存在重复命名节点\n"
    # for _shape, _index_list in _repeat_list.items():
    #     if len(_index_list) > 1:
    #         _is_repeat = True
    #         for _index in _index_list:
    #             _name = _lists[_index]
    #             info += "{}\n".format(_name)

    _lists = cmds.ls(noIntermediate = 1, type = node_type)
    info = "场景存在重复命名节点\n"
    _uuid_info = get_uuid_info()
    for _name in _lists:
        if len(_name.split('|')) != 1:
            _uuid = cmds.ls(_name, uuid = 1)[0]
            # 若len()不等于1，说明当前uuid值下的模型有多个，且为instance形式存在（因为不同的DAG节点有不同的uuid）
            if len(_uuid_info[_uuid]) == 1:
                _is_repeat = True
                info += "{}\n".format(_name)

    if _is_repeat:
        return False, info
    else:
        return True, None

def trans_in_mesh():
    """ check mesh in mesh
    """
    _list = []
    _meshGrp = [x for x in cmds.ls(type='transform') if ('_model_GRP' in x) and cmds.objExists(x+'.treeName')]
    if _meshGrp:
        _all_meshs = cmds.listRelatives(_meshGrp[0],type = "mesh",ad = 1,f = 1)
        _all_trans = cmds.listRelatives(_all_meshs,p = 1,f = 1)
        if _all_trans:
            for i in _all_trans:
                wrongtrans = cmds.listRelatives(i,ad = 1,type = "transform")
                wrongtrans
                if wrongtrans:
                    _list.extend(wrongtrans)
    # print(_list)
    if _list:
        info = "场景存在嵌套模型\n{}".format("\n".join(_list))
        # print(info)
        return False, info
    else:
        return True, None

def isshow(node):
    _value = True
    if cmds.getAttr("%s.v"%node) == 0:
        _value = False
    while True:
        node = cmds.listRelatives(node, p = 1, f = True)
        if not node:
            break
        else:
            node = node[0]
            if cmds.getAttr("%s.v"%node) == 0:
                _value = False
                break
    return _value

def color_set():
    '''顶点着色
    '''
    _color_set = []
    _dags = cmds.ls(dag = 1)
    if not _dags:
        return True, None
    for _dag in _dags:
        _set = cmds.polyColorSet(_dag,q = 1,acs = 1)
        if _set:
            _color_set.extend(_set)
    if _color_set:
        info = "场景存在顶点着色\n{}".format("\n".join(_color_set))
        return False ,info
    else:
        return True, None

def intermediate_shape():
    sel = cmds.ls(io = 1,type = "mesh")
    if sel:
        info = "场景存在转换的中间模型\n{}".format("\n".join(sel))
        return False ,info
    else:
        return True, None

def normal_lock():
    '''法线锁定
    '''
    from random import randint
    meshs = cmds.ls(type = "mesh",io = 0)
    lockmesh = []
    if not meshs:
        return True,None
    for _mesh in meshs:
        _allvtx = cmds.polyEvaluate(_mesh,v = 1)   
        tempvtx = "{}.vtx[{}]".format(_mesh,randint(0,_allvtx))
        if cmds.polyNormalPerVertex(tempvtx,q = 1,allLocked = 1)[0]:
            lockmesh.append(_mesh)
    if lockmesh:
        info = u"模型法线被锁定，请修改\n"
        info += "\n".join(cmds.listRelatives(lockmesh,p = 1))
        return False,info
    else:
        return True,None
