# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import logging

from Qt import QtWidgets, QtGui, QtCore

__all__ = ["ListView"]

logger = logging.getLogger(__name__)

class ListView(QtWidgets.QListView):
    def __init__(self, parent=None):
        super(ListView, self).__init__(parent)

        self.setSpacing(2)

        self.setMouseTracking(True)
        # self.setViewMode(QtWidgets.QListView.IconMode)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setMovement(QtWidgets.QListView.Static)

        # self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        # self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

        self.setFrameShape(QtWidgets.QFrame.NoFrame)

        # self.setAcceptDrops(True)
        # self.setDragEnabled(True)
        # self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)

        self.viewport().setAutoFillBackground( False )

    def paintEvent(self, event):
        _model = self.model()
        if _model:
            if isinstance(_model, QtCore.QSortFilterProxyModel):
                _model = _model.sourceModel()
            if not _model or not _model.rowCount():
                _rect = self.rect()
                painter = QtGui.QPainter()
                painter.begin(self.viewport())
                painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
                _font = QtGui.QFont("Microsoft YaHei UI", 8)
                _font.setPixelSize(24)
                _font.setBold(True)
                painter.setFont(_font)
                _pen = QtGui.QPen(QtGui.QColor("#CACACA"), 1, QtCore.Qt.SolidLine)
                _pen.setWidth(0.1)
                painter.setPen(_pen)
                fm = QtGui.QFontMetrics(_font)
                painter.drawText(_rect, QtCore.Qt.AlignCenter, u"暂无数据")
                painter.end()
                return 
        super(ListView, self).paintEvent(event)
