# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import os
import re

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource

from zwidgets.widgets import lineedit



class TaskListWidget(QtWidgets.QFrame):

    viewed = QtCore.Signal(int)
    checked = QtCore.Signal(int)
    quick_downloaded = QtCore.Signal(int)
    quick_published = QtCore.Signal(int)

    def __init__(self, parent = None):
        super(TaskListWidget, self).__init__(parent)
        self._build()
        self.search_lineedit.search_clicked.connect(self._search)

        self.listwidget.viewed.connect(self.viewed.emit)
        self.listwidget.checked.connect(self.checked.emit)
        self.listwidget.quick_published.connect(self.quick_published.emit)
        self.listwidget.quick_downloaded.connect(self.quick_downloaded.emit)

    def _search(self, text):
        self.task_proxy_model.search(text)

    def load_project_id(self, project_id):
        # _current_project_id = project_id
        # _tasks = zfused_api.task.cache([_current_project_id], False)
        # model = ListModel(_tasks, self.listwidget)
        # self.task_proxy_model.setSourceModel(model)

        _file_provides = zfused_api.zFused.get("file_provide", filter = {"ProjectId": 44, "CompanyId": 13}, fields = ["Id"])
        if _file_provides:
            _file_provides = zfused_api.fileprovide.cache_from_ids([_file_provide.get("Id") for _file_provide in _file_provides])
        else:
            _file_provides = []
        model = ListModel(_file_provides, self.listwidget)
        self.task_proxy_model.setSourceModel(model)

    def load_datas(self, datas):
        model = ListModel(datas, self.listwidget)
        self.task_proxy_model.setSourceModel(model)

    def showEvent(self, event):
        super(TaskListWidget, self).showEvent(event)

    def _build(self):
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setContentsMargins(0,0,0,0)
        _layout.setSpacing(0)

        self.contant_widget = QtWidgets.QFrame()
        _layout.addWidget(self.contant_widget)
        self.contant_layout = QtWidgets.QVBoxLayout(self.contant_widget)
        self.contant_layout.setContentsMargins(0,0,0,0)
        self.contant_layout.setSpacing(0)
        self.setObjectName("widget")

        # search name
        self.search_lineedit = lineedit.SearchLineEdit()
        self.contant_layout.addWidget(self.search_lineedit)
        self.search_lineedit.setMinimumHeight(24)

        # task list widget
        self.listwidget = ListView()
        self.listwidget.setSpacing(4)
        self.listwidget.setViewMode(QtWidgets.QListView.ListMode)
        self.contant_layout.addWidget(self.listwidget)
        self.listwidget.setObjectName("listwidget")
        self.task_proxy_model = ListFilterProxyModel()
        self.listwidget.setModel(self.task_proxy_model)
        self.listwidget.setItemDelegate(ItemDelegate(self.listwidget))


INFO_BACKGROUND_COLOR = "#222222"
INFO_TEXT_COLOR = "#DDDDDD"


class ItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ItemDelegate, self).__init__(parent)

        self._spacing = 4
        self._extend_width = 10

    def _update_index(self, index):
        self.parent().update()

    def paint(self, painter, option, index):
        _data = index.data()
        _id = _data["Id"]
        _file_provide = zfused_api.fileprovide.FileProvide(_id)
        _task = _file_provide.task()
        _name = _task.full_name_code().replace("/","_")

        _fm = painter.fontMetrics()

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        _rect = option.rect

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor(INFO_BACKGROUND_COLOR))
        painter.drawRoundedRect(_rect, 0, 0)

        _thumbnail_rect = QtCore.QRect( _rect.x(), _rect.y(), 
                                        0, 
                                        _rect.height() )
        # _thumbnail_rect = QtCore.QRect( _rect.x(), _rect.y(), 
        #                                 constants.Constants.THUMBNAIL_SIZE[0], 
        #                                 constants.Constants.THUMBNAIL_SIZE[1] )
        # _pixmap = _pixmap = cache.ThumbnailCache.get_pixmap(_task, partial(self._update_index, index))
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
        #         painter.drawPixmap(_rect.x(), _rect.y(), _thumbnail_pixmap)
        # else:
        #     painter.setBrush(QtGui.QColor(color.LetterColor.color(_data["Name"].lower()[0])))
        #     painter.drawRoundedRect(_thumbnail_rect, 1, 1)
        #     painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 255),
        #                               0.2,
        #                               QtCore.Qt.DashLine))
        #     painter.drawRoundedRect(_thumbnail_rect, 1, 1)

        _field_width = 1/4.0*_rect.width()

        # painter name
        painter.setPen(QtGui.QPen(QtGui.QColor(INFO_TEXT_COLOR), 1))
        _name_rect = QtCore.QRect( _rect.x() + _thumbnail_rect.width() + self._spacing,
                                   _rect.y(),
                                   _field_width,
                                   _rect.height() )
        painter.drawText(_name_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, _name)
        # painter.drawText(_name_rect, QtCore.Qt.AlignCenter, _name)

        _project_entity = _task.project_entity()
        _project_entity_name = _project_entity.full_name()
        _projec_entity_rect = QtCore.QRect( _name_rect.x() + _name_rect.width() + self._spacing,
                                            _rect.y(),
                                            _field_width,
                                            _rect.height() )
        # painter.drawText(_projec_entity_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, _project_entity_name)
        painter.drawText(_projec_entity_rect, QtCore.Qt.AlignCenter, _project_entity_name)

        #  painter status rect
        _status_rect = QtCore.QRect( _projec_entity_rect.x() + _projec_entity_rect.width() + self._spacing,
                                     _rect.y(),
                                     _field_width,
                                     _rect.height() )
        _file_provide_version = int(_file_provide.index())
        _task_version = int(len(_task.versions()))
        _status_name = "已是最新"
        if _file_provide_version != _task_version:
            _status_name = "需要更新"
            painter.setPen(QtGui.QColor("#FF0000"))
        else:
            painter.setPen(QtGui.QColor("#007acc"))
        painter.drawText(_status_rect, QtCore.Qt.AlignCenter, "{}/{} {}".format(_file_provide_version, _task_version, _status_name))
        # painter.drawText(_status_rect, QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter, _status_name)

        # painter time
        painter.setPen(QtGui.QPen(QtGui.QColor(INFO_TEXT_COLOR), 1))
        _created_time_rect = QtCore.QRect( _status_rect.x() + _status_rect.width() + self._spacing,
                                           _rect.y(),
                                           _field_width,
                                           _rect.height() )
        _created_time = _file_provide.created_time().strftime("%Y-%m-%d %H:%M:%S")
        painter.drawText(_created_time_rect, QtCore.Qt.AlignCenter, _created_time)

        if option.state & QtWidgets.QStyle.State_MouseOver:
            bgBrush = QtGui.QBrush(QtGui.QColor(200, 200, 200, 150))
            bgPen = QtGui.QPen(QtGui.QColor(60, 60, 60, 0), 0)
            painter.setPen(bgPen)
            painter.setBrush(bgBrush)
            painter.drawRect(option.rect)
        elif option.state & QtWidgets.QStyle.State_Selected:
            bgBrush = QtGui.QBrush(QtGui.QColor(149, 194, 197, 150))
            bgPen = QtGui.QPen(QtGui.QColor(160, 60, 60, 0), 0)
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


class ListView(QtWidgets.QListView):

    viewed = QtCore.Signal(int)
    checked = QtCore.Signal(int)

    quick_downloaded = QtCore.Signal(int)
    quick_published = QtCore.Signal(int)

    def __init__(self, parent=None):
        super(ListView, self).__init__(parent)

        self.setSpacing(8)

        self.setMouseTracking(True)
        
        # self.setViewMode(QtWidgets.QListView.IconMode)
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


class ListFilterProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(ListFilterProxyModel, self).__init__(parent)

        self._search_text = ""
        self._filter_type_list = []
        self._filter_status_list = []
        self._filter_project_step_list = []

        self._need_update = False

    def search(self, text):
        self._search_text = text
        self.invalidateFilter()

    def _search(self, data):
        if not self._search_text:
            return True
        _low_text = self._search_text.lower()
        _low_text_list = re.split(u"；| |;", _low_text)
        for _low_text in _low_text_list:
            try:
                _in_name = _low_text.lower() in data["Name"].lower()
                if not _in_name:
                    return False
            except:
                pass
        return True

    def filter_project_steps(self, project_step_ids):
        self._filter_project_step_list = project_step_ids
        self.invalidateFilter()

    def filter_type(self, type_list=[]):
        self._filter_type_list = type_list
        self.invalidateFilter()

    def filter_status(self, status_list=[]):
        self._filter_status_list = status_list
        self.invalidateFilter()

    def filter_need_update(self, is_need):
        self._need_update = is_need
        self.invalidateFilter()

    def _filter_need_update(self, data):
        if not self._need_update:
            return True
        _file_provide = zfused_api.fileprovide.FileProvide(data.get("Id"))
        _task = _file_provide.task()
        _file_provide_version = int(_file_provide.index())
        _task_version = int(len(_task.versions()))
        if _file_provide_version != _task_version:
            return True
        return False

    def filterAcceptsRow(self, sourceRow, sourceParent):
        assignedTo_index = self.sourceModel().index(sourceRow, 0, sourceParent)
        _data = self.sourceModel().data(assignedTo_index)
        return ( self._search(_data) and \
                 self._filter_need_update(_data) and \
                 self._filter_status(_data) and \
                 self._filter_type(_data) and \
                 self._filter_project_step(_data))

    def filterAcceptsColumn(self, sourceColumn, sourceParent):
        index0 = self.sourceModel().index(0, sourceColumn, sourceParent)
        return True

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

    def _filter_project_step(self, data):
        if not self._filter_project_step_list:
            return True
        _project_step_id = data["ProjectStepId"]
        if _project_step_id in self._filter_project_step_list:
            return True
        return False

class ListModel(QtCore.QAbstractListModel):
    def __init__(self, data=[], parent=None):
        super(ListModel, self).__init__(parent)
        self._items = data

    def rowCount(self, parent = QtCore.QModelIndex()):
        if self._items:
            return len(self._items)
        return 0

    def data(self, index, role=0):
        if not index.isValid() or not 0 <= index.row() < len(self._items):
            return None
        if role == 0:
            return self._items[index.row()]
        elif role == QtCore.Qt.SizeHintRole:
            return QtCore.QSize(100, 40)
