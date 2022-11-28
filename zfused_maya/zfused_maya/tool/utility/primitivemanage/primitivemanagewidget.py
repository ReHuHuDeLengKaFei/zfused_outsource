# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

import zfused_maya.core.record as record

from zfused_maya.node.core import element,assembly

from zwidgets.primitivewidget import primitivemanagewidget

from zfused_maya.ui.widgets import window

import maya.cmds as cmds
import zfused_maya.node.core.attr as attr

__all__ = ["PrimitiveManageWidget"]

logger = logging.getLogger(__name__)


class PrimitiveManageWidget(window._Window):
    def __init__(self, parent = None):
        super(PrimitiveManageWidget, self).__init__()
        self._build()

        self._elements = []

        self.primitive_widget.gpu_import.connect(self._import_gpu)
        self.primitive_widget.inside_refreshed.connect(self._get_elements)
        self.primitive_widget.inside_project_step_changed.connect(self._change_elements)
        self.primitive_widget.selected.connect(self._selected)
        self.primitive_widget.switch_version.connect(self._switch_version)
        self.primitive_widget.optimized.connect(self._optimized)
    

    def _optimized(self):
        assembly.optimize_instance()
        self._get_elements()

    def _switch_version(self, is_version):
        if not self._elements:
            return
        for _element in self._elements:
            print(_element)
            _node = _element.get("namespace")
            _gpu_node = cmds.listRelatives(_node, c = True, type = "gpuCache")
            if _gpu_node:
                _gpu_node = _gpu_node[0]
            _task = zfused_api.task.Task(_element.get("task_id"))
            _production_path = _task.production_path()
            _last_version_index = _task.last_version_index()
            if is_version:
                _gpu_file = "{}/gpu/{}.{:0>4d}.abc".format(_production_path, _task.file_code(), _last_version_index)
                _ass_file = "{}/ass/{}.{:0>4d}.ass".format(_production_path, _task.file_code(), _last_version_index)
            else:
                _gpu_file = "{}/gpu/{}.abc".format(_production_path, _task.file_code())
                _ass_file = "{}/ass/{}.ass".format(_production_path, _task.file_code())
            if os.path.isfile(_gpu_file):
                cmds.setAttr('%s.cacheFileName'%_gpu_node, _gpu_file, type = 'string')

            _is_load = cmds.pluginInfo("mtoa", query=True, loaded = True)
            if _is_load:
                if cmds.listRelatives(_node, c = True, type = "aiStandIn"):
                    _ass_node = cmds.listRelatives(_node, c = True, type = "aiStandIn")[0]
                    if cmds.objExists(_ass_node):
                        if os.path.isfile(_ass_file):
                            cmds.setAttr('%s.dso'%_ass_node, _ass_file, type = 'string')

    
    def _selected(self, datas):
        for _data in datas:
            print(_data)
        _sels = [_data.get("namespace") for _data in datas]
        cmds.select(_sels, r = True)

    def _import_gpu(self, path):
        _name = os.path.basename(os.path.splitext(path)[0])
        _gpu_node = cmds.createNode('gpuCache', n = "{}Shape".format(_name))
        cmds.setAttr('%s.cacheFileName'%_gpu_node, path, type = 'string')

        cmds.setAttr('%s.cmp'%_gpu_node, "|", type = 'string')
        cmds.setAttr('%s.vis'%_gpu_node, 0)
        cmds.setAttr('%s.csh'%_gpu_node, 0)
        cmds.setAttr('%s.rcsh'%_gpu_node, 0)
        cmds.setAttr('%s.mb'%_gpu_node, 0)

        # import ass file
        # if ass file is exists
        _ass_file = path.replace(".abc", ".ass").replace("/gpu/", "/ass/")
        if os.path.isfile(_ass_file):
            # 存在 arnold ass 文件
            cmds.setAttr('%s.ai_self_shadows'%_gpu_node, 0)
            cmds.setAttr('%s.ai_vidr'%_gpu_node, 0)
            cmds.setAttr('%s.ai_visr'%_gpu_node, 0)
            cmds.setAttr('%s.ai_vidt'%_gpu_node, 0)
            cmds.setAttr('%s.ai_vist'%_gpu_node, 0)
            cmds.setAttr('%s.ai_viv'%_gpu_node, 0)
            cmds.setAttr('%s.primaryVisibility'%_gpu_node, 0)
            cmds.setAttr('%s.castsShadows'%_gpu_node, 0)
            cmds.setAttr('%s.aiOpaque'%_gpu_node, 0)

            _name = cmds.listRelatives(_gpu_node, parent = True)[0]
            _ai_node = cmds.createNode("aiStandIn", parent = _name, n = "{}_aiStandin".format(_name))
            cmds.setAttr("{}.v".format(_ai_node), k = False)
            cmds.setAttr("{}.standin_draw_override".format(_ai_node), 3)
            cmds.setAttr("{}.covm[0]".format(_ai_node), 0, 1, 1)
            cmds.setAttr("{}.cdvm[0]".format(_ai_node), 0, 1, 1)
            cmds.setAttr("{}.standin_draw_override".format(_ai_node), 3)
            cmds.setAttr("{}.dso".format(_ai_node), _ass_file, type = "string")
            cmds.setAttr("{}.min".format(_ai_node), -1.0000002, -1, -1.0000005, type = "float3")
            cmds.setAttr("{}.max".format(_ai_node), 1, 1, 1.0000001, type = "float3")
        
    def _change_elements(self, project_step_id):
        _elements = element.gpu_elements()
        # self.primitive_widget.load_elements(_elements) 
        for _element in _elements:
            _gpu_element = element.GPUElement(_element)
            _gpu_element.replace_by_project_step(project_step_id)
        self._get_elements()

    def _get_elements(self):
        self._elements = element.gpu_elements(ignore_reference = False)
        self.primitive_widget.load_elements(self._elements)

    def _build(self):
        self.resize(1600, 900)
        self.set_title_name(u"场景单元(元素)管理")

        self.primitive_widget = primitivemanagewidget.PrimitiveManageWidget()
        self.set_central_widget(self.primitive_widget)

    def showEvent(self, event):
        _project_id = record.current_project_id()
        self.primitive_widget.load_project_id(_project_id)
        super(PrimitiveManageWidget, self).showEvent(event)