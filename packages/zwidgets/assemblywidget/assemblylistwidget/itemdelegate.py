# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function
from functools import partial

import time
import logging
import threading

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import cache,color,resource

from . import constants

__all__ = ["ItemDelegate"]

logger = logging.getLogger(__name__)


_star_bright_pixmap = QtGui.QPixmap(resource.get("icons", "star.png"))


class ItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent = None):
        super(ItemDelegate, self).__init__(parent)
        self._spacing = 4
        self._file_pixmap = QtGui.QPixmap(resource.get("icons", "file_hover.png"))
        self._file_pixmap = self._file_pixmap.scaled(20,20,QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

    def _update(self, index):
        self.parent().update(index)

    def paint(self, painter, option, index):
        _assembly_data = index.data()
        _assembly_id = _assembly_data["Id"]
        _assembly_handle = zfused_api.assembly.Assembly(_assembly_id)
        #_name = _assembly_handle.full_name_code().replace("/","_")

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        _rect = option.rect

        if not option.state & QtWidgets.QStyle.State_MouseOver:
            _rect = QtCore.QRect( _rect.x() + self._spacing, 
                                  _rect.y() + self._spacing,
                                  _rect.width() - self._spacing*2,
                                  _rect.height() - self._spacing*2)

        _pen = QtGui.QPen(QtGui.QColor("#343D46"), 0.1)
        painter.setPen(_pen)
        painter.setBrush(QtGui.QColor(62, 62, 62))
        painter.drawRoundedRect(_rect, 0, 0)

        _pixmap = _pixmap = cache.ThumbnailCache.get_pixmap(_assembly_handle, self.parent().update)
        if _pixmap:
            _pixmap_size = _pixmap.size()
            if _pixmap_size.width() and _pixmap_size.height():
                _label_size = QtCore.QSize(
                    _rect.width(), constants.Constants.THUMBNAIL_HEIGHT)
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
        else:
            _thumbnail_rect = QtCore.QRect( _rect.x(), 
                                            _rect.y(), 
                                            _rect.width(), 
                                            constants.Constants.THUMBNAIL_HEIGHT)
            painter.setBrush(QtGui.QColor(color.LetterColor.color(_assembly_handle.code().lower()[0])))
            painter.drawRoundedRect(_thumbnail_rect, 1, 1)
            painter.setPen(QtGui.QColor(0, 0, 0, 255))
            painter.drawRoundedRect(_thumbnail_rect, 1, 1)

        # painter name
        _name_rect = QtCore.QRect( _rect.x(), 
                                   _rect.y() + constants.Constants.THUMBNAIL_HEIGHT ,
                                   _rect.width(), constants.Constants.INFOMATION_HEIGHT*2 )
        painter.setBrush(QtGui.QColor(constants.Constants.NAME_BACKGROUND_COLOR))
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 1))
        painter.drawRoundedRect(_name_rect, 0, 0)
        _font = QtGui.QFont("Microsoft YaHei UI", 12)
        _font.setPixelSize(constants.Constants.FONT_SIZE)
        _font.setBold(True)
        painter.setFont(_font)
        painter.setPen(QtGui.QPen(QtGui.QColor(constants.Constants.NAME_COLOR), 1))
        _name = _assembly_handle.full_name().replace("/"," - ")
        _name_rect = QtCore.QRect( _rect.x() + self._spacing, 
                                   _rect.y() + constants.Constants.THUMBNAIL_HEIGHT ,
                                   _rect.width(), constants.Constants.INFOMATION_HEIGHT )
        painter.drawText(_name_rect, QtCore.Qt.AlignCenter, _name)
        _code_rect = QtCore.QRect( _rect.x() + self._spacing, 
                                   _rect.y() + constants.Constants.THUMBNAIL_HEIGHT + constants.Constants.INFOMATION_HEIGHT ,
                                   _rect.width(), constants.Constants.INFOMATION_HEIGHT )
        _font.setBold(False)
        painter.setFont(_font)
        painter.setPen(QtGui.QPen(QtGui.QColor(constants.Constants.CODE_COLOR), 1))
        _code = _assembly_handle.code()
        painter.drawText(_code_rect, QtCore.Qt.AlignCenter, _code)

        # file
        _sync_rect = QtCore.QRect( _rect.x(), 
                                   _rect.y() + _rect.height() - 30,
                                   _rect.height(),
                                   30 )
        painter.drawPixmap( _sync_rect.x() + self._spacing,
                            _sync_rect.y() + 5,
                            self._file_pixmap )
        painter.setPen(QtGui.QPen(QtGui.QColor("#EDEDED"), 1))
        # painter.drawText( _sync_rect.x() + self._spacing*2 + 20,
        #                 _sync_rect.y(),
        #                 50,30,
        #                 QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter,
        #                 u"{} 版本".format(len(_assembly_handle.data())) )

        # # painter status
        # _fm = QtGui.QFontMetrics(_font)
        # _status_id = _assembly_handle.status_id()
        # _status_handle = zfused_api.status.Status(_status_id)
        # _status_text = _status_handle.name_code()
        # _status_width = _fm.width(_status_text) + self._spacing
        # _status_color = _status_handle.color()
        # _status_rect = QtCore.QRect( _rect.x() + _rect.width() - _status_width, 
        #                              _rect.y(),
        #                              _status_width,
        #                              constants.Constants.LEVEL_HEIGHT)
        # painter.setBrush(QtGui.QColor(_status_color))
        # painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 1))
        # painter.drawRoundedRect(_status_rect, 0, 0)
        # painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1))
        # painter.drawText(_status_rect, QtCore.Qt.AlignCenter, _status_text)

        if option.state & QtWidgets.QStyle.State_MouseOver:
            painter.setPen(QtGui.QColor(0, 122, 204, 0))
            painter.setBrush(QtGui.QColor(0, 122, 204, 30))
            painter.drawRect(_rect)
        elif option.state & QtWidgets.QStyle.State_Selected:
            painter.setPen(QtGui.QColor(0, 122, 204, 0))
            painter.setBrush(QtGui.QColor(0, 122, 204, 50))
            painter.drawRect(_rect)
        else:
            painter.setPen(QtGui.QColor(255, 255, 255, 0))
            painter.setBrush(QtGui.QColor(200, 200, 200, 0))
            painter.drawRect(_rect)

        painter.restore()

    def sizeHint(self, option, index):
        return QtCore.QSize(constants.Constants.ITEM_DELEGATE_SIZE[0], constants.Constants.ITEM_DELEGATE_SIZE[1])
