# coding:utf-8
#--author-- lanhua.zhou
from __future__ import print_function
from functools import partial

import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import resource,language,cache,zfile

from zwidgets.widgets import button


__all__ = ["PreviewWidget"]

logger = logging.getLogger(__name__)

_scale = 1.2 #图片缩放
_spacing = 8 # 图片间隔距离


class PreviewWidget(QtWidgets.QFrame):
    def __init__(self, parent = None):
        super(PreviewWidget, self).__init__(parent)
        self._build()

        self._entity_id = 0
        self._entity_handle = None

        self._preview_items = []
        self.preview_listwidget.doubleClicked.connect(self._show_media)
        # self.new_preview_button.clicked.connect(self._upload_thumbnail)
        # self.preview_listwidget.removed.connect(self._disconnect)

    # def _disconnect(self, md5s):
    #     _links = zfused_api.zFused.get("file_link", filter = {"FileKey__in":"|".join(md5s), "EntityType":"library_entity", "EntityId": self._entity_id} )
    #     for _link in _links:
    #         zfused_api.zFused.delete("file_link", _link.get("Id"))
    #     self._load_preview()

    # def _upload_finish(self, _zfile, _is_ok):
    #     if _zfile.is_media():
    #         if _zfile._cloud_thumbnail_path:
    #             _md5 = _zfile.file_md5()
    #             zfused_api.file.file_link("library_entity", self._entity_id, _md5)
    #             _file = zfused_api.zFused.get("file", filter = {"MD5": _zfile.file_md5()})[-1]
    #             # _library_handle.update_thumbnail_path(_file.get("Path"))
    #             # _thumbnail = _library_handle.get_thumbnail()
    #             # self.thumbnail_button.set_thumbnail(_thumbnail)
    #             # _file = zfused_api.zFused.get("file", filter = {"MD5": _zfile.file_md5()})[-1]
    #             self._entity_handle.update_thumbnail_path(_file.get("ThumbnailPath"))
        
    #     self.progress_bar.hide()
    #     self._load_preview()

    # def _upload_thumbnail(self):
    #     _dialog = QtWidgets.QFileDialog(self)
    #     _dialog.setWindowTitle(u"选择文件")
    #     _dialog.setNameFilter('Images(*{})'.format(' *'.join(zfile.SUPPORT_IMAGE + zfile.SUPPORT_VIDEO)))
    #     _dialog.setFileMode(QtWidgets.QFileDialog.ExistingFiles)
    #     _dialog.setViewMode(QtWidgets.QFileDialog.Detail)
    #     if _dialog.exec():
    #         _file_names = _dialog.selectedFiles()
    #         if _file_names:
    #             _file_name = _file_names[-1]
    #             _zfile = zfile.LocalFile(_file_name, "library/entity/thumbnail")
    #             _zfile.progress_started.connect(self.progress_bar.showNormal)
    #             _zfile.progress_changed.connect(self.progress_bar.setValue)
    #             _zfile.progress_finished.connect(partial(self._upload_finish, _zfile))
    #             _zfile.thread_upload()

    def _show_media(self, index):
        if hasattr(self.window(), "video_player"):
            self._player = self.window().video_player
        else:
            self._player = self.window().parent().video_player
        _file_database = index.data()
        if _file_database:
            self._zfile = zfile.CloudFile( _file_database, self)
            self._zfile.progress_started.connect(self._player.show)
            self._zfile.progress_changed.connect(self._player.set_progress_value)
            self._zfile.progress_finished.connect(self._load_media)
            self._zfile.thread_download()

    def _load_media(self, is_ok):
        if is_ok:
            self._player.show()
            self._player.load_file(self._zfile._file)
        else:
            self._player.close()

    def load_entity(self, entity_id):
        if self._entity_id == entity_id:
            return
        self._entity_id = entity_id
        self._entity_handle = zfused_api.library.LibraryEntity(entity_id)
        _library_handle = zfused_api.library.Library(self._entity_handle.data().get("LibraryId"))
        self._load_preview()

    def _load_preview(self):
        _file_links = zfused_api.zFused.get("file_link", filter = {"EntityType": "library_entity", "EntityId": self._entity_id})
        _items = []
        if _file_links:
            _md5 = [_file_link.get("FileKey") for _file_link in _file_links]
            _items = zfused_api.zFused.get("file", filter = {"MD5__in": "|".join(_md5)})
        self._preview_items = _items
        _model = ListModel(_items, self.preview_listwidget)
        self.preview_listwidget.setModel(_model)
        self.preview_title_button.setText("预览 · {}".format(len(_items)))

    def _build(self):
        """ build widget
        """
        self._zoom = 1.4
        
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.hide()

        # previews widget
        self.preview_widget = QtWidgets.QFrame()
        _layout.addWidget(self.preview_widget)
        self.preview_layout = QtWidgets.QVBoxLayout(self.preview_widget)
        self.preview_layout.setSpacing(0)
        self.preview_layout.setContentsMargins(0,0,0,0)
        # preview title 
        self.preview_title_layout = QtWidgets.QHBoxLayout()
        self.preview_layout.addLayout(self.preview_title_layout)
        self.preview_title_button = QtWidgets.QPushButton()
        self.preview_title_layout.addWidget(self.preview_title_button)
        self.preview_title_button.setText("预览 · 0")
        self.preview_title_button.setObjectName("attr_title_button")
        # # new preview button
        # self.new_preview_button = button.IconButton( self,
        #                                              resource.get("icons", "add.png"),
        #                                              resource.get("icons", "add_hover.png"),
        #                                              resource.get("icons", "add_pressed.png") )
        # self.preview_title_layout.addWidget(self.new_preview_button)
        self.preview_title_layout.addStretch(True)
        # preview listwidget    
        self.preview_listwidget = ListView()
        self.preview_listwidget.setSpacing( _spacing )
        self.preview_listwidget.setFixedHeight(108*_scale + _spacing*2 + 10 )
        self.preview_listwidget.setItemDelegate(ItemDelegate(self.preview_listwidget))
        self.preview_listwidget.setViewMode(QtWidgets.QListView.IconMode)
        self.preview_listwidget.setResizeMode(QtWidgets.QListView.Adjust)
        self.preview_listwidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.preview_listwidget.setFlow(QtWidgets.QListView.LeftToRight)
        self.preview_listwidget.setWrapping(False)
        self.preview_listwidget.setMovement(QtWidgets.QListView.Static)
        self.preview_listwidget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.preview_layout.addWidget(self.preview_listwidget)

        self.setFixedHeight(108*_scale + _spacing*2 + 10 + 20)


class ItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ItemDelegate, self).__init__(parent)

        self._spacing = 8

        self._font = QtGui.QFont("Microsoft YaHei UI", 9)
        self._font.setPixelSize(10)
        self._font.setBold(True)
        self._font_metrics = QtGui.QFontMetrics(self._font)

    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        _rect = option.rect

        painter.setPen(QtGui.QColor("#FFFFFF"))
        painter.setBrush(QtGui.QColor("#FFFFFF"))
        painter.drawRoundedRect(_rect, 4, 4)

        _url = index.data().get("ThumbnailPath")
        _url = _url.split("storage/")[-1]
        _url = "{}/{}".format(zfused_api.zFused.CLOUD_IMAGE_SERVER_ADDR, _url)
        # painter thumbnail
        _pixmap = cache.CloudImageCache.get_pixmap(_url, self.parent().update)
        if _pixmap:
            _pixmap_size = _pixmap.size()
            if _pixmap_size.width() and _pixmap_size.height():
                _label_size = QtCore.QSize( _rect.width(),
                                            _rect.height() )
                scale = max(float(_label_size.width() / float(_pixmap_size.width())),
                            float(_label_size.height()) / float(_pixmap_size.height()))
                _pixmap = _pixmap.scaled( _pixmap_size.width() * scale, 
                                          _pixmap_size.height() * scale,
                                          QtCore.Qt.KeepAspectRatio, 
                                          QtCore.Qt.SmoothTransformation )
                _thumbnail_pixmap = _pixmap.copy( (_pixmap_size.width() * scale - _label_size.width()) / 2.0, 
                                                  (_pixmap_size.height() * scale - _label_size.height()) / 2.0, 
                                                  _label_size.width(), 
                                                  _label_size.height() )
            painter.drawPixmap(_rect.x(), _rect.y(), _thumbnail_pixmap)
        path = QtGui.QPainterPath()
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 1))
        path.addRect(_rect)
        path.addRoundedRect(_rect, 4, 4)
        painter.setBrush(QtGui.QColor("#FFFFFF"))
        path.setFillRule(QtCore.Qt.OddEvenFill)
        painter.drawPath(path)
        
        # draw type
        _fromat_code = index.data().get("Format")
        _format_width = self._font_metrics.width(_fromat_code)
        _format_rect = QtCore.QRectF( _rect.x() + self._spacing, 
                                     _rect.y() + self._spacing, 
                                     _format_width + self._spacing*2,
                                     20 )
        painter.setBrush(QtGui.QColor(0, 122, 204, 180))
        painter.setPen(QtGui.QColor(0,0,0,0))
        painter.drawRoundedRect(_format_rect, 2, 2)
        painter.setFont(self._font)
        painter.setPen(QtGui.QColor("#FFFFFF"))
        painter.drawText( _format_rect, QtCore.Qt.AlignCenter, _fromat_code )

        # else:
        #     painter.setBrush(QtGui.QColor(color.LetterColor.color(_entity_handle.code().lower()[0])))
        #     painter.setPen(QtGui.QColor(0, 0, 0, 0))
        #     painter.drawRoundedRect(_thumbnail_rect, 0, 0)

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

    def sizeHint(self, option, index):
        return QtCore.QSize(192*_scale, 108*_scale)

class ListModel(QtCore.QAbstractListModel):
    def __init__(self, data = [], parent = None):
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

class ListView(QtWidgets.QListView):
    removed = QtCore.Signal(list)
    def __init__(self, parent=None):
        super(ListView, self).__init__(parent)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.custom_context_menu)

    def _remove(self):
        _indexs = self.selectedIndexes()
        if not _indexs:
            return
        _removes = []
        for _index in _indexs:
            _removes.append(_index.data().get("MD5"))
        self.removed.emit(_removes)

    def custom_context_menu(self, pos):
        """ 自定义右击菜单
        """
        _menu = QtWidgets.QMenu(self)
        _index = self.currentIndex()
        _library_id = _index.data().get("LibraryId")
        # _index = _current_index.sibling(_current_index.row(),0)
        if _index.isValid():
            _menu.addSeparator()
            _menu.addAction(QtGui.QIcon(resource.get("icons", "remove.png")), "移出预览", self._remove )
        _menu.exec_(QtGui.QCursor().pos())

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
                # fm = QtGui.QFontMetrics(_font)
                painter.drawText(_rect, QtCore.Qt.AlignCenter, u"暂无预览")
                painter.end()
                return 
        super(ListView, self).paintEvent(event)