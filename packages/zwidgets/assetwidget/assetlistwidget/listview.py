# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

from zcore import resource

logger = logging.getLogger(__name__)

class ListView(QtWidgets.QListView):
    referenced = QtCore.Signal(int)
    def __init__(self, parent=None):
        super(ListView, self).__init__(parent)

        self.setSpacing(5)
        self.setMouseTracking(True)
        #self.setSelectionRectVisible(True)
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
        _menu = QtWidgets.QMenu(self)
        _current_index = self.indexAt(pos)
        _index = _current_index.sibling(_current_index.row(),0)
        if _index.isValid():
            _menu.addAction(QtGui.QIcon(resource.get("icons", "down.png")), u"引用文件" , self._reference )
        _menu.exec_(QtGui.QCursor().pos())

    def _reference(self):
        _asset_id = self.currentIndex().data().get("Id")
        self.referenced.emit(_asset_id)

    def _paintEvent(self, event):
        super(ListView, self).paintEvent(event)
        _rect = self.rect()
        painter = QtGui.QPainter(self)
        painter.setBrush(QtGui.QColor(255, 255, 0))
        painter.drawRoundedRect(_rect, 0, 0)
        painter.drawText(_rect, QtCore.Qt.AlignCenter, "Name")

    def scrollContentsBy(self, x, y):
        self.setUpdatesEnabled(False)
        super(ListView, self).scrollContentsBy(x, y)
        self.setUpdatesEnabled(True)