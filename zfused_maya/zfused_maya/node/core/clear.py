# coding:utf-8
# --author-- lanhua.zhou

""" zfused maya 清除机制 """

from __future__ import print_function

import logging
import os.path

import pymel.core as pm
import maya.cmds as cmds
import zfused_api
from zfused_maya.core import record
from zfused_maya.node.core import renderinggroup

logger = logging.getLogger(__name__)

def is_show(node):
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

def material_assign_faces():
    """还原按面赋材质
    """
    _polygons = cmds.ls(type = "mesh", ni = True)
    for _polygon in _polygons:
        _trans = cmds.listRelatives(_polygon, p = True)[0]
        _sgs = cmds.listConnections(_polygon, type = "shadingEngine")
        if _sgs:
            _sgs = list(set(_sgs))
            if len(_sgs) == 1:
                _faces = cmds.sets(_sgs[0], q = True)
                _faces = [_face for _face in _faces if "{}.f[".format(_trans) in _face ]
                if len(_faces):
                    # clear
                    _mesh = _faces[0].split("f[")[0]
                    _sg = _sgs[0]
                    cmds.select(_mesh)
                    cmds.hyperShade(assign = "standardSurface1")
                    cmds.hyperShade(assign = _sg)

def multi_rendering_group():
    _renderingdag = [i for i in cmds.ls(dag = 1) if cmds.objExists("{}.rendering".format(i))]
    if _renderingdag:
        for dag in _renderingdag:
            _r = cmds.getAttr("%s.rendering"%dag)
            _v = is_show(dag)
            if not _v:
                cmds.deleteAttr(dag,at = "rendering")

def onModelChange3dc():
    # Get all model editors in Maya and reset the editorChanged event
    for item in pm.lsUI(editors=True):
       if isinstance(item, pm.ui.ModelEditor):
           pm.modelEditor(item, edit=True, editorChanged="")

def lock_file():
    cmds.file(lf = 0)
    cmds.file(save = True, f = True, options = "v=0;")

def unknown_plugins():
    """ clear unknown plugins
    """
    oldplugins = cmds.unknownPlugin(q=True, list=True)
    if not oldplugins:
        return
    for plugin in oldplugins:
        try:
            cmds.unknownPlugin(plugin, remove=True)
        except:
            pass

def animation_layer():
    """ clear animation layer
    """
    _lays = cmds.ls(type = "animLayer")
    if _lays:
        for _lay in _lays:
            cmds.delete(_lay)

def unknown_node():
    allNodes = cmds.ls(type = "unknown")
    if allNodes:
        for node in allNodes:
            try:
                cmds.lockNode(node, lock = False)
                cmds.delete(node)
            except Exception as e:
                # logger.warning(e)
                pass
def camera():
    """ clear camera

    """
    _extra_camera = ["facial_cam"]
    allCameras = cmds.ls(type = "camera")
    initCameras = list(set(allCameras) - set(["frontShape","topShape","perspShape","sideShape"]))
    if initCameras:
        for camera in initCameras:
            _is_extra = False
            for _cam in _extra_camera:
                if _cam in _camera:
                    _is_extra = True
            if _is_extra:
                continue
            cameraTrans = cmds.listRelatives(camera, parent = True)
            try:
                cmds.lockNode(cameraTrans, lock = False)
                cmds.delete(cameraTrans)
            except Exception as e:
                logger.warning(e)

def light():
    """ clear light

    """
    _lights = cmds.ls(type = cmds.listNodeTypes("light"))
    
    if _lights:
        for _light in _lights:
            try:
                #if cmds.objExists(_light):
                if cmds.referenceQuery(_light,isNodeReferenced = True) == False:
                    par = cmds.listRelatives(_light, p = True)
                    cmds.delete(par)
            except Exception as e:
                logger.warning(e)

def anim_curve():
    """ clear animation curve

    """
    NodeList = cmds.ls(type = 'animCurve')
    if NodeList:
        for NodeName in NodeList:
            if cmds.referenceQuery(NodeName,isNodeReferenced = True) == False:
                cmds.delete(NodeName)

def display_layer():
    """ clear diaplay layers

    """
    import pymel.core as core
    DisplayLayer = [Layer for Layer in core.ls(type = 'displayLayer') if not core.referenceQuery(Layer,isNodeReferenced = True) and Layer.name() != 'defaultLayer' and cmds.getAttr("%s.identification"%Layer) != 0]
    if DisplayLayer:
        for Layer in DisplayLayer:
            Layer.attr('drawInfo').disconnect()
            Layer.unlock()
            core.delete(Layer)

def render_layer():
    """ clear render layers

    """
    import pymel.core as core
    RenderLayer = [Layer for Layer in core.ls(type = 'renderLayer') if not core.referenceQuery(Layer,isNodeReferenced = True) and Layer.name() != 'defaultRenderLayer']
    if RenderLayer:
        for Layer in RenderLayer:
            #Layer.attr('drawInfo').disconnect()
            Layer.unlock()
            core.delete(Layer)

def namespace():
    """ clear namespace
    
    """
    NamespaceList = cmds.namespaceInfo(recurse = True,listOnlyNamespaces = True)
    if NamespaceList:
        NamespaceList.reverse()
        for NamespaceName in NamespaceList:
            if NamespaceName != 'shared' and NamespaceName != 'UI':
                cmds.namespace(setNamespace = NamespaceName)
                NamespaceList = cmds.namespaceInfo(recurse = True,listOnlyNamespaces = True)
                NodeList = cmds.namespaceInfo(listOnlyDependencyNodes = True,dagPath = True)
                ParentNamespace = cmds.namespaceInfo(parent = True)
                cmds.namespace(setNamespace = ':')
                if NamespaceList == None:
                    if NodeList == None:
                        try:
                            cmds.namespace(removeNamespace = NamespaceName)
                        except Exception as e:
                            logger.warning(e)
                    else:
                        IsNodeReferenced = False
                        for NodeName in NodeList:
                            if cmds.referenceQuery(NodeName,isNodeReferenced = True) == True:
                                IsNodeReferenced = True
                                break
                        if IsNodeReferenced == False:
                            try:
                                cmds.namespace(force = True,moveNamespace = (NamespaceName,ParentNamespace))
                                cmds.namespace(removeNamespace = NamespaceName)
                            except Exception as e:
                                logger.warning(e)

def reference():
    _reference_nodes = cmds.ls(typ="reference")
    for _reference_node in _reference_nodes:
        try:
            _reference_file = cmds.referenceQuery(_reference_node, f = True)
            _getlinknode = cmds.listConnections(_reference_node)
            if _getlinknode == None and not _reference_file:
                cmds.lockNode(_reference_node, l=0)
                cmds.delete(_reference_node)
        except Exception as e:
            logger.warning(e)
            cmds.lockNode(_reference_node, l=0)
            cmds.delete(_reference_node)


def color_set():
    '''顶点着色
    '''
    _color_set = []
    _dags = cmds.ls(dag = 1)
    if _dags:
        for _dag in _dags:
            if cmds.polyColorSet(_dag,q = 1,acs = 1):
                cmds.polyColorSet(_dag,e = 1,d = 1)

def intermediate_shape():
    sel = cmds.ls(io = 1,type = "mesh")
    if sel:
        cmds.delete(sel)

def _delete_multishape():
    _getmesh = cmds.ls(typ="mesh", l=1)
    _getparent = set(cmds.listRelatives(_getmesh, p=1, f=1))
    for _aname in _getparent:
        _getshape = cmds.listRelatives(_aname, s=1, f=1)
        if _getshape:
            if len(_getshape)>1:
                cmds.delete(_getshape[1:])


def normal_lock():
    '''法线锁定
    '''
    meshs = cmds.ls(type = "mesh",io = 0)
    lockmesh = []
    if meshs:
        for _mesh in meshs:
            cmds.polyNormalPerVertex(_mesh,ufn = 1)

def null_refernece():
    """
    清理 未参考reference
    """
    _references = cmds.ls(rf=True)
    _null_reference = []
    for _reference in _references:
        try:
            cmds.referenceQuery(_reference, f=1)
        except:
            _null_reference.append(_reference)
    if len(_null_reference) !=0:
        for _ref in _null_reference:
            cmds.lockNode(_ref,lock =False)
            cmds.delete(_ref)


def gpu_rename():
    """
    批量修改gpu的名字
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
    _uuid_info = get_uuid_info()
    for _name in _lists:
        if len(_name.split('|')) != 1:
            _uuid = cmds.ls(_name, uuid=1)[0]
            # 若len()不等于1，说明当前uuid值下的模型有多个，且为instance形式存在（因为不同的DAG节点有不同的uuid）
            if len(_uuid_info[_uuid]) == 1:
                _trasform_name =cmds.listRelatives(_name,p=True)[0]
                new_name = _trasform_name+'Gpu'
                cmds.rename(_name,new_name)

def rename_ass():
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
                _trasform_name = cmds.listRelatives(_name, p=True)[0]
                new_name = _trasform_name + 'aiStandIn'
                cmds.rename(_name, new_name)


def del_unused_nodes():
    '''
    删除未使用的节点
    '''
    delete_list = []
    ignore_list = cmds.ls(defaultNodes = True)
    ignore_list += [u'shapeEditorManager',u'poseInterpolatorManager',u'sceneConfigurationScriptNode',u'xgenGlobals']

    undel = cmds.ls(ud = True)
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
                relatives_des = cmds.listRelatives(node,ap = True)
                relatives_par = cmds.listRelatives(node,ad = True)
                if not cons and not relatives_des and not relatives_par:
                    try :
                        cmds.delete(node)
                        delete_list.append(node)
                    except :
                        pass
    print (delete_list)

def delete_type_node():
    '''
    删除特殊类型节点
    '''
    delete_type = ['shapeEditorManager','poseInterpolatorManager']

    for de in delete_type:
        node_list = cmds.ls(type = de)
        for node in node_list:
            _inr = cmds.referenceQuery(node, inr = True)
            if not _inr:
                logger.warning('{} is deep reference node , cannot be deleted'.format(node))
            else:
                cmds.delete(node)

def cancle_rendering_attr():
    from . import renderinggroup
    imported_assets = []
    all_assets = renderinggroup.nodes()
    for asset in all_assets:
        _is_reference = cmds.referenceQuery(asset, isNodeReferenced=True)
        if not _is_reference:
            imported_assets.append(asset)
    for _node in imported_assets:
        cmds.setAttr("%s.rendering"%_node, 0)


def rename_file():
    _task_id  = record.current_task_id()
    if not _task_id:
        return False
    _task = zfused_api.task.Task(_task_id)
    #_project_entity = _task.project_entity()
    _name = _task.full_code()
    _file_name = cmds.file(q=True, sn=True)
    _short_file_name = cmds.file(q=True,sn=True,shn=True)
    _file_path = os.path.dirname(_file_name)
    _suffix = os.path.splitext(_file_name)[-1]
    _new_file_name = _name +_suffix
    _new_file_path = os.path.join(_file_path,_new_file_name)
    if os.path.exists(_new_file_path):
        _new_file_path = '{}/temp_{}'.format(_file_path,_new_file_name)
    _file_format = 'mayaAscii'
    if _suffix =='mb':
        _file_format = 'mayaBinary'
    cmds.file(rename = _new_file_path)
    cmds.file(save=True, type=_file_format, f=True, options="v=0;")


def horizon():
    """
    修复最低点低于水平面
    :return:
    """

    geo_groups = [i for i in cmds.ls(type='transform', l=True) if
                  cmds.objExists("{}.Name".format(i)) and cmds.getAttr('{}.Name'.format(i)) == 'geometry']
    _rending_node = renderinggroup.nodes()
    check_node = list(set(geo_groups + _rending_node))

    for _node in check_node:
        miny = cmds.getAttr('{}.boundingBoxMinY'.format(_node))
        ty = cmds.getAttr('{}.ty'.format(_node))
        m_y = ty +abs(miny)
        cmds.setAttr('{}.ty'.format(_node),m_y)
        cmds.makeIdentity(_node,t=True,a=True)