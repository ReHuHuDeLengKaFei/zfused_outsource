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

    def paint(self, painter, option, index):

        self._font = painter.font()

        _data = index.data()
        _id = _data["Id"]
        _assembly = zfused_api.assembly.Assembly(_id)
        _name = _assembly.full_name_code().replace("/","_")

        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        _rect = option.rect
        _pen = QtGui.QPen(QtGui.QColor(constants.Constants.INFO_TEXT_COLOR), 0.1)
        painter.setPen(_pen)
        painter.setBrush(QtGui.QColor(constants.Constants.INFO_BACKGROUND_COLOR))
        painter.drawRoundedRect(option.rect, 0, 0)

        _thumbnail_rect = QtCore.QRectF( _rect.x(), _rect.y(), 
                                        constants.THUMBNAIL_SIZE[0], 
                                        constants.THUMBNAIL_SIZE[1] )

        # _pixmap = cache.ThumbnailCache.get_pixmap(_assembly, self.parent().parent().update)
        # if _pixmap:
        #     _pixmap_size = _pixmap.size()
        #     if _pixmap_size.width() and _pixmap_size.height():
        #         _label_size = QtCore.QSize(constants.THUMBNAIL_SIZE[0], 
        #                                     constants.THUMBNAIL_SIZE[1])
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
        #         # self.THUMBNAIL_PIXMAP[_id] = _thumbnail_pixmap
        #         painter.drawPixmap(_rect.x(), _rect.y(), _thumbnail_pixmap)
        # else:
        #     painter.setBrush(QtGui.QColor(color.LetterColor.color(_assembly.code().lower()[0])))
        #     painter.drawRoundedRect(_thumbnail_rect, 1, 1)
        #     painter.setPen(QtGui.QPen(QtGui.QColor(
        #         0, 0, 0, 255), 0.2, QtCore.Qt.DashLine))
        #     painter.drawRoundedRect(_thumbnail_rect, 1, 1)


        # # 绘制 name
        # self._font.setPixelSize(13)
        # self._font.setBold(True)
        # painter.setFont(self._font)
        painter.setPen(QtGui.QPen(QtGui.QColor("#333333")))
        _link_full_name = _assembly.full_name().replace("/"," - ")
        _link_rect = QtCore.QRectF( _thumbnail_rect.x() + self._extend_width,
                                   _thumbnail_rect.y() + _thumbnail_rect.height() + self._spacing,
                                   _thumbnail_rect.width() - self._extend_width*2 ,
                                   20 )
        painter.drawText(_link_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, _link_full_name)

        # 绘制 code
        painter.setPen(QtGui.QPen(QtGui.QColor("#666666")))
        _step_rect = QtCore.QRectF( _link_rect.x(),
                                   _link_rect.y() + _link_rect.height() + self._spacing,
                                   _link_rect.width(),
                                   20 )
        _project_step_name = _assembly.code()
        painter.drawText(_step_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, _project_step_name)

        #  绘制任务名
        # self._font.setPixelSize(12)
        # self._font.setBold(False)
        # _fm = QtGui.QFontMetrics(self._font)
        # painter.setFont(self._font)
        # painter.setPen(QtGui.QPen(QtGui.QColor(constants.INFO_TEXT_COLOR), 1))
        # if _assembly:
        #     _name_code = _assembly.data()["Name"]
        # else:
        #     _name_code = "暂无任务"
        # _name_rect = QtCore.QRectF( _step_rect.x(),
        #                            _step_rect.y() + _step_rect.height() + self._spacing,
        #                            _step_rect.width() ,
        #                            24 )
        # painter.drawText(_name_rect, QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter, _name_code)

        # #  绘制任务状态
        # _status_handle = zfused_api.status.Status(_assembly.data()["StatusId"])
        # _status_code = _status_handle.name()
        # _status_width = _fm.width(_status_code) + self._extend_width
        # _status_rect = QtCore.QRectF( _rect.x() + (_rect.width() - _status_width)/2,
        #                              _rect.y() + _rect.height() - 20,
        #                              _status_width,
        #                              20 )
        # painter.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0), 1))
        # painter.setBrush(QtGui.QColor(_status_handle.data()["Color"]))
        # painter.drawRoundedRect(_status_rect, 2, 2)
        # painter.setPen(QtGui.QPen(QtGui.QColor("#FFFFFF"), 1))
        # painter.drawText(_status_rect, QtCore.Qt.AlignCenter, _status_code)

        # # draw line
        # _status_rect = QtCore.QRectF( _rect.x(), 
        #                              _rect.y() + _rect.height() - 4,
        #                              _rect.width(),
        #                              4)
        # painter.setPen(QtGui.QPen(QtGui.QColor(0,0,0,0), 1))
        # painter.setBrush(QtGui.QBrush(QtGui.QColor(_status_handle.color())))
        # painter.drawRoundedRect(_status_rect, 0, 0 )

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

    # def sizeHint(self, option, index):
    #     return QtCore.QSize(constants.ITEM_DELEGATE_SIZE[0], constants.ITEM_DELEGATE_SIZE[1])