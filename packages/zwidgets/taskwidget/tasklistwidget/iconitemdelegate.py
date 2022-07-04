# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import datetime
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import cache,color

from . import constants

__all__ = ["IconItemDelegate"]

logger = logging.getLogger(__name__)


class IconItemDelegate(QtWidgets.QStyledItemDelegate):
    THUMBNAIL_PIXMAP = {}
    THUMBNAIL = {}

    def __init__(self, parent=None):
        super(IconItemDelegate, self).__init__(parent)

        self._spacing = 2
        self._extend_width = 10

        self._font = QtGui.QFont("Microsoft YaHei UI", 9)

    def paint(self, painter, option, index):
        _data = index.data()
        _id = _data["Id"]
        _task_handle = zfused_api.task.Task(_id, _data)
        _project_entity_handle = _task_handle.project_entity() # zfused_api.objects.Objects(_task_handle.data()["ProjectEntityType"], _task_handle.data()["ProjectEntityId"])
        _project_step_handle = _task_handle.project_step() # zfused_api.step.ProjectStep(_task_handle.data()["ProjectStepId"])
        _name = _task_handle.full_name_code().replace("/","_")

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        _rect = option.rect
        _pen = QtGui.QPen(QtGui.QColor(constants.Constants.INFO_TEXT_COLOR), 0.1)
        painter.setPen(_pen)
        painter.setBrush(QtGui.QColor(constants.Constants.INFO_BACKGROUND_COLOR))
        painter.drawRoundedRect(option.rect, 0, 0)

        _pixmap = cache.ThumbnailCache.get_pixmap(_project_entity_handle, self.parent().parent().update)

        _thumbnail_rect = QtCore.QRectF( _rect.x(), _rect.y(), 
                                        constants.THUMBNAIL_SIZE[0], 
                                        constants.THUMBNAIL_SIZE[1] )
        if _pixmap:
            _pixmap_size = _pixmap.size()
            if _pixmap_size.width() and _pixmap_size.height():
                _label_size = QtCore.QSize(constants.THUMBNAIL_SIZE[0], 
                                            constants.THUMBNAIL_SIZE[1])
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
                # self.THUMBNAIL_PIXMAP[_id] = _thumbnail_pixmap
                painter.drawPixmap(_rect.x(), _rect.y(), _thumbnail_pixmap)
        else:
            painter.setBrush(QtGui.QColor(color.LetterColor.color(_task_handle.code().lower()[0])))
            painter.drawRoundedRect(_thumbnail_rect, 1, 1)
            painter.setPen(QtGui.QPen(QtGui.QColor(
                0, 0, 0, 255), 0.2, QtCore.Qt.DashLine))
            painter.drawRoundedRect(_thumbnail_rect, 1, 1)

        # 绘制link
        self._font.setPixelSize(12)
        self._font.setBold(True)
        painter.setFont(self._font)
        _project_handle = zfused_api.project.Project(_project_entity_handle.data()["ProjectId"])
        painter.setPen(QtGui.QPen(QtGui.QColor("#222222")))
        if _project_entity_handle.object() == "asset":
            _link_full_name = _project_entity_handle.full_name()
        else:
            _link_full_name = _project_entity_handle.full_code()
        _link_rect = QtCore.QRectF( _thumbnail_rect.x() + self._extend_width,
                                   _thumbnail_rect.y() + _thumbnail_rect.height() + self._spacing,
                                   _thumbnail_rect.width() - self._extend_width*2 ,
                                   20 )
        painter.drawText(_link_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, _link_full_name)

        # 绘制project step
        _step_rect = QtCore.QRectF( _link_rect.x(),
                                   _link_rect.y() + _link_rect.height() + self._spacing,
                                   _link_rect.width(),
                                   20 )
        if _project_step_handle:
            painter.setPen(QtGui.QPen(QtGui.QColor(_project_step_handle.color())))
            _project_step_name = _project_step_handle.name_code()
        else:
            painter.setPen(QtGui.QPen(QtGui.QColor("#FF0000")))
            _project_step_name = "还未选择任务步骤"
        self._font.setBold(True)
        painter.setFont(self._font)
        painter.drawText(_step_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, _project_step_name)

        #  绘制任务名
        self._font.setPixelSize(12)
        self._font.setBold(False)
        _fm = QtGui.QFontMetrics(self._font)
        painter.setFont(self._font)
        painter.setPen(QtGui.QPen(QtGui.QColor(constants.INFO_TEXT_COLOR), 1))
        if _task_handle:
            _name_code = _task_handle.data()["Name"]
        else:
            _name_code = "暂无任务"
        _name_rect = QtCore.QRectF( _step_rect.x(),
                                   _step_rect.y() + _step_rect.height() + self._spacing,
                                   _step_rect.width() ,
                                   24 )
        painter.drawText(_name_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, _name_code)

        #  绘制任务状态
        _status_handle = zfused_api.status.Status(_task_handle.data()["StatusId"])
        _status_code = _status_handle.name()
        _status_width = _fm.width(_status_code) + self._extend_width
        _status_rect = QtCore.QRectF( _rect.x() + (_rect.width() - _status_width)/2,
                                     _rect.y() + _rect.height() - 20,
                                     _status_width,
                                     20 )
        painter.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0), 1))
        painter.setBrush(QtGui.QColor(_status_handle.data()["Color"]))
        painter.drawRoundedRect(_status_rect, 2, 2)
        painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 1))
        painter.drawText(_status_rect, QtCore.Qt.AlignCenter, _status_code)

        # draw line
        _status_rect = QtCore.QRectF( _rect.x(), 
                                     _rect.y() + _rect.height() - 4,
                                     _rect.width(),
                                     4)
        painter.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0), 1))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(_status_handle.color())))
        painter.drawRoundedRect(_status_rect, 0, 0 )

        _name = "子任务"
        _name_width = _fm.width(_name) + self._spacing
        _name_height = _fm.height()
        _sub_task_rect = QtCore.QRect( _rect.x() + ( _rect.width() - _name_width) / 2,
                                       _rect.y() + self._spacing,
                                       _name_width,
                                       _name_height)
        if _task_handle.is_sub_task():
            painter.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0), 1))
            painter.setBrush(QtGui.QBrush(QtGui.QColor("#e1a021")))
            painter.drawRoundedRect(_sub_task_rect, 2, 2)
            painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 1))
            painter.drawText( _sub_task_rect, QtCore.Qt.AlignCenter, _name)
        if _task_handle.has_sub_task():
            painter.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0), 1))
            painter.setBrush(QtGui.QBrush(QtGui.QColor("#007fce")))
            painter.drawRoundedRect(_sub_task_rect, 2, 2)
            painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 1))
            painter.drawText(_sub_task_rect, QtCore.Qt.AlignCenter, "主任务")


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
        return QtCore.QSize(constants.ITEM_DELEGATE_SIZE[0], constants.ITEM_DELEGATE_SIZE[1])