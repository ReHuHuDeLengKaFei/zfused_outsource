# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

from zcore import resource

__all__ = ["ListView"]

logger = logging.getLogger(__name__)

class ListView(QtWidgets.QListView):

    viewed = QtCore.Signal(int)
    checked = QtCore.Signal(int)
    quick_downloaded = QtCore.Signal(int)
    quick_published = QtCore.Signal(int)

    def __init__(self, parent=None):
        super(ListView, self).__init__(parent)

        self.setSpacing(8)

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
        # _menu.setFixedWidth(200)
        _current_index = self.indexAt(pos)
        _index = _current_index.sibling(_current_index.row(),0)
        if _index.isValid():
            _data = _index.data()
            _menu.addSeparator()
            _menu.addAction(QtGui.QIcon(resource.get("icons", "view.png")), u"查看任务信息", self._view)
            _menu.addSeparator()
            _menu.addAction(QtGui.QIcon(resource.get("icons", "check.png")), u"任务检查", self._check)
            _menu.addSeparator()
            _menu.addAction(QtGui.QIcon(resource.get("icons", "download.png")), u"任务文件领取", self._download)
            _menu.addAction(QtGui.QIcon(resource.get("icons", "upload.png")), u"任务文件上传", self._publish)

        _menu.exec_(QtGui.QCursor().pos())

    def _view(self):
        _index = self.currentIndex()
        if _index.isValid():
            _data = _index.data()
            self.viewed.emit(_data.get("Id"))

    def _check(self):
        _index = self.currentIndex()
        if _index.isValid():
            _data = _index.data()
            self.checked.emit(_data.get("Id"))

    def _download(self):
        _index = self.currentIndex()
        if _index.isValid():
            _data = _index.data()
            self.quick_downloaded.emit(_data.get("Id"))

    def _publish(self):
        _index = self.currentIndex()
        if _index.isValid():
            _data = _index.data()
            self.quick_published.emit(_data.get("Id"))