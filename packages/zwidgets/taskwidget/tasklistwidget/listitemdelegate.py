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
        _id = _data["Id"]
        _task = zfused_api.task.Task(_id, _data)
        _name = _task.full_name_code().replace("/","_")

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        _rect = option.rect
        _pen = QtGui.QPen(QtGui.QColor(constants.Constants.INFO_TEXT_COLOR), 0.1)
        painter.setPen(_pen)
        painter.setBrush(QtGui.QColor(constants.Constants.INFO_BACKGROUND_COLOR))
        painter.drawRoundedRect(_rect, 0, 0)

        _pixmap = _pixmap = cache.ThumbnailCache.get_pixmap(_task, self.parent().update)
        if _pixmap:
            _pixmap_size = _pixmap.size()
            if _pixmap_size.width() and _pixmap_size.height():
                _label_size = QtCore.QSize( constants.Constants.THUMBNAIL_SIZE[0], 
                                            constants.Constants.THUMBNAIL_SIZE[1] )
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
            _thumbnail_rect = QtCore.QRect( _rect.x(), _rect.y(), 
                                            constants.Constants.THUMBNAIL_SIZE[0], 
                                            constants.Constants.THUMBNAIL_SIZE[1] )
            painter.setBrush(QtGui.QColor(color.LetterColor.color(_data["Name"].lower()[0])))
            painter.drawRoundedRect(_thumbnail_rect, 1, 1)
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 255),
                                      0.2,
                                      QtCore.Qt.DashLine))
            painter.drawRoundedRect(_thumbnail_rect, 1, 1)

        # info widget
        _info_rect = QtCore.QRect(
                _rect.x() + constants.Constants.THUMBNAIL_SIZE[0],
                _rect.y(),
                _rect.width() - constants.Constants.THUMBNAIL_SIZE[0],
                _rect.height()
            )
        #  painter status rect
        _status_rect = QtCore.QRect(
                _info_rect.x(),
                _info_rect.y(),
                _info_rect.width(),
                5
            )
        _status_id = _task.data()["StatusId"]
        _status_handle = zfused_api.status.Status(_status_id)
        painter.setBrush(QtGui.QColor(_status_handle.data()["Color"]))
        painter.drawRoundedRect(_status_rect, 0, 0)
        
        #  绘制任务名
        _font = QtGui.QFont("Microsoft YaHei UI", 9)
        _font.setPixelSize(12)
        _font.setBold(True)
        _fm = QtGui.QFontMetrics(_font)
        painter.setFont(_font)
        painter.setPen(QtGui.QPen(QtGui.QColor(constants.Constants.INFO_TEXT_COLOR), 1))
        _name_code = _task.data()["Name"]
        _name_rect = QtCore.QRect(
                _status_rect.x() + self._extend_width,
                _status_rect.y() + _status_rect.height() + self._spacing,
                _fm.width(_name_code) + self._extend_width,
                20
            )
        painter.drawText(_name_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, _name_code)

        #  绘制任务状态
        _status_handle = zfused_api.status.Status(_task.data()["StatusId"])
        _status_code = _status_handle.name_code()
        _status_rect = QtCore.QRect(
                #_name_rect.x() + _name_rect.width() + self._extend_width,
                _rect.x() + _rect.width() - _fm.width(_status_code) - self._extend_width -self._spacing,
                _name_rect.y() + self._spacing,
                _fm.width(_status_code) + self._extend_width,
                20 - self._spacing*2
            )
        painter.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0), 1))
        painter.setBrush(QtGui.QColor(_status_handle.data()["Color"]))
        painter.drawRoundedRect(_status_rect, 2, 2)
        painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 1))
        painter.drawText(_status_rect, QtCore.Qt.AlignCenter, _status_code)


        # 绘制link
        _project_entity = _task.project_entity()
        if _task.data()["ProjectEntityType"] == "asset":
            _link_full_name = _project_entity.full_name()
        else:
            _link_full_name = _project_entity.full_code()
        _link_rect = QtCore.QRect(
                _name_rect.x(),
                _name_rect.y() + _name_rect.height() + self._spacing,
                _fm.width(_link_full_name),
                20
            )
        painter.setPen(QtGui.QPen(QtGui.QColor(constants.Constants.INFO_TEXT_COLOR), 1))
        painter.drawText(_link_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, _link_full_name)
        
        #  绘制任务步骤
        _project_step_handle = zfused_api.step.ProjectStep(_task.data()["ProjectStepId"])
        #_step_handle = zfused_api.step.Step(_task.data()["StepId"])
        _step_code = _project_step_handle.name_code()
        _step_rect = QtCore.QRect(
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

        #  绘制时间
        _font = QtGui.QFont("Microsoft YaHei UI", 9)
        _font.setPixelSize(12)
        #_font.setBold(True)
        _fm = QtGui.QFontMetrics(_font)
        painter.setFont(_font)
        try:
            _start_time_text = _task.start_time().strftime("%Y-%m-%d")
        except:
            _start_time_text = u"未设置起始时间"
        try:
            _end_time_text = _task.end_time().strftime("%Y-%m-%d")
        except:
            _end_time_text = u"未设置结束时间"
        _time_rect = QtCore.QRect(
                _link_rect.x(),
                _link_rect.y() + _link_rect.height() + self._spacing,
                _info_rect.width() - self._extend_width*2,
                20
            )
        painter.setPen(QtGui.QPen(QtGui.QColor(constants.Constants.INFO_TEXT_COLOR), 1))
        painter.drawText(_time_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, u"{}".format(_start_time_text))
        painter.drawText(_time_rect, QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter, u"{}".format(_end_time_text))

        if _task.start_time() and _task.end_time():
            _time_progress_x = _time_rect.x()
            _time_progress_y = _time_rect.y() + _time_rect.height()
            _time_progress_width = _time_rect.width()
            _time_progress_height = 3
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 0), 1))
            painter.setBrush(QtGui.QColor("#5C5C5C"))
            painter.drawRoundedRect(_time_progress_x, _time_progress_y, _time_progress_width, _time_progress_height, 2, 2)
            if not _task.start_time() > datetime.datetime.now():
                _use_date = _task.end_time() - datetime.datetime.now()
                if _use_date.days <= 0:
                    _use_time_width = _time_progress_width
                else:
                    _all_date = _task.end_time() - _task.start_time()
                    _use_per = _use_date.days/float(_all_date.days)
                    _use_time_width = _time_progress_width * _use_per
                painter.setBrush(QtGui.QColor("#FF0000"))
                painter.drawRoundedRect(_time_progress_x, _time_progress_y, _use_time_width, _time_progress_height, 2, 2)

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
        return QtCore.QSize(constants.Constants.ITEM_DELEGATE_SIZE[0], constants.Constants.ITEM_DELEGATE_SIZE[1])
