# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import re

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from zwidgets.widgets import lineedit



class VersionListWidget(QtWidgets.QFrame):
    
    def __init__(self, parent = None):
        super(VersionListWidget, self).__init__(parent)
        self._build()

    def load_task_id(self, task_id):
        _task = zfused_api.task.Task(task_id)
        self.load_versions(_task.versions())
        
    def load_versions(self, versions):
        versions.reverse()
        self.model = ListModel(versions)
        self.proxy_model.setSourceModel(self.model)
        self.list_view.setModel(self.proxy_model)

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setContentsMargins(0,0,0,0)
        _layout.setSpacing(0)

        #  资产列表
        self.list_view = ListView()
        _layout.addWidget(self.list_view)
        self.proxy_model = ListFilterProxyModel()
        self.list_view.setItemDelegate(ItemDelegate(self.list_view))


class ItemDelegate(QtWidgets.QStyledItemDelegate):
    THUMBNAIL_PIXMAP = {}
    THUMBNAIL = {}

    def __init__(self, parent=None):
        super(ItemDelegate, self).__init__(parent)

        self._spacing = 4

    def paint(self, painter, option, index):
        _version_data = index.data()
        _version_id = _version_data["Id"]
        _version_handle = zfused_api.version.Version(_version_id, _version_data)

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        _rect = option.rect

        _pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), 0.1)
        painter.setPen(_pen)
        painter.setBrush(QtGui.QColor("#5C5C5C"))
        painter.drawRoundedRect(option.rect, 0, 0)

        _fm = QtGui.QFontMetrics(painter.font())

        # painter index
        _index_str = "%04d"%(_version_handle.data()["Index"])
        _index_rect = QtCore.QRectF(_rect.x(),
                                   _rect.y(),
                                   _fm.width(_index_str) + self._spacing,
                                   _rect.height()
                                    )
        painter.drawText(_index_rect, QtCore.Qt.AlignCenter, _index_str)


        _thumbnail_rect = QtCore.QRectF( _index_rect.x() + _index_rect.width() + self._spacing,
                                         _rect.y(),
                                         0,
                                         _rect.height())
        # # painter thumbnail
        # _thumbnail_rect = QtCore.QRectF( _index_rect.x() + _index_rect.width() + constants.Constants.SPACING,
        #                                  _rect.y(),
        #                                  constants.Constants.THUMBNAIL_SIZE[0],
        #                                  constants.Constants.THUMBNAIL_SIZE[1])
        # _pixmap = cache.ThumbnailCache.get_pixmap(_version_handle, self.parent().parent().update )
        # if _pixmap:
        #     _pixmap_size = _pixmap.size()
        #     if _pixmap_size.width() and _pixmap_size.height():
        #         _label_size = QtCore.QSize( constants.Constants.THUMBNAIL_SIZE[0], 
        #                                     constants.Constants.THUMBNAIL_SIZE[1] )
        #         scale = max(float(_label_size.width() / float(_pixmap_size.width())),
        #                     float(_label_size.height()) / float(_pixmap_size.height()))
        #         _pixmap = _pixmap.scaled( _pixmap_size.width() * scale, 
        #                                   _pixmap_size.height() * scale,
        #                                   QtCore.Qt.KeepAspectRatio, 
        #                                   QtCore.Qt.SmoothTransformation )
        #         _thumbnail_pixmap = _pixmap.copy( (_pixmap_size.width() * scale - _label_size.width()) / 2.0, 
        #                                           (_pixmap_size.height() * scale - _label_size.height()) / 2.0, 
        #                                           _label_size.width(), 
        #                                           _label_size.height() )
        #         painter.drawPixmap(_thumbnail_rect.x(), _thumbnail_rect.y(), _thumbnail_pixmap)
        # else:
        #     painter.setBrush(QtGui.QColor(color.LetterColor.color(_version_data["Name"].lower()[0])))
        #     painter.drawRoundedRect(_thumbnail_rect, 1, 1)
        #     painter.setPen(QtGui.QPen( QtGui.QColor(0, 0, 0, 255), 
        #                                0.2, 
        #                                QtCore.Qt.DashLine))
        #     painter.drawRoundedRect(_thumbnail_rect, 1, 1)

        # painter time
        _pen = QtGui.QPen(QtGui.QColor("#FFFFFF"), 0.1)
        painter.setPen(_pen)
        _create_time_text = _version_handle.created_time().strftime("%Y-%m-%d %H:%M:%S")
        _time_rect = QtCore.QRectF(_thumbnail_rect.x() + _thumbnail_rect.width() + self._spacing,
                                  _rect.y(),
                                  _fm.width(_create_time_text) + self._spacing,
                                  _rect.height())
        painter.drawText(_time_rect, QtCore.Qt.AlignCenter, _create_time_text)

        _name_rect = QtCore.QRectF( _time_rect.x() + _time_rect.width() + self._spacing,
                                    _rect.y(),
                                    0,
                                    _rect.height() )

        # painter description
        _description = _version_handle.description()
        _description_rect = QtCore.QRectF(  _name_rect.x() + _name_rect.width() + self._spacing,
                                            _rect.y(),
                                            _fm.width(_description),
                                            _rect.height() )
        painter.drawText(_description_rect, QtCore.Qt.AlignCenter, _description)

        if option.state & QtWidgets.QStyle.State_Selected:
            bgBrush = QtGui.QBrush(QtGui.QColor(149, 194, 197, 150))
            bgPen = QtGui.QPen(QtGui.QColor(160, 60, 60, 0), 0)
            painter.setPen(bgPen)
            painter.setBrush(bgBrush)
            painter.drawRect(option.rect)
        elif option.state & QtWidgets.QStyle.State_MouseOver:
            bgBrush = QtGui.QBrush(QtGui.QColor(200, 200, 200, 50))
            bgPen = QtGui.QPen(QtGui.QColor(60, 60, 60, 0), 0)
            painter.setPen(bgPen)
            painter.setBrush(bgBrush)
            painter.drawRect(option.rect)
        else:
            bgBrush = QtGui.QBrush(QtGui.QColor(200, 200, 200, 0))
            bgPen = QtGui.QPen(QtGui.QColor(160, 60, 60, 0), 0)
            painter.setPen(bgPen)
            painter.setBrush(bgBrush)
            painter.drawRect(option.rect)

        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(100, 40)


class ListView(QtWidgets.QListView):
    def __init__(self, parent=None):
        super(ListView, self).__init__(parent)
        self.setSpacing(5)
        self.setMouseTracking(True)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.viewport().setAutoFillBackground( False )

    def _paintEvent(self, event):
        super(ListView, self).paintEvent(event)
        _rect = self.rect()
        painter = QtGui.QPainter(self)
        painter.setBrush(QtGui.QColor(255, 255, 0))
        painter.drawRoundedRect(_rect, 0, 0)
        painter.drawText(_rect, QtCore.Qt.AlignCenter, "Name")


class ListFilterProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(ListFilterProxyModel, self).__init__(parent)

        # 状态删选列表
        self._search_text = ""
        self._filter_type_list = []
        self._filter_status_list = []

    def search(self, text):
        self._search_text = text
        self.invalidateFilter()

    def filter_type(self, type_list=[]):
        self._filter_type_list = type_list
        self.invalidateFilter()

    def filter_status(self, status_list=[]):
        self._filter_status_list = status_list
        self.invalidateFilter()

    def filterAcceptsRow(self, sourceRow, sourceParent):
        assignedTo_index = self.sourceModel().index(sourceRow, 0, sourceParent)
        _data = self.sourceModel().data(assignedTo_index)
        return (self._search(_data) and self._filter_status(_data) and self._filter_type(_data))

    def filterAcceptsColumn(self, sourceColumn, sourceParent):
        # print self.headerData(0)

        index0 = self.sourceModel().index(0, sourceColumn, sourceParent)
        return True

    def _search(self, data):
        if not self._search_text:
            return True
        if self._search_text.lower() in data["Name"].lower() or self._search_text.lower() in data["Code"].lower():
            return True
        return False

    def _filter_type(self, data):
        if not self._filter_type_list:
            return True
        if data["TypeId"] in self._filter_type_list:
            return True
        return False

    def _filter_status(self, data):
        if not self._filter_status_list:
            return True
        if data["StatusId"] in self._filter_status_list:
            return True
        return False


class ListModel(QtCore.QAbstractListModel):
    """
    asset model

    """

    def __init__(self, data=[], parent=None):
        super(ListModel, self).__init__(parent)
        self._items = data

    def rowCount(self, parent = QtCore.QModelIndex()):
        """
        return len asset
        """
        if self._items:
            return len(self._items)
        return 0

    def data(self, index, role=0):
        if not index.isValid() or not 0 <= index.row() < len(self._items):
            return None

        if role == 0:
            return self._items[index.row()]
