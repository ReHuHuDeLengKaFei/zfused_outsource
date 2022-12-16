# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import requests
import datetime
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import cache,color

from . import constants

__all__ = ["ListItemDelegate"]

logger = logging.getLogger(__name__)


class ListItemDelegate(QtWidgets.QStyledItemDelegate):
    THUMBNAIL_PIXMAP = {}
    THUMBNAIL = {}

    def __init__(self, parent=None):
        super(ListItemDelegate, self).__init__(parent)

        self._spacing = 2
        self._extend_width = 10

    def paint(self, painter, option, index):
        _data = index.data()
        _task_id = _data["task_id"]
        _task = zfused_api.task.Task(_task_id)
        _name = _task.name_code().replace("/","_")

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        _rect = option.rect
        _pen = QtGui.QPen(QtGui.QColor(constants.Constants.INFO_TEXT_COLOR), 0.1)
        painter.setPen(_pen)
        painter.setBrush(QtGui.QColor(constants.Constants.INFO_BACKGROUND_COLOR))
        painter.drawRoundedRect(option.rect, 0, 0)

        _pixmap = _pixmap = cache.ThumbnailCache.get_pixmap(_task, self.parent().update)
        if _pixmap:
            _pixmap_size = _pixmap.size()
            if _pixmap_size.width() and _pixmap_size.height():
                _label_size = QtCore.QSize( constants.ITEM_DELEGATE_SIZE[0], 
                                            constants.ITEM_DELEGATE_SIZE[1] )
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
            _thumbnail_rect = QtCore.QRectF( _rect.x(), _rect.y(), 
                                            constants.ITEM_DELEGATE_SIZE[0], 
                                            constants.ITEM_DELEGATE_SIZE[1] )
            painter.setBrush(QtGui.QColor(color.LetterColor.color(_task.code().lower()[0])))
            painter.drawRoundedRect(_thumbnail_rect, 1, 1)
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 255),
                                      0.2,
                                      QtCore.Qt.DashLine))
            painter.drawRoundedRect(_thumbnail_rect, 1, 1)

        # info widget
        _info_rect = QtCore.QRectF(
                _rect.x() + constants.ITEM_DELEGATE_SIZE[0],
                _rect.y(),
                _rect.width() - constants.ITEM_DELEGATE_SIZE[0],
                _rect.height()
            )
        #  painter status rect
        _status_rect = QtCore.QRectF(
                _info_rect.x(),
                _info_rect.y(),
                _info_rect.width(),
                5
            )
        # _status_id = _task.data()["StatusId"]
        # _status_handle = zfused_api.status.Status(_status_id)
        # painter.setBrush(QtGui.QColor(_status_handle.data()["Color"]))
        # painter.drawRoundedRect(_status_rect, 0, 0)

        #  绘制任务名
        _font = painter.font()
        # _font.setPixelSize(12)
        _fm = QtGui.QFontMetrics(_font)
        painter.setFont(_font)
        painter.setPen(QtGui.QPen(QtGui.QColor(constants.Constants.INFO_TEXT_COLOR), 1))
        _name_code = _task.name()
        _name_rect = QtCore.QRectF(
                _status_rect.x() + self._extend_width,
                _status_rect.y() + _status_rect.height() + self._spacing,
                _fm.width(_name_code) + self._extend_width,
                20
            )
        painter.drawText(_name_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, _name_code)

        #  绘制任务状态
        _status_handle = _task.status()
        _status_code = _status_handle.name_code()
        _status_rect = QtCore.QRectF( _rect.x() + _rect.width() - _fm.width(_status_code) - self._extend_width -self._spacing,
                                      _name_rect.y() + self._spacing,
                                      _fm.width(_status_code) + self._extend_width,
                                      20 - self._spacing*2 )
        # painter.setPen(QtCore.Qt.NoPen)
        # painter.setBrush(QtGui.QColor(_status_handle.color()))
        # painter.drawRoundedRect(_status_rect, 2, 2)
        # painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 1))
        # painter.drawText(_status_rect, QtCore.Qt.AlignCenter, _status_code)


        # 绘制link
        _project_entity = _task.project_entity()
        if _task.data()["ProjectEntityType"] == "asset":
            _link_full_name = _project_entity.full_name()
        else:
            _link_full_name = _project_entity.full_code()
        _link_rect = QtCore.QRectF(
                _name_rect.x(),
                _name_rect.y() + _name_rect.height() + self._spacing,
                _fm.width(_link_full_name),
                20
            )
        painter.setPen(QtGui.QPen(QtGui.QColor(constants.Constants.INFO_TEXT_COLOR), 1))
        painter.drawText(_link_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, _link_full_name)
        
        #  绘制任务步骤
        _project_step_handle = _task.project_step()
        _step_code = _project_step_handle.name_code()
        _step_rect = QtCore.QRectF(
                _link_rect.x() + _link_rect.width() + self._extend_width,
                _link_rect.y() + self._spacing,
                _fm.width(_step_code) + self._extend_width,
                20 - self._spacing*2
            )
        painter.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0), 1))
        painter.setBrush(QtGui.QColor(_project_step_handle.color()))
        painter.drawRoundedRect(_step_rect, 2, 2)
        painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 1))
        painter.drawText(_step_rect, QtCore.Qt.AlignCenter, _step_code)


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

    # def sizeHint(self, option, index):
    #     return QtCore.QSize(constants.Constants.ITEM_DELEGATE_SIZE[0], constants.Constants.ITEM_DELEGATE_SIZE[1])
