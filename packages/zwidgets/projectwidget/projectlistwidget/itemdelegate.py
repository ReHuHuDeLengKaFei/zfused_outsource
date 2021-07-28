# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function
from functools import partial

import datetime
import logging

from Qt import QtWidgets, QtGui, QtCore

import zfused_api

from zcore import cache,color,resource

from . import constants

__all__ = ["ItemDelegate"]

logger = logging.getLogger(__name__)


class ItemDelegate(QtWidgets.QStyledItemDelegate):
    THUMBNAIL_PIXMAP = {}
    THUMBNAIL = {}

    def __init__(self, parent=None):
        super(ItemDelegate, self).__init__(parent)

        self._spacing = 15
        self._spacing_height = 6

        self._star_bright_pixmap = QtGui.QPixmap(resource.get("icons", "star_on.png"))


    def _paint_active(self, painter, option, status_item):
        _rect = option.rect
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 0))
        painter.setBrush(QtGui.QColor(constants.Constants.STATUS_BACKGROUND_COLOR))
        painter.drawRoundedRect(option.rect, 1, 1)

        fm = QtGui.QFontMetrics(painter.font())

        painter.setPen(QtGui.QPen(QtGui.QColor("#A5A6A8"), 1))
        _status_text = u"激活 · active"
        _status_rect = QtCore.QRectF(
            _rect.x() + 10, _rect.y(), fm.width(_status_text), _rect.height())
        painter.drawText(_status_rect, QtCore.Qt.AlignLeft |
                         QtCore.Qt.AlignVCenter, _status_text)
        painter.setPen(QtGui.QPen(QtGui.QColor("#A5A6A8"), 1))
        painter.drawLine(_status_rect.x() + _status_rect.width() + 10,
                         _rect.y() + _rect.height()/2.0,
                         _rect.x() + _rect.width(),
                         _rect.y() + _rect.height()/2.0)

    def _paint_status(self, painter, option, status_item):
        _rect = option.rect
        _status_handle = zfused_api.status.Status(status_item.id())

        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 0))
        #painter.setBrush(QtGui.QColor(_status_handle.data()["Color"]))
        painter.setBrush(QtGui.QColor(constants.Constants.STATUS_BACKGROUND_COLOR))
        painter.drawRoundedRect(option.rect, 1, 1)

        fm = QtGui.QFontMetrics(painter.font())

        painter.setPen(QtGui.QPen(QtGui.QColor(_status_handle.data()["Color"]), 1))
        _status_text = u"{} · {}".format(_status_handle.full_name_code(), 
                                         status_item.child_count())
        _status_rect = QtCore.QRectF(_rect.x() + 10, 
                                    _rect.y(), 
                                    fm.width(_status_text), 
                                    _rect.height())
        painter.drawText(_status_rect, QtCore.Qt.AlignLeft |
                         QtCore.Qt.AlignVCenter, _status_text)

        painter.setPen(QtGui.QPen(QtGui.QColor(_status_handle.data()["Color"]), 1))
        painter.drawLine(_status_rect.x() + _status_rect.width() + 10,
                         _rect.y() + _rect.height()/2.0,
                         _rect.x() + _rect.width(),
                         _rect.y() + _rect.height()/2.0)

    def _update(self, index):
        self.parent().update(index)

    def _paint_project(self, painter, option, project_item, index):
        _rect = option.rect
        _project_handle = zfused_api.project.Project(project_item.id())
        painter.setPen(QtGui.QPen(QtGui.QColor(constants.Constants.PROJECT_NAME_COLOR), 0.01))
        painter.setBrush(QtGui.QColor(
            constants.Constants.PROJECT_BACKGROUND_COLOR))
        painter.drawRoundedRect(_rect, 1, 1)
        _id = _project_handle.id()

        _pixmap = cache.ThumbnailCache.get_pixmap(_project_handle, partial(self.parent().update, index))
        _thumbnail_rect = QtCore.QRectF( _rect.x(), _rect.y(),  
                                        constants.THUMBNAIL_SIZE[0], 
                                        constants.THUMBNAIL_SIZE[1] )
        _project_color_x = _rect.x() + self._spacing
        _project_color_y = _rect.y() + self._spacing_height
        _project_color_width = _rect.width() - self._spacing * 2
        _project_color_height = constants.THUMBNAIL_HEIGHT
        if _pixmap:
            _pixmap_size = _pixmap.size()
            if _pixmap_size.width() and _pixmap_size.height():
                _label_size = QtCore.QSize(constants.THUMBNAIL_SIZE[0], 
                                            constants.THUMBNAIL_SIZE[1])
                scale = max(float(_label_size.width() / float(_pixmap_size.width())),
                            float(_label_size.height()) / float(_pixmap_size.height()))
                _pixmap = _pixmap.scaled(_pixmap_size.width() * scale, _pixmap_size.height() * scale, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
                _pixmap = _pixmap.copy((_pixmap_size.width() * scale - _label_size.width()) / 2.0, (_pixmap_size.height(
                ) * scale - _label_size.height()) / 2.0, _label_size.width(), _label_size.height())
            painter.drawPixmap(_rect.x(), _rect.y(), _pixmap)
        else:
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 0), 1))
            painter.setBrush(QtGui.QBrush(
                QtGui.QColor(_project_handle.profile["Color"])))
            painter.drawRoundedRect(_project_color_x, _project_color_y,
                                    _project_color_width, _project_color_height, 4, 4)
        # 绘制color
        _item_color_width = constants.COLOR_DIAMETER
        _item_color_height = constants.COLOR_DIAMETER
        _item_color_x = _rect.x() + (_rect.width() - _item_color_width) / 2.0
        _item_color_y = _thumbnail_rect.y() + _thumbnail_rect.height() - _item_color_height/2.0
        _color_rect = QtCore.QRectF(_item_color_x,
                                       _item_color_y,
                                       _item_color_width,
                                       _item_color_height)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor(_project_handle.color()))
        painter.drawEllipse(_item_color_x, _item_color_y, _item_color_width, _item_color_height)
        # 绘制项目名称
        _project_name_x = _thumbnail_rect.x() + self._spacing
        _project_name_y = _color_rect.y() + _color_rect.height() + self._spacing_height
        _project_name_width = _thumbnail_rect.width() - self._spacing*2
        _project_name_height = 20
        painter.setPen(QtGui.QPen(QtGui.QColor(constants.PROJECT_NAME_COLOR), 1))
        painter.drawText( _project_name_x, _project_name_y, _project_name_width, _project_name_height,
                          QtCore.Qt.AlignCenter, _project_handle.full_name_code())
        
        
        _priority = _project_handle.data().get("Priority")
        if _priority:
            # 绘制项目优先级
            _priority_rect = QtCore.QRectF( _rect.x() + self._spacing,
                                        _project_name_y + 20 +self._spacing_height,
                                        _rect.width() - self._spacing*2,
                                        20 )
            # draw star
            for _index in range(_priority):
                _star_x = _priority_rect.x() + _index*20
                _star_y = _priority_rect.y()
                # if self._starCount > _index:
                #     painter.drawPixmap(_star_x, _star_y, self._star_bright_pixmap)
                # else:
                #     painter.drawPixmap(_star_x, _star_y, self._star_dark_pixmap)
                painter.drawPixmap(_star_x, _star_y, self._star_bright_pixmap)
        
        # 绘制项目时间
        _font = QtGui.QFont("Microsoft YaHei UI",9)  
        _font.setPixelSize(11)      
        painter.setFont(_font)
        _project_time_x = _rect.x() + self._spacing
        _project_time_width = _rect.width() - self._spacing*2
        _project_time_height = 15
        _project_time_y = _rect.y() + _rect.height() - _project_time_height - self._spacing_height*2
        _start_time = _project_handle.start_time()
        _end_time = _project_handle.end_time()
        if _start_time and _end_time:
            # 绘制起始时间
            _font = QtGui.QFont("Microsoft YaHei UI", 8)
            _font.setPixelSize(12)
            painter.setFont(_font)
            painter.setPen(QtGui.QPen(QtGui.QColor(constants.PROJECT_NAME_COLOR), 1))
            fm = QtGui.QFontMetrics(_font)
            _start_time_text = _start_time.strftime("%Y-%m-%d")
            _end_time_text = _end_time.strftime("%Y-%m-%d")
            _time_text = "{0} - {1}".format(_start_time_text, _end_time_text)
            _time_start_x = _rect.x() + self._spacing
            _time_start_width = fm.width(_start_time_text) + self._spacing
            _time_start_height = 10
            _time_start_y = _rect.y() + _rect.height() - 30
            painter.drawText(_time_start_x, _time_start_y, _time_start_width, _time_start_height,
                             QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter|QtCore.Qt.AlignTop, _start_time_text) 
            _time_end_width = fm.width(_end_time_text)
            _time_end_height = 10
            _time_end_x = _rect.x() + _rect.width() - _time_end_width - self._spacing
            _time_end_y = _rect.y() + _rect.height() - 30
            painter.drawText(_time_end_x, _time_end_y, _time_end_width, _time_end_height,
                             QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter|QtCore.Qt.AlignTop, _end_time_text) 
            _time_progress_x = _time_start_x
            _time_progress_y = _time_start_y + _project_time_height
            _time_progress_width = _rect.x() + _rect.width() - _time_progress_x - self._spacing
            _time_progress_height = 2
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 0), 1))
            painter.setBrush(QtGui.QColor("#555555"))
            painter.drawRoundedRect(_time_progress_x, _time_progress_y, _time_progress_width, _time_progress_height, 2, 2)  
            if not _project_handle.start_time() > datetime.datetime.now():
                if _project_handle.end_time() < datetime.datetime.now():
                    painter.setBrush(QtGui.QColor("#FF0000"))
                else:
                    painter.setBrush(QtGui.QColor("#007acc"))
                _use_date = datetime.datetime.now() - _project_handle.start_time()
                if _use_date.days <= 0:
                    _use_time_width = _time_progress_width
                else:
                    _all_date = _project_handle.end_time() - _project_handle.start_time()
                    _use_per = _use_date.days/float(_all_date.days)
                    _use_time_width = _time_progress_width * _use_per
                _use_time_width = min(_time_progress_width, _use_time_width)
                painter.drawRoundedRect(_time_progress_x, _time_progress_y, _use_time_width, _time_progress_height, 2, 2)

    def paint(self, painter, option, index):
        _item = index.data()
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        _font = QtGui.QFont("Microsoft YaHei UI", 9)
        _font.setPixelSize(14)
        _font.setBold(True)
        painter.setFont(_font)

        if _item.object() == "status":
            self._paint_status(painter, option, _item)
        elif _item.object() == "active":
            self._paint_active(painter, option, _item)
        elif _item.object() == "project":
            self._paint_project(painter, option, _item, index)

        if _item.object() == "project":
            if option.state & QtWidgets.QStyle.State_MouseOver:
                bgBrush = QtGui.QBrush(QtGui.QColor(200, 200, 200, 150))
                bgPen = QtGui.QPen(QtGui.QColor(60, 60, 60, 0), 0)
                painter.setPen(bgPen)
                painter.setBrush(bgBrush)
                painter.drawRect(option.rect)
            elif option.state & QtWidgets.QStyle.State_Selected:
                bgBrush = QtGui.QBrush(QtGui.QColor(255, 255, 255, 150))
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
        _item = index.data()
        if _item.object() == "status":
            return QtCore.QSize(self.parent().width(), 20)
        if _item.object() == "active":
            return QtCore.QSize(self.parent().width(), 20)
        elif _item.object() == "project":
            return QtCore.QSize(constants.Constants.ITEM_DELEGATE_SIZE[0], constants.Constants.ITEM_DELEGATE_SIZE[1])