# coding:utf-8
# --author-- lanhua.zhou

""" zfused maya 检查机制 """

from __future__ import print_function

import copy
import os

import maya.api.OpenMaya as om
import maya.cmds as cmds
import pymel.core as pm
import xgenm as xg

import zfused_api

from zfused_maya.core import record

from . import property, renderinggroup, shadingengine, texture, xgen


class Check(object):
    """ check base object
    """
    value = False


def texture_is_chinese():
    """
    检查贴图路径是否有中文
    """
    
    _nodes = texture.nodes()
    if not _nodes:
        return True, None
    _error_nodes = []
    info = u"以下节点含有中文，请检查\n"
    for _node_attr in _nodes:
        _node_textures = []
        _node = _node_attr.split(".")[0]
        _path = texture._get_file_full_name(_node_attr)
        _is_reference = cmds.referenceQuery(_node, isNodeReferenced=True)
        if _is_reference:
            continue
        _mode, _ani = 0, 0
        if cmds.objExists("%s.uvTilingMode" % _node):
            _mode = cmds.getAttr("%s.uvTilingMode" % _node)
        if cmds.objExists("%s.useFrameExtension" % _node):
            _ani = cmds.getAttr("%s.useFrameExtension" % _node)
        if "<UDIM>" in os.path.basename(_path):
            _mode = 1
        if not _mode and not _ani:
            _node_textures.append(_path)
        else:
            if _mode:
                _node_textures.extend(texture.get_udim_texfile(_path, False))
            if _ani:
                _node_textures.extend(texture.get_frame_texfile(_path, False))
        for _file in _node_textures:
            for ch in _file:
                if u'\u4e00' <= ch <= u'\u9fff':
                    _error_nodes.append(_node)
                    continue
                else:
                    continue
    if _error_nodes:
        _error_nodes = list(set(_error_nodes))
        for _error_node in _error_nodes:
            info += u"{}\n".format(_error_node)
        return False, info
    return True, None
    
    # if not _files:
    #     return True, None
    # _error_path = []
    # info = u"以下路径含有中文，请检查\n"
    # for _file in _files:
    #     for ch in _file:
    #         if u'\u4e00' <= ch <= u'\u9fff':
    #             _error_path.append(_file)
    #         else:
    #             continue
    # if _error_path:
    #     _error_path = list(set(_error_path))
    #     for _path in _error_path:
    #         info += u"{}\n".format(_path)
    #     return False, info
    # return True, None


# =======================================================================================================
# 检查贴图等不在制作路径下
def external_file_path():
    _task_id = record.current_task_id()
    if not _task_id:
        return False, u"未选择制作任务\n"
    _task = zfused_api.task.Task(_task_id)
    _project = _task.project()
    _paths = "|".join([_project.work_path()])


def texture_work_path():
    """ check texture file not in work path
    """
    _task_id = record.current_task_id()
    _task = zfused_api.task.Task(_task_id)
    _project = _task.project()
    # _project_id = record.current_project_id()
    _backup_path = _project.backup_path()
    _work_path = _project.work_path()
    _production_path = _project.production_path()
    
    _files = texture.files()
    if not _files:
        return True, None
    
    _error_path = []
    info = u"以下路径的贴图未在项目work路径下\n"
    for _file in _files:
        if _work_path in _file or _production_path in _file or _backup_path in _file:
            continue
        else:
            _error_path.append(os.path.dirname(_file))
            # info += "{}\n".format(_path)
    if _error_path:
        _error_path = list(set(_error_path))
        for _path in _error_path:
            info += "{}\n".format(_path)
        return False, info
    return True, None


# =======================================================================================================
# 生长面检查
def grow_caching():
    """检测毛发生长面
    """
    grow_caching = []
    allDags = cmds.ls(dag=True)
    for dag in allDags:
        if cmds.objExists("%s.grow_caching" % dag):
            value = cmds.getAttr("%s.grow_caching" % dag)
            if value:
                grow_caching.append(dag)
    if not grow_caching:
        info = u"文件不存在生长面grow_caching属性组\n"
        return False, info
    if len(grow_caching) > 1:
        info = u"文件存在超过一个生长面grow_caching属性组\n"
        for _grow in grow_caching:
            info += "{}\n".format(_grow)
        return False, info
    return True, None


# =======================================================================================================
# 通用检查
# 检查maya关于通用检查

# =======================================================================================================
# 检查场景多余摄像机
def useless_camera():
    """ check camera
    """
    _extra_camera = ["facial_cam"]
    _cameras = cmds.ls(type="camera")
    _left_cameras = list(set(_cameras) - set(["frontShape", "topShape", "perspShape", "sideShape"]))
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
        return False, info
    return True, None


# 检查摄像机名称和Shape名重复
def error_name_camera():
    """ check camera shape name
    """
    _cameras = cmds.ls(type="camera")
    _left_cameras = list(set(_cameras) - set(["frontShape", "topShape", "perspShape", "sideShape"]))
    _repeat_name = []
    if _left_cameras:
        info = u"摄像机名称与Shape名重复\n"
        for _camera in _left_cameras:
            _parent = cmds.listRelatives(_camera, p=True)[0]
            if _camera.split('|')[-1] == _parent.split('|')[-1]:
                _repeat_name.append(_parent)
                info += "{}\n".format(_parent)
    if _repeat_name:
        return False, info
    return True, None


# =======================================================================================================
# 检查几何体结构是否一致
def geometry_structure():
    """模型几何体结构检查
    """
    # 获取当前的任务
    _task_id = record.current_task_id()
    _task = zfused_api.task.Task(_task_id)
    _project_entity = _task.project_entity()
    _property = _project_entity.property("geometry")
    info = ""
    if not _property:
        return True, None
    # 检查preveiw模型有无记录md5值【临时添加】
    if not _property[0].has_key("md5"):
        info += u"【上游文件提示】：资产模型需要重新上传，以此更新模型结构信息\n"
    _asset_md5 = ["{}_{}".format(_pro.get("transform"), _pro.get("md5")) for _pro in _property]
    # get current geometry
    _geometry = property.get_geometrys()
    _cur_md5 = ["{}_{}".format(_geo.get("transform"), _geo.get("md5")) for _geo in _geometry]
    if _cur_md5 != _asset_md5:
        info += u"【当前文件提示】：文件几何体结构与资产模型文件结构不统一,请修正统一(文件层级或者拓扑不一致，请自行检查)\n"
        for _prodic, _geodic in zip(_property, _geometry):
            if "{}_{}".format(_prodic.get("transform"), _prodic.get("md5")) != "{}_{}".format(_geodic.get("transform"),
                                                                                              _geodic.get("md5")):
                info += "{}\n".format(_geodic["transform"])
        return False, info
    return True, None


# =======================================================================================================
# 检查是否存在引擎材质颜色 
def engine_color():
    # get shading engines
    _nodes = shadingengine.nodes()
    _error_nodes = []
    for _node in _nodes:
        if not cmds.objExists("{}.shadingcolor".format(_node)):
            _error_nodes.append(_node)
    if _error_nodes:
        info = u"存在未赋予shadingcolor的材质引擎,请用材质引擎颜色插件检查\n"
        for _node in _error_nodes:
            info += "{}\n".format(_node)
        return False, info
    return True, None


def engine_shader():
    # get shading engines
    _nodes = shadingengine.nodes()
    _error_nodes = []
    for _node in _nodes:
        _ori_material = cmds.listConnections("{}.surfaceShader".format(_node), s=True)
        if not _ori_material:
            continue
        _ori_material = _ori_material[0]
        if _ori_material.startswith("zfused_shading_color_"):
            _error_nodes.append(_node)
    if _error_nodes:
        info = u"存在zfused_shading_color材质,请用材质引擎颜色插件检查\n"
        for _node in _error_nodes:
            info += "{}\n".format(_node)
        return False, info
    return True, None


# =======================================================================================================
# 
def tree_name():
    """ 检查模型结构名称
    """
    _task_id = record.current_task_id()
    if not _task_id:
        return False, u"未选择制作任务\n"
    _task = zfused_api.task.Task(_task_id)
    _project_entity = _task.project_entity()
    _name = _project_entity.file_code()
    for _i in cmds.ls(tr=1):
        try:
            _asset_name = cmds.getAttr("%s.treeName" % _i)
            if _asset_name == _name:
                return True, _asset_name
        except:
            pass
    return False, u"文件大纲组命名与任务名不匹配,任务名为 {} \n".format(_name)


# =======================================================================================================
# 检查场景多余修型节点
def defult_asset_node():
    nodes = cmds.ls("defaultLegacyAssetGlobals")
    if not nodes:
        return True, None
    _info = u"存在不应存在的修型节点，请处理\n"
    for _node in nodes:
        _info += _node
    return False, _info


# =======================================================================================================
# 检查场景非标准材质球
def standard_surface():
    _default_materials = ["lambert1", "particleCloud1", "standardSurface1"]
    _materials = cmds.ls(mat=True)
    _materials = list(set(_materials) - set(_default_materials))
    _is_error = False
    info = u"场景存在非标准材质球(standard surface material)\n"
    for _material in _materials:
        _type = cmds.nodeType(_material)
        if _type not in ["standardSurface", "lambert", "phong", "blin", "displacementShader"]:
            _is_error = True
            info += "{}\n".format(_material)
    if _is_error:
        return False, info
    return True, None


# =======================================================================================================
# 检查模型是否丢失材质球
def lost_material():
    _polygons = cmds.ls(type="mesh", ni=True)
    _is_error = False
    info = u"场景存在mesh丢失材质球(lost material)\n"
    for _polygon in _polygons:
        if cmds.nodeType(_polygon) != "mesh":
            continue
        _sgs = cmds.listConnections(_polygon, type="shadingEngine")
        if not _sgs:
            _is_error = True
            info += "{}\n".format(_polygon)
    if _is_error:
        return False, info
    return True, None


# =======================================================================================================
# 检查模型按面赋材质球
def multi_material():
    _polygons = cmds.ls(type="mesh", ni=True)
    _is_error = False
    info = u"场景存在单mesh多材质球(multi material)\n"
    for _polygon in _polygons:
        if cmds.nodeType(_polygon) != "mesh":
            continue
        _sgs = cmds.listConnections(_polygon, type="shadingEngine")
        if _sgs:
            _sgs = list(set(_sgs))
            if len(_sgs) > 1:
                _is_error = True
                info += "{}\n".format(_polygon)
    if _is_error:
        return False, info
    return True, None


# =======================================================================================================
# 检查模型单材质按面赋材质
def material_assign_faces():
    _polygons = cmds.ls(type="mesh", ni=True)
    _is_error = False
    info = u"场景存在单材质球按面赋材质(face assign)[重新选择物体赋下材质]\n"
    for _polygon in _polygons:
        if cmds.nodeType(_polygon) != "mesh":
            continue
        _trans = cmds.listRelatives(_polygon, p=True)[0]
        _sgs = cmds.listConnections(_polygon, type="shadingEngine")
        if _sgs:
            _sgs = list(set(_sgs))
            if len(_sgs) == 1:
                _faces = cmds.sets(_sgs[0], q=True)
                _faces = [_face for _face in _faces if "{}.f[".format(_trans) in _face]
                # print(_faces)
                if len(_faces):
                    # print(_faces)
                    _is_error = True
                    info += "{}\n".format(_polygon)
    if _is_error:
        return False, info
    return True, None


# =======================================================================================================
# 检查场景是否被锁
def lock_file():
    _is_lock = cmds.file(q=True, lf=True)
    if _is_lock:
        return False, u"文件处于锁住状态"
    return True, None


# =======================================================================================================
# 检查通道属性非空
def check_attr():
    # get all transform
    _un = ["front", "persp", "side", "top"]
    _all_trans = cmds.ls(type="transform")
    _use_tans = list(set(_all_trans) - set(_un))
    _de = []
    for _tans in _use_tans:
        _t = cmds.getAttr("%s.translate" % _tans)
        _r = cmds.getAttr("%s.rotate" % _tans)
        _s = cmds.getAttr("%s.scale" % _tans)
        # _child = cmds.listRelatives(_tans, c = True, type = "mesh")
        # if _child:
        if _t != [(0.0, 0.0, 0.0)] or _r != [(0.0, 0.0, 0.0)] or _s != [(1.0, 1.0, 1.0)]:
            _de.append(_tans)
    if _de:
        info = u"通道属性值不为空\n"
        for child in _de:
            info += "{}\n".format(child)
        return False, info
    return True, None


# =======================================================================================================
# 检查模型存在历史记录
def check_history():
    _history = []
    allDags = pm.ls(dag=1)
    for dag in allDags:
        _his = dag.history()
        # _his = [n for n in dag.history(il=1, pdo = True)]
        _his = [n for n in dag.history(il=1, pdo=True) if n.type() not in ["shadingEngine", "AlembicNode", "time"]]
        if _his and dag.type() == "mesh":
            _history.append(dag)
    if _history:
        _history = list(set(_history))
        info = u"错误:部分模型存在历史记录\n"
        for child in _history:
            info += u"%s\n" % child
        return False, info
    
    return True, None


# =======================================================================================================
# 检查场景是否存在多个渲染组
def multi_rendering_group():
    rendering = []
    _renderingdag = [i for i in cmds.ls(dag=1) if cmds.objExists("{}.rendering".format(i))]
    if _renderingdag:
        for dag in _renderingdag:
            value = cmds.getAttr("%s.rendering" % dag)
            if value:
                rendering.append(dag)
        if rendering:
            if len(rendering) == 1:
                return True, None
            else:
                info = u"存在超过一个的可渲染组，请隐藏不参加渲染的组并关闭rendering属性\n"
                info += "\n".join(rendering)
                return False, info
    else:
        info = u"没有可用渲染组，请修改rendering属性值\n"
        info += "\n".join(_renderingdag)
        return False, info


# =======================================================================================================
# 检查模型是否存在渲染组
def rendering_group():
    rendering = []
    allDags = cmds.ls(dag=True)
    for dag in allDags:
        if cmds.objExists("%s.rendering" % dag):
            value = cmds.getAttr("%s.rendering" % dag)
            if value:
                rendering.append(dag)
    if not rendering:
        info = u"文件组织结构错误,请用分组工具分组整合文件\n"
        return False, info
    return True, None


# =======================================================================================================
# 检查相同重复模型
def equal_mesh():
    _info = {}
    _error_meshs = []
    _top_dags = cmds.ls(type="mesh")
    for _top_dag in _top_dags:
        # get dag hierarchy
        allDags = cmds.ls(_top_dag, dag=True, ni=True, type="mesh")
        # print allDags
        for dag in allDags:
            if cmds.nodeType(dag) != "mesh":
                continue
            selectionList = om.MSelectionList()
            selectionList.add(dag)
            node = selectionList.getDependNode(0)
            fnMesh = om.MFnMesh(node)
            dag_info = ""
            dag_info += " %s" % (fnMesh.numVertices)
            dag_info += " %s" % (fnMesh.numEdges)
            dag_info += " %s" % (fnMesh.numPolygons)
            # _info.append(dag_info)
            if dag_info in _info:
                _error_meshs.append(fnMesh.name())
                _error_meshs.append(_info[dag_info])
            else:
                _info[dag_info] = fnMesh.name()
    if _error_meshs:
        _info = u"场景存在拓扑相同模型\n"
        _info += "\n".join(set(_error_meshs))
        return False, _info
    return True, None


# =======================================================================================================
# 检查场景集合Assembly是否存在渲染组
def scene_rendering_group():
    rendering = []
    allDags = cmds.ls(dag=True)
    for dag in allDags:
        if cmds.objExists("%s.rendering" % dag):
            value = cmds.getAttr("%s.rendering" % dag)
            if value:
                rendering.append(dag)
    if rendering:
        info = u"场景存在rendering属性，请删除或者勾去选项\n"
        info += "\n".join(rendering)
        return False, info
    return True, None


# =======================================================================================================
# 
def groom_caching_group():
    rendering = []
    allDags = cmds.ls(dag=True)
    for dag in allDags:
        if cmds.objExists("%s.groom_caching" % dag):
            value = cmds.getAttr("%s.groom_caching" % dag)
            if value:
                rendering.append(dag)
    if not rendering:
        info = u"文件不存在生长面组,请检查整合文件\n"
        return False, info
    return True, None


def camera_name():
    _task_id = record.current_task_id()
    if not _task_id:
        return False, u"没有任务ID"
    _task = zfused_api.task.Task(_task_id)
    _project_entity = _task.project_entity()
    _name = _project_entity.file_code()
    info = u"当前摄像机名称与任务名{}不匹配\n".format(_name)
    if not cmds.ls("*%s*" % _name, type="camera"):
        return False, info
    return True, None


def file_name():
    _info = u"当前文件名称与任务名不匹配\n"
    _task_id = record.current_task_id()
    if not _task_id:
        return False, _info
    _task = zfused_api.task.Task(_task_id)
    _project_entity = _task.project_entity()
    _name = _project_entity.file_code()
    _file_name = cmds.file(q=True, sn=True)
    if _name not in os.path.basename(_file_name):
        return False, _info
    return True, None


def file_node():
    """ check file node is not null
    """
    _file_nodes = texture.error_nodes()
    if _file_nodes:
        info = u"file节点存在错误贴图路径,请用贴图管理工具检查\n"
        for _file_node in _file_nodes:
            info += "{}\n".format(_file_node)
        return False, info
    # 检查贴图空格
    return texture_space()
    return True, None


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
    _lays = cmds.ls(type="animLayer")
    if _lays:
        _lays.remove('BaseAnimation')
    if len(_lays) > 0:
        info = u"场景存在多余动画层\n"
        for _layer in _lays:
            info += "{}\n".format(_layer)
        return False, info
    return True, None


def unknown_node():
    """ check unknown nodes
    """
    _nodes = cmds.ls(type="unknown")
    if len(_nodes) > 0:
        info = "场景存在未知节点\n"
        for _node in _nodes:
            info += "{}\n".format(_node)
        return False, info
    return True, None


def camera():
    """ check camera
    """
    _extra_camera = ["facial_cam"]
    _cameras = cmds.ls(type="camera")
    _left_cameras = list(set(_cameras) - set(["frontShape", "topShape", "perspShape", "sideShape"]))
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
        return False, info
    return True, None


def light():
    """ check light
    """
    _lights = cmds.ls(type=cmds.listNodeTypes("light"))
    
    if _lights:
        info = "场景存在多余灯光节点\n"
        for _light in _lights:
            info += "{}\n".format(_light)
        return False, info
    return True, None


def anim_curve():
    """ check anim curves
    """
    _cures = cmds.ls(type='animCurve')
    if _cures:
        info = "场景存在动画曲线\n"
        for _cure in _cures:
            info += "{}\n".format(_cure)
        return False, info
    return True, None


def display_layer():
    """ check display layer
    """
    import pymel.core as core
    _layers = [Layer for Layer in core.ls(type='displayLayer') if not core.referenceQuery(Layer,
                                                                                          isNodeReferenced=True) and Layer.name() != 'defaultLayer' and cmds.getAttr(
        "%s.identification" % Layer) != 0]
    _layers = [_layer for _layer in _layers if _layer != "norender"]
    if _layers:
        info = "场景存在显示层\n"
        for _layer in _layers:
            info += "{}\n".format(_layer)
        return False, info
    return True, None


def render_layer():
    """ check render layer
    """
    import pymel.core as core
    _layers = [Layer for Layer in core.ls(type='renderLayer') if
               not core.referenceQuery(Layer, isNodeReferenced=True) and Layer.name() != 'defaultRenderLayer']
    if _layers:
        info = "场景存在渲染层\n"
        for _layer in _layers:
            info += "{}\n".format(_layer)
        return False, info
    return True, None


# =========================================================================================
# name space 相关
def namespace():
    """ check namespace
    """
    _namespaces = cmds.namespaceInfo(recurse=True, listOnlyNamespaces=True)
    _namespaces = list(set(_namespaces) - set(["shared", "UI"]))
    if _namespaces:
        info = "场景中存在命名空间\n"
        for _namespace in _namespaces:
            info += "{}\n".format(_namespace)
        return False, info
    return True, None


def equal_namespace():
    """ 检查文件中存在相同namespace
    """
    _rf_nodes = cmds.ls(rf=True)
    _rf_ns_node = {}
    _error_rf_nodes = []
    for _rf_node in _rf_nodes:
        _inr = cmds.referenceQuery(_rf_node, inr=True)
        if not _inr:
            try:
                _namespace = cmds.referenceQuery(_rf_node, namespace=True)
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
            info += "{} - {}\n".format(_error_rf_node[0], _error_rf_node[1])
        return False, info
    return True, None


def multi_namespace():
    """ 检查文件中存在 多级 namespace
    """
    
    # #set the current naemspace to world
    # curNS = cmds.namespaceInfo(cur=True)
    # cmds.namespace(set=":")
    #
    # #because maya can only list the child namespaces of the current set namespace, we have to recursively go through setting
    # #and checking child namespaces
    #
    # #start by getting the worlds children
    # namespaces = []
    # childspaces = cmds.namespaceInfo(lon=True)
    #
    # while childspaces:
    #     #move the current add spaces into the namespaces list (what we will return)
    #     namespaces.extend(childspaces)
    #     #create a list from the childspaces so that we can check for their children
    #     checkspaces = childspaces
    #     #empty the childspaces so all new children can be added to it for the next round
    #     childspaces = []
    #     #cycle through the current checkspaces and get their child namespaces
    #     for check in checkspaces:
    #         cmds.namespace(set=(":" + check))
    #         grandchildspaces = cmds.namespaceInfo(lon=True)
    #         if grandchildspaces:
    #             childspaces.extend(grandchildspaces)
    #
    # #remove default namespaces
    # if namespaces.count('UI'): namespaces.remove('UI')
    # if namespaces.count('shared'): namespaces.remove('shared')
    #
    # cmds.namespace(set=(":" + curNS))
    # namespaces.sort()
    #
    # _error_rf_nodes = []
    # if namespaces:
    #     for _namespace in namespaces:
    #         if len(_namespace.split(":")) >= 2:
    #             _error_rf_nodes.append(_namespace)
    #
    # # return _error_rf_nodes
    # if _error_rf_nodes:
    #     info = "场景存在 多级 namespace 参考\n"
    #     for _error_rf_node in _error_rf_nodes:
    #         info += "{} - {}\n".format(_error_rf_node[0], _error_rf_node[1])
    #     return False, info
    # return True, None
    
    _rendergrps = renderinggroup.nodes()
    _error_rf_nodes = []
    for dag in _rendergrps:
        _reference = cmds.referenceQuery(dag, inr=1)
        if not _reference:
            continue
        _namespace = cmds.referenceQuery(dag, ns=True)
        if _namespace:
            if len(_namespace.split(":")) >= 3:
                _error_rf_nodes.append(dag)
    
    if _error_rf_nodes:
        info = u"场景存在 多级 namespace 参考\n"
        for _error_rf_node in _error_rf_nodes:
            info += "{}\n".format(_error_rf_node)
        return False, info
    return True, None


def repeat(node_type="mesh"):
    """ 检查重命名
    """
    
    def get_uuid_info():
        # 记录相同uuid下的mesh
        uuid_dict = {}
        #render_node  =renderinggroup.nodes()
        _meshes = cmds.ls(type='mesh', ap=True)
        for _mesh in _meshes:
            if cmds.nodeType(_mesh) != "mesh":
                continue
            _uuid = cmds.ls(_mesh, uuid=True)[0]
            uuid_dict.setdefault(_uuid, []).append(_mesh)
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
    #render_node = renderinggroup.nodes()
    _lists = cmds.ls(noIntermediate=1, type=node_type)
    info = "场景存在重复命名节点\n"
    _uuid_info = get_uuid_info()
    for _name in _lists:
        if len(_name.split('|')) != 1:
            _uuid = cmds.ls(_name, uuid=1)[0]
            print(_uuid)
            # 若len()不等于1，说明当前uuid值下的模型有多个，且为instance形式存在（因为不同的DAG节点有不同的uuid）
            if len(_uuid_info[_uuid]) == 1:
                _is_repeat = True
                info += "{}\n".format(_name)
    
    if _is_repeat:
        return False, info
    else:
        return True, None


def gpu_repart():
    """
    检查GPU 重命名
    """
    
    def get_uuid_info():
        # 记录相同uuid下的mesh
        uuid_dict = {}
        _meshes = cmds.ls(type='gpuCache', ap=True)
        for _mesh in _meshes:
            _uuid = cmds.ls(_mesh, uuid=True)[0]
            uuid_dict.setdefault(_uuid, []).append(_mesh)
        return uuid_dict
    
    _is_repeat = False
    _lists = cmds.ls(noIntermediate=1, type='gpuCache')
    info = u"场景存在重复命名gpu节点\n"
    _uuid_info = get_uuid_info()
    for _name in _lists:
        if len(_name.split('|')) != 1:
            _uuid = cmds.ls(_name, uuid=1)[0]
            # 若len()不等于1，说明当前uuid值下的模型有多个，且为instance形式存在（因为不同的DAG节点有不同的uuid）
            if len(_uuid_info[_uuid]) == 1:
                _is_repeat = True
                info += "{}\n".format(_name)
    
    if _is_repeat:
        return False, info
    else:
        return True, None


def ass_repeat():
    """
    检查ASS是否重名
    :return:
    """
    
    def get_uuid_info():
        # 记录相同uuid下的mesh
        uuid_dict = {}
        _meshes = cmds.ls(type='aiStandIn', ap=True)
        for _mesh in _meshes:
            _uuid = cmds.ls(_mesh, uuid=True)[0]
            uuid_dict.setdefault(_uuid, []).append(_mesh)
        return uuid_dict
    
    _is_repeat = False
    _lists = cmds.ls(noIntermediate=1, type='aiStandIn')
    info = u"场景存在重复命名ass节点\n"
    _uuid_info = get_uuid_info()
    for _name in _lists:
        if len(_name.split('|')) != 1:
            _uuid = cmds.ls(_name, uuid=1)[0]
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
    _meshGrp = [x for x in cmds.ls(type='transform') if ('_model_GRP' in x) and cmds.objExists(x + '.treeName')]
    if _meshGrp:
        _all_meshs = cmds.listRelatives(_meshGrp[0], type="mesh", ad=1, f=1)
        _all_trans = cmds.listRelatives(_all_meshs, p=1, f=1)
        if _all_trans:
            for i in _all_trans:
                wrongtrans = cmds.listRelatives(i, ad=1, type="transform")
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
    if cmds.getAttr("%s.v" % node) == 0:
        _value = False
    while True:
        node = cmds.listRelatives(node, p=1, f=True)
        if not node:
            break
        else:
            node = node[0]
            if cmds.getAttr("%s.v" % node) == 0:
                _value = False
                break
    return _value


def color_set():
    '''顶点着色
    '''
    _color_set = []
    _dags = cmds.ls(dag=1)
    if not _dags:
        return True, None
    for _dag in _dags:
        _set = cmds.polyColorSet(_dag, q=1, acs=1)
        if _set:
            _color_set.extend(_set)
    if _color_set:
        info = "场景存在顶点着色\n{}".format("\n".join(_color_set))
        return False, info
    else:
        return True, None


def intermediate_shape():
    sel = cmds.ls(io=1, type="mesh")
    if sel:
        info = "场景存在转换的中间模型\n{}".format("\n".join(sel))
        return False, info
    else:
        return True, None


def normal_lock():
    '''法线锁定
    '''
    from random import randint
    meshs = cmds.ls(type="mesh", io=0)
    lockmesh = []
    if not meshs:
        return True, None
    for _mesh in meshs:
        if cmds.nodeType(_mesh) != "mesh":
            continue
        try:
            _allvtx = cmds.polyEvaluate(_mesh, v=1)
            tempvtx = "{}.vtx[{}]".format(_mesh, randint(0, _allvtx))
            if cmds.polyNormalPerVertex(tempvtx, q=1, allLocked=1)[0]:
                lockmesh.append(_mesh)
        except:
            lockmesh.append(_mesh)
    if lockmesh:
        info = u"模型法线被锁定，请修改；或者存在重合点，请合并重合点\n"
        info += "\n".join(cmds.listRelatives(lockmesh, p=1))
        return False, info
    else:
        return True, None


def polygon_edge5():
    '''5边或者更多边的多边形
    '''
    meshs = cmds.ls(type="mesh", io=0)
    if not meshs:
        return True, None
    edge5_list = []
    for _mesh in meshs:
        if cmds.nodeType(_mesh) != "mesh":
            continue
        cmds.select(_mesh, replace=True)
        cmds.polySelectConstraint(mode=3, type=0x0008, size=3)
        cmds.polySelectConstraint(disable=True)
        edge5 = cmds.filterExpand(ex=True, sm=34) or []
        if edge5 != []:
            print(_mesh)
            edge5_list.append(_mesh)
    if edge5_list:
        info = u"有5边或者更多边的多边形，请修改\n"
        info += "\n".join(cmds.listRelatives(edge5_list, p=1))
        return False, info
    else:
        return True, None


# =======================================================================================================
# key animation
# 检查maya关于key帧的相关检查
def useless_key():
    ''' 检查是否存在错误位置的k帧
        缓存是从geometry组开始发布的
        该组的父组不允许存在任何k帧信息
    '''
    
    def get_key_attr(grp, _list=[]):
        checkattr = set(
            ["visibility", "translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ", "scaleX",
             "scaleY", "scaleZ"])
        while True:
            grp = cmds.listRelatives(grp, p=1, f=1, type="transform")
            if not grp:
                break
            else:
                grp = grp[0]
                _usedAttr = cmds.listConnections(grp, p=1, c=1, d=0)
                if _usedAttr:
                    _checkattr = list(set([i[len(i.split(".")[0]) + 1:] for i in _usedAttr[::2]]) & checkattr)
                    if _checkattr:
                        _list.append(grp)
        return _list
    
    _rendergrps = renderinggroup.nodes()
    if not _rendergrps:
        return True, None
    key_attr = []
    for _rendergrp in _rendergrps:
        get_key_attr(_rendergrp, key_attr)
    if not key_attr:
        return True, None
    _info = u"存在错误的k帧位置，请使用控制器重新k帧并移除错误k帧信息\n"
    _info += "\n".join(key_attr)
    return False, _info


def keys():
    """
    检查文件当中是否存在K 帧信息
    :return:
    """
    attr_list = ['animCurveUL', 'animCurveUA', 'parentConstraint']
    all_trans = cmds.ls(type='transform')
    error_node = []
    for _tran in all_trans:
        if cmds.keyframe(_tran, query=True, keyframeCount=True) != 0:
            error_node.append(_tran)
    _info = u"文件存在K 帧，请检查！\n"
    if not error_node:
        return True, None
    error_node_copy = copy.deepcopy(error_node)
    for _node in error_node_copy:
        if cmds.nodeType(_node) in attr_list:
            error_node.remove(_node)
        sources = cmds.listConnections(_node, s=True, d=False)
        if sources:
            if cmds.nodeType(sources[0]) in attr_list:
                error_node.remove(_node)
    if not error_node:
        return True, None
    for node in error_node:
        if cmds.nodeType(node) in attr_list:
            continue
        sources = cmds.listConnections(node, s=True, d=False)
        if sources:
            if cmds.nodeType(sources[0]) in attr_list:
                continue
        _info += '{}\n'.format(node)
    return False, _info


# =======================================================================================================
# reference
# 检查maya关于reference相关检查
def null_reference():
    """null reference node
    """
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


def reference():
    """ check reference file
    """
    _references = cmds.ls(type="reference")
    if _references:
        info = "场景存在参考文件\n"
        for _reference in _references:
            info += "{}\n".format(_reference)
        return False, info
    return True, None


def reference_file_node():
    """ check reference file
    """
    pass


def unrecord_reference_file():
    """检查文件中未记录在zf数据库的文件
    """
    _un_record = []
    _reference_nodes = cmds.ls(rf=True)
    info = "场景存在参考文件非zf登记文件\n"
    _is_unrecord = False
    for _node in _reference_nodes:
        try:
            _file_path = cmds.referenceQuery(_node, f=True, wcn=True)
            _production_files = zfused_api.zFused.get("production_file_record", filter={
                "Path": _file_path})
            if not _production_files:
                _is_unrecord = True
                info += "{}\n".format(_node)
        except:
            pass
    if _is_unrecord:
        return False, info
    return True, None


def postfix_group():
    """ 检查所有组名是否后缀为_group
    """
    _node_list = cmds.ls(et='transform')
    _gro_list = []
    _is_error = False
    info = u"场景存在不是以_group为后缀的组名\n"
    
    for i in _node_list:
        _child = cmds.listRelatives(i, c=True, type='shape')
        if _child == None:
            _gro_list.append(i)
    for j in _gro_list:
        # info = '...\n'
        _gro_name = str(j)
        if _gro_name.endswith('_group') == False:
            info += u"{}\n".format(_gro_name)
            _is_error = True
    if _is_error:
        return False, info
    return True, None


def scene_path():
    """ 检查场景路径
    """
    _scene_path = cmds.file(sceneName=True, query=True)
    if not all(ord(c) < 128 for c in _scene_path):
        info = "场景路径有中文\n"
        return False, info
    return True, None


def node_name():
    """ 检查模型不规范命名
    """
    _task_id = record.current_task_id()
    _task_entity = zfused_api.task.Task(_task_id)
    _asset_name = _task_entity.project_entity().code()
    
    _node_list = cmds.ls(dag=True, transforms=True)
    _wrongnode = []
    info = u"场景存在不规范的命名\n"
    
    _defult_cam = ['persp', 'top', 'front', 'side']
    for cam in _defult_cam:
        _node_list.remove(cam)
    for i in _node_list:
        if 'pasted' in str(i) or 'polySurface' in str(i) or _asset_name not in str(i):
            _wrongnode.append(i)
    if _wrongnode != []:
        for _node in _wrongnode:
            _node_name = str(_node)
            info += u"{}\n".format(_node)
        return False, info
    return True, None


def material_name():
    """ 检查材质不规范命名
    """
    _task_id = record.current_task_id()
    _task_entity = zfused_api.task.Task(_task_id)
    _asset_name = _task_entity.project_entity().code()
    
    _node_list = cmds.ls(mat=True)
    _wrongnode = []
    info = u"场景存在不规范的材质命名\n"
    
    _defult_shader = ['standardSurface1', 'particleCloud1', 'lambert1']
    for _shader in _defult_shader:
        _node_list.remove(_shader)
    for i in _node_list:
        if 'pasted' in str(i) or 'polySurface' in str(i) or 'aiStandard' in str(i) or 'lambert' in str(
                i) or _asset_name not in str(i):
            _wrongnode.append(i)
    if _wrongnode != []:
        for _node in _wrongnode:
            _node_name = str(_node)
            info += u"{}\n".format(_node_name)
        return False, info
    return True, None


def unrecord_gpu():
    """
    检查当前文件里面的GPU 是否在服务器记录
    :return:
    """
    _gpu_caches = cmds.ls(type='gpuCache')
    _un_record = []
    info = "场景存在参考文件非zf登记GPU\n"
    _is_unrecord = False
    for _gpu_cache in _gpu_caches:
        _gpu_cache_path = cmds.getAttr('{}.cacheFileName'.format(_gpu_cache))
        _production_files = zfused_api.zFused.get("production_file_record", filter={
            "Path": _gpu_cache_path})
        if not _production_files:
            _is_unrecord = True
            info += "{}\n".format(_gpu_cache)
    if _is_unrecord:
        return False, info
    return True, None


# 此功能 329 已存在，需删除
# def texture_path():
#     """
#        检查未成功导入的贴图文件
#     """
#     path_list = cmds.filePathEditor(query=True, ld="")
#     info = u'有未成功导入的贴图文件：\n'
#     _is_error = False

#     for path in path_list:        
#         file_path = cmds.filePathEditor(query=True,  ld=path, status = True)[0]
#         is_right = cmds.filePathEditor(query=True,  ld=path, status = True)[1]
#         #file_path,is_right = cmds.filePathEditor(query=True,  ld=path, status = True)
#         if int(is_right) != 1:
#             files = cmds.filePathEditor(query=True,  lf=path, status = True)
#             for i in range(0, len(files), 2):
#                 name,mes = files[i:i + 2]
#                 strname = str(name)
#                 if int(mes) == 0 and strname.endswith('.wav')== False:
#                     info += u"{}/{}\n".format(file_path,name)
#                     _is_error = True               
#     if _is_error:
#         return False, info
#     return True, None

# def texture_space():
#     """
#        检查贴图文件路径带空格
#     """
#     path_list = cmds.filePathEditor(query=True, ld="")
#     info = u'有路径内带空格的贴图文件：\n'
#     _is_error = False
#
#     if not path_list:
#         return True, None
#
#     for path in path_list:
#         names = cmds.filePathEditor(query=True, lf=path)
#         for name in names:
#             fullpath = u"{}/{}\n".format(path, name)
#             if ' ' in fullpath:
#                 info += u"{}\n".format(fullpath)
#                 _is_error = True
#     if _is_error:
#         return False, info
#     return True, None


def texture_space():
    """
       检查贴图文件路径带空格
    """
    info = u'有路径内带空格的贴图文件：\n'
    _file_list = texture.files()
    _is_error = False
    if not _file_list:
        return True, None
    for _path in _file_list:
        if ' ' in _path:
            info += u"{}\n".format(_path)
            _is_error = True
    if _is_error:
        return False, info
    return True, None


def get_ancestors(node, checked=None):
    """
       获取组的所有祖先父级
    """
    if not checked:
        checked = []
    ancestors = []
    checked.append(node)
    parents = cmds.listRelatives(node, ap=True)
    if parents:
        for _parent in parents:
            if _parent not in checked:
                checked.append(_parent)
                ancestors.append(_parent)
                ancestors += get_ancestors(_parent, checked=checked)
    return ancestors


def constraint_pos():
    """
       检查模型geo组所有父级下是否存在约束节点
    """
    _node_list = cmds.ls(et='transform')
    _gro_list = []
    _is_error = False
    info = u"存在非规范位置的约束节点\n"
    
    for _node in _node_list:
        _child = cmds.listRelatives(_node, c=True, type='shape')
        if _child == None:
            _gro_list.append(_node)
    for _gro in _gro_list:
        # p = cmds.getAttr("%s.rendering"%_gro, type= True)
        _attrlist = cmds.listAttr(_gro)
        if 'rendering' in _attrlist:
            _anclist = get_ancestors(_gro)
            for _anc in _anclist:
                _conslist = cmds.listRelatives(_anc, type='constraint')
                if _conslist:
                    for _cons in _conslist:
                        info += "{}\n".format(_cons)
                    return False, info
    return True, None


def meshuv_sets():
    checkItem = []
    info = u"存在多套uvSet 或uvSet名称不为map1\n"
    _is_error = False
    for mesh in cmds.ls(type='mesh', long=1):
        if cmds.nodeType(mesh) != "mesh":
            continue
        uvsets = list(set(cmds.polyUVSet(mesh, q=1, auv=1)))
        if len(uvsets) > 1:
            info += u"{}\n".format(mesh)
            _is_error = True
        else:
            if len(uvsets) == 1:
                if uvsets[0] != 'map1':
                    info += u'{}\n'.format(mesh)
                    _is_error = True
    
    if _is_error is True:
        return False, info
    return True, None


def groom_caching_grp():
    """
    检查生长面组是否唯一且存在
    :return:
    """
    all_tr = cmds.ls(transforms=True)
    check_list = []
    for tr in all_tr:
        if cmds.objExists('{}.groom_caching'.format(tr)) is True:
            if not tr in check_list:
                check_list.append(tr)
    
    if len(check_list) == 1:
        return True, None
    elif len(check_list) == 0:
        info = u'生长面组不存在，请添加\n'
        return False, info
    else:
        info = u'生长面组不唯一\n'
        for _group in check_list:
            info += u'{}\n'.format(_group)
            return False, info


def out_curve_grp():
    """
    检查输出曲线组是否存在且唯一
    :return:
    """
    all_tr = cmds.ls(transforms=True)
    check_list = []
    for tr in all_tr:
        if cmds.objExists('{}.out_curve'.format(tr)) is True:
            if not tr in check_list:
                check_list.append(tr)
    
    if len(check_list) == 1:
        return True, None
    elif len(check_list) == 0:
        info = u'输出曲线组不存在，请添加\n'
        return False, info
    else:
        info = u'输出曲组不唯一\n'
        for _group in check_list:
            info += u'{}\n'.format(_group)
            return False, info


def growmesh_sole():
    """
    检查生长面唯一性
    :return:
    """
    # 获取文件内信息
    all_growmeshs = xgen.get_file_grow_meshs()
    all_transforms = cmds.ls(tr=True)
    # 获取数据库信息
    task_id = record.current_task_id()
    _project_entity = zfused_api.task.Task(task_id).project_entity()
    _project_property = _project_entity.property()
    _geometry = _project_property.get('geometry')
    error_meshs = []
    info = u'下列生长面命名不唯一\n'
    for growmesh in all_growmeshs:  # type: object
        _count = all_transforms.count(growmesh)
        if _count != 1:
            error_meshs.append(growmesh)
            continue
        growmesh_shape = cmds.ls(growmesh, dag=True, shapes=True)[0]
        if _geometry:
            for geo in _geometry:
                if geo.get('transform') == growmesh or geo.get('shape') == growmesh_shape:
                    error_meshs.append(growmesh)
                    break
    if len(error_meshs) == 0:
        return True, None
    else:
        for _mesh in error_meshs:
            info += u'{}\n'.format(_mesh)
    
    return False, info


def desc_growmesh():
    """
    检查所有描述的生长面是否存在
    :return:
    """
    _growmeshs = []
    _all_palettes = xg.palettes()
    error_list = []
    for _palette in _all_palettes:
        _pale_descs = xg.descriptions(_palette)
        for _desc in _pale_descs:
            _grow_meshs = xg.boundGeometry(_palette, _desc)
            for _mesh in _grow_meshs:
                if not cmds.objExists(_mesh):
                    error_list.append(_desc)
    info = u'下列描述的生长面不存在\n'
    if len(error_list) == 0:
        return True, None
    else:
        for _des in error_list:
            info += u'{}\n'.format(_des)
    return False, info


def model_description():
    """
    检查生长面组下的模型都为生长面
    :return:
    """
    info = u'没有生长面组\n'
    cache_grp = xgen.get_groom_caching_grp()
    if not cache_grp:
        return False, info
    _all_mesh = xgen.get_file_grow_meshs()
    _trs = cmds.listRelatives(cache_grp, children=True, type='transform')
    error_meshs = []
    for _transform in _trs:
        if not _transform in _all_mesh:
            error_meshs.append(_transform)
    
    info = u'下列模型不为生长面但是在生长面组\n'
    if len(error_meshs) == 0:
        return True, None
    else:
        for _mesh in error_meshs:
            info += u'{}\n'.format(_mesh)
    return False, info


def descriptionGuides():
    """
    检查是否有空描述
    :return:
    """
    all_description = xg.descriptions()
    error_descs = []
    for _dsc in all_description:
        guides = xg.descriptionGuides(_dsc)
        if not guides:
            error_descs.append(_dsc)
    info = u'下列描述为空描述，确认是否应该存在\n'
    if len(error_descs) == 0:
        return True, None
    else:
        for _mesh in error_descs:
            info += u'{}\n'.format(_mesh)
    return False, info


def dyc_guide_link():
    """
    检查输出曲线是否都能找到Guide
    :return:
    """
    error_list = []
    _out_curve_grp = xgen.get_all_out_curve_grp()
    if not _out_curve_grp:
        return False, u'找不到动力曲线组\n'
    _all_curves = cmds.ls(_out_curve_grp, dag=True, type='nurbsCurve', l=True)
    for _curve_shape in _all_curves:
        _curve = cmds.listRelatives(_curve_shape, parent=True, f=True)[0]
        if xgen.get_guide_outcurve(_curve) is None:
            error_list.append(_curve)
    info = u'动力学曲线无法找到生长曲线\n'
    if not error_list:
        return True, None
    for _curve in error_list:
        info += u'{}\n'.format(_curve)
    return False, info


def follicle_guide_link():
    """
    检查毛囊曲线是否能找到生长曲线
    :return:
    """
    error_list = []
    all_follicles = cmds.ls(type='follicle')
    if not all_follicles:
        return True, None
    for _follicleshape in all_follicles:
        _follicle_curve = xgen.get_follical_curve(_follicleshape)
        if _follicle_curve:
            if xgen.get_guide_follicle(_follicle_curve[0]) is None:
                error_list.append(_follicleshape)
    info = u'部分毛囊无法匹配到guide引导线\n'
    if not error_list:
        return True, None
    for follicle in error_list:
        info += u'{}\n'.format(follicle)
    return False, info


def guide_sole():
    """
    检查guide 唯一性
    :return:
    """
    error_list = []
    info = u'以下引导线不唯一\n'
    _descriptions = xg.descriptions()
    for _description in _descriptions:
        _guides = xg.descriptionGuides(_description)
        for _guide in _guides:
            short_name = _guide.split('|')[-1]
            _num = len(cmds.ls(short_name))
            if _num != 1:
                error_list.append(_description)
    if not error_list:
        return True, None
    for _error in error_list:
        info += '{}\n'.format(_error)
    
    return False, info


def xgen_node_reference():
    """
    检查毛发和描述和引导线是否均为参考
    :return:
    """
    error_list = []
    info = u'下列xgen 结点不是来自参考文件，请检查\n'
    _all_palettes = xg.palettes()
    for _palette in _all_palettes:
        if not cmds.referenceQuery(_palette, isNodeReferenced=True):
            error_list.append(_palette)
            continue
        palette_descriptions = xg.descriptions(_palette)
        for _description in palette_descriptions:
            if not cmds.referenceQuery(_description, isNodeReferenced=True):
                error_list.append(_palette)
                continue
            _guides = xg.descriptionGuides(_description)
            for _guide in _guides:
                if not cmds.referenceQuery(_guide, isNodeReferenced=True):
                    error_list.append(_guide)
                    continue
    if not error_list:
        return True, None
    for _error in error_list:
        info += '{}\n'.format(_error)
    return False, info


def last_version():
    """
    检查参考文件是否为最新版本文件
    :return:
    """
    error_nodes = []
    _reference_nodes = cmds.ls(rf=True)
    for _rfn in _reference_nodes:
        try:
            _file_path = cmds.referenceQuery(_rfn, filename=True)
            _production_files = zfused_api.zFused.get("production_file_record", filter={
                "Path": _file_path})
            if not _production_files:
                continue
            if len(_production_files) != 1:
                continue
            _index = _production_files[0].get('Index')
            _task_id = _production_files[0].get('TaskId')
            task_entity = zfused_api.task.Task(_task_id)
            _task_last_index = task_entity.last_version_index()
            if _index != _task_last_index:
                error_nodes.append(_rfn)
        except:
            continue
    info = u'下列参考不是最新版资产，请检查\n'
    if not error_nodes:
        return True, None
    for node in error_nodes:
        info += '{}\n'.format(node)
    
    return False, info


def tx():
    """
    检查贴图tx 是否转换
    :return:
    """
    
    def comp_ctime(file1, file2):
        """
        判断贴图时间和tx 时间，正常应该是tx 时间大于贴图时间
        :param file1: 贴图
        :param file2: tx
        :return:
        """
        time1 = int(os.path.getmtime(file1))
        time2 = int(os.path.getmtime(file2))
        if time1 <= time2:
            return True
        return False
    
    _files = texture.files()
    _error_nodes = []
    for _file in _files:
        _file_name, _suffix = os.path.splitext(_file)
        _tx_file = _file_name + '.tx'
        if not os.path.exists(_tx_file):
            _error_nodes.append(_file)
            continue
        if comp_ctime(_file, _tx_file) is False:
            _error_nodes.append(_file)
    if not _error_nodes:
        return True, None
    info = u'下列贴图文件的tx不存在或时间不正确 \n'
    for _node in _error_nodes:
        info += '{}\n'.format(_node)
    return False, info


def collection_path():
    """
    检查collection的路径是否为多重路径
    :return:
    """
    
    all_palette = xg.palettes()
    if not all_palette:
        return True, None
    error_node = []
    for _palette in all_palette:
        _file_path = xg.expandFilepath(xg.getAttr('xgDataPath', _palette), '', False, False)
        _paths_ = _file_path.split(';')
        if len(_paths_) != 1:
            error_node.append(_palette)
            continue
        if not os.path.exists(_paths_[0]):
            error_node.append(_palette)
            continue
    
    if not error_node:
        return True, None
    info = u'xgen 路径为多重路径或文件路径不存在\n'
    for _node in error_node:
        info += '{}\n'.format(_node)
    
    return False, info


def check_unused_nodes():
    '''
    检查没有用到的节点
    '''
    delete_list = []
    info = u'存在未使用的节点\n'
    ignore_list = cmds.ls(defaultNodes=True)
    ignore_list += [u'shapeEditorManager', u'poseInterpolatorManager', u'sceneConfigurationScriptNode', u'xgenGlobals']
    undel = cmds.ls(ud=True)
    
    nodes = cmds.ls()
    for node in nodes:
        if node not in undel:
            _is_reference = cmds.referenceQuery(node, isNodeReferenced=True)
            if _is_reference:
                continue
            if 'xgenGlobals' in node:
                continue
            if node not in ignore_list:
                type = cmds.nodeType(node)
                cons = cmds.listConnections(node)
                relatives_des = cmds.listRelatives(node, ap=True)
                relatives_par = cmds.listRelatives(node, ad=True)
                if not cons and not relatives_des and not relatives_par:
                    delete_list.append(node)
                    info += u'{}\n'.format(node)
    
    if delete_list:
        return False, info
    else:
        return True, None


def check_default_name():
    '''
    检查默认命名
    '''
    defaults = [
        'polySurface', 'pSphere', 'pCube', 'pCylinder', 'pCone', 'pPlane', 'pTorus', 'pPrism',
        'pPyramid', 'pPipe', 'pHelix', 'pSolid',
        'nurbSurface', 'nurbsSphere',
        'nurbsCube', 'topnurbsCube', 'bottomnurbsCube', 'leftnurbsCube',
        'rightnurbsCube', 'frontnurbsCube',
        'backnurbsCube', 'nurbsCylinder', 'nurbsCone', 'nurbsPlane', 'nurbsTorus',
        'nurbsCircle', 'curve', 'nurbsSquare', 'topnurbsSquare', 'leftnurbsSquare', 'bottomnurbsSquare',
        'rightnurbsSquare',
        'locator', 'group', 'null', 'joint']
    
    info = u"场景存在默认命名\n"
    _wrongnode = []
    
    lists = cmds.ls(dag=True, transforms=True)
    for default in defaults:
        for list in lists:
            if default in list:
                _wrongnode.append(list)
    
    if _wrongnode != []:
        for _node in _wrongnode:
            _node_name = str(_node)
            info += u"{}\n".format(_node)
        return False, info
    return True, None


def repet_model():
    """
    检查模型组里是否有完全相同的模型
    :return:
    """
    all_nodes = cmds.ls(type='mesh')
    _dict = {}
    error_nodes =[]
    
    for _node in all_nodes:
        if cmds.nodeType(_node) != "mesh":
            continue
        _node_max = cmds.getAttr('{}.boundingBoxMax'.format(_node))
        _node_min = cmds.getAttr('{}.boundingBoxMin'.format(_node))
        _list = [_node_min,_node_max]
        if not _list in _dict.values():
            _dict[_node] = _list
        else:
            error_nodes.append(_node)
            _a = list(_dict.keys())[list(_dict.values()).index(_list)]
            error_nodes.append(_a)
    info = u'以下节点有疑似完全相同\n'
    if not error_nodes:
        return True,None
    for _n in error_nodes:
        info += _n+'\n'
    return False,info

def imported_assets():
    """检查被导入的资产
    """
    imported_assets = []
    all_assets = renderinggroup.nodes()
    info = u'存在导入的资产，请视情况清理；如果没有用处请删掉或者点击修复按钮\n'
    for asset in all_assets:
        _is_reference = cmds.referenceQuery(asset, isNodeReferenced=True)
        if not _is_reference:
            imported_assets.append(asset)
            info += u"{}\n".format(asset)
    if not imported_assets:
        return True, None
    else:
        return False, info