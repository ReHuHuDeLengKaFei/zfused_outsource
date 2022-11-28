# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

from zcore import resource

__all__ = ["ListView"]

logger = logging.getLogger(__name__)

class ListView(QtWidgets.QListView):
    download = QtCore.Signal(QtCore.QModelIndex)
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
        # _menu.setFixedWidth(200)
        _current_index = self.indexAt(pos)
        _index = _current_index.sibling(_current_index.row(),0)
        if _index.isValid():
            _data = _index.data()
            _menu.addSeparator()
            _menu.addAction(QtGui.QIcon(resource.get("icons", "download.png")), u"导入", self._download)
            _menu.addSeparator()
        _menu.exec_(QtGui.QCursor().pos())

    def _download(self):
        _index = self.currentIndex()
        if _index.isValid():
            _data = _index.data()
            self.download.emit(_index)


