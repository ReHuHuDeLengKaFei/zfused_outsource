# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function
from functools import partial

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,language

import zfused_maya.core.record as record

import zfused_maya.node.core.relatives as relatives
import zfused_maya.node.core.element as element

from . import listmodel
from . import listview
from . import itemdelegate


__all__ = ["ElementListWidget"]

logger = logging.getLogger(__name__)


class ElementListWidget(QtWidgets.QFrame):
    refresh = QtCore.Signal(int)
    def __init__(self, parent = None):
        super(ElementListWidget, self).__init__(parent)
        
        self._build()
        
        self.list_view.customContextMenuRequested.connect(self._change_elements)
        self.update_element_action.triggered.connect(self._update_selected)

    def showEvent(self, event):
        super(ElementListWidget, self).showEvent(event)
        self._script_job()

    def batch_switch_project_step_id(self, project_step_id):
        _scene_elements = element.reference_elements()
        if _scene_elements:
            for _scene_element in _scene_elements:
                _element = element.ReferenceElement(_scene_element)
                _element.replace_by_project_step(project_step_id, True)
                #　self._replace_by_project_step(_element, project_step_id)

    def _script_job(self):
        import maya.cmds as cmds
        #if exists 
        allJobs = cmds.scriptJob(lj = True)
        for job in allJobs:
            if "zfused_maya.tool.utility.elementmanage.elementlistwidget.elementlistwidget" in job:
                id = int(job.split(":")[0])
                cmds.scriptJob(kill= id, force=True)
        # if not is_exist:
        cmds.scriptJob(e = ("PostSceneRead", self.refresh_scene), protected = True)

    def _update_selected(self):
        """ selected elements
        """
        _indexs = self.list_view.selectedIndexes()
        if not _indexs:
            return 
        for _index in _indexs:
            _data = _index.data()
            _element_handle = element.ReferenceElement(_data)
            _element_handle.update()

        # # relatives
        # relatives.create_relatives()

    def _replace_by_project_step(self, element_handle, project_step_id):
        """ 替换为 proeject step id 文件
        
        """
        _element_handle = element_handle
        _element_handle.replace_by_project_step(project_step_id, True)

        # # relatives
        # relatives.create_relatives()

    def _replace_by_derivative(self, element_handle, link_object, link_id):
        _element_handle = element_handle
        _element_handle.replace_by_derivative(link_object, link_id, True)

    def _select_element(self):
        import maya.cmds as cmds
        _index = self.list_view.currentIndex()
        if not _index:
            return
        _data = _index.data()
        # _element_handle = element.ReferenceElement(_data)
        _reference_node = _data.get("reference_node")
        _nodes = cmds.referenceQuery(_reference_node, n = True)
        cmds.select(_nodes, r = True)

    def _change_elements(self):
        """
        """
        self.change_element_by_derivative_menu.clear()
        self.change_element_by_step_menu.clear()
        # get current version
        _index = self.list_view.currentIndex()
        if not _index:
            return
        _data = _index.data()
        _element_handle = element.ReferenceElement(_data)

        _link_handle = zfused_api.objects.Objects(_data["link_object"], _data["link_id"])
        if hasattr(_link_handle, "derivatives"):
            derivatives = _link_handle.derivatives()
            if derivatives:
                for der in derivatives:
                    _obj_handle = zfused_api.objects.Objects(der["object"], der["id"])
                    action = self.change_element_by_derivative_menu.addAction(_obj_handle.name_code())
                    action.triggered.connect(partial(self._replace_by_derivative, _element_handle ,der["object"], der["id"]))
        # self.change_element_menu.exec_(QtGui.QCursor.pos())
        
        # 获取step
        _project_step_handle = zfused_api.step.ProjectStep(_data["project_step_id"])
        # _step = zfused_api.zFused.get("project_step", filter={"ProjectId":  _data["project_id"], "StepId": _project_step_handle.data()["StepId"]})
        _step = zfused_api.zFused.get("project_step", filter={"ProjectId":  _data["project_id"], "Object": _project_step_handle.data().get("Object")})
        if len(_step) >= 2:
            for _s in _step:
                action = self.change_element_by_step_menu.addAction("%s(%s)" % (_s["Name"], _s["Code"]))
                action.triggered.connect(partial(self._replace_by_project_step, _element_handle, _s["Id"]))

        self.change_element_menu.exec_(QtGui.QCursor.pos())

    def refresh_scene(self):
        # get scene elements
        _scene_elements = element.reference_elements() # + element.gpu_elements()
        self.model = listmodel.ListModel(_scene_elements)
        self.proxy_model.setSourceModel(self.model)
        self.list_view.setModel(self.proxy_model)        
        self.list_view.repaint()
        self.refresh.emit(len(_scene_elements))

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setContentsMargins(0,0,0,0)
        _layout.setSpacing(0)

        #  资产列表
        self.list_view = listview.ListView()
        self.list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        _layout.addWidget(self.list_view)
        self.proxy_model = listmodel.ListFilterProxyModel()
        self.item_delegate = itemdelegate.ItemDelegate(self.list_view)
        self.list_view.setItemDelegate(self.item_delegate)

        _layout.addWidget(self.list_view)

        # change element menu
        self.change_element_menu = QtWidgets.QMenu(self)
        self.replace_element_menu = self.change_element_menu.addMenu(u"替换元素")
        self.change_element_by_derivative_menu = self.replace_element_menu.addMenu(u"关联元素")
        self.change_element_by_step_menu = self.replace_element_menu.addMenu(u"关联步骤")
        self.change_element_menu.addSeparator()
        # update element menu
        self.update_element_action = self.change_element_menu.addAction(u"更新至最新")
        self.change_element_menu.addSeparator()
        action = self.change_element_menu.addAction("选择物体")
        action.triggered.connect(self._select_element)