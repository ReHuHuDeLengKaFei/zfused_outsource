# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function
from functools import partial

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

__all__ = ["ListView"]

logger = logging.getLogger(__name__)

class ListView(QtWidgets.QListView):
    download = QtCore.Signal(QtCore.QModelIndex)
    replace_by_project_step_id = QtCore.Signal(int)
    def __init__(self, parent=None):
        super(ListView, self).__init__(parent)

        self.setSpacing(12)

        self.setMouseTracking(True)
        
        self.setViewMode(QtWidgets.QListView.IconMode)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)

        self.viewport().setAutoFillBackground( False )


        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.custom_context_menu)

    def custom_context_menu(self, pos):
        """ 自定义右击菜单
        """
        _selected_indexs = self.selectionModel().selectedRows()
        _menu = QtWidgets.QMenu(self)
        _menu.setFixedWidth(200)
        _current_index = self.indexAt(pos)
        _index = _current_index.sibling(_current_index.row(),0)
        if _index.isValid():
            _data = _index.data()


            _menu.addSeparator()
            _menu.addAction(QtGui.QIcon(resource.get("icons", "download.png")), u"导入", self._download)

            _menu.addSeparator()
            self.change_element_by_step_menu = _menu.addMenu(u"替换关联步骤")
            _menu.addSeparator()


            # 获取step
            _project_step_handle = zfused_api.step.ProjectStep(_data["project_step_id"])
            _step = zfused_api.zFused.get("project_step", filter={"ProjectId":  _data["project_id"], "Object": _project_step_handle.data().get("Object")})
            if len(_step) >= 2:
                for _s in _step:
                    action = self.change_element_by_step_menu.addAction("%s(%s)" % (_s["Name"], _s["Code"]))
                    action.triggered.connect(partial(self.replace_by_project_step_id.emit, _s["Id"]))


        _menu.exec_(QtGui.QCursor().pos())

    def _download(self):
        _index = self.currentIndex()
        if _index.isValid():
            _data = _index.data()
            self.download.emit(_index)




    # def _change_elements(self):
    #     """
    #     """
    #     self.change_element_by_derivative_menu.clear()
    #     self.change_element_by_step_menu.clear()
    #     # get current version
    #     _index = self.list_view.currentIndex()
    #     if not _index:
    #         return
    #     _data = _index.data()

    #     _element_handle = element.ReferenceElement(_data)

    #     _link_handle = zfused_api.objects.Objects(_data["link_object"], _data["link_id"])
    #     if hasattr(_link_handle, "derivatives"):
    #         derivatives = _link_handle.derivatives()
    #         if derivatives:
    #             for der in derivatives:
    #                 _obj_handle = zfused_api.objects.Objects(der["object"], der["id"])
    #                 action = self.change_element_by_derivative_menu.addAction(_obj_handle.name_code())
    #                 action.triggered.connect(partial(self._replace_by_derivative, _element_handle ,der["object"], der["id"]))
        
    #     # 获取step
    #     _project_step_handle = zfused_api.step.ProjectStep(_data["project_step_id"])
    #     _step = zfused_api.zFused.get("project_step", filter={"ProjectId":  _data["project_id"], "Object": _project_step_handle.data().get("Object")})
    #     if len(_step) >= 2:
    #         for _s in _step:
    #             action = self.change_element_by_step_menu.addAction("%s(%s)" % (_s["Name"], _s["Code"]))
    #             action.triggered.connect(partial(self._replace_by_project_step, _element_handle, _s["Id"]))

    #     self.change_element_menu.exec_(QtGui.QCursor.pos())